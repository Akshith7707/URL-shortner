# Architecture — AWS URL Shortener

## Overview

This project implements a serverless URL shortener on AWS. Clients call an **API Gateway HTTP API**, which invokes **Lambda** functions that read and write mappings in **DynamoDB**. **CloudWatch** collects logs and error alarms. Infrastructure is defined with **AWS CDK (TypeScript)** and deployed via **CloudFormation**.

## Diagram

```mermaid
flowchart LR
  Client[Client] -->|POST /shorten| HttpApi[API_Gateway_HTTP_API]
  Client -->|GET /health| HttpApi
  Client -->|GET /{code}| HttpApi
  HttpApi --> CreateFn[Lambda_CreateUrl]
  HttpApi --> RedirectFn[Lambda_Redirect]
  CreateFn -->|PutItem| Table[DynamoDB_Urls]
  RedirectFn -->|GetItem UpdateItem| Table
  CreateFn --> CWLogs[CloudWatch_Logs]
  RedirectFn --> CWLogs
  HttpApi --> AccessLogs[API_Access_Logs]
  CreateFn --> AlarmCreate[Alarm_Create_Errors]
  RedirectFn --> AlarmRedirect[Alarm_Redirect_Errors]
```

## Request flows

### Create short URL

1. Client sends `POST /shorten` with JSON `{ "url": "https://example.com" }`.
2. API Gateway routes the request to `url-shortener-create`.
3. Lambda validates the URL, generates a base62 short code, and writes the item with a conditional `PutItem` (`attribute_not_exists(shortCode)`).
4. On collision, Lambda retries with a new code (up to 5 times).
5. Response `201` includes `shortCode`, `shortUrl`, `longUrl`, and `createdAt`.

### Redirect

1. Client sends `GET /{code}`.
2. API Gateway routes to `url-shortener-redirect`.
3. Lambda `GetItem`s by `shortCode`.
4. If found, returns `301` with `Location: <longUrl>` and best-effort increments `hitCount`.
5. If missing, returns `404`.

## AWS services

| Service | Purpose |
|---|---|
| Amazon API Gateway (HTTP API) | Public HTTPS endpoint, routing, CORS, access logs |
| AWS Lambda (Node.js 24) | Stateless business logic (create + redirect) |
| Amazon DynamoDB | Durable key-value store for short-code mappings |
| IAM | Least-privilege execution roles and resource policies |
| Amazon CloudWatch Logs | Lambda application logs + API access logs (7-day retention) |
| Amazon CloudWatch Alarms | Alert when Lambda `Errors` >= 1 in a 1-minute period |
| AWS X-Ray (Lambda tracing) | Optional distributed tracing (`Tracing.ACTIVE`) |
| AWS CDK / CloudFormation | Infrastructure as code and deployment |

## Data model

**Table:** `url-shortener-urls`  
**Billing:** On-demand (`PAY_PER_REQUEST`)  
**Primary key:** `shortCode` (STRING)

| Attribute | Type | Description |
|---|---|---|
| `shortCode` | S | Partition key (7-char base62) |
| `longUrl` | S | Destination URL |
| `createdAt` | S | ISO-8601 creation timestamp |
| `hitCount` | N | Redirect counter |
| `lastAccessedAt` | S | Last successful redirect time |

## IAM (least privilege)

| Principal | Allowed actions | Resource |
|---|---|---|
| Create Lambda role | `dynamodb:PutItem` | Urls table ARN |
| Redirect Lambda role | `dynamodb:GetItem`, `dynamodb:UpdateItem` | Urls table ARN |
| Both Lambda roles | CloudWatch Logs write | Own log groups |
| API Gateway | `lambda:InvokeFunction` | Create/Redirect functions (resource policy) |
| API Gateway | `logs:CreateLogStream`, `logs:PutLogEvents` | Access log group |

## API contract

| Method | Path | Success | Notes |
|---|---|---|---|
| `GET` | `/health` | `200 { "status": "ok" }` | Liveness |
| `POST` | `/shorten` | `201` with short URL payload | Body: `{ "url": "..." }` |
| `GET` | `/{code}` | `301 Location` | Unknown code → `404` |

## Cost notes (demo)

Pay-per-use services: DynamoDB on-demand, Lambda, HTTP API, CloudWatch Logs.  
Destroy the stack when finished: `npx cdk destroy`.
