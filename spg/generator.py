from .config import PASSWORD_PATTERNS, DEFAULT_PATTERN

def build_password(
    prefix: str,
    base_number: str,
    special_chars: str,
    service_name: str,
    user_letter: str = "",
    selected_pattern: str = DEFAULT_PATTERN
) -> tuple[str | None, str | None]:
    
    # 1. Independent Validation
    if not prefix or not base_number or not special_chars or not service_name:
        return None, "All main fields (Prefix, Base, Special, Service) are required."

    if not prefix.isalpha():
        return None, "Prefix must contain only letters."
        
    if not base_number.isdigit():
        return None, "Base number must contain only digits."
        
    if len(user_letter) > 3 or (user_letter and not user_letter.isalpha()):
        return None, "Capitalize letters must be alphabetical and up to 3 characters."
        
    if not all(char.isalnum() or char in '-_' for char in service_name):
        return None, "Service name contains invalid characters (only letters, numbers, -, _ are allowed)."

    try:
        base_num_int = int(base_number)
        if base_num_int < 0 or base_num_int > 9999999:
            return None, "Base number is out of valid range."
    except ValueError:
        return None, "Base number must be an integer."

    # 2. Capitalization Logic
    if user_letter:
        capital_letters = user_letter.upper()
        middle = f"{len(service_name)}{capital_letters}"
    else:
        middle = f"{len(service_name)}"

    # 3. Build Components
    length = len(service_name)
    end_number = base_num_int + length

    # 4. Apply Pattern
    template = PASSWORD_PATTERNS.get(selected_pattern, PASSWORD_PATTERNS[DEFAULT_PATTERN])
    
    password_components = {
        'prefix': prefix,
        'middle': middle,
        'special_chars': special_chars,
        'end_number': str(end_number)
    }
    
    final_password = template.format(**password_components)

    # 5. Compatibility Notice (Not a strict security warning)
    warning_msg = None
    if not any(char.isupper() for char in final_password):
        warning_msg = "Notice: This pattern does not contain uppercase letters. This is fine if it fits your mental model, but we recommend adding at least one capital letter."

    return final_password, warning_msg