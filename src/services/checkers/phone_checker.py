import re

class PhoneChecker:
    def __init__(self):
        # Phone number regex pattern - matches various formats
        self.phone_pattern = r"\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}"

    def contains_phone(self, text: str) -> bool:
        """Check if text contains phone numbers"""
        return bool(re.search(self.phone_pattern, text))

    def find_phone_numbers(self, text: str) -> list:
        """Find all phone numbers in text"""
        return re.findall(self.phone_pattern, text)

    def mask_phone(self, phone: str, mask_type: int, defined_text: str = "") -> str:
        """
        Mask phone number based on mask type
        mask_type: 0=NONE, 1=ASTERISK, 2=DEFINED_TEXT, 3=PARTIAL
        """
        if mask_type == 0:  # NONE
            return phone
        elif mask_type == 1:  # ASTERISK
            return "*" * len(phone)
        elif mask_type == 2:  # DEFINED_TEXT
            return defined_text if defined_text else "[MASKED_PHONE]"
        elif mask_type == 3:  # PARTIAL
            # Keep last 4 digits visible
            if len(phone) > 4:
                return "*" * (len(phone) - 4) + phone[-4:]
            else:
                return "*" * len(phone)
        else:
            return "[MASKED_PHONE]" 