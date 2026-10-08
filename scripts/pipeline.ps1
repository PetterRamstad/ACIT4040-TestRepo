param(
    [string]$Command = "full",
    [ValidateSet("dev", "research", "production")]
    [string]$Profile = "dev",
    [switch]$DryRun,
    [switch]$Resume,
    [switch]$Force
)

$arguments = @("$PSScriptRoot\pipeline.py", $Command, "--profile", $Profile)
if ($DryRun) { $arguments += "--dry-run" }
if ($Resume) { $arguments += "--resume" }
if ($Force) { $arguments += "--force" }
& python @arguments
exit $LASTEXITCODE
