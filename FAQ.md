# Frequently Asked Questions (FAQ)

This document answers common questions about **iBijan Pass**, its password-generation modes, local data protection, and backups.

- [General](#general)
- [Mental Mode](#mental-mode)
- [Cryptographic Mode](#cryptographic-mode)
- [Master Passwords and Backups](#master-passwords-and-backups)
- [Security and Privacy](#security-and-privacy)
- [Installation and Compatibility](#installation-and-compatibility)
- [Development and Contributions](#development-and-contributions)

---

## General

### What is iBijan Pass?

iBijan Pass is an offline desktop application for generating service-specific passwords. It offers two approaches: **Mental Mode**, which uses a personal pattern, and **Cryptographic Mode**, which uses deterministic cryptographic derivation. It also includes an encrypted local Vault for passwords you choose to save. In Cryptographic Mode, reproducing a previous password requires the original service metadata (including its salt and generation settings) as well as the same Master Secret. The Master Secret and service details alone are not sufficient: setting up the service from scratch on another device creates a new salt and produces a different password.

### Is iBijan Pass a password manager?

Not primarily. Its main purpose is to generate passwords that can be reproduced when the same inputs, Master Secret, and original service metadata are available. Unlike a conventional password manager, it does not require you to save every generated password. However, you can store selected passwords in its encrypted local Vault.

### Why does iBijan Pass have two generation modes?

The two modes address different preferences:

- **Mental Mode** is designed for people who prefer a memorable, repeatable personal pattern.
- **Cryptographic Mode** is designed for people who want deterministic, service-specific passwords derived using cryptographic techniques.

Neither approach is suitable for every user or every situation. Choose a mode with an understanding of its security properties and limitations.

### Is iBijan Pass free and open source?

Yes. iBijan Pass is released under the [MIT License](LICENSE). You can use, study, modify, and redistribute the software in accordance with that license.

---

## Mental Mode

### What is Mental Mode?

Mental Mode generates passwords from a repeatable personal pattern. You choose the main inputs, including a prefix, a base number, special characters, the service name, and optional capitalization. The application also performs one fixed calculation automatically: it adds the length of the service name to your base number. This calculation is built into the current implementation; it is not a formula that the user configures.

The idea is to remember your chosen inputs and the pattern rather than memorize a separate random string for every service.

### How does the service-length calculation work?

The application uses the exact value entered in the **Service Name** field and counts its characters. It uses that count in two places:

```text
service_length = len(service_name)
middle_component = str(service_length) + user_letter.upper()  # if provided
calculated_number = int(base_number) + service_length
```

If you do not enter optional capitalization letters, the middle component contains only the service length. The current implementation accepts up to three optional letters; it converts them to uppercase and appends them to the service-length component. These letters do not change the calculated number.

For example, if your base number is `100`:

| Service Name | Service length | Calculated number | Middle component with `k` |
| --- | ---: | ---: | ---: |
| `google` | 6 | `106` | `6K` |
| `yahoo` | 5 | `105` | `5K` |

This arithmetic is built into the current implementation and cannot be changed by the user. You choose the input values, but the application calculates the service-length component and the final number automatically.

The selected password pattern determines how the components (prefix, middle component, special characters, and calculated number) are arranged in the final password. Therefore, the formula above explains the automatic calculation; it is not, by itself, the complete final-password template. Use the same Service Name value, inputs, and selected pattern whenever you need to reproduce the same Mental Mode password.

### Is Mental Mode cryptographically random?

No. Mental Mode is designed for memorability and convenience; it is not a cryptographic password-derivation method. Its security depends on the secrecy and complexity of your chosen pattern.

### Can someone discover my pattern if one of my passwords is exposed?

Potentially. If an attacker obtains one or more passwords generated from the same pattern, they may be able to infer parts of the pattern and predict other outputs. Avoid simple or reused patterns, and do not treat Mental Mode as a replacement for cryptographically generated passwords when stronger protection is required.

### Should I use Mental Mode for every account?

That is not recommended as a blanket rule. Consider the sensitivity of each account and the limitations of your pattern. For accounts where you prefer a cryptographically derived password, use Cryptographic Mode or another suitable password-generation approach. You can also save selected passwords in the local Vault.

---

## Cryptographic Mode

### How does Cryptographic Mode work?

Cryptographic Mode derives a deterministic password from your **Master Secret** together with service- and account-related information. The current implementation uses `scrypt` and HMAC-SHA256. Service-specific metadata, including a salt and generation settings, is stored in the application's encrypted data so the same output can be reproduced later.

The exact output depends on the Master Secret and the corresponding service metadata and settings. **The original salt is essential:** if you set up the service from scratch on a fresh installation without importing its original metadata, the application creates a new salt. The resulting password will be different, even when the Master Secret and service/account details are identical.

### Will the same Master Secret and service details produce the same password on every device?

**No—not by themselves.** On a new device or fresh installation, if you enter the same Master Secret, service name, and account details but do not import the original service metadata, the application creates a new salt for the newly configured service. Because the salt is part of the derivation, the resulting password will be different. To reproduce the original password, first import the `.ibpass` backup containing that service's original metadata, then use the same Master Secret and generation settings.

### Are the generated passwords random?

The generation process is deterministic: the same Master Secret and the same service metadata and settings produce the same output. The result is intended to be random-looking, but it is not a newly random value each time you generate it.

### Does each service get a different password?

Cryptographic Mode uses service- and account-related information to derive service-specific outputs. Use the correct service and account details consistently, and keep each service's metadata intact. As with any password-generation system, do not assume that a password is suitable for a website until you have checked that it meets that website's requirements.

### If one generated password is exposed, are all my other passwords exposed?

Not automatically. A single output does not, by itself, reveal the Master Secret or directly disclose the outputs for other services. However, this is not a guarantee that every compromise is harmless. The strength and confidentiality of your Master Secret, the derivation design, the service metadata, and the security of your device and backups all matter. A weak Master Secret can create additional risk, including the possibility of offline guessing attacks.

### Why does Cryptographic Mode use a salt?

A salt is service-specific data used as part of the derivation process. In iBijan Pass, the salt must remain the same to reproduce the same password. It is stored in the encrypted service metadata and included in the application's backup data. A salt does not need to be secret, but losing or replacing it changes the derived output.

### Does Cryptographic Mode save the generated passwords?

Generated passwords are not stored by the application in Cryptographic Mode. The application stores the service metadata needed to reproduce them. You can separately choose to save a password in the encrypted Vault; saved Vault entries are included when you export all data.

### Does Cryptographic Mode support multiple accounts for one service?

Yes. Cryptographic Mode supports saving multiple accounts for a service. Keep the account information associated with each saved service entry accurate so you can select the intended account and reproduce the corresponding password.

---

## Master Passwords and Backups

### What is the difference between the Application Master Password and the Cryptographic Mode Master Secret?

They serve different purposes:

- **Application Master Password:** Used to unlock the application and derive the key that protects its encrypted local data.
- **Cryptographic Mode Master Secret:** Used to derive service-specific passwords in Cryptographic Mode.

You can technically use the same text for both, but using separate secrets is recommended.

### What happens if I forget my Application Master Password?

The Application Master Password protects access to the application's encrypted local data. It cannot simply be recovered from the encrypted data. The application provides a Factory Reset path, but a reset is not a way to decrypt data protected by a forgotten password. Before resetting, make sure you understand what data may be lost and whether you have a usable backup.

### What happens if I forget my Cryptographic Mode Master Secret?

You will not be able to regenerate the Cryptographic Mode passwords that depend on that secret. A backup preserves the service metadata, but it does not replace the Master Secret. Keep the Master Secret in a separate, secure place.

### What is included in an `.ibpass` backup?

When you export **All Data**, the backup includes your Profiles, Cryptographic Mode service metadata (including the original salts and generation settings), and Vault items. The backup is protected with a custom Backup Password.

Generated Cryptographic Mode passwords are not included unless you explicitly saved them in the Vault. The service metadata is what allows the application to reproduce the same output after restoring the backup; it is not the generated password itself.

### Why do I need a backup to reproduce the same Cryptographic Mode password on another device?

The service metadata contains information required to reproduce the same output, including each service's original salt and generation settings. On a new device, import the relevant `.ibpass` backup before recreating or using the service, then enter the same Cryptographic Mode Master Secret. If you do not import the original metadata and create the service again, the application generates a new salt. The resulting password will therefore be different, even if the Master Secret, service name, account details, and visible generation settings are identical.

### Is the Backup Password the same as the Application Master Password?

No. The Backup Password is separate and is used to protect the `.ibpass` backup file. Keep it safe and do not store it alongside the backup. If you lose it, you may not be able to recover the backup's contents.

### Does the backup contain my Cryptographic Mode Master Secret?

No. You must retain the corresponding Master Secret separately. The backup contains the service metadata needed for reproduction, not a substitute for the secret itself.

---

## Security and Privacy

### Does iBijan Pass require an internet connection?

The application's core password-generation and local data-management features work offline. No cloud account or online service is required for password generation. The project states that no telemetry is intentionally collected.

### How is local application data protected?

The application uses Fernet authenticated encryption, which combines AES-128-CBC encryption with HMAC-SHA256 authentication. The Application Master Password is used with `scrypt` to derive the local encryption key. Sensitive files are also given restrictive `0600` permissions on supported POSIX systems.

### Does iBijan Pass protect me from malware, keyloggers, or phishing?

No. iBijan Pass is a password-generation and local-vault application, not an antivirus, endpoint-protection, or phishing-detection tool. Malware running on your device may be able to access information while you use it, and the application cannot prevent you from entering a password on a fraudulent website. Keep your operating system protected and use multi-factor authentication where available.

### Are clipboard contents automatically protected or cleared?

Clipboard contents may remain available to other applications or clipboard-history tools, depending on your operating system and configuration. Clear the clipboard after pasting a password, especially on shared or untrusted devices.

### Has iBijan Pass undergone an independent security audit?

No. The project has not yet undergone an independent third-party security audit. The source code is publicly available for review, but open source by itself does not prove that software is free of vulnerabilities. Do not treat the application as the sole protection for high-value accounts without evaluating your own security requirements.

### Does atomic file writing guarantee that data can never be corrupted?

No. Critical files use atomic replacement to reduce the risk of incomplete writes and certain forms of file corruption. This is a reliability measure, not a guarantee against every possible failure, such as storage-device failure or broader system damage. Maintain regular backups.

---

## Installation and Compatibility

### Which operating systems are currently supported?

Official pre-built packages are currently provided for Linux:

- **AppImage** — recommended for most Linux distributions.
- **DEB** — for Debian-based distributions such as Debian, Ubuntu, Linux Mint, and Kali.
- **RPM** — for distributions that use RPM packages, such as Fedora and compatible systems.

Windows and macOS support are planned for future releases; no release date is currently promised.

### Can I run iBijan Pass from source?

Yes. The project README lists Python 3.10 or later as a requirement. Follow the [installation instructions in the README](README.md) to create a virtual environment, install dependencies, and run the application.

### Where can I download the latest release?

Download the available packages from the [GitHub Releases page](https://github.com/ibijan-com/ibijan-pass/releases).

### Where should I report an installation problem or a bug?

Please open an [issue on GitHub](https://github.com/ibijan-com/ibijan-pass/issues). Include the iBijan Pass version, Linux distribution and version, package type, steps to reproduce the problem, and any relevant error message or sanitized log.

**Never include your Application Master Password, Cryptographic Mode Master Secret, generated passwords, decrypted files, or private backup contents in an issue.**

---

## Development and Contributions

### Can I contribute to iBijan Pass?

Yes. Bug reports, thoughtful feature suggestions, documentation improvements, and code contributions are welcome. Please use [GitHub Issues](https://github.com/ibijan-com/ibijan-pass/issues) to discuss a problem or proposal, and submit a Pull Request for code or documentation changes.

### Is there a roadmap for Windows, macOS, Android, or browser extensions?

The currently published pre-built packages are for Linux. Windows and macOS support are planned. Other platforms and integrations, such as Android or browser extensions, may be considered in the future, but they should not be treated as committed features or scheduled releases.

### Where can I find the source code and license?

The source code is available in the [iBijan Pass GitHub repository](https://github.com/ibijan-com/ibijan-pass), and the project is distributed under the [MIT License](LICENSE).

---

## Security Reminder

No password-generation approach can compensate for a weak secret, a compromised device, unsafe password reuse, or phishing. Use a strong and unique Master Secret, keep your backups protected, use multi-factor authentication where available, and choose the generation mode that fits your needs and risk tolerance.

If you discover a potential security vulnerability, avoid posting sensitive exploit details or personal data in a public issue. Use a private channel to contact the maintainer so the report can be reviewed responsibly.
