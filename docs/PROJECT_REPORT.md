# Project Report — AWS URL Shortener

**Mode:** Zero additional AWS spend (local complete)  
**Identity note:** AWS CLI authenticated as **root** — cloud deploy intentionally blocked; do not deploy as root.  
**Region (for future cloud):** `ap-south-1`  
**IaC:** AWS CDK v2 (TypeScript)  
**Lambda runtime:** Node.js 24.x  
**Date:** 2026-10-31

## 1. Objective

Serverless URL shortener with API Gateway + Lambda + DynamoDB, least-privilege IAM, CloudWatch, and full IaC — runnable **locally at $0** until a non-root deploy is explicitly approved.

## 2. Status snapshot

| Area | Status |
|---|---|
| Backend handlers (`create-url`, `redirect`) | Complete |
| CDK stack (DynamoDB, HTTP API, IAM, Logs, Alarms) | Complete + `cdk synth` OK |
| Docs (README, architecture, local guide) | Complete |
| Cloud bootstrap / deploy | **Blocked** (cost + root identity) |
| Local DynamoDB + API + smoke tests | **Passing** |

## 3. What was already done before this local push

- Project scaffold under `C:\Users\nithi\Projects\url-shortener`
- AWS CLI + CDK CLI installed
- Full CDK stack + Lambda handlers
- Unit tests + CloudFormation synth evidence
- README / architecture / smoke script draft

## 4. What was completed in the zero-cost local phase

- `DYNAMODB_ENDPOINT` support via `lambda/shared/dynamo.ts`
- `docker-compose.yml` for DynamoDB Local
- JAR fallback `scripts/local-setup-jar.ps1` (used when Docker engine down)
- Local API Gateway stand-in `scripts/local-api.ts` on `:3000`
- Integration tests `test/handlers.local.test.ts`
- `npm run deploy` / `destroy` hard-blocked
- Smoke test fixed for Windows (`curl.exe` Location header)

## 5. Local verification evidence

| Check | Result |
|---|---|
| `npm run test:unit` | Passed (CDK assertions) |
| `npm run test:local` | **3/3 passed** against DynamoDB Local |
| `.\scripts\smoke-test.ps1 -ApiUrl http://127.0.0.1:3000` | **All passed** |
| Evidence file | `evidence/local-smoke-test.txt` |

Example successful flow:

1. `GET /health` → `{ "status": "ok" }`
2. `POST /shorten` → `201` with `shortCode` / `shortUrl`
3. `GET /{code}` → `301` Location to long URL
4. Unknown code → `404`

## 6. Missing / deferred (by design)

| Item | Notes |
|---|---|
| AWS SAM CLI | Not installed; not required — local API + DynamoDB Local covers E2E |
| Docker engine | May need Desktop started; JAR path works without it |
| Non-root IAM user | Create before any future cloud deploy |
| `cdk bootstrap` / `cdk deploy` | Not run; would create billable resources |
| Live CloudWatch in AWS | N/A until deploy; local uses console logs |

## 7. Backend + infrastructure readiness

**Yes — ready for local use and future cloud deploy.**

- Handlers implement create / redirect / validation / collision retry / hit count
- Stack encodes least-privilege DynamoDB actions, HTTP API routes, log groups, alarms
- Synth already validated resource shape and IAM statements

## 8. How to run locally (zero cost)

See [LOCAL.md](LOCAL.md).

```powershell
npm run local:setup:jar
npm run local:api
.\scripts\smoke-test.ps1 -ApiUrl "http://127.0.0.1:3000"
```

## 9. Future cloud deploy (optional, billable)

**Ask first. Never as root.**

1. Create IAM user/role with least privilege (not root)
2. Configure that identity in AWS CLI
3. Explicitly approve `cdk bootstrap` (if needed) and `cdk deploy` for `ap-south-1`
4. Re-enable deploy scripts only after approval

## 10. Conclusion

Project is a complete working URL shortener **locally** with production-shaped CDK/IaC ready on disk, at **$0 AWS spend**. Cloud verification remains gated on a non-root identity and your explicit approval.
