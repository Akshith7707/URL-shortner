<#
.SYNOPSIS
  Smoke-test the URL shortener API (local or cloud).

.PARAMETER ApiUrl
  Base API URL (e.g. http://127.0.0.1:3000 or https://xxxxx.execute-api.ap-south-1.amazonaws.com)

.EXAMPLE
  .\scripts\smoke-test.ps1 -ApiUrl "http://127.0.0.1:3000"
#>
param(
  [Parameter(Mandatory = $true)]
  [string]$ApiUrl
)

$ErrorActionPreference = 'Stop'
$base = $ApiUrl.TrimEnd('/')

Write-Host "==> Health check"
$health = Invoke-RestMethod -Method GET -Uri "$base/health"
if ($health.status -ne 'ok') { throw "Health check failed: $($health | ConvertTo-Json)" }
Write-Host "OK: $($health | ConvertTo-Json -Compress)"

Write-Host "==> Create short URL"
$body = @{ url = 'https://docs.aws.amazon.com/lambda/latest/dg/welcome.html' } | ConvertTo-Json
$created = Invoke-RestMethod -Method POST -Uri "$base/shorten" -ContentType 'application/json' -Body $body
if (-not $created.shortCode) { throw "Create failed: $($created | ConvertTo-Json)" }
Write-Host "OK: $($created | ConvertTo-Json -Compress)"

Write-Host "==> Redirect (expect 301)"
$curlOut = curl.exe -s -i -o - "$base/$($created.shortCode)"
$statusLine = ($curlOut | Select-Object -First 1)
$locationLine = $curlOut | Where-Object { $_ -match '^Location:\s*(.+)$' } | Select-Object -First 1
if ($statusLine -notmatch '301') { throw "Expected 301, got: $statusLine" }
if (-not $locationLine) { throw "Missing Location header. Raw:`n$curlOut" }
$location = ($locationLine -replace '^Location:\s*', '').Trim()
if ($location -ne $created.longUrl) { throw "Location mismatch: $location" }
Write-Host "OK: 301 -> $location"

Write-Host "==> Unknown code (expect 404)"
$missing = curl.exe -s -o NUL -w "%{http_code}" "$base/doesnotexist999"
if ($missing -ne '404') { throw "Expected 404, got $missing" }
Write-Host "OK: 404 for unknown short code"

Write-Host ""
Write-Host "All smoke tests passed."
