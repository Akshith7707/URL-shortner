<#
.SYNOPSIS
  Start DynamoDB Local (Docker) and create the url-shortener table.
  No AWS cloud resources. No AWS charges.
#>
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "==> Checking Docker"
docker info | Out-Null

Write-Host "==> Starting DynamoDB Local on port 8000"
docker compose up -d dynamodb-local

Write-Host "==> Waiting for DynamoDB Local"
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
  try {
    $tcp = Test-NetConnection -ComputerName 127.0.0.1 -Port 8000 -WarningAction SilentlyContinue
    if ($tcp.TcpTestSucceeded) { $ready = $true; break }
  } catch {}
  Start-Sleep -Seconds 1
}
if (-not $ready) { throw "DynamoDB Local did not become ready on port 8000" }

$env:AWS_ACCESS_KEY_ID = 'local'
$env:AWS_SECRET_ACCESS_KEY = 'local'
$env:AWS_DEFAULT_REGION = 'ap-south-1'
$Endpoint = 'http://127.0.0.1:8000'
$Table = 'url-shortener-urls'

Write-Host "==> Ensuring table exists: $Table"
$existing = aws dynamodb list-tables --endpoint-url $Endpoint --region ap-south-1 | ConvertFrom-Json
if ($existing.TableNames -contains $Table) {
  Write-Host "Table already exists"
} else {
  aws dynamodb create-table `
    --endpoint-url $Endpoint `
    --region ap-south-1 `
    --table-name $Table `
    --attribute-definitions AttributeName=shortCode,AttributeType=S `
    --key-schema AttributeName=shortCode,KeyType=HASH `
    --billing-mode PAY_PER_REQUEST | Out-Null
  Write-Host "Table created"
}

Write-Host ""
Write-Host "Local DynamoDB ready."
Write-Host "Next: npm run local:api"
Write-Host "Then:  Invoke-RestMethod http://127.0.0.1:3000/health"
