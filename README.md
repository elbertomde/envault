# envault

> A CLI tool for managing and encrypting environment variable files across projects with team sharing support.

---

## Installation

```bash
pip install envault
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended for CLI tools):

```bash
pipx install envault
```

---

## Usage

**Initialize envault in your project:**
```bash
envault init
```

**Encrypt your `.env` file:**
```bash
envault encrypt .env --output .env.vault
```

**Decrypt a vault file:**
```bash
envault decrypt .env.vault --output .env
```

**Share with your team by pushing to a remote store:**
```bash
envault push --project my-app --env production
envault pull --project my-app --env production
```

**List managed environments:**
```bash
envault list
```

---

## How It Works

`envault` encrypts your environment files using AES-256 encryption and stores them securely. Team members with the correct key can pull and decrypt shared configurations without ever exposing secrets in plain text in version control.

Add `.env` to your `.gitignore` and safely commit `.env.vault` instead.

---

## Requirements

- Python 3.8+
- `cryptography` >= 41.0

---

## License

This project is licensed under the [MIT License](LICENSE).