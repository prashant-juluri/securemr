
# SecureMR

AI-assisted security reviews for Pull Requests and Merge Requests.

SecureMR helps development teams detect and fix security issues directly in their **code review workflow**.

It combines:

• **Static analysis (Semgrep)**  
• **CI-aware diff detection**  
• **AI-generated explanations and remediation**

Instead of presenting raw scanner output, SecureMR provides **actionable guidance developers can understand immediately**.

Security findings appear directly in **CI logs and Pull Request / Merge Request comments**.

---

# Why SecureMR

Traditional static analysis tools often produce results like:

`python.sqlalchemy.security.sqlalchemy-execute-raw-query`

These identifiers provide little context and are often ignored.

SecureMR converts scanner output into **developer-friendly guidance**:

```
Explanation:
Raw SQL queries allow attackers to inject arbitrary SQL statements
when user input is not parameterized.

Risk Level: HIGH

Suggested Fix:
Use parameterized queries through SQLAlchemy's query builder.
```

This helps teams **shift security left** without requiring deep security expertise.

---

# How SecureMR Works

SecureMR runs inside CI pipelines and analyzes **only the code introduced in a Pull Request or Merge Request**.

Pipeline:

Source Code → Semgrep Security Scan → CI Diff Detection → New Vulnerability Detection → AI Security Review → PR/MR Comment + CI Logs

Only **new vulnerabilities introduced by the change** are analyzed by the AI pipeline.

---

# AI Security Review

Each finding is processed by three specialized agents.

### Explain Agent
Explains the vulnerability in plain language.

### Risk Agent
Evaluates exploitability and real-world impact.

### Fix Agent
Provides remediation guidance with secure code examples.

---

# Security Rules

SecureMR runs Semgrep with curated rule packs:

```
p/default
p/secrets
p/dockerfile
p/supply-chain
```

These detect issues such as:

• SQL injection  
• command injection  
• hardcoded secrets  
• insecure deserialization  
• unsafe subprocess execution  
• container privilege issues  
• dependency risks  

Example rule IDs:

`python.sqlalchemy.security.sqlalchemy-execute-raw-query`  
`python.lang.security.audit.command-injection`  
`dockerfile.security.missing-user.missing-user`

---

# Quick Start

SecureMR is distributed as a Docker image.

```
docker pull prashantjuluri/securemr:latest
```

---

# Running SecureMR Locally

You can test SecureMR against any repository locally.

```
docker run --rm   -e OPENAI_API_KEY=<your_api_key>   -v $(pwd):/target   prashantjuluri/securemr:latest   python securemr.py /target
```

The scan results will appear in the console.

---

# GitHub Actions Setup

Create the workflow file:

`.github/workflows/securemr.yml`

Example workflow:

```yaml
name: SecureMR Security Scan

on:
  pull_request:
  push:
    branches: [ main ]

permissions:
  contents: read
  pull-requests: write
  issues: write

jobs:
  security-scan:

    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run SecureMR
        run: |
          docker run --rm \
            -e OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }} \
            -e GITHUB_TOKEN=${{ secrets.GITHUB_TOKEN }} \
            -e GITHUB_ACTIONS=true \
            -e GITHUB_REPOSITORY=${{ github.repository }} \
            -e GITHUB_EVENT_PATH=/event.json \
            -e GITHUB_BASE_SHA=${{ github.event.pull_request.base.sha }} \
            -e GITHUB_SHA=${{ github.event.pull_request.head.sha }} \
            -v ${{ github.workspace }}:/target \
            -v ${{ github.event_path }}:/event.json \
            prashantjuluri/securemr:latest \
            python securemr.py /target
```

Notes:

• `fetch-depth: 0` is important. Without full git history, diff detection may fall back to a full repository scan.  
• `GITHUB_TOKEN`, `GITHUB_EVENT_PATH`, `GITHUB_REPOSITORY`, `GITHUB_BASE_SHA`, and `GITHUB_SHA` must be passed into the container explicitly. GitHub sets them for the runner, not automatically for `docker run`.  
• PR comments require the `pull-requests: write` and `issues: write` permissions shown above.

---

# GitHub Secrets

Add the following secret:

`OPENAI_API_KEY`

Location:

Repository Settings → Secrets → Actions

GitHub also provides a default `GITHUB_TOKEN`, but you still need to pass it into the container as shown above if you want SecureMR to post PR comments.

SecureMR uses these GitHub values inside the container:

```
GITHUB_SHA
GITHUB_BASE_SHA
GITHUB_REPOSITORY
GITHUB_EVENT_PATH
GITHUB_WORKSPACE
```

For pull request workflows, set:

• `GITHUB_BASE_SHA` to `${{ github.event.pull_request.base.sha }}`  
• `GITHUB_SHA` to `${{ github.event.pull_request.head.sha }}`

---

# GitLab CI Setup

Add this job to `.gitlab-ci.yml`.

```yaml
stages:
  - security


securemr_scan:

  stage: security

  image: docker:24

  services:
    - docker:24-dind

  variables:
    DOCKER_TLS_CERTDIR: ""
    DOCKER_DRIVER: overlay2
    GIT_DEPTH: "0"

  rules:
    # Run on merge request pipelines
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

    # Run on pushes to main
    - if: $CI_COMMIT_BRANCH == "main"

    # Allow manual execution
    - when: manual


  before_script:

    - echo "Starting SecureMR security scan"
    - docker version


  script:
  - echo "Running SecureMR scan"
  - docker pull prashantjuluri/securemr:latest
  - git remote -v
  - git config --get remote.origin.url
  - |
    docker run --rm \
    -e GITLAB_CI=$GITLAB_CI \
    -e OPENAI_API_KEY=$OPENAI_API_KEY \
    -e GITLAB_TOKEN=$GITLAB_TOKEN \
    -e CI_PROJECT_ID=$CI_PROJECT_ID \
    -e CI_MERGE_REQUEST_IID=$CI_MERGE_REQUEST_IID \
    -e CI_API_V4_URL=$CI_API_V4_URL \
    -e CI_MERGE_REQUEST_TARGET_BRANCH_NAME=$CI_MERGE_REQUEST_TARGET_BRANCH_NAME \
    -e CI_MERGE_REQUEST_DIFF_BASE_SHA=$CI_MERGE_REQUEST_DIFF_BASE_SHA \
    -e CI_COMMIT_SHA=$CI_COMMIT_SHA \
    -v $CI_PROJECT_DIR:/target \
    prashantjuluri/securemr:latest \
    python securemr.py /target


  allow_failure: false
```

Notes:

• `GIT_DEPTH: "0"` helps ensure the merge request base commit is available for diff detection.  
• `CI_COMMIT_SHA` must be passed into the container. SecureMR uses it together with `CI_MERGE_REQUEST_DIFF_BASE_SHA` to detect changed files.  
• Merge request comments require `CI_MERGE_REQUEST_IID`, `CI_API_V4_URL`, `CI_PROJECT_ID`, and `GITLAB_TOKEN`.  
• Push or manual pipelines can still run SecureMR, but MR comments and MR-specific diff detection only work on merge request pipelines.

---

# GitLab CI Variables

Configure the following variables in:

Project Settings → CI/CD → Variables

Required variables:

```
OPENAI_API_KEY
GITLAB_TOKEN
```

To allow SecureMR to post findings into Merge Request comments, create a GitLab access token with `api` scope and store it as `GITLAB_TOKEN`.

---

# Example Output

Example CI output:

```
🔒 SecureMR Security Report

File: api/search.py
Rule: `python.sqlalchemy.security.sqlalchemy-execute-raw-query`

Explanation:
Executing raw SQL queries without parameterization can lead to SQL injection.

Risk Level: HIGH

Suggested Fix:
Use SQLAlchemy parameterized queries instead of raw SQL strings.
```

---

# OpenAI Cost per Pull Request

SecureMR only runs AI analysis on **new vulnerabilities introduced by the PR/MR**.

Typical usage:

| Agent | Model |
|------|------|
| Explain | GPT-4o |
| Risk | GPT-4o-mini |
| Fix | GPT-4o |

Average usage:

1–3 findings per PR

Typical cost:

< $0.01 per PR

---

# Troubleshooting

### No vulnerabilities reported

Ensure your PR contains code triggering a Semgrep rule.

Example:

```python
import os
os.system("ping " + user_input)
```

### Full repository scan instead of PR/MR-only scan

If SecureMR cannot find the base commit inside CI, it falls back to a full repository scan.

To avoid that:

• In GitHub Actions, use `fetch-depth: 0` and pass `GITHUB_BASE_SHA` plus the PR head SHA into the container.  
• In GitLab CI, set `GIT_DEPTH: "0"` and pass both `CI_MERGE_REQUEST_DIFF_BASE_SHA` and `CI_COMMIT_SHA` into the container.

### No PR/MR comment posted

Check the workflow variables and permissions:

• GitHub requires `GITHUB_TOKEN`, `GITHUB_EVENT_PATH`, `GITHUB_REPOSITORY`, `pull-requests: write`, and `issues: write`.  
• GitLab requires `GITLAB_TOKEN` with `api` scope, plus `CI_PROJECT_ID`, `CI_MERGE_REQUEST_IID`, and `CI_API_V4_URL`.

### OpenAI key not set

If `OPENAI_API_KEY` is missing, SecureMR falls back to the bundled local llama-cpp model instead of disabling AI entirely.

---

# Roadmap

• SARIF output support  
• GitHub Code Scanning integration  
• Container scanning with Trivy  
• Dependency scanning  
• Multi-language support  
• Cost-optimized AI pipeline  

---

# License

MIT License

---

# Contributing

Issues and pull requests are welcome.
