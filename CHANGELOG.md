# Changelog

## [v1.1.0] - 2026-10-29

### ✨ New Features
- **Cryptographic Mode:** Introduced a highly secure, deterministic password generator based on HMAC-SHA256 and a Master Secret. It generates site-specific passwords without saving them to the database.
- **Multi-Account Support:** You can now save multiple accounts per service in Cryptographic Mode (e.g., `google | work@gmail.com` and `google | personal@gmail.com`).
- **Forgot Password Button:** Added a "Forgot Master Password?" link to the login screen to guide users through a secure Factory Reset if they lose their password.

### 🛡️ Major Security & Reliability Overhaul
- **Atomic File Writes:** All data is now written to secure temporary files and atomically replaced. This prevents data corruption if the app crashes or power is lost.
- **Transactional Backup Import:** Importing a backup is now fully transactional. If restoring one section (e.g., Vault) fails, all changes are rolled back, and your existing data remains untouched.
- **Cryptographic State Machine:** The app now refuses to start if the encryption key is missing but encrypted data exists, preventing accidental data overwrites.
- **Independent Input Validation:** Password generation enforces strict character and length rules internally.
- **Removed Fast SHA-256 Hash:** Authentication now relies entirely on the secure `scrypt` KDF.
- **Backup Integrity:** Backups now strictly require a password, and corrupted Vault files will halt the export process instead of creating incomplete backups.

### 💅 UI/UX Improvements
- Completely redesigned the UI with a tabbed interface to separate Mental Mode and Cryptographic Mode.
- Updated the `Help Guide` with comprehensive instructions for both modes.
- Changed the default backup file extension to `.ibpass`.

### ⚠️ Breaking Changes
- Due to the new atomic storage and KDF architecture, this version cannot read local files created by versions `1.0.2` and older. Users MUST export a backup from the old version and import it into the new version.

---

## [v1.0.2] - 2026-10-28
### Changed
- Renamed "Profiles" to "Saved Patterns" across the UI to align with the app's philosophy.
- Added an instructional hint text below the pattern selection area.

---

## [v1.0.1] - 2026-10-27
### Added
- Bulk Delete in Vault: Added multi-select capability (`Ctrl+A` or `Shift+Click`) to delete multiple saved passwords at once.
- Capitalization Upgrade: The "Capitalize Letter(s)" input now accepts up to 3 characters.
### Fixed
- Removed the redundant "Quotation" feature.
- Fixed a critical bug where profiles were not being saved to disk due to missing file write logic.

---

## [v1.0.0] - 2026-10-27
### 🛡️ MAJOR SECURITY UPGRADE
- **True Master Password Architecture:** Implemented `scrypt` KDF.
- **Secure Portable Backups:** Backup files (.ibpass) are now encrypted using `scrypt` and a unique salt.
- **File System Permissions:** Sensitive files now have strict `0600` permissions.
- **Atomic File Writes:** Data is written to temporary files first.
- **Data Loss Prevention:** The application will now refuse to overwrite or reset data if the encryption key is missing or corrupted.

### ⚠️ Breaking Changes
- Due to the new KDF architecture, this version cannot read files created by versions 0.9.3 and older. Users must perform a Factory Reset and restore their data using a `.ibpass` backup file.

---

## [v0.9.3] - 2026-10-27
### Added
- **New Branding Tagline:** Updated the UI to reflect "Memorable Password Generation" and "A personal-pattern approach".
- **Updated Title Bar:** The main window title now dynamically shows the new tagline.

### UI/UX Improvements
- Changed the default backup file extension from `.spg` to `.ibpass` to align with the branding.
- Updated README and installation instructions for the new version.

---

## [v0.9.2] - 2026-10-26
### Added
- **Portable Backups:** Replaced complex encryption keys with an optional backup password. Backup files can now be imported on ANY computer, even after a Factory Reset.
- **Auto-Load Profile:** The application now automatically loads the first profile immediately after a successful import.

### Fixed
- Fixed an issue where the Vault encryption key would mismatch after importing a backup from another system.
- Fixed custom error dialogs to prevent them from being resizable.
- Fixed the application to automatically restart after performing a Factory Reset.
- Fixed YAML syntax error in GitHub Actions workflow.

### UI/UX Improvements
- Added clearer error messages for invalid backup passwords.
