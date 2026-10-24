param(
    [string]$JavaHome,
    [string]$SdkRoot
)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
$nativeRoot = Join-Path $repoRoot 'native'
$localConfigPath = Join-Path $nativeRoot 'toolchain.local.json'
$localConfig = if (Test-Path -LiteralPath $localConfigPath) { Get-Content -LiteralPath $localConfigPath -Raw | ConvertFrom-Json } else { $null }
if (-not $JavaHome) { $JavaHome = if ($localConfig.javaHome) { $localConfig.javaHome } else { $env:JAVA_HOME } }
if (-not $SdkRoot) { $SdkRoot = if ($localConfig.sdkRoot) { $localConfig.sdkRoot } else { $env:ANDROID_HOME } }
$previousJava = $env:JAVA_HOME
$previousAndroid = $env:ANDROID_HOME
try {
    if ($JavaHome) { $env:JAVA_HOME = $JavaHome }
    if ($SdkRoot) {
        $sdkPath = (Resolve-Path -LiteralPath $SdkRoot).Path.Replace('\', '/')
        $env:ANDROID_HOME = $sdkPath
        Set-Content -LiteralPath (Join-Path $nativeRoot 'local.properties') -Value "sdk.dir=$sdkPath" -Encoding utf8
    }
    & (Join-Path $nativeRoot 'gradlew.bat') -p $nativeRoot --no-daemon --console=plain ':gpt-viewer:assembleDebug' ':paper-viewer:assembleDebug' ':paper-viewer:testDebugUnitTest' ':gpt-viewer:lintDebug' ':paper-viewer:lintDebug' ':adb-helper:assembleDebug' ':adb-helper:lintDebug'
    if ($LASTEXITCODE -ne 0) { throw 'Native build or verification failed.' }
    $output = Join-Path $repoRoot 'dist'
    New-Item -ItemType Directory -Force -Path $output | Out-Null
    $checksums = @()
    foreach ($app in @('gpt-viewer', 'paper-viewer', 'adb-helper')) {
        $source = Join-Path $nativeRoot "$app/build/outputs/apk/debug/$app-debug.apk"
        $name = "$app-android-debug.apk"
        $destination = Join-Path $output $name
        Copy-Item -LiteralPath $source -Destination $destination -Force
        $checksums += [ordered]@{ file = $name; bytes = (Get-Item -LiteralPath $destination).Length; sha256 = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLower() }
    }
    $checksums | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $output 'android-apk-checksums.json') -Encoding utf8
    $checksums | Format-Table
} finally {
    $env:JAVA_HOME = $previousJava
    $env:ANDROID_HOME = $previousAndroid
}
