import re

class EmailChecker:
    def __init__(self):
        # Email regex pattern
        self.email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

    def contains_email(self, text: str) -> bool:
        """Check if text contains email addresses"""
        return bool(re.search(self.email_pattern, text))

    def find_emails(self, text: str) -> list:
        """Find all email addresses in text"""
        return re.findall(self.email_pattern, text)

    def mask_email(self, email: str, mask_type: int, defined_text: str = "") -> str:
        """
        Mask email based on mask type
        mask_type: 0=NONE, 1=ASTERISK, 2=DEFINED_TEXT, 3=PARTIAL
        """
        if mask_type == 0:  # NONE
            return email
        elif mask_type == 1:  # ASTERISK
            return "*" * len(email)
        elif mask_type == 2:  # DEFINED_TEXT
            return defined_text if defined_text else "[MASKED_EMAIL]"
        elif mask_type == 3:  # PARTIAL
            if "@" in email:
                username, domain = email.split("@", 1)
                if len(username) > 2:
                    masked_username = username[:2] + "*" * (len(username) - 2)
                else:
                    masked_username = "*" * len(username)
                return f"{masked_username}@{domain}"
            else:
                return "*" * len(email)
        else:
            return "[MASKED_EMAIL]" 