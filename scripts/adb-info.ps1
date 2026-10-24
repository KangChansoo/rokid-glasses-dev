param(
    [string]$Serial,
    [string]$AdbPath = 'adb'
)
$ErrorActionPreference = 'Stop'
if (-not (Get-Command $AdbPath -ErrorAction SilentlyContinue)) { throw 'Install Android Platform Tools or pass -AdbPath.' }
$rows = @(& $AdbPath devices)
if ($LASTEXITCODE -ne 0) { throw 'Could not list ADB devices.' }
$ready = @($rows | ForEach-Object {
    if ($_ -match '^(\S+)\s+device\s*$') { $Matches[1] }
})
if (-not $Serial) {
    if ($ready.Count -ne 1) { throw "Found $($ready.Count) ready transports. Pass -Serial using the first column of adb devices. IP and mDNS can describe the same glasses." }
    $Serial = $ready[0]
}
if ($Serial -notin $ready) { throw 'The specified transport is not in device state. Check adb devices and select the current endpoint.' }
$result = [ordered]@{}
foreach ($entry in @(
    @{ Label = 'Model'; Property = 'ro.product.model' },
    @{ Label = 'Manufacturer'; Property = 'ro.product.manufacturer' },
    @{ Label = 'Android'; Property = 'ro.build.version.release' },
    @{ Label = 'API'; Property = 'ro.build.version.sdk' }
)) {
    $value = & $AdbPath -s $Serial shell getprop $entry.Property
    if ($LASTEXITCODE -ne 0) { throw 'Reading device information failed.' }
    $result[$entry.Label] = ($value -join '').Trim()
}
[pscustomobject]$result
