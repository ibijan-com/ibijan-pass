"""
Configuration and constants for SPG.

This module contains only static configuration — no dependencies
on other modules in the package. It can be safely imported anywhere.
"""

import os

# ============================================================
# Application metadata
# ============================================================
APP_NAME = "iBijan Pass" 
APP_VERSION = "1.1.10"
APP_AUTHOR = "iBijan"
APP_WEBSITE = "https://ibijan.com"
APP_DESCRIPTION = "Offline, encrypted password generator with custom patterns"


# ============================================================
# File system paths
# ============================================================
CONFIG_DIR = os.path.expanduser("~/.spg")
KEY_FILE = os.path.join(CONFIG_DIR, "key.key")
MASTER_HASH_FILE = os.path.join(CONFIG_DIR, "master.hash")
VAULT_FILE = os.path.join(CONFIG_DIR, "vault.enc")
PROFILES_FILE = os.path.join(CONFIG_DIR, "profiles.enc")
CRYPTO_SERVICES_FILE = os.path.join(CONFIG_DIR, "crypto_services.enc")

# ============================================================
# Password patterns
# Each pattern defines the order of: prefix, middle, special_chars, end_number
# ============================================================
PASSWORD_PATTERNS = {
    "PREFIX + MIDDLE + SPECIAL + END_NUMBER": "{prefix}{middle}{special_chars}{end_number}",
    "END_NUMBER + MIDDLE + SPECIAL + PREFIX": "{end_number}{middle}{special_chars}{prefix}",
    "SPECIAL + PREFIX + MIDDLE + END_NUMBER": "{special_chars}{prefix}{middle}{end_number}",
    "MIDDLE + END_NUMBER + PREFIX + SPECIAL": "{middle}{end_number}{prefix}{special_chars}",
    "PREFIX + SPECIAL + MIDDLE + END_NUMBER": "{prefix}{special_chars}{middle}{end_number}",
    "END_NUMBER + SPECIAL + PREFIX + MIDDLE": "{end_number}{special_chars}{prefix}{middle}",
}

DEFAULT_PATTERN = "PREFIX + MIDDLE + SPECIAL + END_NUMBER"


# ============================================================
# Validation rules
# ============================================================
ALLOWED_SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?~"

# ============================================================
# Brand Colors (Persian Blue theme)
# ============================================================
# ============================================================
# Brand Colors (Persian Theme)
# ============================================================
BRAND_PRIMARY    = "#1C39BB"   # Persian Blue
BRAND_DARK       = "#142C8E"
BRAND_LIGHT      = "#3A56D4"
BRAND_VERY_LIGHT = "#E8ECFA"

COLOR_SUCCESS    = "#00A693"   # Persian Green 
COLOR_WARNING    = "#F59E0B"   # Amber 
COLOR_DANGER     = "#CC3333"   # Persian Red 

COLOR_NEUTRAL    = "#6B7280"
COLOR_BG         = "#FFFFFF"
COLOR_BG_ALT     = "#F9FAFB"
# ============================================================
# UI Text
# ============================================================
APP_TAGLINE    = "Memorable Password Generation"

UI_FONT_FAMILY = "Helvetica" 
UI_FONT_SIZE = 10
