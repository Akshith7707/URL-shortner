#!/usr/bin/env python3
"""Generate ~20 page academic project report (reference-style) with realistic screenshots."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "report-assets"
OUT = ROOT / "docs" / "URL_Shortener_Project_Report.pdf"


class Report(FPDF):
    def header(self) -> None:
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(100, 100, 100)
        self.cell(
            0,
            8,
            "URL Shortener using Lambda + DynamoDB | Akshith Reddy Ponna",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        self.set_draw_color(190, 190, 190)
        y = self.get_y()
        self.line(10, y, 200, y)
        self.ln(6)

    def footer(self) -> None:
        self.set_y(-14)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"{self.page_no()}", align="C")

    def t(self, text: str, size=11, style="", h=6, color=(30, 30, 30)) -> None:
        self.set_x(self.l_margin)
        self.set_text_color(*color)
        self.set_font("Helvetica", style, size)
        self.multi_cell(0, h, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def h1(self, text: str) -> None:
        self.ln(2)
        self.t(text, size=14, style="B", h=8, color=(15, 76, 129))
        self.set_draw_color(15, 76, 129)
        y = self.get_y()
        self.line(10, y, 200, y)
        self.ln(3)

    def h2(self, text: str) -> None:
        self.ln(2)
        self.t(text, size=12, style="B", h=7, color=(20, 20, 20))

    def p(self, text: str) -> None:
        self.t(text, size=11, h=6)
        self.ln(1)

    def bullets(self, items: list[str]) -> None:
        for item in items:
            self.set_x(self.l_margin + 3)
            self.set_font("Helvetica", size=11)
            self.set_text_color(30, 30, 30)
            self.multi_cell(0, 6, f"- {item}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def fig(self, path: Path, caption: str, w: float = 165) -> None:
        if not path.exists():
            self.p(f"[Missing figure: {path.name}]")
            return
        if self.get_y() > 155:
            self.add_page()
        self.ln(2)
        self.set_x(self.l_margin + 5)
        self.image(str(path), w=w)
        self.ln(2)
        self.t(caption, size=9, style="I", h=5, color=(70, 70, 70))
        self.ln(2)


def build() -> Path:
    pdf = Report(format="A4")
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.set_margins(12, 14, 12)

    # ===== 1 Cover =====
    pdf.add_page()
    pdf.ln(28)
    pdf.t("MVSR ENGINEERING COLLEGE", size=13, style="B", h=7, color=(20, 20, 20))
    pdf.ln(2)
    pdf.t("Cloud Infrastructure and DevOps Engineer Domain", size=12, h=6, color=(60, 60, 60))
    pdf.ln(14)
    pdf.t("PROJECT REPORT", size=12, style="B", h=7, color=(15, 76, 129))
    pdf.ln(4)
    pdf.t("URL Shortener using Lambda + DynamoDB", size=18, style="B", h=9)
    pdf.ln(3)
    pdf.t(
        "A Serverless URL Shortening System using Amazon API Gateway,\nAWS Lambda, Amazon DynamoDB and AWS CDK",
        size=11,
        h=6,
        color=(60, 60, 60),
    )
    pdf.ln(18)
    pdf.t("Submitted by:", size=11, style="B", h=6)
    pdf.t("Akshith Reddy Ponna", size=13, style="B", h=7)
    pdf.t("Roll Number: 2451-23-751-028", size=11, h=6)
    pdf.ln(8)
    pdf.t("GitHub Repository:", size=11, style="B", h=6)
    pdf.t("https://github.com/Akshith7707/URL-shortner", size=11, h=6)
    pdf.ln(8)
    pdf.t("Academic Year: 2026 - 2027", size=11, h=6)
    pdf.t("Date: 31 October 2026", size=11, h=6)

    # ===== 2 Certificate + Acknowledgment =====
    pdf.add_page()
    pdf.h1("2. Certificate")
    pdf.p(
        'This is to certify that the project report titled "URL Shortener using Lambda + DynamoDB" '
        "submitted by Akshith Reddy Ponna (Roll No. 2451-23-751-028) in partial fulfillment of the "
        "requirements of the Cloud Infrastructure and DevOps Engineer domain project has been carried "
        "out as part of academic project work."
    )
    pdf.ln(10)
    pdf.p("Guide Signature: ____________________")
    pdf.ln(6)
    pdf.p("HOD Signature: _______________________")
    pdf.ln(6)
    pdf.p("Principal Signature: _________________")
    pdf.ln(10)
    pdf.h1("3. Acknowledgment")
    pdf.p(
        "I would like to express my sincere gratitude to my project guide and faculty members for their "
        "continuous support, guidance and encouragement throughout the development of this project."
    )
    pdf.p(
        "I also thank the Department for providing the academic environment and resources required to "
        "complete this work. Finally, I thank my friends and family for their support during the project."
    )

    # ===== 3 Abstract =====
    pdf.add_page()
    pdf.h1("4. Abstract")
    pdf.p(
        "Cloud computing enables developers to build scalable applications without managing physical servers. "
        "This project implements a serverless URL shortener on Amazon Web Services using Amazon API Gateway, "
        "AWS Lambda and Amazon DynamoDB. The system accepts a long URL, stores a short code mapping, and "
        "redirects users from the short link to the original destination."
    )
    pdf.p(
        "Infrastructure is defined using AWS Cloud Development Kit (CDK) with TypeScript, following "
        "least-privilege IAM design and CloudWatch logging/monitoring. To avoid additional AWS spending "
        "during development and evaluation, the application was verified end-to-end using DynamoDB Local "
        "and a local API stand-in that invokes the same Lambda handlers."
    )
    pdf.p(
        "Test results confirm successful health checks, short-URL creation, HTTP 301 redirection and "
        "HTTP 404 handling for unknown codes. The project demonstrates practical DevOps and cloud "
        "engineering skills: architecture design, Infrastructure as Code, secure IAM, automated testing "
        "and documentation."
    )

    # ===== TOC =====
    pdf.h1("5. Table of Contents")
    toc = [
        "1. Cover Page",
        "2. Certificate",
        "3. Acknowledgment",
        "4. Abstract",
        "5. Table of Contents",
        "6. Introduction",
        "7. Literature Survey",
        "8. Problem Statement",
        "9. Objectives",
        "10. Existing System",
        "11. Proposed System",
        "12. System Architecture",
        "13. Technologies Used",
        "14. Implementation Methodology",
        "15. System Testing",
        "16. Results and Discussion",
        "17. Advantages and Limitations",
        "18. Applications",
        "19. Future Scope",
        "20. Conclusion",
        "21. References",
    ]
    for item in toc:
        pdf.t(item, size=11, h=6)

    # ===== Introduction =====
    pdf.add_page()
    pdf.h1("6. Introduction")
    pdf.h2("6.1 Background")
    pdf.p(
        "Modern applications increasingly rely on cloud platforms to reduce operational overhead and improve "
        "scalability. Serverless computing is a cloud model where the cloud provider runs the compute layer "
        "and developers focus on business logic. AWS Lambda, API Gateway and DynamoDB are commonly used "
        "together for lightweight HTTP APIs."
    )
    pdf.h2("6.2 Need for the Project")
    pdf.p("Long URLs are difficult to share in messages, documents and social media. A URL shortener:")
    pdf.bullets(
        [
            "Converts a long URL into a compact short code",
            "Stores the mapping in a durable database",
            "Redirects clients from the short URL to the original URL",
            "Can track usage with counters and logs",
        ]
    )
    pdf.h2("6.3 Scope")
    pdf.p(
        "This project covers design, Infrastructure as Code, application logic, security (IAM least privilege), "
        "monitoring design, local verification and documentation. Production custom domains and authentication "
        "are listed as future enhancements."
    )

    # ===== Literature =====
    pdf.add_page()
    pdf.h1("7. Literature Survey")
    pdf.h2("7.1 Serverless Computing")
    pdf.p(
        "Serverless platforms execute code in response to events and scale automatically. Compared with "
        "always-on virtual machines, serverless can reduce idle cost for spiky workloads such as URL "
        "shortening APIs."
    )
    pdf.h2("7.2 API Gateway and Lambda Integration")
    pdf.p(
        "Amazon API Gateway exposes HTTPS endpoints and integrates with Lambda using proxy integration. "
        "HTTP APIs provide a lower-cost option for simple REST-style routes, which suits create and redirect "
        "operations in this project."
    )
    pdf.h2("7.3 NoSQL Key-Value Storage")
    pdf.p(
        "Amazon DynamoDB is a managed NoSQL database optimized for key-based access. A short-code lookup is "
        "a natural partition-key access pattern and provides single-digit millisecond reads at scale."
    )
    pdf.h2("7.4 Infrastructure as Code")
    pdf.p(
        "AWS CDK allows infrastructure to be defined in general-purpose languages and synthesized to "
        "CloudFormation. This improves repeatability, reviewability and alignment between application and "
        "infrastructure code."
    )

    # ===== Problem / Objectives =====
    pdf.h1("8. Problem Statement")
    pdf.p(
        "Manual or single-server URL shortener designs suffer from operational complexity, weak scaling "
        "characteristics and inconsistent deployment practices. There is a need for an automated, serverless "
        "design that can create short links, redirect users reliably, enforce least-privilege access and be "
        "deployed reproducibly using Infrastructure as Code."
    )
    pdf.h1("9. Objectives")
    pdf.bullets(
        [
            "Design a serverless URL shortener architecture on AWS",
            "Implement create and redirect APIs using Lambda and DynamoDB",
            "Define infrastructure using AWS CDK (TypeScript)",
            "Apply least-privilege IAM permissions",
            "Configure CloudWatch logging and error alarms in the stack",
            "Validate the system with automated and smoke tests",
            "Document architecture, results and future cloud deployment steps",
        ]
    )

    # ===== Existing / Proposed =====
    pdf.add_page()
    pdf.h1("10. Existing System")
    pdf.p(
        "Traditional URL shorteners are often hosted on a single application server with a relational database. "
        "Limitations include:"
    )
    pdf.bullets(
        [
            "Server management overhead (patching, capacity planning)",
            "Single point of failure if only one instance is used",
            "Difficulty reproducing infrastructure across environments",
            "Broader IAM permissions than necessary in many student demos",
        ]
    )
    pdf.h1("11. Proposed System")
    pdf.p(
        "The proposed system is a serverless URL shortener. Clients call an HTTP API. Lambda functions "
        "perform create and redirect logic. DynamoDB stores mappings. CDK defines all resources."
    )
    pdf.h2("11.1 Key Features")
    pdf.bullets(
        [
            "POST /shorten to create a short code",
            "GET /{code} returns HTTP 301 redirect",
            "GET /health for liveness checks",
            "Conditional writes to avoid short-code collisions",
            "Hit counter on successful redirects",
            "Least-privilege IAM and CloudWatch monitoring design",
            "Local zero-cost execution path for verification",
        ]
    )
    pdf.h2("11.2 Working Principle")
    pdf.p(
        "When a client submits a long URL, the Create Lambda validates the URL, generates a base62 short "
        "code and writes an item to DynamoDB. The response includes shortCode and shortUrl. When a client "
        "opens the short URL, the Redirect Lambda reads the item and returns Location: <longUrl> with status "
        "301. Unknown codes return 404."
    )
    pdf.h2("11.3 Comparison with Existing System")
    pdf.bullets(
        [
            "Existing: single server / manual setup  |  Proposed: serverless managed services",
            "Existing: fixed capacity  |  Proposed: automatic scaling with Lambda concurrency",
            "Existing: manual recovery  |  Proposed: managed service durability and retries",
            "Existing: ad-hoc setup  |  Proposed: CDK Infrastructure as Code",
            "Existing: broad permissions common in demos  |  Proposed: least-privilege IAM by function",
        ]
    )

    # ===== Architecture =====
    pdf.add_page()
    pdf.h1("12. System Architecture")
    pdf.p(
        "Figure 1 shows the target AWS architecture. In local verification mode, DynamoDB Local and a local "
        "HTTP API replace the managed API Gateway endpoint while using the same Lambda handler code."
    )
    pdf.fig(
        ASSETS / "architecture-diagram.jpg",
        "Figure 1: System architecture - Client, API Gateway, Lambda functions, DynamoDB and CloudWatch.",
        w=170,
    )
    pdf.h2("12.1 Components")
    pdf.bullets(
        [
            "API Gateway HTTP API: entry point for /shorten, /health and /{code}",
            "Lambda CreateUrl: validation, code generation, PutItem",
            "Lambda Redirect: GetItem, UpdateItem hit count, 301 response",
            "DynamoDB table url-shortener-urls with partition key shortCode",
            "CloudWatch log groups and error alarms",
        ]
    )
    pdf.h2("12.2 Data Model")
    pdf.bullets(
        [
            "shortCode (S) - partition key",
            "longUrl (S) - destination URL",
            "createdAt (S) - ISO timestamp",
            "hitCount (N) - redirect counter",
            "lastAccessedAt (S) - last redirect time",
        ]
    )

    # ===== Technologies =====
    pdf.add_page()
    pdf.h1("13. Technologies Used")
    pdf.bullets(
        [
            "Amazon API Gateway (HTTP API)",
            "AWS Lambda (Node.js 24.x)",
            "Amazon DynamoDB",
            "AWS IAM",
            "Amazon CloudWatch Logs and Alarms",
            "AWS CDK v2 (TypeScript) / CloudFormation",
            "DynamoDB Local for zero-cost testing",
            "Jest for unit and local integration tests",
            "Git / GitHub for source control",
        ]
    )

    pdf.h1("14. Implementation Methodology")
    pdf.h2("Step 1: Project scaffolding")
    pdf.p("Initialize an AWS CDK TypeScript application and define the UrlShortenerStack.")
    pdf.h2("Step 2: DynamoDB table")
    pdf.p(
        "Create table url-shortener-urls with partition key shortCode and on-demand billing mode in the CDK stack."
    )
    pdf.h2("Step 3: Lambda handlers")
    pdf.p(
        "Implement create-url and redirect handlers with URL validation, collision retry, structured logging "
        "and support for DYNAMODB_ENDPOINT for local testing."
    )
    pdf.h2("Step 4: API Gateway routes")
    pdf.p("Wire POST /shorten, GET /health and GET /{code} using HttpApi and Lambda integrations.")
    pdf.h2("Step 5: IAM least privilege")
    pdf.p("Grant PutItem only to Create Lambda; GetItem and UpdateItem only to Redirect Lambda.")
    pdf.h2("Step 6: Monitoring")
    pdf.p("Attach log groups with 7-day retention and CloudWatch alarms on Lambda Errors.")
    pdf.h2("Step 7: Local verification")
    pdf.p(
        "Run DynamoDB Local, start the local API, execute unit/integration tests and smoke tests. "
        "Cloud deploy was deferred to avoid AWS charges and because root credentials must not be used for deployment."
    )

    pdf.add_page()
    pdf.h2("14.1 Project Structure")
    pdf.bullets(
        [
            "bin/url-shortener.ts - CDK application entry point",
            "lib/url-shortener-stack.ts - DynamoDB, Lambda, HTTP API, IAM, Logs, Alarms",
            "lambda/create-url/index.ts - create + health handlers",
            "lambda/redirect/index.ts - redirect handler",
            "lambda/shared/dynamo.ts - DynamoDB client factory (cloud/local)",
            "scripts/local-api.ts - local API Gateway stand-in",
            "scripts/local-setup.ps1 / local-setup-jar.ps1 - DynamoDB Local setup",
            "scripts/smoke-test.ps1 - end-to-end smoke tests",
            "test/ - Jest unit and local integration tests",
            "docs/ - architecture, local guide and this report",
        ]
    )
    pdf.h2("14.2 IAM Design Details")
    pdf.p(
        "Security is a core DevOps concern. The stack avoids broad AdministratorAccess on application roles."
    )
    pdf.bullets(
        [
            "Create function role: dynamodb:PutItem on the table ARN only",
            "Redirect function role: dynamodb:GetItem and dynamodb:UpdateItem only",
            "Both roles receive AWSLambdaBasicExecutionRole for CloudWatch Logs",
            "X-Ray put permissions are included because tracing is enabled",
            "API Gateway receives lambda:InvokeFunction through resource-based policy statements",
            "No AWS access keys are hardcoded in source files",
        ]
    )
    pdf.h2("14.3 API Examples")
    pdf.p("Create request body:")
    pdf.t('{ "url": "https://docs.aws.amazon.com/" }', size=10, h=6, color=(40, 40, 40))
    pdf.p("Successful create response includes shortCode, shortUrl, longUrl and createdAt.")
    pdf.p("Redirect response is not JSON; it is an HTTP 301 with a Location header.")

    # ===== Testing =====
    pdf.add_page()
    pdf.h1("15. System Testing")
    pdf.p("Testing was performed locally against DynamoDB Local and the local API at http://127.0.0.1:3000.")
    pdf.h2("15.1 Test Cases")
    pdf.bullets(
        [
            "Health check returns HTTP 200 and {status: ok}",
            "Valid POST /shorten returns HTTP 201 with shortCode and shortUrl",
            "Invalid JSON / missing URL returns HTTP 400",
            "GET /{code} for existing mapping returns HTTP 301 with Location",
            "Unknown short code returns HTTP 404",
            "CDK unit tests assert table, functions, API and IAM statements",
        ]
    )
    pdf.h2("15.2 Tools")
    pdf.bullets(
        [
            "Jest unit and local integration tests",
            "PowerShell smoke-test.ps1",
            "curl.exe for redirect header inspection",
            "Playwright desktop screenshots (1366x768) for report evidence",
        ]
    )

    # ===== Results =====
    pdf.add_page()
    pdf.h1("16. Results and Discussion")
    pdf.p(
        "The following figures were captured at a standard desktop viewport (1366x768) from the working "
        "local deployment. They show end-to-end behavior of the URL shortener handlers."
    )
    pdf.h2("16.1 Demo Console Overview")
    pdf.fig(
        ASSETS / "fig-demo-console.png",
        "Figure 2: Local demo console showing health and create/redirect panels at normal desktop scale.",
        w=168,
    )

    pdf.add_page()
    pdf.h2("16.2 Health Endpoint")
    pdf.fig(
        ASSETS / "fig-health-browser.png",
        "Figure 3: Browser response for GET /health returning {\"status\":\"ok\"}.",
        w=168,
    )
    pdf.h2("16.3 Create Short URL")
    pdf.fig(
        ASSETS / "fig-create-json.png",
        "Figure 4: Successful POST /shorten response (HTTP 201) with shortCode, shortUrl, longUrl and createdAt.",
        w=168,
    )

    pdf.add_page()
    pdf.h2("16.4 Redirect Response")
    pdf.fig(
        ASSETS / "fig-redirect-headers.png",
        "Figure 5: Redirect response headers showing HTTP 301 Moved Permanently and Location of the long URL.",
        w=168,
    )
    pdf.h2("16.5 Not Found Handling")
    pdf.fig(
        ASSETS / "fig-404.png",
        "Figure 6: Unknown short code returns HTTP 404 with an error payload.",
        w=168,
    )

    pdf.add_page()
    pdf.h2("16.6 Smoke Test Terminal Output")
    pdf.fig(
        ASSETS / "fig-terminal.png",
        "Figure 7: PowerShell smoke test output confirming health, create, redirect and 404 cases.",
        w=168,
    )
    pdf.h2("16.7 Source Repository")
    pdf.fig(
        ASSETS / "fig-github.png",
        "Figure 8: GitHub repository https://github.com/Akshith7707/URL-shortner containing the project source.",
        w=168,
    )

    pdf.add_page()
    pdf.h2("16.8 Summary of Observations")
    pdf.bullets(
        [
            "Health endpoint is available and returns a clear OK payload",
            "Create flow stores mappings and returns a usable short URL",
            "Redirect flow issues HTTP 301 with the correct Location header",
            "Missing codes are handled with HTTP 404",
            "Infrastructure code synthesizes cleanly with least-privilege IAM statements",
            "Local verification proves functional correctness without AWS cloud charges",
        ]
    )

    # ===== Advantages / Future / Conclusion =====
    pdf.h1("17. Advantages and Limitations")
    pdf.h2("Advantages")
    pdf.bullets(
        [
            "Serverless design reduces server management effort",
            "Pay-per-use model is cost-efficient for variable traffic",
            "IaC enables repeatable deployments",
            "Least-privilege IAM improves security posture",
            "Local testing path supports zero-cost evaluation",
        ]
    )
    pdf.h2("Limitations")
    pdf.bullets(
        [
            "Cloud deploy was not executed in this submission to avoid AWS spend and root-user risk",
            "No custom domain or HTTPS certificate management in the current demo",
            "No authentication/rate limiting on the public create API",
            "CORS is open for demo purposes and should be restricted in production",
        ]
    )

    pdf.add_page()
    pdf.h1("18. Applications")
    pdf.bullets(
        [
            "Marketing campaign links and QR codes",
            "Internal documentation deep-link shortening",
            "Social media sharing of long product URLs",
            "Academic and portfolio project demos",
            "Learning platform for serverless DevOps skills",
        ]
    )

    pdf.h1("19. Future Scope")
    pdf.bullets(
        [
            "Deploy with a non-root IAM role after budget approval",
            "Add custom domain with ACM certificate",
            "Add API authentication (API keys / Cognito / JWT)",
            "Add analytics dashboard for hit counts",
            "Add TTL/expiry for temporary links",
            "Add CI/CD pipeline for CDK deployments",
            "Add AWS WAF for abuse protection",
        ]
    )

    pdf.add_page()
    pdf.h1("20. Conclusion")
    pdf.p(
        "This project successfully designs and implements a serverless URL shortener using AWS Lambda, "
        "API Gateway and DynamoDB, with infrastructure defined in AWS CDK. The implementation includes "
        "secure IAM design, monitoring configuration, automated tests and complete documentation."
    )
    pdf.p(
        "End-to-end verification was completed locally using DynamoDB Local and a local API, confirming "
        "create, redirect and error-handling behavior. The same codebase is ready for AWS deployment when "
        "a non-root identity and explicit cost approval are available."
    )
    pdf.p(
        "Through this work, practical experience was gained in serverless architecture, Infrastructure as "
        "Code, least-privilege security and DevOps-style validation - core skills for Cloud Infrastructure "
        "and DevOps Engineer roles."
    )

    pdf.ln(6)
    pdf.t("Declaration", size=12, style="B", h=7)
    pdf.p(
        "I, Akshith Reddy Ponna (Roll No: 2451-23-751-028), submit this project report for the domain "
        "Cloud Infrastructure and DevOps Engineer. The project title is URL Shortener using Lambda + DynamoDB."
    )
    pdf.ln(8)
    pdf.p("Student Signature: ____________________")
    pdf.ln(4)
    pdf.p("Date: 31 / 10 / 2026")

    # ===== References =====
    pdf.add_page()
    pdf.h1("21. References")
    refs = [
        "1. AWS Documentation - https://docs.aws.amazon.com/",
        "2. AWS Lambda Developer Guide - https://docs.aws.amazon.com/lambda/",
        "3. Amazon API Gateway Developer Guide - https://docs.aws.amazon.com/apigateway/",
        "4. Amazon DynamoDB Developer Guide - https://docs.aws.amazon.com/dynamodb/",
        "5. AWS CDK Documentation - https://docs.aws.amazon.com/cdk/",
        "6. Choose between HTTP APIs and REST APIs - https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-vs-rest.html",
        "7. DynamoDB Local - https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html",
        "8. IAM best practices - https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html",
        "9. Project repository - https://github.com/Akshith7707/URL-shortner",
    ]
    for r in refs:
        pdf.t(r, size=11, h=7)
        pdf.ln(1)

    pdf.ln(8)
    pdf.h2("Appendix A: How to Run Locally")
    pdf.bullets(
        [
            "npm install",
            "npm run local:setup:jar",
            "npm run local:api",
            ".\\scripts\\smoke-test.ps1 -ApiUrl http://127.0.0.1:3000",
        ]
    )
    pdf.h2("Appendix B: Submission Links")
    pdf.bullets(
        [
            "GitHub: https://github.com/Akshith7707/URL-shortner",
            "Report PDF: docs/URL_Shortener_Project_Report.pdf",
        ]
    )

    pdf.add_page()
    pdf.h1("Appendix C: Learning Outcomes")
    pdf.p("By completing this project, the following outcomes were achieved:")
    pdf.bullets(
        [
            "Ability to design a serverless application architecture on AWS",
            "Hands-on experience with AWS CDK for Infrastructure as Code",
            "Understanding of least-privilege IAM for Lambda and DynamoDB",
            "Practical API design for create and redirect workflows",
            "Experience with local emulation (DynamoDB Local) for cost-safe testing",
            "Documentation and evidence preparation for academic submission",
        ]
    )
    pdf.ln(4)
    pdf.h1("Appendix D: Sequence of Operations")
    pdf.h2("Create flow")
    pdf.bullets(
        [
            "Client sends POST /shorten with JSON body containing url",
            "API Gateway invokes Create Lambda",
            "Lambda validates protocol/host and rejects unsafe local targets",
            "Lambda generates a 7-character base62 short code",
            "Lambda writes item with condition attribute_not_exists(shortCode)",
            "On collision, Lambda retries with a new code",
            "Client receives HTTP 201 with shortCode and shortUrl",
        ]
    )
    pdf.h2("Redirect flow")
    pdf.bullets(
        [
            "Client sends GET /{code}",
            "API Gateway invokes Redirect Lambda",
            "Lambda validates short-code format",
            "Lambda reads DynamoDB item by shortCode",
            "If missing, return HTTP 404",
            "If found, best-effort increment hitCount and return HTTP 301 Location",
        ]
    )
    pdf.h2("Local zero-cost mapping")
    pdf.bullets(
        [
            "API Gateway -> scripts/local-api.ts on port 3000",
            "DynamoDB service -> DynamoDB Local on port 8000",
            "Same handler source files used for both local and cloud paths",
        ]
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUT))
    return OUT


if __name__ == "__main__":
    path = build()
    from pypdf import PdfReader

    pages = len(PdfReader(str(path)).pages)
    print(f"Wrote {path} ({pages} pages)")
