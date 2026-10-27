# Changelog

## [v1.0.2] - 2026-10-28

### Added
- **Clear Service Button:** Added a dedicated button to clear only the "Service Name" field. This allows users to keep their mental pattern loaded while quickly generating a password for a new website.

### Changed
- **Mental Patterns Concept:** Renamed "Profiles" to "Saved Patterns" across the UI to better align with the core philosophy of the application (saving base components rather than site-specific profiles).
- **Save Button:** Renamed "Save As New" to "Save Pattern" for consistency.

### UI/UX Improvements
- Added an instructional hint text below the pattern selection area to guide users on how to use saved patterns for new services.
- Increased the font size of the hint text for better readability.

---

## [v1.0.1] - 2026-10-27
...

## [v1.0.1] - 2026-10-27

### Added
- **Bulk Delete in Vault:** Added multi-select capability (`Ctrl+A` or `Shift+Click`) to the Vault table, allowing users to delete multiple saved passwords at once.
- **Capitalization Upgrade:** The "Capitalize Letter(s)" input now accepts up to 3 characters, giving users more flexibility in generating passwords (e.g., typing "gom" will directly insert "GOM" instead of searching the service name).

### Fixed
- Removed the redundant "Quotation" feature from the UI, as users can simply add quotes to the "Special Characters" field.
- Fixed a critical bug where profiles were not being saved to disk due to missing file write logic in the storage layer.

---

## [v1.0.0] - 2026-10-27

###  MAJOR SECURITY UPGRADE
- **True Master Password Architecture:** Implemented `scrypt` KDF. The master password now actually protects the encryption keys. An attacker with access to your files cannot decrypt them without the master password.
- **Secure Portable Backups:** Backup files (.ibpass) are now encrypted using `scrypt` and a unique salt, making them highly resistant to brute-force attacks.
- **File System Permissions:** Sensitive files in `~/.spg` now have strict `0600` permissions (Linux/macOS).
- **Atomic File Writes:** Data is written to temporary files first to prevent corruption during unexpected crashes.
- **Data Loss Prevention:** The application will now refuse to overwrite or reset data if the encryption key is missing or corrupted.

###  Breaking Changes
- Due to the new KDF architecture, this version cannot read files created by versions 0.9.3 and older. Users must perform a Factory Reset and restore their data using a `.ibpass` backup file.

...
## [v0.9.3] - 2026-10-27

###  Added
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
