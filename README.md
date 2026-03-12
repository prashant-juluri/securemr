# SecureMR

**AI-powered security review for Pull Requests and Merge Requests**

SecureMR helps developers discover and fix security issues directly in their code review workflow. It combines **static analysis (Semgrep)** with **AI-assisted explanations and fixes** to make security findings actionable.

Instead of showing raw scanner output, SecureMR provides:

* 📖 **Clear explanation of the vulnerability**
* ⚠️ **Risk assessment**
* 🛠 **Suggested secure fix**

All directly inside CI logs or MR/PR comments.

---

# Why SecureMR?

Traditional SAST tools produce results like:

```
python.sqlalchemy.security.sqlalchemy-execute-raw-query
```

Which developers often ignore because they lack context.

SecureMR converts findings into developer-friendly guidance:

```
Explanation:
The Dockerfile runs containers as root by default, which increases the
risk of privilege escalation if the container is compromised.

Risk Level: MEDIUM

Suggested Fix:
Create a non-root user and run the container with the USER directive.
```

This helps teams **shift security left** without requiring deep security expertise.

---

# Architecture

SecureMR follows a simple pipeline:

```
Code → Semgrep Scan → AI Review Pipeline → CI Output
```

AI review consists of three specialized agents:

```
Explain Agent → explains the vulnerability  
Risk Agent → evaluates exploitability and impact  
Fix Agent → suggests secure code remediation
```

---

# Features

* Static analysis powered by **Semgrep**
* AI-assisted security explanations
* Suggested remediation examples
* Works in **GitHub Actions**
* Works in **GitLab CI**
* Containerized for easy integration
* Designed for **shift-left security workflows**

---

# Quick Start

SecureMR is distributed as a Docker image.

```
docker pull prashantjuluri/securemr:latest
```

---

# Running Locally

You can test SecureMR locally against any repository.

```
docker run --rm \
  -e OPENAI_API_KEY=<your_api_key> \
  -v $(pwd):/target \
  prashantjuluri/securemr:latest \
  python securemr.py /target
```

---

# GitHub Actions Setup

Create the file:

```
.github/workflows/securemr.yml
```

Example workflow:

```yaml
name: SecureMR Security Scan

on:
  pull_request:
  push:
    branches: [ main ]

jobs:
  security-scan:

    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Run SecureMR
        run: |
          docker run --rm \
            -e OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }} \
            -v ${{ github.workspace }}:/target \
            prashantjuluri/securemr:latest \
            python securemr.py /target
```

---

# GitHub Secrets

Add this secret:

```
OPENAI_API_KEY
```

Location:

```
Repository Settings → Secrets → Actions
```

---

# GitLab CI Setup

Add the following to `.gitlab-ci.yml`.

```yaml
securemr_scan:

  stage: test

  image: docker:24

  services:
    - docker:24-dind

  script:

    - echo "Running SecureMR scan"

    - docker run --rm \
        -e OPENAI_API_KEY=$OPENAI_API_KEY \
        -e GITLAB_TOKEN=$GITLAB_TOKEN \
        -e CI_PROJECT_ID=$CI_PROJECT_ID \
        -e CI_MERGE_REQUEST_IID=$CI_MERGE_REQUEST_IID \
        -e CI_API_V4_URL=$CI_API_V4_URL \
        -v $CI_PROJECT_DIR:/target \
        prashantjuluri/securemr:latest \
        python securemr.py /target
```

---

# GitLab Variables

Add these variables in:

```
GitLab → Settings → CI/CD → Variables
```

```
OPENAI_API_KEY
GITLAB_TOKEN
```

The GitLab token allows SecureMR to post findings directly in **Merge Request comments**.

---

# Example Output

```
🔒 SecureMR Security Report

File: api/search.py
Rule: python.sqlalchemy.security.sqlalchemy-execute-raw-query

Explanation:
Raw SQL queries without parameterization allow SQL injection.

Risk Level: HIGH

Suggested Fix:
Use parameterized queries with SQLAlchemy's query builder.
```

---

# Roadmap

Planned improvements:

* SARIF output support
* GitHub Code Scanning integration
* Additional scanners

  * Trivy
  * Snyk
* Multi-language security analysis
* Cost-optimized AI pipeline

---

# Security Philosophy

SecureMR is built around a simple idea:

> Security tools should help developers fix problems, not just detect them.

By combining static analysis with AI explanations, SecureMR makes security findings **understandable and actionable**.

---

# License

MIT License

---

# Author

**Prashant Juluri**

---

# Contributing

Contributions and feedback are welcome.
