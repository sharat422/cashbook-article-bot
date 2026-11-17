$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$configuration = Get-Content -LiteralPath (Join-Path $projectRoot 'schedule.json') -Raw | ConvertFrom-Json
if ((Get-TimeZone).Id -ne $configuration.windows.timezone_id) {
    throw "Windows timezone differs from schedule.json. Review trigger times before installing tasks."
}
if (-not (Test-Path -LiteralPath (Join-Path $projectRoot '.venv\Scripts\python.exe'))) {
    throw 'Create the project Python environment first.'
}
$identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name
$principal = New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -WakeToRun `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 45)
foreach ($entry in $configuration.windows.tasks) {
    if ($entry.slot -notin @('guide', 'explainer')) { throw 'Invalid scheduled slot.' }
    $arguments = '/d /c ""' + (Join-Path $projectRoot 'run_slot.cmd') + '" ' + $entry.slot + '"'
    $existing = Get-ScheduledTask -TaskName $entry.name -ErrorAction SilentlyContinue
    if ($existing -and @($existing.Actions | Where-Object { $_.Arguments -ne $arguments }).Count) {
        throw "Task name already belongs to another action: $($entry.name)"
    }
    $action = New-ScheduledTaskAction -Execute (Join-Path $env:WINDIR 'System32\cmd.exe') `
        -Argument $arguments -WorkingDirectory $projectRoot
    $at = [datetime]::Today.Add([timespan]::Parse($entry.time))
    $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $entry.day -At $at
    Register-ScheduledTask -TaskName $entry.name -Action $action -Trigger $trigger `
        -Principal $principal -Settings $settings -Description "Prepare the weekly $($entry.slot) article; human review required; never publishes." `
        -Force | Select-Object TaskName, State
}
