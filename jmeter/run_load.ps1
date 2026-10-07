<#
Runs ONE open-loop JMeter run against the triage service and keeps its evidence.
Run this on the load-generator machine, never on the machine hosting the service.

Before calling it, the service host must already be up with the matching MODEL and RUN_ID.
Add -ShowRunId to print the RUN_ID for a set of arguments without running anything.

Load test (constant arrival rate, per minute):
  .\jmeter\run_load.ps1 -TargetHost 192.168.1.20 -Model llama3.2:1b -Scenario stretch -Run 1 -Rate 1 -SearchRate 0.2 -DurationMin 30

Stress test (arrival rate stepped up without draining between steps):
  .\jmeter\run_load.ps1 -TargetHost 192.168.1.20 -Model llama3.2:1b -Scenario stress -Run 1 -StepRates "2,4,6,8,10" -StepMin 10

Files written to results/jtl/ (or -OutDir):  <RUN_ID>.jtl  <RUN_ID>.properties  <RUN_ID>.meta.json  <RUN_ID>.jmeter.log
#>
param(
    [Parameter(Mandatory = $true)][string]$TargetHost,
    [Parameter(Mandatory = $true)][string]$Model,
    [Parameter(Mandatory = $true)][string]$Scenario,
    [Parameter(Mandatory = $true)][int]$Run,
    [double]$Rate = 0,              # POST /tickets arrivals per minute (load test)
    [double]$DurationMin = 30,      # arrival window in minutes (load test)
    [string]$StepRates = "",        # stress test: POST /tickets arrivals per minute for each step, e.g. "2,4,6,8"
    [double]$MaxRate = 120,         # safety limit on any arrival rate (per minute); a typo above it aborts the run
    [double]$StepMin = 10,          # minutes per step (stress test)
    [double]$SearchRate = 0,        # GET /search arrivals per minute
    [double]$DrainMin = 6,          # no new arrivals; lets in-flight requests finish (> service's 300 s Ollama timeout)
    [int]$Port = 8000,
    [int]$ResponseTimeoutMs = 330000,
    [string]$JMeterHome = $env:JMETER_HOME,
    [string]$OutDir = "",           # default results\jtl; point elsewhere for a plumbing check
    [switch]$SkipWarmup,
    [switch]$ShowRunId
)
$ErrorActionPreference = "Stop"
$inv = [System.Globalization.CultureInfo]::InvariantCulture
function Num([double]$x) { return $x.ToString("0.####", $inv) }

$runId = "{0}_{1}_run{2}" -f $Model.Replace(":", "-").Replace("/", "-"), $Scenario, $Run
if ($ShowRunId) { $runId; return }

$repo = Split-Path -Parent $PSScriptRoot
$outDir = if ($OutDir) { $OutDir } else { Join-Path $repo "results\jtl" }
$feeder = Join-Path $PSScriptRoot "feeder.tsv"
$plan = Join-Path $PSScriptRoot "triage_load.jmx"
$jtl = Join-Path $outDir "$runId.jtl"
$propsFile = Join-Path $outDir "$runId.properties"
$metaFile = Join-Path $outDir "$runId.meta.json"
$baseUrl = "http://${TargetHost}:$Port"

if (-not $JMeterHome) { throw "Set JMETER_HOME or pass -JMeterHome (the folder that contains bin\jmeter.bat)." }
$jmeterBat = Join-Path $JMeterHome "bin\jmeter.bat"
if (-not (Test-Path $jmeterBat)) { throw "jmeter.bat not found at $jmeterBat" }
if (-not (Test-Path $feeder)) { throw "Missing $feeder. Run: py scripts\make_feeder.py" }
if (Test-Path $jtl) { throw "$jtl already exists. Evidence is never overwritten: use a new -Run number." }
New-Item -ItemType Directory -Force $outDir | Out-Null

# --- schedule (Open Model Thread Group) ---------------------------------
# parsed by hand: PowerShell would read an unquoted 2,4,6 as the single number 246
$steps = @($StepRates.Split(",") | Where-Object { $_.Trim() } | ForEach-Object { [double]::Parse($_.Trim(), $inv) })
foreach ($r in $steps + $Rate + $SearchRate) {
    if ($r -lt 0 -or $r -gt $MaxRate) { throw "Arrival rate $r/min is outside 0..$MaxRate. Check the arguments (or raise -MaxRate)." }
}
if ($steps.Count -gt 0) {
    $parts = foreach ($r in $steps) { "rate($(Num $r)/min) random_arrivals($(Num $StepMin) min) rate($(Num $r)/min)" }
    $arrivalMin = $StepMin * $steps.Count
} elseif ($Rate -gt 0) {
    $parts = @("rate($(Num $Rate)/min) random_arrivals($(Num $DurationMin) min) rate($(Num $Rate)/min)")
    $arrivalMin = $DurationMin
} else {
    throw "Give either -Rate (load test) or -StepRates (stress test)."
}
$schedule = ($parts -join " ") + " pause($(Num $DrainMin) min)"
if ($SearchRate -gt 0) {
    $searchSchedule = "rate($(Num $SearchRate)/min) random_arrivals($(Num $arrivalMin) min) rate($(Num $SearchRate)/min) pause($(Num $DrainMin) min)"
} else {
    $searchSchedule = "pause(1 s)"
}

# --- the service must be reachable and empty (fresh RUN_ID) ---------------
$stats = Invoke-RestMethod -Uri "$baseUrl/stats" -TimeoutSec 30
if (@($stats.PSObject.Properties).Count -gt 0) {
    throw "GET /stats is not empty. Restart the service with RUN_ID=$runId so the run starts from an empty database."
}

# --- warm-up: loads the model; logged by the service, excluded from results
$warmup = $null
if (-not $SkipWarmup) {
    $line = Get-Content $feeder -Tail 1
    $tab = $line.IndexOf("`t")
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $resp = Invoke-WebRequest -UseBasicParsing -Method Post -Uri "$baseUrl/tickets" -ContentType "application/json" -Body $line.Substring($tab + 1) -TimeoutSec 900
    $sw.Stop()
    $warmup = [ordered]@{
        request_id = [string]$resp.Headers["X-Request-ID"]
        row_id     = [int]$line.Substring(0, $tab)
        elapsed_ms = $sw.ElapsedMilliseconds
    }
    Write-Host "Warm-up done in $($sw.ElapsedMilliseconds) ms (request_id $($warmup.request_id))"
}

# --- per-run properties: the exact JMeter configuration, kept as evidence --
@"
host=$TargetHost
port=$Port
response_timeout_ms=$ResponseTimeoutMs
feeder=feeder.tsv
search_terms=search_terms.csv
schedule=$schedule
search_schedule=$searchSchedule
seed=$Run
search_seed=$($Run + 1000)
sample_variables=row_id,request_id
jmeter.save.saveservice.output_format=csv
jmeter.save.saveservice.print_field_names=true
jmeter.save.saveservice.timestamp_format=ms
"@ | Set-Content -Path $propsFile -Encoding ascii

$meta = [ordered]@{
    run_id            = $runId
    model             = $Model
    scenario          = $Scenario
    run               = $Run
    target            = $baseUrl
    post_rate_per_min = $Rate
    step_rates_per_min = $steps
    step_min          = $StepMin
    search_rate_per_min = $SearchRate
    arrival_window_min = $arrivalMin
    drain_min         = $DrainMin
    schedule          = $schedule
    search_schedule   = $searchSchedule
    warmup            = $warmup
    jmeter_started_ms = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
}
$meta | ConvertTo-Json -Depth 4 | Set-Content -Path $metaFile -Encoding ascii

Write-Host "RUN_ID   $runId"
Write-Host "Schedule $schedule"
& $jmeterBat -n -t $plan -q $propsFile -l $jtl -j (Join-Path $outDir "$runId.jmeter.log")
if ($LASTEXITCODE -ne 0) { throw "JMeter exited with code $LASTEXITCODE" }

$meta["jmeter_finished_ms"] = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
$meta | ConvertTo-Json -Depth 4 | Set-Content -Path $metaFile -Encoding ascii

$samples = (Get-Content $jtl | Measure-Object -Line).Lines - 1
Write-Host "Finished: $samples samples in $jtl"
Write-Host "Next: copy results/logs/$runId.log from the service host, then run: py scripts\summarize_load.py"
