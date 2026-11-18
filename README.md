# iBijan Pass

**Memorable Password Generation — Built Around Your Own Pattern**

iBijan Pass is an offline desktop application designed to help you generate reproducible, service-specific passwords using personal patterns or deterministic cryptographic derivation.

Unlike conventional password managers, iBijan Pass focuses primarily on **generating passwords** rather than requiring you to maintain a database of every password you use. It also includes an encrypted vault for passwords you explicitly choose to save.

**Website:** [ibijan.com](https://ibijan.com)  
**Repository:** [github.com/ibijan-com/ibijan-pass](https://github.com/ibijan-com/ibijan-pass)

> **Platform Support:** Official pre-built packages are currently available for **Linux** (AppImage, DEB, and RPM). Windows and macOS support are planned for future releases.

---

## Features

- **Dual Generation Modes:** Choose between Mental Mode, which uses memorable personal patterns, and Cryptographic Mode, which uses deterministic cryptographic derivation.
- **Deterministic Generation:** Reproduce the same password using the same generation inputs, Master Secret, service metadata, and generation settings.
- **Privacy Masking:** Account identifiers in Cryptographic Mode are masked by default. A visibility toggle allows you to reveal them when needed.
- **Clean Interface:** Secondary actions are organized into standard `File`, `Tools`, and `Help` menus to keep the main interface focused.
- **Portable Backup & Restore:** Export your Profiles, Crypto Services metadata, and Vault into a single `.ibpass` backup file protected by a custom backup password.
- **Offline by Design:** Core password generation and local data management work without an internet connection. No telemetry is intentionally collected.
- **Encrypted Local Storage:** Local application data is protected using Fernet authenticated encryption (AES-128-CBC with HMAC-SHA256). Sensitive files are protected with restrictive file permissions (`0600`) on supported POSIX systems.

---

## Generation Modes

### 1. Mental Mode

Mental Mode generates passwords using a repeatable personal pattern configured by you.

- **Inputs:** A personal prefix, a base number, special characters, the service name, and optional capitalization.
- **Benefits:** Provides a memorable approach to generating service-specific passwords without having to remember a completely different random password for every service.
- **Security Considerations:** Mental Mode is designed for memorability and convenience, not as a replacement for cryptographically generated passwords. Its security depends on the secrecy and complexity of your personal pattern. If an attacker obtains multiple passwords generated from the same pattern, they may be able to reverse-engineer your formula.

### 2. Cryptographic Mode

Cryptographic Mode generates deterministic, service-specific passwords using a Master Secret and service/account information.

- **How It Works:** Passwords are derived using a Master Secret, the memory-hard key derivation function `scrypt`, and HMAC-SHA256. Each service uses its own salt and generation settings, which are stored as encrypted metadata to support consistent password reproduction across devices.
- **Benefits:** Generates cryptographically derived, random-looking passwords without storing the generated passwords themselves. With the same Master Secret and corresponding service metadata, the same password can be reproduced on another device.
- **Salt and Metadata:** The service salt is stored as part of the encrypted service metadata. The salt does not need to be secret, but it must remain unchanged for consistent password reproduction.
- **Security Considerations:** Your Master Secret is essential for regenerating passwords in Cryptographic Mode. Anyone who obtains your Master Secret and the corresponding service metadata may be able to reproduce your generated passwords. Keep your Master Secret confidential and protect your encrypted backups.

> **Important:** Cryptographic Mode service metadata is included in backups, allowing passwords to be regenerated on another device when the corresponding Master Secret is available. Generated passwords themselves are not included unless you explicitly save them in the Vault.

---

## Installation (Linux)

Download the latest available packages from the [GitHub Releases](https://github.com/ibijan-com/ibijan-pass/releases) page.

### Option 1: AppImage (Recommended for most Linux distributions)

Download the AppImage file, then make it executable and run it:

```bash
chmod +x ibijan-pass-<version>-x86_64.AppImage
./ibijan-pass-<version>-x86_64.AppImage
```

### Option 2: DEB Package (Ubuntu / Debian / Linux Mint / Kali)

Download the `.deb` package, then install it using:

```bash
sudo apt install ./ibijan-pass_<version>_amd64.deb
```

### Option 3: RPM Package (Fedora / CentOS / RHEL)

On systems using DNF, download the `.rpm` package and install it using:

```bash
sudo dnf install ./ibijan-pass-<version>-1.x86_64.rpm
```

### Option 4: Run from Source (Developers)

**Requirement:** Python 3.10 or later.

```bash
git clone https://github.com/ibijan-com/ibijan-pass.git
cd ibijan-pass

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python -m spg
```

---

## First-Time Setup

Upon first launch, you will be asked to create an **Application Master Password**. This password is used to derive the local encryption key that protects the application's encrypted data, including Profiles, Vault items, and Crypto Services metadata.

> **Important:** The Application Master Password is different from the Master Secret used in Cryptographic Mode.
>
> - **Application Master Password:** Unlocks the application and protects its local encrypted data.
> - **Cryptographic Mode Master Secret:** Is used to derive your service-specific passwords.
>
> You can technically use the same text for both, but using separate secrets is recommended.

**Keep both secrets safe.** Losing the relevant secret may prevent you from accessing protected data or regenerating passwords.

---

## Backup & Restore

iBijan Pass provides a portable encrypted backup format (`.ibpass`) to help you transfer your application data between devices.

### Exporting a Backup

1. Open the application and navigate to **File → Export Data**.
2. Select **All Data** to include your Profiles, Crypto Services metadata, and Vault items.
3. Set a strong **Backup Password**. This password is used to encrypt the backup file.
4. Choose a location and save the resulting `.ibpass` file.

### Restoring a Backup

1. Install and open iBijan Pass on the destination device.
2. Navigate to **File → Import Data**.
3. Select your `.ibpass` file and provide the corresponding Backup Password.
4. Your exported Profiles, Crypto Services metadata, and Vault items will be restored.

> **Important:** The Backup Password is separate from your Application Master Password. Keep it confidential and do not store it alongside the backup file. If you lose the Backup Password, you may not be able to recover the contents of that backup.

**Cryptographic Mode portability:** Backups include the service metadata required to reproduce generated passwords. You must also have the corresponding Cryptographic Mode Master Secret. The generated passwords themselves are not stored in the backup unless they were explicitly saved in the Vault.

---

## Security Considerations & Limitations

- **Application Master Password:** The local encryption key is derived from the Application Master Password using `scrypt`.
- **Encrypted Local Data:** Application data is protected using Fernet authenticated encryption. File permissions provide an additional layer of local protection on supported POSIX systems.
- **Atomic File Writes:** Critical data files use atomic replacement to reduce the risk of file corruption during interrupted write operations.
- **Clipboard Caution:** Clipboard contents may remain accessible to other applications. We recommend clearing your clipboard after pasting passwords.
- **Mental Mode Limitations:** Mental Mode passwords are based on user-defined patterns and are not cryptographically random. Their security depends on the secrecy and complexity of the chosen pattern.
- **Master Secret Protection:** Anyone who obtains your Cryptographic Mode Master Secret and the corresponding service metadata may be able to regenerate your passwords.
- **No Independent Security Audit:** iBijan Pass has not yet undergone an independent third-party security audit. Do not rely on it as the sole protection for high-value accounts without considering your own security requirements.
- **Platform Support:** Official pre-built packages are currently available for Linux. Other platforms are planned for future releases.

---

## Contributing

Contributions are welcome!

If you find a bug, have a feature suggestion, or want to contribute code, please feel free to open an [Issue](https://github.com/ibijan-com/ibijan-pass/issues) or submit a Pull Request.

---

## License

This project is licensed under the [MIT License](LICENSE).
