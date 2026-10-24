"""
Password generation logic for SPG.

Pure logic module — no UI dependencies (no tkinter).
Returns tuples of (password, warning_message) so the UI can
decide how to present warnings to the user.
"""

from .config import PASSWORD_PATTERNS, DEFAULT_PATTERN


def build_password(
    prefix: str,
    base_number: str,
    special_chars: str,
    service_name: str,
    user_letter: str = "",
    quotation_style: str = "single",
    selected_pattern: str = DEFAULT_PATTERN
) -> tuple[str | None, str | None]:
    """
    Builds the password based on provided settings.

    Returns:
        (password, warning_message):
        - password (str | None): The generated password, or None if validation fails.
        - warning_message (str | None): A warning to show the user, or None if everything was normal.
    """
    
    # 1. Basic Validation
    if not all([prefix, base_number, special_chars, service_name]):
        return None, "Please fill in all required fields."

    try:
        base_num_int = int(base_number)
    except ValueError:
        return None, "Base number must be an integer."

    # 2. Capitalization Logic (Updated)
    # If user_letter is provided, use it. If empty, leave it blank.
    if user_letter:
        capital_letter = user_letter.upper()
        middle = f"{len(service_name)}{capital_letter}"
    else:
        middle = f"{len(service_name)}"

    # 3. Quotation Style Selection
    if quotation_style == "single":
        suffix = "'"
    elif quotation_style == "double":
        suffix = '"'
    else:
        suffix = ""

    # 4. Build Components
    length = len(service_name)
    end_number = base_num_int + length

    # 5. Apply Pattern
    template = PASSWORD_PATTERNS.get(selected_pattern, PASSWORD_PATTERNS[DEFAULT_PATTERN])
    
    password_components = {
        'prefix': prefix,
        'middle': middle,
        'special_chars': special_chars,
        'end_number': str(end_number)
    }
    
    base_password = template.format(**password_components)

    # 6. Add Quotations
    if quotation_style != "none":
        final_password = f"{suffix}{base_password}{suffix}"
    else:
        final_password = base_password

    # 7. Security Warning (Check for missing uppercase letters)
    warning_msg = None
    if not any(char.isupper() for char in final_password):
        warning_msg = "Security Warning: Your generated password does not contain any uppercase letters."

    return final_password, warning_msg