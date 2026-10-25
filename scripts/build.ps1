param(
    [ValidateSet('all', 'adb-helper', 'gpt-viewer', 'paper-viewer')]
    [string]$App = 'all',
    [string]$JavaHome,
    [string]$SdkRoot
)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
$localConfigPath = Join-Path $repoRoot 'toolchain.local.json'
$localConfig = if (Test-Path -LiteralPath $localConfigPath) { Get-Content -LiteralPath $localConfigPath -Raw | ConvertFrom-Json } else { $null }
if (-not $JavaHome) { $JavaHome = if ($localConfig.javaHome) { $localConfig.javaHome } else { $env:JAVA_HOME } }
if (-not $SdkRoot) { $SdkRoot = if ($localConfig.sdkRoot) { $localConfig.sdkRoot } else { $env:ANDROID_HOME } }
if (-not $SdkRoot) { throw 'Pass -SdkRoot or configure toolchain.local.json / ANDROID_HOME.' }
$previousJava = $env:JAVA_HOME
$previousAndroid = $env:ANDROID_HOME
try {
    if ($JavaHome) { $env:JAVA_HOME = $JavaHome }
    $sdkPath = (Resolve-Path -LiteralPath $SdkRoot).Path.Replace([char]92, [char]47)
    $env:ANDROID_HOME = $sdkPath
    $sdkProperty = $sdkPath.Replace(':', '\:')
    [System.IO.File]::WriteAllText((Join-Path $repoRoot 'local.properties'), "sdk.dir=$sdkProperty`n", [System.Text.UTF8Encoding]::new($false))
    $apps = if ($App -eq 'all') { @('adb-helper', 'gpt-viewer', 'paper-viewer') } else { @($App) }
    $tasks = @()
    foreach ($name in $apps) {
        $tasks += ":${name}:assembleDebug", ":${name}:lintDebug"
        if ($name -eq 'paper-viewer') { $tasks += ':paper-viewer:testDebugUnitTest' }
    }
    & (Join-Path $repoRoot 'gradlew.bat') -p $repoRoot --no-daemon --console=plain @tasks
    if ($LASTEXITCODE -ne 0) { throw 'Android build or verification failed.' }
    $output = Join-Path $repoRoot 'dist'
    New-Item -ItemType Directory -Force -Path $output | Out-Null
    foreach ($name in $apps) {
        $source = Join-Path $repoRoot "build/$name/outputs/apk/debug/$name-debug.apk"
        Copy-Item -LiteralPath $source -Destination (Join-Path $output "$name-android-debug.apk") -Force
    }

    # One inventory for every APK in the flat distribution folder.
    $tools = Join-Path $sdkPath 'build-tools/36.0.0'
    $packages = @{
        'adb-helper-android-debug.apk' = 'dev.rokidapps.adbhelper'
        'gpt-viewer-android-debug.apk' = 'dev.rokidapps.gptviewer'
        'paper-viewer-android-debug.apk' = 'dev.rokidapps.paperviewer'
    }
    $artifacts = @()
    foreach ($apk in (Get-ChildItem -LiteralPath $output -File -Filter '*.apk' | Sort-Object Name)) {
        $badging = (& (Join-Path $tools 'aapt.exe') dump badging $apk.FullName) -join "`n"
        if ($LASTEXITCODE -ne 0) { throw "Could not inspect $($apk.Name)." }
        $packageMatch = [regex]::Match($badging, "package: name='([^']+)' versionCode='([^']+)' versionName='([^']*)'")
        if (-not $packageMatch.Success) { throw "Missing package metadata: $($apk.Name)." }
        $permissions = @([regex]::Matches($badging, "(?m)^uses-permission[^:]*: name='([^']+)'") | ForEach-Object { $_.Groups[1].Value })
        $project = $packages.ContainsKey($apk.Name)
        $backupDisabled = $null
        if ($project) {
            if ($packageMatch.Groups[1].Value -ne $packages[$apk.Name]) { throw 'Unexpected project APK package.' }
            if ($permissions.Count -ne 0) { throw 'Project APK unexpectedly requests permissions.' }
            $manifest = (& (Join-Path $tools 'aapt.exe') dump xmltree $apk.FullName AndroidManifest.xml) -join "`n"
            if ($LASTEXITCODE -ne 0) { throw 'Could not inspect project manifest.' }
            $backupDisabled = $manifest -match 'allowBackup[^\n]*0x0\s*(\n|$)'
            if (-not $backupDisabled -or $manifest -notmatch 'dataExtractionRules') { throw 'Project backup exclusions are missing.' }
            if ($badging -notmatch "sdkVersion:'31'" -or $badging -notmatch "targetSdkVersion:'36'" -or $badging -notmatch 'launchable-activity:') { throw 'Unexpected project Android compatibility metadata.' }
        }
        $null = & (Join-Path $tools 'apksigner.bat') verify $apk.FullName
        if ($LASTEXITCODE -ne 0) { throw "APK signature verification failed: $($apk.Name)." }
        $null = & (Join-Path $tools 'zipalign.exe') -c 4 $apk.FullName
        if ($LASTEXITCODE -ne 0) { throw "APK alignment verification failed: $($apk.Name)." }
        $origin = if ($project) { 'project' } else { 'external' }
        $artifacts += [ordered]@{
            file = $apk.Name
            origin = $origin
            package = $packageMatch.Groups[1].Value
            version = $packageMatch.Groups[3].Value
            versionCode = $packageMatch.Groups[2].Value
            minSdk = [regex]::Match($badging, "(?m)^sdkVersion:'([^']+)'").Groups[1].Value
            targetSdk = [regex]::Match($badging, "(?m)^targetSdkVersion:'([^']+)'").Groups[1].Value
            bytes = $apk.Length
            sha256 = (Get-FileHash -LiteralPath $apk.FullName -Algorithm SHA256).Hash.ToLower()
            permissions = $permissions
            backupDisabled = $backupDisabled
            verification = [ordered]@{ signatureValid = $true; zipAligned = $true }
        }
    }
    $inventory = [ordered]@{ schemaVersion = 1; artifacts = $artifacts }
    $pending = Join-Path $output '.artifacts.tmp'
    $inventory | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $pending -Encoding utf8
    Move-Item -LiteralPath $pending -Destination (Join-Path $output 'artifacts.json') -Force
    $artifacts | ForEach-Object { [pscustomobject]@{ file = $_.file; origin = $_.origin; bytes = $_.bytes; sha256 = $_.sha256 } } | Format-Table
} finally {
    $env:JAVA_HOME = $previousJava
    $env:ANDROID_HOME = $previousAndroid
}
