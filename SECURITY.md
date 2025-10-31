# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please **do not** open a public issue. Instead, please email the maintainers directly or create a private security advisory.

### What to Report

- Exposure of sensitive data (credentials, tokens, API keys)
- Remote code execution vulnerabilities
- Authentication/authorization bypasses
- Data leakage or privacy concerns
- Any issue that could compromise user privacy or data security

### What NOT to Report

- Issues with OCR accuracy (these are expected limitations)
- General bugs or feature requests (use regular Issues for these)

## Security Best Practices

### Credentials Management

- **Never commit credentials.json, token.json, or any API keys to the repository**
- Store credentials in `~/.config/itbl/` directory (which is gitignored)
- Use environment variables when possible: `GOOGLE_APPLICATION_CREDENTIALS`
- Rotate credentials if accidentally exposed

### Data Privacy

- This tool processes images **offline by default** - no data is sent to external services unless you explicitly use Google Sheets output
- When using Google Sheets, only extracted structured data is sent (not the original images)
- OCR processing happens locally using Tesseract
- Review your Google Sheets permissions before sharing

### Recommendations

1. Keep your dependencies updated: `pip install --upgrade itbl`
2. Review extracted data before committing to your bookkeeping system
3. Use the triage mode (`--triage`) to review low-confidence extractions
4. Keep your Tesseract installation updated for better OCR security

## Security Acknowledgments

We thank security researchers who responsibly disclose vulnerabilities.

