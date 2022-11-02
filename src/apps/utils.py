def check_password_name(val):
    options = ["password", "pasword", "passwrd", "psswrd", "secret", "secrets", "key"]
    for x in options:
        if x in val:
            return True
        if x in val.lower():
            return True
    return False
