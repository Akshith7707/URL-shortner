# Local zero-cost development

Run the full URL shortener **on your machine**. No `cdk bootstrap`, no `cdk deploy`, no AWS cloud resources, no AWS spend.

## What you need

| Tool | Status in this workspace | Purpose |
|---|---|---|
| Node.js + npm | Present | App + CDK synth/tests |
| Docker Desktop | Installed (start engine if needed) | DynamoDB Local container |
| AWS CLI | Present | Talk to **local** DynamoDB via `--endpoint-url` only |
| AWS SAM CLI | **Not installed** | Optional; not required for this local path |
| Java | Present | DynamoDB Local JAR fallback when Docker engine is down |

## Steps

```powershell
cd C:\Users\nithi\Projects\url-shortener

# 1) Start DynamoDB Local + create table
# Prefer Docker when Docker Desktop engine is running:
.\scripts\local-setup.ps1
# Or JAR fallback (no Docker daemon required):
.\scripts\local-setup-jar.ps1

# 2) Start local API (stands in for API Gateway)
npm run local:api

# 3) In another terminal — smoke test
.\scripts\smoke-test.ps1 -ApiUrl "http://127.0.0.1:3000"
```

## Tests

```powershell
# CDK unit tests (no local DB needed)
npm run test:unit

# Handler integration tests (need DynamoDB Local on :8000)
npm run local:setup:jar   # or local:setup
npm run test:local
```

## Environment used locally

| Variable | Value |
|---|---|
| `DYNAMODB_ENDPOINT` | `http://127.0.0.1:8000` |
| `TABLE_NAME` | `url-shortener-urls` |
| `AWS_ACCESS_KEY_ID` | `local` (dummy) |
| `AWS_SECRET_ACCESS_KEY` | `local` (dummy) |

Dummy keys talk to DynamoDB Local only. They do **not** use your root AWS credentials.

## Stop local stack

```powershell
docker compose down
```

## Later (when you want cloud deploy — optional)

**Warning:** Cloud deploy creates billable resources. Never deploy with the root user.

1. Create a **non-root IAM user** with least privilege.
2. Switch AWS CLI to that identity (`aws sts get-caller-identity` must not show root).
3. Explicitly approve bootstrap + deploy in chat before any agent runs them.
4. See README for the cloud section (scripts remain blocked until you opt in).
