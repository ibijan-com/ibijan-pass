# iBijan Pass
**Memorable Password Generation**  
*A personal-pattern approach to generating memorable passwords.*

iBijan Pass is a secure, offline desktop application that generates highly customizable passwords based on your own patterns. It features a built-in encrypted vault and a profile management system to keep your accounts safe without relying on cloud services.

**Website:** [ibijan.com](https://ibijan.com)  
**Repository:** [github.com/ibijan-com/ibijan-pass](https://github.com/ibijan-com/ibijan-pass)

> **Note:** Currently, official pre-built packages are provided for **Linux** (AppImage, DEB, RPM). Windows and macOS support is planned for future releases.

---

## Features

- **Custom Generation Patterns:** Define exactly how your password is constructed using Prefixes, Base Numbers, Special Characters, and specific patterns.
- **Portable Backup & Restore:** Export your data (Profiles and Vault) into a single `.ibpass` file. You can protect it with a custom password and restore it on **any computer**, even after a factory reset.
- **Encrypted Vault:** Save generated passwords securely. View them in a clean table format, add optional notes, and easily copy or bulk-delete multiple entries.
- **Secure Profiles (🔒):** Add an extra layer of authentication for highly sensitive accounts (like Banking) requiring the Master Password.
- **Military-Grade Encryption:** All local data is encrypted using AES-128 (Fernet).
- **Auto-Load:** After importing a backup, the app automatically loads your first profile for immediate use.
- **100% Offline:** No internet connection is required, and zero telemetry is collected.

---

## Screenshots
*(You can add your application screenshots here later)*

---

## Installation (Linux)

You can download the latest packages from the [Releases](https://github.com/ibijan-com/ibijan-pass/releases) page.

### Option 1: AppImage (Recommended for all distros)
~~~bash
# Download the AppImage
chmod +x ibijan-pass-1.0.1-x86_64.AppImage
./ibijan-pass-1.0.1-x86_64.AppImage
~~~

### Option 2: DEB Package (Ubuntu / Debian / Kali)
~~~bash
# Download the .deb file, then run:
sudo apt install ./ibijan-pass_1.0.1_amd64.deb
~~~

### Option 3: RPM Package (Fedora / CentOS / RHEL)
~~~bash
# Download the .rpm file, then run:
sudo rpm -i ibijan-pass-1.0.1-1.x86_64.rpm
~~~

### Option 4: Run from Source (Developers)
Requires Python 3.8+.

~~~bash
git clone https://github.com/ibijan-com/ibijan-pass.git
cd ibijan-pass
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spg
~~~

## Backup & Restore Workflow

Moving your data between computers has never been easier:

1. Click **Export** and select "All Data".
2. Set a **Backup Password** (highly recommended) or leave it blank for a portable unprotected backup.
3. Save the `.ibpass` file.
4. On the new machine (or after a factory reset), open iBijan Pass, click **Import**, enter the password (if set), and select the file.
5. Your profiles and vault items will be immediately restored.

---

## Security & Privacy

- **True Master Password:** Your master password is used to derive the encryption key using `scrypt`. Without it, your data is mathematically inaccessible.
- **Strict File Permissions:** Saved data is protected with `0600` permissions on Unix systems.
- **Local Storage:** All data is stored locally in `~/.spg/` and is encrypted at rest.
- **No Telemetry:** We don't collect any data.

> **Important Migration Note:** If you used version 0.9.3 or older, you cannot open your old data directly with v1.0.0. Please export a backup from the old version, upgrade, and import it back.

---

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request or open an Issue.

##  License
This project is licensed under the MIT License.
