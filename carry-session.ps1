<#
.SYNOPSIS
  Copy a Claude Code conversation from one project folder into another.

.DESCRIPTION
  Claude Code stores each conversation as a .jsonl transcript under
  ~/.claude/projects/<encoded-path>/, where <encoded-path> is the working
  directory with ':' and '\' replaced by '-'. Sessions are therefore scoped to
  the directory you launched `claude` from - start it somewhere else and the
  history is not there.

  This copies a transcript into this project's folder so `claude --resume`
  can see it.

  IMPORTANT: exit the source session first. A live session is still being
  written to, so copying mid-conversation snapshots an incomplete transcript.

.EXAMPLE
  .\carry-session.ps1 -From C:\path\to\old-project -Latest
  .\carry-session.ps1 -From C:\path\to\old-project -List
  .\carry-session.ps1 -From C:\path\to\old-project -SessionId <session-id>
#>
[CmdletBinding(DefaultParameterSetName = 'Latest')]
param(
    [Parameter(Mandatory)][string]$From,
    [Parameter(ParameterSetName = 'Latest')][switch]$Latest,
    [Parameter(ParameterSetName = 'List')][switch]$List,
    [Parameter(ParameterSetName = 'ById', Mandatory)][string]$SessionId,
    [string]$To = $PSScriptRoot
)

function Get-ProjectKey([string]$path) {
    # C:\path\to\drone-wood-frame  ->  C--path-to-drone-wood-frame
    (Resolve-Path $path).Path.TrimEnd('\').Replace(':', '-').Replace('\', '-')
}

$store = Join-Path $env:USERPROFILE '.claude\projects'
$srcDir = Join-Path $store (Get-ProjectKey $From)
$dstDir = Join-Path $store (Get-ProjectKey $To)

if (-not (Test-Path $srcDir)) { throw "No sessions recorded for $From (looked in $srcDir)" }

$sessions = Get-ChildItem $srcDir -Filter *.jsonl | Sort-Object LastWriteTime -Descending
if (-not $sessions) { throw "No .jsonl transcripts in $srcDir" }

if ($List) {
    $sessions | Select-Object @{n='SessionId';e={$_.BaseName}},
                              @{n='Modified';e={$_.LastWriteTime}},
                              @{n='SizeKB';e={[math]::Round($_.Length/1KB,1)}} |
        Format-Table -AutoSize
    return
}

$src = if ($SessionId) {
    $match = $sessions | Where-Object BaseName -eq $SessionId
    if (-not $match) { throw "Session $SessionId not found in $srcDir" }
    $match
} else {
    $sessions[0]
}

if (-not (Test-Path $dstDir)) { New-Item -ItemType Directory -Path $dstDir -Force | Out-Null }

$dst = Join-Path $dstDir $src.Name
if (Test-Path $dst) {
    Write-Warning "$($src.BaseName) is already in the target project. Overwriting."
}
Copy-Item $src.FullName $dst -Force

Write-Host ""
Write-Host "Copied session $($src.BaseName)" -ForegroundColor Green
Write-Host "  from  $From"
Write-Host "  to    $To"
Write-Host ""
Write-Host "Now run this from $To :" -ForegroundColor Cyan
Write-Host "  claude --resume $($src.BaseName)"
Write-Host ""
Write-Host "Note: this is a SNAPSHOT. The two copies diverge from here on." -ForegroundColor DarkGray
