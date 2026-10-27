from .config import PASSWORD_PATTERNS, DEFAULT_PATTERN

def build_password(
    prefix: str,
    base_number: str,
    special_chars: str,
    service_name: str,
    user_letter: str = "",
    selected_pattern: str = DEFAULT_PATTERN
) -> tuple[str | None, str | None]:
    
    if not all([prefix, base_number, special_chars, service_name]):
        return None, "Please fill in all required fields."

    try:
        base_num_int = int(base_number)
    except ValueError:
        return None, "Base number must be an integer."

    # 1. Capitalization Logic (Uses all typed letters)
    if user_letter:
        # Directly use whatever the user typed and convert it to uppercase
        capital_letters = user_letter.upper()
        middle = f"{len(service_name)}{capital_letters}"
    else:
        middle = f"{len(service_name)}"

    # 2. Build Components
    length = len(service_name)
    end_number = base_num_int + length

    # 3. Apply Pattern
    template = PASSWORD_PATTERNS.get(selected_pattern, PASSWORD_PATTERNS[DEFAULT_PATTERN])
    
    password_components = {
        'prefix': prefix,
        'middle': middle,
        'special_chars': special_chars,
        'end_number': str(end_number)
    }
    
    final_password = template.format(**password_components)

    # 4. Security Warning (Check for missing uppercase letters)
    warning_msg = None
    if not any(char.isupper() for char in final_password):
        warning_msg = "Security Warning: Your generated password does not contain any uppercase letters."

    return final_password, warning_msg