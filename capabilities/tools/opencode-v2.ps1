[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$Project = ".",

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$OpenCodeArguments
)

$workspaceRoot = [System.IO.Path]::GetFullPath(
    (Join-Path -Path $PSScriptRoot -ChildPath "..\..")
)
$projectCandidate = if ([System.IO.Path]::IsPathRooted($Project)) {
    $Project
} else {
    Join-Path -Path $workspaceRoot -ChildPath $Project
}
$projectPath = [System.IO.Path]::GetFullPath($projectCandidate).TrimEnd("\", "/")
$workspacePrefix = $workspaceRoot.TrimEnd("\", "/") + [System.IO.Path]::DirectorySeparatorChar

if (
    -not $projectPath.Equals(
        $workspaceRoot,
        [System.StringComparison]::OrdinalIgnoreCase
    ) -and
    -not $projectPath.StartsWith(
        $workspacePrefix,
        [System.StringComparison]::OrdinalIgnoreCase
    )
) {
    [Console]::Error.WriteLine("Project must stay inside the V2 workspace: $workspaceRoot")
    exit 2
}

# GetFullPath 不解析 Windows junction/reparse point，必须逐组件核验真实目标。
$probe = $workspaceRoot
$relativeSegments = $projectPath.Substring($workspaceRoot.Length).TrimStart("\", "/")
foreach ($segment in ($relativeSegments -split "[\\/]")) {
    if (-not $segment) { continue }
    $probe = Join-Path -Path $probe -ChildPath $segment
    $item = Get-Item -LiteralPath $probe -Force -ErrorAction SilentlyContinue
    if ($null -eq $item) { break }
    if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
        $target = $item.Target
        if (-not $target) {
            [Console]::Error.WriteLine("Project path contains an unresolvable reparse point: $probe")
            exit 2
        }
        $targetFull = [System.IO.Path]::GetFullPath([string]$target)
        if (
            -not $targetFull.Equals(
                $workspaceRoot,
                [System.StringComparison]::OrdinalIgnoreCase
            ) -and
            -not $targetFull.StartsWith(
                $workspacePrefix,
                [System.StringComparison]::OrdinalIgnoreCase
            )
        ) {
            [Console]::Error.WriteLine("Project path traverses a reparse point escaping the V2 workspace: $probe")
            exit 2
        }
    }
}

if (-not (Test-Path -LiteralPath $projectPath -PathType Container)) {
    [Console]::Error.WriteLine("Project directory does not exist: $projectPath")
    exit 2
}

$runtimeRoot = Join-Path -Path $workspaceRoot -ChildPath "runtime\opencode"
$env:XDG_CONFIG_HOME = Join-Path -Path $workspaceRoot -ChildPath ".local"
$env:XDG_DATA_HOME = Join-Path -Path $runtimeRoot -ChildPath "data"
$env:XDG_CACHE_HOME = Join-Path -Path $runtimeRoot -ChildPath "cache"
$env:XDG_STATE_HOME = Join-Path -Path $runtimeRoot -ChildPath "state"
$env:TEMP = Join-Path -Path $runtimeRoot -ChildPath "tmp"
$env:TMP = $env:TEMP
$env:TMPDIR = $env:TEMP

@(
    $env:XDG_CONFIG_HOME
    $env:XDG_DATA_HOME
    $env:XDG_CACHE_HOME
    $env:XDG_STATE_HOME
    $env:TEMP
) | ForEach-Object {
    New-Item -ItemType Directory -Path $_ -Force | Out-Null
}

# Desktop shortcuts and long-lived terminals can retain an old PATH after the
# user npm prefix changes. Read the persisted user value so this launcher finds
# the managed OpenCode installation without requiring a Windows sign-out.
$userNpmPrefix = [Environment]::GetEnvironmentVariable(
    "NPM_CONFIG_PREFIX",
    "User"
)
if (
    -not [string]::IsNullOrWhiteSpace($userNpmPrefix) -and
    (Test-Path -LiteralPath $userNpmPrefix -PathType Container)
) {
    $env:NPM_CONFIG_PREFIX = $userNpmPrefix
    $env:Path = $userNpmPrefix + [System.IO.Path]::PathSeparator + $env:Path
}

Push-Location -LiteralPath $projectPath
try {
    if ($OpenCodeArguments.Count -eq 0) {
        & opencode "."
    } else {
        & opencode @OpenCodeArguments
    }
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
