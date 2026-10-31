# Виконати на Windows із .NET SDK 8/9, Git та підключенням до NuGet.
# НЕ записує "success" без успішного завершення фактичних dotnet команд.
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$work = Join-Path $env:TEMP ('sr02-v20-verify-' + [Guid]::NewGuid().ToString('N').Substring(0,8))
$before = Join-Path $work 'before'
$after = Join-Path $work 'after'
$logs = Join-Path $root 'audit\verified-logs'
New-Item -ItemType Directory -Path $work,$logs -Force | Out-Null

function RunDotnet($dir,$log,$args) {
    Push-Location $dir
    try {
        Write-Host ">>> dotnet $($args -join ' ') @ $dir"
        $output = & dotnet @args 2>&1
        $output | Out-File -LiteralPath $log -Encoding utf8
        if ($LASTEXITCODE -ne 0) {throw "dotnet command failed ($LASTEXITCODE); see $log"}
    } finally {Pop-Location}
}

function CoverageRate($path) {
    $xmlFile=Get-ChildItem -Path $path -Filter 'coverage.cobertura.xml' -Recurse -File | Select-Object -First 1
    if (-not $xmlFile) {return $null}
    [xml]$xml = Get-Content -LiteralPath $xmlFile.FullName
    $classes = @($xml.coverage.packages.package.classes.class)
    $target = $classes | Where-Object {($_.filename -like '*ResultTable.cs') -or ($_.name -eq 'SportEvents.ResultTable')} | Select-Object -First 1
    if (-not $target) {return $null}
    return [math]::Round(100 * [double]$target.'line-rate',2)
}

try {
    & git -C $root worktree add --detach $before 56ca2fc | Out-Null
    if ($LASTEXITCODE -ne 0) {throw 'Failed to prepare baseline tests worktree'}
    & git -C $root worktree add --detach $after after-refactoring | Out-Null
    if ($LASTEXITCODE -ne 0) {throw 'Failed to prepare refactored worktree'}

    foreach ($pair in @(@('before',$before),@('after',$after))) {
        $stage=$pair[0];$dir=$pair[1]
        RunDotnet $dir (Join-Path $logs "$stage-build.log") @('build','src/Legacy.csproj','-c','Release','-v:q')
        RunDotnet $dir (Join-Path $logs "$stage-tests.log") @('test','Legacy.Tests/Legacy.Tests.csproj','-c','Release','--collect:XPlat Code Coverage','--logger','console;verbosity=normal')
        RunDotnet $dir (Join-Path $logs "$stage-output.log") @('run','--project','src/Legacy.csproj','-c','Release','--no-build')
    }
    $oldBytes=[IO.File]::ReadAllBytes((Join-Path $logs 'before-output.log'))
    $newBytes=[IO.File]::ReadAllBytes((Join-Path $logs 'after-output.log'))
    $same=([Convert]::ToBase64String($oldBytes) -eq [Convert]::ToBase64String($newBytes))
    $coverageBefore = CoverageRate $before
    $coverageAfter = CoverageRate $after
    if (-not $same) {throw 'Program stdout differs between before and after; see logs'}
    if ($null -eq $coverageAfter) {throw 'ResultTable coverage cannot be located in Cobertura'}
    if ($coverageAfter -lt 60) {throw "Coverage ResultTable $coverageAfter% is below 60%"}
    $result=[ordered]@{
        timestamp=(Get-Date).ToString('o')
        environment='Windows / installed dotnet SDK'
        baseline_tag='baseline (code) / 56ca2fc (characterization tests)'
        after_tag='after-refactoring'
        build_before='passed'
        build_after='passed'
        tests_before='passed'
        tests_after='passed'
        output_bytes_identical=$true
        ResultTable_line_coverage_before_percent=$coverageBefore
        ResultTable_line_coverage_after_percent=$coverageAfter
    }
    ($result | ConvertTo-Json) | Set-Content -LiteralPath (Join-Path $root 'audit\validation-results.json') -Encoding UTF8
    Write-Host "SUCCESS: tests and output equal; ResultTable coverage=$coverageAfter%"
} catch {
    Write-Host "NOT VERIFIED: $($_.Exception.Message)" -ForegroundColor Red
    throw
} finally {
    if (Test-Path $after) {& git -C $root worktree remove --force $after | Out-Null}
    if (Test-Path $before) {& git -C $root worktree remove --force $before | Out-Null}
}
