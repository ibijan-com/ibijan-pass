"""
Password generation logic for SPG.

Pure logic module — no UI dependencies (no tkinter).
Returns tuples of (password, warning_message) so the UI can
decide how to present warnings to the user.
"""

import random
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
    
    # 1. Basic Validation (UI normally enforces this, but we double-check)
    if not all([prefix, base_number, special_chars, service_name]):
        return None, "Please fill in all fields."

    try:
        base_num_int = int(base_number)
    except ValueError:
        return None, "Base number must be an integer."

    # 2. Capitalization Logic
    warning_msg = None
    if user_letter:
        if user_letter.lower() in service_name.lower():
            # Find letter in service and capitalize it
            idx = service_name.lower().index(user_letter.lower())
            capital_letter = service_name[idx].upper()
        else:
            # Letter not found in service
            capital_letter = random.choice(service_name).upper()
            warning_msg = (
                f"The letter '{user_letter}' is not in service name '{service_name}'.\n"
                f"Randomly capitalizing: '{capital_letter}'"
            )
    else:
        # No letter specified — pick randomly
        capital_letter = random.choice(service_name).upper()

    # 3. Quotation Style Selection
    if quotation_style == "single":
        suffix = "'"
    elif quotation_style == "double":
        suffix = '"'
    else:
        suffix = ""

    # 4. Build Components
    length = len(service_name)
    middle = f"{length}{capital_letter}"
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

    return final_password, warning_msg
