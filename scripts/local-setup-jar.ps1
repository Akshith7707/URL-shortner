<#
.SYNOPSIS
  Fallback: run DynamoDB Local from the official JAR (no Docker).
  Downloads into .tools/ (gitignored). Zero AWS cloud cost.
#>
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$Tools = Join-Path $Root '.tools'
$DynDir = Join-Path $Tools 'dynamodb-local'
$Jar = Join-Path $DynDir 'DynamoDBLocal.jar'
$Zip = Join-Path $Tools 'dynamodb_local_latest.zip'
$Url = 'https://d1ni2b6xgvw0s0.cloudfront.net/v2.x/dynamodb_local_latest.zip'

New-Item -ItemType Directory -Force -Path $Tools | Out-Null

if (-not (Test-Path $Jar)) {
  Write-Host "==> Downloading DynamoDB Local JAR (public AWS download, not a billable API call)"
  Invoke-WebRequest -Uri $Url -OutFile $Zip
  Expand-Archive -Path $Zip -DestinationPath $DynDir -Force
}

# Kill previous local instance on 8000 if we started one
Get-CimInstance Win32_Process |
  Where-Object { $_.CommandLine -match 'DynamoDBLocal.jar' } |
  ForEach-Object { Write-Host "Stopping prior DynamoDB Local PID $($_.ProcessId)"; Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

Write-Host "==> Starting DynamoDB Local on :8000 (JAR)"
$proc = Start-Process -FilePath 'java' `
  -ArgumentList @('-Djava.library.path=./DynamoDBLocal_lib', '-jar', 'DynamoDBLocal.jar', '-sharedDb', '-inMemory', '-port', '8000') `
  -WorkingDirectory $DynDir `
  -WindowStyle Hidden `
  -PassThru
Write-Host "PID $($proc.Id)"

$ready = $false
for ($i = 0; $i -lt 40; $i++) {
  $tcp = Test-NetConnection -ComputerName 127.0.0.1 -Port 8000 -WarningAction SilentlyContinue
  if ($tcp.TcpTestSucceeded) { $ready = $true; break }
  Start-Sleep -Seconds 1
}
if (-not $ready) { throw 'DynamoDB Local JAR did not open port 8000' }

$env:AWS_ACCESS_KEY_ID = 'local'
$env:AWS_SECRET_ACCESS_KEY = 'local'
$env:AWS_DEFAULT_REGION = 'ap-south-1'
$Endpoint = 'http://127.0.0.1:8000'
$Table = 'url-shortener-urls'

Write-Host "==> Ensuring table exists: $Table"
$existing = aws dynamodb list-tables --endpoint-url $Endpoint --region ap-south-1 | ConvertFrom-Json
if ($existing.TableNames -contains $Table) {
  Write-Host 'Table already exists'
} else {
  aws dynamodb create-table `
    --endpoint-url $Endpoint `
    --region ap-south-1 `
    --table-name $Table `
    --attribute-definitions AttributeName=shortCode,AttributeType=S `
    --key-schema AttributeName=shortCode,KeyType=HASH `
    --billing-mode PAY_PER_REQUEST | Out-Null
  Write-Host 'Table created'
}

Write-Host ''
Write-Host 'Local DynamoDB ready (JAR mode).'
Write-Host 'Next: npm run local:api'
