# Security Policy

## Supported Versions

The following versions of DeepVerify are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| latest (main) | :white_check_mark: |
| older releases | :x: |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue in DeepVerify, please help us by reporting it responsibly.

### Private Vulnerability Reporting (Preferred)

You can report vulnerabilities privately using GitHub's built-in private vulnerability reporting feature:

1. Go to the [Security tab](../../security) of this repository.
2. Click **"Report a vulnerability"**.
3. Fill in the details of the vulnerability and submit.

This allows you to report the issue directly to the maintainers without publicly disclosing it. GitHub's private vulnerability reporting keeps the details confidential until a fix is ready.

> **Note:** Private vulnerability reporting must be enabled by the repository maintainers via **Settings → Security → Private vulnerability reporting → Enable**.

### Email Disclosure

If you prefer, you can also report vulnerabilities by email. Please send a description of the issue, steps to reproduce, and any relevant proof-of-concept to the repository maintainers. You can reach us by opening a [GitHub Discussion](../../discussions) or contacting the repository owner directly via their GitHub profile.

### What to Include

When reporting a vulnerability, please provide:
- A description of the vulnerability and its potential impact
- Steps to reproduce the issue
- Any relevant logs, screenshots, or proof-of-concept code
- Suggested fix (if available)

## What to Expect After Reporting

- **Acknowledgement:** We aim to acknowledge your report within **48 hours**.
- **Assessment:** We will assess the severity and impact of the vulnerability within **7 days**.
- **Fix & Disclosure:** We will work on a fix and coordinate a disclosure timeline with you. We follow responsible disclosure practices and aim to release a fix before any public disclosure.
- **Credit:** With your permission, we will credit you in the release notes for responsible disclosure.

## Security Best Practices for Contributors

- Do not commit secrets, API keys, or credentials to the repository.
- Use the `.env.example` file as a template and keep actual `.env` files out of version control.
- Review dependency updates from Dependabot and apply security patches promptly.
