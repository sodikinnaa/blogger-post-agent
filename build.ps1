$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$distDir = Join-Path $root 'dist'
$buildDir = Join-Path $root 'build'
$releaseDir = Join-Path $distDir 'BloggerPost'
$exePath = Join-Path $releaseDir 'BloggerPost.exe'

if (Test-Path $distDir) {
    Remove-Item -Recurse -Force $distDir
}

if (Test-Path $buildDir) {
    Remove-Item -Recurse -Force $buildDir
}

Get-ChildItem -Path $root -Filter '*.spec' | Remove-Item -Force

python -m pip install pyinstaller

$pyInstallerArgs = @(
    '-m',
    'PyInstaller',
    '--name',
    'BloggerPost',
    '--onefile',
    '--console',
    '--add-data',
    'promt;promt',
    'cli.py'
)

python @pyInstallerArgs

New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null

if (Test-Path (Join-Path $distDir 'BloggerPost.exe')) {
    Move-Item (Join-Path $distDir 'BloggerPost.exe') $exePath -Force
}

New-Item -ItemType Directory -Force -Path (Join-Path $releaseDir 'credential\blogs') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $releaseDir 'promt') | Out-Null

if (Test-Path (Join-Path $root '.env')) {
    Copy-Item (Join-Path $root '.env') (Join-Path $releaseDir '.env') -Force
} elseif (Test-Path (Join-Path $root 'env.example')) {
    Copy-Item (Join-Path $root 'env.example') (Join-Path $releaseDir '.env') -Force
}

if (Test-Path (Join-Path $root 'api\credential\blogs\secret.json')) {
    Copy-Item (Join-Path $root 'api\credential\blogs\secret.json') (Join-Path $releaseDir 'credential\blogs\secret.json') -Force
}

if (Test-Path (Join-Path $root 'api\credential\blogs\credentials.storage')) {
    Copy-Item (Join-Path $root 'api\credential\blogs\credentials.storage') (Join-Path $releaseDir 'credential\blogs\credentials.storage') -Force
}

if (Test-Path (Join-Path $root 'promt')) {
    Copy-Item (Join-Path $root 'promt\*') (Join-Path $releaseDir 'promt') -Recurse -Force
}

Write-Host ''
Write-Host 'Build selesai.'
Write-Host "EXE: $exePath"
Write-Host "Folder distribusi: $releaseDir"