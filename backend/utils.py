def get_user_email(headers: dict):
    """
    Extracts the user email from the headers.
    """
    if "x-goog-authenticated-user-email" in headers:
        return headers["x-goog-authenticated-user-email"].split(":")[1]
    else:
        return "test.user@email.com"