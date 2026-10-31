#!/usr/bin/env python3
"""Generate the official project PDF report with screenshots."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "report-assets"
OUT = ROOT / "docs" / "URL_Shortener_Project_Report.pdf"


class ReportPDF(FPDF):
    def header(self) -> None:
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(90, 90, 90)
        self.cell(0, 8, "URL Shortener using Lambda + DynamoDB | Akshith Reddy Ponna", align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def _text(self, text: str, size: int = 11, style: str = "", h: float = 6) -> None:
        self.set_x(self.l_margin)
        self.set_font("Helvetica", style, size)
        self.multi_cell(0, h, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def section_title(self, text: str) -> None:
        self.set_text_color(15, 76, 129)
        self.ln(4)
        self._text(text, size=14, style="B", h=8)
        self.set_draw_color(15, 76, 129)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)
        self.set_text_color(30, 30, 30)

    def body(self, text: str) -> None:
        self.set_text_color(30, 30, 30)
        self._text(text, size=11, h=6)
        self.ln(2)

    def bullet(self, text: str) -> None:
        self.set_x(self.l_margin + 4)
        self.set_font("Helvetica", size=11)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 6, f"- {text}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def kv(self, key: str, value: str) -> None:
        self.set_text_color(30, 30, 30)
        self._text(f"{key}: {value}", size=11, style="B", h=6)

    def add_image_safe(self, path: Path, caption: str, w: float = 180) -> None:
        if not path.exists():
            self.body(f"[Missing image: {path.name}]")
            return
        self.ln(2)
        if self.get_y() > 160:
            self.add_page()
        self.set_x(self.l_margin)
        self.image(str(path), w=w)
        self.ln(2)
        self.set_text_color(80, 80, 80)
        self._text(caption, size=9, style="I", h=5)
        self.set_text_color(30, 30, 30)
        self.ln(3)


def build() -> Path:
    pdf = ReportPDF(format="A4")
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=18)

    # -------- Cover --------
    pdf.add_page()
    pdf.ln(30)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(15, 76, 129)
    pdf.multi_cell(0, 8, "Cloud Infrastructure and DevOps Engineer", align="C")
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(20, 20, 20)
    pdf.multi_cell(0, 10, "URL Shortener using Lambda + DynamoDB", align="C")
    pdf.ln(6)
    pdf.set_font("Helvetica", size=12)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 7, "End-to-End Project Report", align="C")
    pdf.ln(20)
    pdf.set_font("Helvetica", size=12)
    pdf.set_text_color(30, 30, 30)
    for line in [
        "Student Name: Akshith Reddy Ponna",
        "Roll Number: 2451-23-751-028",
        "Domain: Cloud Infrastructure and DevOps Engineer",
        "Title: URL Shortener using Lambda + DynamoDB",
        "GitHub: https://github.com/Akshith7707/URL-shortner",
        "Region (designed): ap-south-1 (Mumbai)",
        "IaC: AWS CDK (TypeScript)",
        "Date: 31 October 2026",
    ]:
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 8, line, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(16)
    pdf.set_font("Helvetica", "I", 10)
    pdf.multi_cell(
        0,
        5,
        "This report documents architecture, implementation, IAM design, local verification with screenshots, and future cloud deployment notes.",
        align="C",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )

    # -------- 1. Introduction --------
    pdf.add_page()
    pdf.section_title("1. Introduction and Objective")
    pdf.body(
        "The goal of this project is to design and implement a serverless URL shortener on AWS using "
        "Amazon API Gateway, AWS Lambda, and Amazon DynamoDB, managed with Infrastructure as Code (AWS CDK). "
        "The system accepts a long URL, returns a short code, and redirects users from the short link to the original URL."
    )
    pdf.body("Key learning outcomes covered:")
    for item in [
        "Serverless architecture design on AWS",
        "Infrastructure as Code with AWS CDK (TypeScript)",
        "Least-privilege IAM for Lambda and DynamoDB",
        "API design for create and redirect flows",
        "CloudWatch logging and monitoring design",
        "Local zero-cost validation using DynamoDB Local",
    ]:
        pdf.bullet(item)

    pdf.section_title("2. Problem Statement")
    pdf.body(
        "Long URLs are difficult to share. A URL shortener stores a mapping between a compact short code and the original URL. "
        "When a client requests the short code, the service responds with an HTTP 301 redirect to the long URL. "
        "The solution must be scalable, low-maintenance, and cost-efficient. A serverless design fits these requirements."
    )

    # -------- Architecture --------
    pdf.section_title("3. System Architecture")
    pdf.body(
        "The application is fully serverless. Clients call an HTTP API. API Gateway routes requests to Lambda functions. "
        "Lambda reads and writes mappings in DynamoDB. CloudWatch collects logs and error alarms."
    )
    pdf.add_image_safe(
        ASSETS / "architecture-diagram.jpg",
        "Figure 1. High-level architecture (Client -> API Gateway -> Lambda -> DynamoDB + CloudWatch).",
        w=185,
    )
    pdf.body("Request flows:")
    pdf.bullet("POST /shorten: Create Lambda validates URL, generates a base62 short code, PutItem into DynamoDB, returns shortUrl.")
    pdf.bullet("GET /{code}: Redirect Lambda GetItem by shortCode; on hit returns 301 Location; increments hitCount.")
    pdf.bullet("GET /health: Liveness check returning { status: ok }.")
    pdf.bullet("Unknown code: HTTP 404 Short URL not found.")

    # -------- AWS Services --------
    pdf.add_page()
    pdf.section_title("4. AWS Services Used")
    services = [
        ("Amazon API Gateway (HTTP API)", "Public HTTPS front door; routes /shorten, /health, /{code}; CORS and access logs."),
        ("AWS Lambda (Node.js 24)", "Business logic for create and redirect handlers; auto-scales; pay per invoke."),
        ("Amazon DynamoDB", "Key-value store for shortCode -> longUrl; on-demand billing mode in CDK stack."),
        ("IAM", "Least-privilege execution roles. Create: PutItem only. Redirect: GetItem + UpdateItem only."),
        ("Amazon CloudWatch", "Lambda log groups, API access logs (7-day retention), error alarms."),
        ("AWS CDK / CloudFormation", "Defines and synthesizes all infrastructure as code for repeatable deployments."),
        ("AWS X-Ray (configured)", "Tracing.ACTIVE enabled on Lambda for distributed tracing when deployed."),
    ]
    for name, desc in services:
        pdf.set_text_color(30, 30, 30)
        pdf._text(name, size=11, style="B", h=6)
        pdf._text(desc, size=11, h=6)
        pdf.ln(1)

    pdf.section_title("5. Data Model")
    pdf.body("Table name: url-shortener-urls")
    pdf.bullet("Partition key: shortCode (String)")
    pdf.bullet("longUrl (String) - destination URL")
    pdf.bullet("createdAt (String) - ISO-8601 timestamp")
    pdf.bullet("hitCount (Number) - redirect counter")
    pdf.bullet("lastAccessedAt (String) - last successful redirect time")
    pdf.body(
        "Short codes are 7-character base62 values generated with crypto.randomBytes. "
        "Writes use ConditionExpression attribute_not_exists(shortCode) with retry on collision."
    )

    # -------- Implementation --------
    pdf.add_page()
    pdf.section_title("6. Implementation Overview")
    pdf.body("Project structure:")
    for line in [
        "bin/url-shortener.ts - CDK app entry (region ap-south-1)",
        "lib/url-shortener-stack.ts - DynamoDB, Lambdas, HTTP API, IAM, Logs, Alarms",
        "lambda/create-url/index.ts - POST /shorten + GET /health",
        "lambda/redirect/index.ts - GET /{code} redirect",
        "lambda/shared/dynamo.ts - DynamoDB client with local endpoint support",
        "scripts/local-api.ts - Local API Gateway stand-in",
        "scripts/local-setup*.ps1 - DynamoDB Local setup (Docker or JAR)",
        "docs/ - architecture, local guide, this report",
    ]:
        pdf.bullet(line)

    pdf.section_title("7. API Contract")
    pdf.bullet("GET /health -> 200 { status: ok }")
    pdf.bullet('POST /shorten body { "url": "https://..." } -> 201 { shortCode, shortUrl, longUrl, createdAt }')
    pdf.bullet("GET /{code} -> 301 Location: <longUrl>")
    pdf.bullet("Invalid/missing URL -> 400; unknown code -> 404")

    pdf.section_title("8. IAM Least Privilege")
    pdf.bullet("Create Lambda role: dynamodb:PutItem on table ARN only (+ basic logs + X-Ray)")
    pdf.bullet("Redirect Lambda role: dynamodb:GetItem and dynamodb:UpdateItem only")
    pdf.bullet("API Gateway invoke permissions scoped to routes via Lambda resource policy")
    pdf.bullet("No AWS credentials hardcoded in source code")

    pdf.section_title("9. Monitoring Design")
    pdf.bullet("Log groups: /aws/lambda/url-shortener-create, /aws/lambda/url-shortener-redirect")
    pdf.bullet("API access logs: /aws/apigateway/url-shortener")
    pdf.bullet("Alarms: url-shortener-create-errors, url-shortener-redirect-errors (Errors >= 1)")
    pdf.bullet("Retention: 7 days for demo cost control")

    # -------- Testing --------
    pdf.add_page()
    pdf.section_title("10. Testing and Verification")
    pdf.body(
        "To keep AWS spend at zero during development and evaluation, the stack was synthesized with CDK "
        "and executed end-to-end locally using DynamoDB Local and a local HTTP API that invokes the same Lambda handlers. "
        "Cloud deploy (cdk bootstrap / cdk deploy) was intentionally not performed with the root user."
    )
    pdf.body("Automated tests:")
    pdf.bullet("CDK unit tests (Jest assertions on DynamoDB, Lambda, HTTP API, IAM, outputs) - passed")
    pdf.bullet("Local handler integration tests against DynamoDB Local - 3/3 passed")
    pdf.bullet("Smoke script scripts/smoke-test.ps1 - health, create, 301 redirect, 404 - passed")

    pdf.add_image_safe(
        ASSETS / "ss-health.png",
        "Figure 2. Health endpoint response in browser: GET http://127.0.0.1:3000/health => {\"status\":\"ok\"}.",
        w=170,
    )
    pdf.add_image_safe(
        ASSETS / "ss-e2e-demo.png",
        "Figure 3. Local end-to-end demo page showing health check and successful POST /shorten response with shortCode.",
        w=170,
    )

    pdf.add_page()
    pdf.add_image_safe(
        ASSETS / "ss-e2e-redirect-404.png",
        "Figure 4. Redirect success (HTTP 301 + Location) and missing-code handling (HTTP 404).",
        w=170,
    )

    pdf.section_title("11. Repository and Submission Artifact")
    pdf.body(
        "Source code, infrastructure, documentation, and local tooling are published on GitHub."
    )
    pdf.kv("Repository", "https://github.com/Akshith7707/URL-shortner")
    pdf.add_image_safe(
        ASSETS / "ss-github.png",
        "Figure 5. GitHub repository Akshith7707/URL-shortner (main branch) containing project source.",
        w=170,
    )

    # -------- How to run --------
    pdf.add_page()
    pdf.section_title("12. How to Run Locally (Zero AWS Cost)")
    pdf.body("Prerequisites: Node.js, npm, Java (for DynamoDB Local JAR) or Docker Desktop.")
    for step in [
        "cd into the project root",
        "npm install",
        "npm run local:setup:jar   (or npm run local:setup if Docker engine is running)",
        "npm run local:api         (serves http://127.0.0.1:3000)",
        ".\\scripts\\smoke-test.ps1 -ApiUrl http://127.0.0.1:3000",
    ]:
        pdf.bullet(step)
    pdf.body("Detailed instructions: docs/LOCAL.md")

    pdf.section_title("13. Cloud Deployment Notes (Future)")
    pdf.body(
        "The CDK stack is ready for deployment to ap-south-1. Deployment was deferred to avoid AWS charges and because "
        "authentication was available only as the AWS root user. Root must not be used for deployments."
    )
    pdf.bullet("Create a non-root IAM user/role with least privilege")
    pdf.bullet("Configure AWS CLI with that identity")
    pdf.bullet("Approve and run: npx cdk bootstrap (once per account/region if needed)")
    pdf.bullet("Approve and run: npx cdk deploy")
    pdf.bullet("Re-run smoke tests against the ApiUrl stack output")
    pdf.body("npm run deploy / destroy are blocked in package.json during zero-cost mode.")

    pdf.section_title("14. Security Considerations")
    for item in [
        "No secrets committed to Git",
        "URL validation rejects localhost and link-local/metadata hosts",
        "Least-privilege DynamoDB actions per function",
        "CORS open (*) suitable for demo only; restrict origins for production",
        "Conditional writes prevent short-code overwrite collisions",
    ]:
        pdf.bullet(item)

    pdf.section_title("15. Results and Conclusion")
    pdf.body(
        "The project delivers a complete serverless URL shortener design and implementation: "
        "infrastructure as code, Lambda application logic, DynamoDB data model, IAM least privilege, "
        "monitoring design, documentation, automated tests, and verified local end-to-end behavior with screenshots. "
        "The same codebase can be deployed to AWS when a non-root identity and budget approval are available."
    )
    pdf.ln(4)
    pdf._text("Declaration", size=11, style="B", h=6)
    pdf._text(
        "I, Akshith Reddy Ponna (Roll No: 2451-23-751-028), submit this project report for the Cloud Infrastructure "
        "and DevOps Engineer domain. The work presented is part of my project submission "
        "URL Shortener using Lambda + DynamoDB.",
        size=11,
        h=6,
    )
    pdf.ln(12)
    pdf._text("Student Signature: ____________________", size=11, h=6)
    pdf.ln(4)
    pdf._text("Date: 31 / 10 / 2026", size=11, h=6)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUT))
    return OUT


if __name__ == "__main__":
    path = build()
    print(f"Wrote {path}")
