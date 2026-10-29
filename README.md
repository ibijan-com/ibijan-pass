# iBijan Pass
**Memorable Password Generation**  
*A personal-pattern approach to generating memorable passwords.*

iBijan Pass is a secure, offline desktop application that generates highly customizable passwords. It features a dual-mode system: Mental Mode (for memorable, pattern-based passwords) and Cryptographic Mode (for highly secure, deterministic passwords). It also includes a built-in encrypted vault and a robust backup system.

**Website:** [ibijan.com](https://ibijan.com)  
**Repository:** [github.com/ibijan-com/ibijan-pass](https://github.com/ibijan-com/ibijan-pass)

> **Note:** Currently, official pre-built packages are provided for **Linux** (AppImage, DEB, RPM). Windows and macOS support is planned for future releases.

---

## Features

### Dual Generation Modes
- **Mental Mode:** Generate passwords based on personal patterns (Prefix, Base Number, Special Characters) that are easy for the human brain to remember and recreate.
- **Cryptographic Mode:** Generate deterministic, site-specific passwords using a Master Secret and HMAC-SHA256. The same secret and service details will always generate the exact same highly secure password on any device, without ever saving the password to disk.

### Security & Storage
- **Encrypted Vault:** Save generated passwords securely. View them in a clean table format, add optional notes, and easily copy or bulk-delete multiple entries.
- **True Master Password:** Your Application Master Password is used to derive the encryption key using `scrypt`.
- **Atomic Storage:** All data is saved using atomic file replacement to prevent corruption during unexpected crashes.
- **Strict File Permissions:** Saved data is protected with `0600` permissions on Unix systems.
- **Portable Backup & Restore:** Export all your data (Profiles, Crypto Services, and Vault) into a single `.ibpass` file. Protect it with a custom backup password and restore it anywhere.
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
chmod +x ibijan-pass-1.1.0-x86_64.AppImage
./ibijan-pass-1.1.0-x86_64.AppImage
~~~

### Option 2: DEB Package (Ubuntu / Debian / Kali)
~~~bash
# Download the .deb file, then run:
sudo apt install ./ibijan-pass_1.1.0_amd64.deb
~~~

### Option 3: RPM Package (Fedora / CentOS / RHEL)
~~~bash
# Download the .rpm file, then run:
sudo rpm -i ibijan-pass-1.1.0-1.x86_64.rpm
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
2. Set a **Backup Password** (Required for security).
3. Save the `.ibpass` file.
4. On the new machine (or after a factory reset), open iBijan Pass, click **Import**, enter the password, and select the file.
5. Your profiles, crypto services, and vault items will be securely restored.

---

## Important Migration Note

If you used version `1.0.2` or older, you must export your data before upgrading to `1.1.0`. Due to major security and storage architecture improvements (Atomic Writes and State Machine), older local files cannot be opened directly by the new version.

---

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request or open an Issue.

## License
This project is licensed under the MIT License.
