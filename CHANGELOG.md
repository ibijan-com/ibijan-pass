# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.1.12] - 2026-11-21

### Fixed
- **Critical Vault Import Bug:** Fixed a critical data loss bug where importing a backup would overwrite and delete newer passwords stored in the local Vault. The import process now safely **merges** incoming Vault entries with existing ones without data loss.
- **Silent Import Conflicts:** Importing Profiles or Crypto Services with identical names but different settings no longer silently ignores the backup data. The application now detects these conflicts and prompts the user to either **Keep Existing** data or **Replace with Backup**.

### Security & Reliability
- **KDF Parameter Validation:** Added strict validation for the `kdf_n` parameter in imported backup files (restricting it to safe bounds). This prevents maliciously crafted backup files from causing memory exhaustion (Local DoS) during decryption.

## [v1.1.11] - 2026-11-19

### Changed
- **Standard Menu Bar:** Moved secondary actions (Export, Import, Open Config, File Locations, Clear Vault, Factory Reset, Help, and About) into a standard application Menu Bar (`File`, `Tools`, `Help`). This significantly reduces UI clutter and cognitive load, making the main window more spacious and focused on password generation.
- **Help Guide Update:** Completely redesigned the in-app Help Guide. Added a new "Overview" tab that explains the difference between Mental Mode and Cryptographic Mode, and provided updated instructions reflecting the new menu layout.

---

## [v1.1.10] - 2026-11-18

*This is the first officially supported stable release of iBijan Pass. Previous releases in the v1.1.x series were development/pre-release builds.*

### Added
- **Privacy Masking:** Account identifiers in the Cryptographic Mode Saved Services list are now masked by default (e.g., `bij***@gmail.com`). Added a visibility toggle to reveal or hide the account identifier in the input field.
- **Security Tips Panels:** Added contextual security notices to both tabs to educate users about pattern reuse and Master Secret management.
- **Pattern Tooltip:** Added a dynamic tooltip and a preview label below the Pattern dropdown to prevent text truncation.

### Changed
- **UI/UX Layout Overhaul:** Reorganized the Mental Mode settings into a balanced two-column grid. Moved System, Data Transfer, and Data Management actions into three distinct columns at the bottom for better visual organization.
- **Application Icon:** Added a custom application icon with a transparent background. Improved application icon and title integration across supported Linux desktop environments.
- **Cryptographic Mode Stabilization:** Refined and stabilized the deterministic, site-specific password generation system introduced in v1.1.0, using a Master Secret, `scrypt`, and HMAC-SHA256. Generated passwords are not stored by the application.

### Security & Architecture
- **KDF Parameter Versioning:** Added explicit versioning and storage of `scrypt` parameters in `key.key` and `.ibpass` backup files, enabling the application to identify and correctly process supported KDF configurations.
- **Removed Legacy Hash:** Removed the legacy standalone SHA-256 master-password hash. Master-password verification and key derivation now use the `scrypt`-based architecture.
- **Transactional Backup Import:** Improved backup import with validation, staged file updates, and rollback handling to reduce the risk of partial data replacement.

### Fixed
- Fixed the `Ctrl+A` (Select All) key binding on Linux/X11 systems.
- Fixed issues with application window class identification and desktop integration on Linux.

---

## [v1.1.0] - 2026-10-29

### Added
- **Cryptographic Mode (Pre-release):** Introduced a deterministic, site-specific password generator using a Master Secret, `scrypt`, and HMAC-SHA256. Generated passwords are not stored by the application.
- **Multi-Account Support:** Added support for saving multiple accounts per service in Cryptographic Mode.
- **Forgot Master Password:** Added a "Forgot Master Password?" option to the login screen to guide users through a Factory Reset.

### Security & Reliability
- **Independent Input Validation:** Password generation now enforces character and length restrictions internally, independently of UI validation.
- **Backup Integrity:** Backups now require a password, and corrupted Vault files prevent the export process from proceeding.

---

## [v1.0.2] - 2026-10-28

### Changed
- Renamed "Profiles" to "Saved Patterns" throughout the application UI.
- Added an instructional hint below the Saved Patterns selection area.

---

## [v1.0.1] - 2026-10-27

### Added
- **Bulk Delete in Vault:** Added multi-selection support for deleting multiple saved passwords at once.
- **Capitalization Upgrade:** Expanded the "Capitalize Letter(s)" input to accept up to three characters.

### Changed
- Removed the redundant Quotation feature.

### Fixed
- Fixed a critical bug that prevented profiles from being saved to disk due to missing file-write logic.

---

## [v1.0.0] - 2026-10-27

### Security
- **Master Password Architecture:** Implemented a `scrypt`-based Key Derivation Function (KDF) for master-password-based key derivation.
- **Encrypted Portable Backups:** Introduced portable `.ibpass` backup files encrypted using `scrypt` and a unique salt.
- **File System Permissions:** Applied restrictive `0600` permissions to sensitive files on supported POSIX systems.
- **Atomic File Writes:** Implemented atomic file replacement using temporary files to reduce the risk of data corruption during writes.
- **Data Loss Prevention:** Added safeguards to prevent the application from overwriting or resetting existing encrypted data when its encryption key is missing.

---

## [v0.9.3] - 2026-10-27

### Added
- **Branding Tagline:** Updated the application branding to use "Memorable Password Generation".
- **Dynamic Window Title:** Updated the main window title to display the new branding tagline.

---

## [v0.9.2] - 2026-10-26

### Added
- **Portable Backups:** Introduced portable backup files using an optional backup password.
- **Auto-Load Profile:** Added automatic loading of the first available profile after a successful backup import.

### Fixed
- Fixed an issue that caused the Vault encryption key to become mismatched after importing a backup.
- Fixed custom error dialogs to prevent them from being resized.
- Fixed the application to restart automatically after a Factory Reset.
