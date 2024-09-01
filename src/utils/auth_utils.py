import string

def validate_password(new_password, confirm_password):
    if new_password != confirm_password:
        return "Passwords do not match"

    if len(new_password) < 8:
        return "Password must be at least 8 characters"

    required_chars = [
        string.ascii_letters, string.ascii_letters, string.digits, string.punctuation
    ]

    for chars in required_chars:

        for char in chars:
            if char in new_password:
                break
        else:
            return "Password must contain at least one Uppercase character, "\
                    "One lowercase character, one number character, and one "\
                    "punctuation character."

    return True