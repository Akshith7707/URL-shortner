# AWS URL Shortener

Serverless URL shortener built with **AWS CDK (TypeScript)**, **API Gateway HTTP API**, **AWS Lambda (Node.js 24)**, and **Amazon DynamoDB**.

Region default: **`ap-south-1`** (Mumbai).

## Architecture

```mermaid
flowchart LR
  Client[Client] -->|POST /shorten| HttpApi[API_Gateway_HTTP_API]
  Client -->|GET /{code}| HttpApi
  HttpApi --> CreateFn[Lambda_CreateUrl]
  HttpApi --> RedirectFn[Lambda_Redirect]
  CreateFn -->|PutItem| Table[DynamoDB_Urls]
  RedirectFn -->|GetItem UpdateItem| Table
  CreateFn --> CW[CloudWatch]
  RedirectFn --> CW
  HttpApi --> CW
```

See [docs/architecture.md](docs/architecture.md) for service explanations, IAM, and the data model.  
See [docs/LOCAL.md](docs/LOCAL.md) for the **zero-cost local** workflow.  
See [docs/PROJECT_REPORT.md](docs/PROJECT_REPORT.md) for the project report.

## Zero-cost local run (recommended now)

No bootstrap. No deploy. No AWS cloud resources. Uses **DynamoDB Local** in Docker.

```powershell
cd C:\Users\nithi\Projects\url-shortener
npm install
.\scripts\local-setup.ps1     # Docker DynamoDB Local + table
npm run local:api             # http://127.0.0.1:3000
```

Smoke:

```powershell
Invoke-RestMethod http://127.0.0.1:3000/health
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:3000/shorten `
  -ContentType "application/json" `
  -Body '{"url":"https://docs.aws.amazon.com/"}'
curl.exe -I http://127.0.0.1:3000/<shortCode>
```

Stop:

```powershell
npm run local:down
```

## Prerequisites

- Node.js 20+ and npm
- Docker Desktop (for DynamoDB Local)
- AWS CDK CLI (`npm install -g aws-cdk`) — synth/tests only
- AWS CLI v2 — optional for local table setup via `--endpoint-url` (dummy keys; not root)

**Do not deploy with the root user.** Cloud deploy is blocked in npm scripts until you opt in later with a non-root IAM identity.

## Project layout

```
bin/url-shortener.ts          # CDK app entry
lib/url-shortener-stack.ts    # Infrastructure stack
lambda/create-url/index.ts    # POST /shorten + GET /health
lambda/redirect/index.ts      # GET /{code}
lambda/shared/dynamo.ts       # DynamoDB client (cloud + local endpoint)
docker-compose.yml            # DynamoDB Local
scripts/local-setup.ps1       # Start local DB + create table
scripts/local-api.ts          # Local API Gateway stand-in
scripts/smoke-test.ps1        # End-to-end smoke tests
docs/                         # Architecture + local guide + report
```

## Install

```powershell
cd C:\Users\nithi\Projects\url-shortener
npm install
```

## Synthesize (no AWS changes)

```powershell
npm run build
npx cdk synth
```

## Cloud deploy (DISABLED for zero-cost mode)

`npm run deploy` / `npm run destroy` are blocked on purpose.

When you later want cloud (billable), use a **non-root IAM user**, then explicitly approve bootstrap + deploy. Until then: stay on [docs/LOCAL.md](docs/LOCAL.md).

## Test

Unit (no Docker):

```powershell
npm run test:unit
```

Local integration (DynamoDB Local must be up):

```powershell
.\scripts\local-setup.ps1
npm run test:local
```

Against local API:

```powershell
.\scripts\smoke-test.ps1 -ApiUrl "http://127.0.0.1:3000"
```

## API

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `POST` | `/shorten` | Body `{ "url": "https://..." }` → short URL |
| `GET` | `/{code}` | `301` redirect to the long URL |

## Monitoring

- Lambda log groups: `/aws/lambda/url-shortener-create`, `/aws/lambda/url-shortener-redirect`
- API access logs: `/aws/apigateway/url-shortener`
- Alarms: `url-shortener-create-errors`, `url-shortener-redirect-errors`
- Retention: 7 days (demo cost control)

## Cleanup

```powershell
npx cdk destroy
```

This deletes the stack resources (table uses `RemovalPolicy.DESTROY` for demos).

## Security notes

- No AWS credentials are hardcoded.
- Create Lambda may only `PutItem`; Redirect may only `GetItem` + `UpdateItem`.
- Input validation rejects non-http(s) URLs and common local/metadata hosts.
- CORS is open (`*`) for demo use — tighten for production.

## License

MIT (demo / learning project)
