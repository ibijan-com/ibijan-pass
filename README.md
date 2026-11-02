# iBijan Pass
**Memorable Password Generation — Built Around Your Own Pattern**

iBijan Pass is a secure, offline desktop application designed to help you create reproducible, service-specific passwords using personal patterns or deterministic cryptographic generation. 

Unlike conventional password managers, iBijan Pass focuses primarily on **generating** passwords rather than requiring you to maintain a database of every password you use. It features a built-in encrypted vault for the passwords you do want to save.

**Website:** [ibijan.com](https://ibijan.com)  
**Repository:** [github.com/ibijan-com/ibijan-pass](https://github.com/ibijan-com/ibijan-pass)

> **Note:** Currently, official pre-built packages are provided for **Linux** (AppImage, DEB, RPM). Windows and macOS support is planned for future releases.

---

## Features

- **Dual Generation Modes:** Choose between Mental Mode (for memorable patterns) and Cryptographic Mode (for deterministic, highly secure passwords).
- **Deterministic Generation:** Reproduce the exact same password by supplying the same generation inputs. No need to save the password itself.
- **Profile Management:** Organize and reuse your generation configurations (prefixes, base numbers, patterns).
- **Optional Local Vault:** Save selected credentials securely in a local, encrypted table. Add notes, copy, or bulk-delete entries.
- **Portable Backup & Restore:** Export all your data (Profiles, Crypto Services, and Vault) into a single `.ibpass` file. You can protect it with a custom password and restore it on **any computer**.
- **100% Offline:** No internet connection is required, and zero telemetry is collected.
- **Military-Grade Encryption:** All local data is encrypted using AES-128 (Fernet) with strict `0600` file permissions on Unix systems.

---

## Generation Modes

### 1. Mental Mode
Mental Mode generates passwords using a repeatable personal pattern configured by you.
*   **Inputs:** A personal prefix, a base number, special characters, the service name, and optional capitalization.
*   **Why use it?** It provides a memorable approach to password generation, reducing the need to memorize an arbitrary pattern for every service.
*   **Security Note:** The security of this mode depends on the secrecy and complexity of your chosen pattern. A memorable pattern should not automatically be considered cryptographically strong. If an attacker obtains multiple passwords generated from the same pattern, they may reverse-engineer your formula.

### 2. Cryptographic Mode
Cryptographic Mode generates deterministic, service-specific passwords using a Master Secret (which is different from your Application Master Password) and the service/account name.
*   **How it works:** It derives a password using HMAC-SHA256 and a unique, random salt per service. 
*   **Why use it?** It allows you to generate highly secure, random-looking passwords (up to 128 characters) without ever saving them to disk. The same Master Secret and service details will reproduce the exact same password on any device.
*   **Security Note:** Anyone who obtains your Master Secret and the backup data may be able to regenerate the passwords. Protecting the Master Secret is therefore essential.

---

## Installation (Linux)

You can download the latest packages from the [Releases](https://github.com/ibijan-com/ibijan-pass/releases) page.

### Option 1: AppImage (Recommended for all distros)
~~~bash
# Download the AppImage
chmod +x ibijan-pass-1.1.2-x86_64.AppImage
./ibijan-pass-1.1.2-x86_64.AppImage
~~~

### Option 2: DEB Package (Ubuntu / Debian / Linux mint / Kali)
~~~bash
# Download the .deb file, then run:
sudo apt install ./ibijan-pass_1.1.2_amd64.deb
~~~

### Option 3: RPM Package (Fedora / CentOS / RHEL)
~~~bash
# Download the .rpm file, then run:
sudo rpm -i ibijan-pass-1.1.2-1.x86_64.rpm
~~~

### Option 4: Run from Source (Developers)
Requires Python 3.10+.

~~~bash
git clone https://github.com/ibijan-com/ibijan-pass.git
cd ibijan-pass
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spg
~~~

---

## Backup & Restore Workflow

Moving your data between computers has never been easier:

1. Click **Export** and select "All Data".
2. Set a strong **Backup Password** (Required for security).
3. Save the `.ibpass` file.
4. On the new machine (or after a factory reset), open iBijan Pass, click **Import**, enter the password, and select the file.
5. Your profiles, crypto services, and vault items will be securely restored.

*Important: Do not store the backup password alongside the backup file. Losing the backup password may make the backup unrecoverable.*

---

## Security Considerations

- **True Master Password:** Your Application Master Password is used to derive the local encryption key using `scrypt`. Without it, your local data is mathematically inaccessible.
- **Atomic Storage:** All data is saved using atomic file replacement to prevent corruption during unexpected crashes.
- **Independent Validation:** Password generation enforces strict character and length rules internally.
- **Clipboard Caution:** Clipboard contents may remain accessible to other applications. We recommend clearing your clipboard after pasting passwords.
- **No Independent Audit:** This application has not yet undergone an independent third-party security audit. Do not rely on it as the sole protection for high-value accounts.

> **Important Migration Note:** If you used version `1.0.2` or older, you must export your data before upgrading to `1.1.2`. Due to major security and storage architecture improvements, older local files cannot be opened directly by the new version.

---

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request or open an Issue.

## License
This project is licensed under the MIT License.
