
class EmailNotFoundException(Exception):
    def __init__(self, email_addr: str):
        super().__init__(f"Email address {email_addr} not found in contacts table.")