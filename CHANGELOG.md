# Changelog

## [v0.9.2] - 2024-10-26

### ✨ Added
- **Portable Backups:** Replaced complex encryption keys with an optional backup password. Backup files can now be imported on ANY computer, even after a Factory Reset.
- **Auto-Load Profile:** The application now automatically loads the first profile immediately after a successful import.

### 🐛 Fixed
- Fixed an issue where the Vault encryption key would mismatch after importing a backup from another system.
- Fixed custom error dialogs to prevent them from being resizable.
- Fixed the application to automatically restart after performing a Factory Reset.
- Fixed YAML syntax error in GitHub Actions workflow.

### 💅 UI/UX Improvements
- Added clearer error messages for invalid backup passwords.
