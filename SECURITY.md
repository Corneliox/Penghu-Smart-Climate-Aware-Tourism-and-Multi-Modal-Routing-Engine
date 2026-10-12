# 🛡️ Security Policy

## Supported Versions

We actively maintain and provide security updates for the latest major release of **Penghu Cool-Ride**:

| Version | Supported          | Status |
| :--- | :---: | :--- |
| **v2.x** | :white_check_mark: | Currently Supported (Active Development) |
| **v1.x** | :warning:          | Limited Support (Critical Vulnerability Fixes Only) |
| **< 1.0** | :x:               | Unsupported |

---

## 🔒 Reporting a Vulnerability

The project team takes the security of this open-source application seriously. If you discover a security vulnerability, we appreciate your help in disclosing it responsibly.

### 1. How to Report
Please **DO NOT** report security vulnerabilities through public GitHub issues or discussions.

Instead, please report vulnerabilities using one of the following private methods:
* **GitHub Private Vulnerability Reporting**: Go to the repository's [Security tab](https://github.com/Corneliox/MapNodeWeightRecommendation/security) and click **"Report a vulnerability"**.
* **Direct Maintainer Contact**: Contact [@Corneliox](https://github.com/Corneliox) via GitHub.

### 2. What to Include in Your Report
To help us triage and resolve the issue quickly, please provide:
* A description of the vulnerability and its potential impact.
* Step-by-step reproduction steps or a minimal Proof of Concept (PoC).
* Any specific browser, operating system, or device versions affected.
* Potential remediation suggestions, if known.

### 3. Response Process & Timeline
* **Initial Acknowledgment**: Within **48 hours** of receiving your report.
* **Assessment & Verification**: We will confirm the issue and evaluate its severity.
* **Remediation & Patch**: A fix will be developed, tested, and released as a hotfix or patch release.
* **Public Disclosure**: Once the fix is published, an acknowledgment will be credited to the reporter (unless anonymity is requested).

---

## 🏗️ Architecture & Security Principles

### 1. Client-Side Static Execution (Zero Server-Side Risk)
* The web application is 100% static client-side JavaScript, HTML, and CSS hosted on GitHub Pages.
* There are no centralized server-side databases, authentication backends, or stored user credentials.
* No personal identifying information (PII) or geolocation data is recorded, logged, or sent to external servers.

### 2. Environment Variables & API Key Protection
* Sensitive API credentials (e.g., Google Routes or Google Places API keys) must **NEVER** be committed to the repository.
* `.gitignore` explicitly excludes `.env` and local credentials.
* The public web app relies entirely on free, open, and client-safe public endpoints (Open-Meteo API, Wikimedia REST API, Open Source Routing Machine).

### 3. Third-Party Dependencies & CDNs
* All CDN dependencies (Leaflet, Lucide, Tailwind, KaTeX) are fetched from reputable registries. Where possible, Subresource Integrity (SRI) hashes are implemented to prevent upstream tampering.
* Automated GitHub Actions workflows are configured with minimal, least-privilege token permissions.
