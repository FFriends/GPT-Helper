#Requires -Version 7.0
<#
Run coop_helper.py in an existing WSL 2 distribution as its default Linux user.
Does not install WSL, enable virtualization, change execution policy, or start a Coop VM by itself.
Example: .\Coop.ps1 -CoopArguments @('install', '--confirm')
#>
[CmdletBinding()]
param(
    [string]$Distribution = 'Ubuntu-24.04',
    [string]$LinuxUser,
    [string[]]$CoopArguments = @('--help')
)
$ErrorActionPreference = 'Stop'
if (-not $IsWindows) { throw 'Run this wrapper on Windows, or use python3 coop_helper.py on Linux.' }
$wslCommand = Get-Command wsl.exe -CommandType Application -ErrorAction Stop
$helperPath = Join-Path $PSScriptRoot 'coop_helper.py'
if (-not (Test-Path -LiteralPath $helperPath -PathType Leaf)) { throw 'coop_helper.py must be beside Coop.ps1.' }
$wslOptions = @('--distribution', $Distribution)
if ($LinuxUser) { $wslOptions += @('--user', $LinuxUser) }
# No shell command strings, inherited tokens, or machine-specific home paths.
$translatedPath = & $wslCommand.Source @wslOptions --exec /usr/bin/wslpath -a -u $helperPath
if ($LASTEXITCODE -ne 0 -or -not $translatedPath) { throw 'Cannot access the helper in the selected WSL distribution.' }
& $wslCommand.Source @wslOptions --cd / --exec /usr/bin/env -i PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin /usr/bin/python3 -I ([string]$translatedPath).Trim() @CoopArguments
exit $LASTEXITCODE
