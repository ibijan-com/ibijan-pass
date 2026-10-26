# 🔐 iBijan Pass
**Smart, Offline, and Encrypted Password Generator**

iBijan Pass is a secure, offline desktop application that generates highly customizable passwords based on your own patterns. It features a built-in encrypted vault and a profile management system to keep your accounts safe without relying on cloud services.

🌐 **Website:** [ibijan.com](https://ibijan.com)  
🐙 **Repository:** [github.com/ibijan-com/ibijan-pass](https://github.com/ibijan-com/ibijan-pass)

> **Note:** Currently, official pre-built packages are provided for **Linux** (AppImage, DEB, RPM). Windows and macOS support is planned for future releases.

---

## ✨ Features

- **Custom Generation Patterns:** Define exactly how your password is constructed using Prefixes, Base Numbers, Special Characters, and specific patterns.
- **Portable Backup & Restore:** Export your data (Profiles and Vault) into a single `.spg` file. You can protect it with a custom password and restore it on **any computer**, even after a factory reset.
- **Encrypted Vault:** Save generated passwords securely. View them in a clean table format with optional notes for each account.
- **Secure Profiles (🔒):** Add an extra layer of authentication for highly sensitive accounts (like Banking) requiring the Master Password.
- **Military-Grade Encryption:** All local data is encrypted using AES-128 (Fernet).
- **Auto-Load:** After importing a backup, the app automatically loads your first profile for immediate use.
- **100% Offline:** No internet connection is required, and zero telemetry is collected.

---

## 📸 Screenshots
*(You can add your application screenshots here later)*

---

## 🚀 Installation (Linux)

You can download the latest packages from the [Releases](https://github.com/ibijan-com/ibijan-pass/releases) page.

### Option 1: AppImage (Recommended for all distros)
AppImage is a portable format that runs on almost any Linux distribution without installation.

~~~bash
# Download the AppImage
chmod +x ibijan-pass-0.9.2-x86_64.AppImage
./ibijan-pass-0.9.2-x86_64.AppImage
~~~

### Option 2: DEB Package (Ubuntu / Debian / Kali)

~~~bash
# Download the .deb file, then run:
sudo apt install ./ibijan-pass_0.9.2_amd64.deb
~~~

### Option 3: RPM Package (Fedora / CentOS / RHEL)

~~~bash
# Download the .rpm file, then run:
sudo rpm -i ibijan-pass-0.9.2-1.x86_64.rpm
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

---

## 💾 Backup & Restore Workflow

Moving your data between computers has never been easier:

1. Click **Export** and select "All Data".
2. Set a **Backup Password** (highly recommended) or leave it blank for a portable unprotected backup.
3. Save the `.spg` file.
4. On the new machine (or after a factory reset), open iBijan Pass, click **Import**, enter the password (if set), and select the file.
5. Your profiles and vault items will be immediately restored.

---

## 🛡️ Security & Privacy

- **Master Password:** Protects access to the application. Cannot be recovered if lost.
- **Local Storage:** All data is stored locally in `~/.spg/` and is encrypted at rest.
- **No Telemetry:** We don't collect any data.

---

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request or open an Issue.

## 📄 License
This project is licensed under the MIT License.
