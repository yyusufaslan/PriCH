import re
import json
from typing import List, Dict, Any
from src.db.clipboard_repository import ClipboardRepository
from src.services.checkers.spacy_checker import SpacyChecker
from src.services.checkers.email_checker import EmailChecker
from src.services.checkers.phone_checker import PhoneChecker
from src.services.checkers.code_checker import CodeChecker

class TextProcessor:
    def __init__(self, config):
        self.config = config
        self.db = ClipboardRepository()
        self.spacy_checker = SpacyChecker()
        self.email_checker = EmailChecker()
        self.phone_checker = PhoneChecker()
        self.code_checker = CodeChecker()
        # Don't automatically load spaCy model - let it be loaded on demand

    def process_text(self, text: str, last_mask_mappings: List[Dict[str, Any]], active_window: str) -> str:
        try:
            processed_text = text
            mask_mappings = []
            timestamp = self.get_current_timestamp()

            # disabled masking, just record the text then return it
            if getattr(self.config, 'disable_masking', False):
                self.db.add_entry(text, processed_text, active_window, timestamp, mask_mappings)
                return processed_text

            # Process each pattern type
            processed_text = self.process_custom_regex(processed_text, mask_mappings)
            print(f"processed_text custom regex:::: {processed_text}")
            processed_text = self.process_ai(processed_text, mask_mappings)
            print(f"processed_text ai:::: {processed_text}")
            processed_text = self.process_emails(processed_text, mask_mappings)
            print(f"processed_text emails:::: {processed_text}")
            processed_text = self.process_phone_numbers(processed_text, mask_mappings)
            print(f"processed_text phone numbers:::: {processed_text}")
            processed_text = self.process_code(processed_text, mask_mappings)
            print(f"processed_text code:::: {processed_text}")

            # Clear previous mappings and store new ones
            last_mask_mappings.clear()
            last_mask_mappings.extend(mask_mappings)
            
            # Save to database with mask mappings
            self.db.add_entry(text, processed_text, active_window, timestamp, mask_mappings)   
            return processed_text
            
        except Exception as e:
            import traceback
            print(f"Error in process_text: {e}")
            print(f"Error details: {traceback.format_exc()}")
            print(f"Input text: {text[:100]}...")
            print(f"Active window: {active_window}")
            # Return original text on error
            return text

    def process_custom_regex(self, processed_text: str, mask_mappings: List[Dict[str, Any]]) -> bool:
        """Process custom regex patterns if enabled"""
        
        # Check if custom regex is enabled and text is long enough
        if (self.config.custom_regex_enabled):
            
            custom_regex_patterns = self.config.customRegexPatterns
            for pattern_config in custom_regex_patterns:
                if pattern_config.get('enabled', False):
                    try:
                        regex_pattern = pattern_config.get('regex', '')
                        replacement_base = pattern_config.get('replacement', '')
                        
                        # Find all matches
                        matches = list(re.finditer(regex_pattern, processed_text))
                        count = 0
                        
                        # Process matches in reverse order to maintain positions
                        for match in reversed(matches):
                            replacement = f"{replacement_base}{count} "
                            original_text = match.group(0)
                            
                            # Add to mask mappings
                            if self.add_to_mask_mappings(mask_mappings, original_text, replacement, 
                                                        f"CUSTOM_REGEX ({regex_pattern})"):
                                # Replace in text
                                start, end = match.span()
                                processed_text = processed_text[:start] + replacement + processed_text[end:]
                                count += 1
                                
                    except re.error as e:
                        print(f"Invalid regex pattern: {e}")
                    except Exception as e:
                        print(f"Error processing custom regex: {e}")
        
        return processed_text

    def process_code(self, processed_text: str, mask_mappings: List[Dict[str, Any]]) -> bool:
        """Process code protection if enabled"""
        # Check if code protection is enabled and text contains code
        if (self.config.code_protection_enabled and 
            self.code_checker.contains_code(processed_text)):
            
            code_protection_types = getattr(self.config, 'codeProtectionTypes', [])
            replacement_map = self.code_checker.process_code(processed_text, code_protection_types)
            
            for original, replacement in replacement_map.items():
                if self.add_to_mask_mappings(mask_mappings, original, replacement, "Code"):
                    # Replace all occurrences
                    processed_text = processed_text.replace(original, replacement)
        
        return processed_text

    def process_emails(self, processed_text: str, mask_mappings: List[Dict[str, Any]]) -> bool:
        """Process email masking if enabled"""
        if (self.config.email_enabled):
            # Check if email masking is enabled and text contains emails
            email_mask_type = self.config.email_mask_type  # 0 = NONE
            if email_mask_type != 0 and self.email_checker.contains_email(processed_text):
                
                email_matches = self.email_checker.find_emails(processed_text)
                print(f"email_matches:::: {email_matches}")
                for match in email_matches:
                    email_defined_text = self.config.email_defined_text
                    masked_email = self.email_checker.mask_email(match, email_mask_type, email_defined_text)
                    
                    # Replace in text
                    processed_text = processed_text.replace(match, masked_email)
                    print(f"masked_email replaced email:::: {masked_email}")
                    # Add to mappings
                    if self.add_to_mask_mappings(mask_mappings, match, masked_email, "EMAIL"):
                        if self.config.debugMode:
                            print(f"Masked Email: {match} -> {masked_email}")
        
        return processed_text

    def process_phone_numbers(self, processed_text: str, mask_mappings: List[Dict[str, Any]]) -> bool:
        """Process phone number masking if enabled"""
        
        if (self.config.phone_enabled):
            # Check if phone masking is enabled and text contains phones
            phone_mask_type = self.config.phone_mask_type  # 0 = NONE
            if phone_mask_type != 0 and self.phone_checker.contains_phone(processed_text):
                
                phone_matches = self.phone_checker.find_phone_numbers(processed_text)
                for match in phone_matches:
                    phone_defined_text = self.config.phone_defined_text
                    masked_phone = self.phone_checker.mask_phone(match, phone_mask_type, phone_defined_text)
                    print(f"masked_phone:::: {masked_phone}")
                    # Replace in text
                    processed_text = processed_text.replace(match, masked_phone)
                    print(f"processed_text replaced phone number:::: {processed_text}")
                    # Add to mappings
                    if self.add_to_mask_mappings(mask_mappings, match, masked_phone, "PHONE"):
                        if self.config.debugMode:
                            print(f"Masked Phone: {match} -> {masked_phone}")
        
        return processed_text

    def process_ai(self, processed_text: str, mask_mappings: List[Dict[str, Any]]) -> bool:
        """Process AI-based masking if enabled"""
        
        # Check if AI processing is enabled and text is long enough
        if (self.config.ai_enabled):
            
            try:
                # Try to load spaCy model if not already loaded
                if not self.spacy_checker.nlp and not self.spacy_checker.nlp_models:
                    self.spacy_checker.load_spacy_model("en_core_web_sm")
                
                # Use AI processing if available
                if self.spacy_checker.nlp or self.spacy_checker.nlp_models:
                    replacement_map = self.spacy_checker.analyze_and_replace_entities(processed_text)
                    
                    if replacement_map:
                        # Process the AI mappings
                        for original, replacement in replacement_map.items():
                            if self.add_to_mask_mappings(mask_mappings, original, replacement, "Spacy"):
                                if self.config.debugMode:
                                    print(f"Masked Spacy: {original} -> {replacement}")
                                
                                # Replace all occurrences
                                processed_text = processed_text.replace(original, replacement)
                            else:
                                if self.config.debugMode:
                                    print(f"Did not add to mask mappings: {original} -> {replacement}")
                    else:
                        if self.config.debugMode:
                            print("AI processing failed or returned empty result")
                else:
                    print("spaCy not available - skipping AI processing")
                    
            except Exception as e:
                print(f"AI processing exception: {e}")
        
        return processed_text

    def is_text_masked(self, text: str) -> bool:
        """Check if text is masked by checking database and patterns"""
        # First check if this text exists as a masked text in the database
        if self.db.is_masked_text_in_history(text):
            if self.config.debugMode:
                print(f"isTextMasked: {text} is true")
            return True

        # Fallback to pattern checking if not found in database
        mask_patterns = [
            "[MASKED_EMAIL]", "[MASKED_PHONE]", "[MASKED_METHOD]", 
            "[MASKED_PARAM]", "[MASKED_API_KEY]", "[PERSON]", "[ORGANIZATION]"
        ]
        
        return any(pattern in text for pattern in mask_patterns)

    def get_original_text(self, masked_text: str) -> str:
        """Get original text from database or return masked text"""
        # Try to get original text from database
        original_text = self.db.get_original_text(masked_text)
        
        if original_text:
            return original_text

        # If not found in database, return the masked text
        return masked_text

    def replace_values_with_keys(self, text: str, original_text: str, mappings: List[Dict[str, Any]]) -> str:
        """Replace masked values with original text using regex patterns"""
        result = text
        
        # Sort mappings by length (descending) to handle longer matches first
        sorted_mappings = sorted(mappings, key=lambda x: len(x.get('maskedText', '')), reverse=True)

        for mapping in sorted_mappings:
            masked_text = mapping.get('maskedText', '')
            original_text_mapping = mapping.get('originalText', '')
            
            if not masked_text or not original_text_mapping:
                continue
            
            # Create regex pattern to match masked text with optional number suffix
            mask_base = masked_text
            number_pos = -1
            for i, char in enumerate(mask_base):
                if char.isdigit():
                    number_pos = i
                    break
            
            if number_pos != -1:
                # Create pattern with optional digits
                before_digits = mask_base[:number_pos]
                after_digits = mask_base[number_pos:].rstrip('0123456789')
                pattern = f"{re.escape(before_digits)}\\d*{re.escape(after_digits)}"
            else:
                pattern = re.escape(mask_base)
            
            try:
                # Find all matches and replace
                matches = list(re.finditer(pattern, result))
                for match in reversed(matches):
                    # Find the original text's context
                    if original_text_mapping in original_text:
                        # Replace while preserving the case and surrounding context
                        start, end = match.span()
                        result = result[:start] + original_text_mapping + result[end:]
                        
            except re.error as e:
                print(f"Regex error: {e}")
                continue
        
        return result

    def add_to_mask_mappings(self, mask_mappings: List[Dict[str, Any]], original_text: str, 
                           masked_text: str, mask_type: str) -> bool:
        """Add to mask mappings if not already present and not in should erase list"""
        try:
            # Check if already in mappings
            for mapping in mask_mappings:
                if mapping.get('originalText') == original_text:
                    return False
            
            # Check should erase list
            should_erase_list = self.get_should_erase_list()
            
            # Debug logging
            if getattr(self.config, 'debugMode', False):
                print(f"Should erase list: {should_erase_list}")
                print(f"Original text: {original_text}")
            
            should_erase = any(pattern in original_text for pattern in should_erase_list)
            
            if should_erase:
                if getattr(self.config, 'debugMode', False):
                    print(f"Text '{original_text}' matches should_erase pattern, skipping")
                return False
            else:
                mask_mappings.append({
                    "originalText": original_text,
                    "maskedText": masked_text,
                    "maskType": mask_type
                })
                return True
                
        except Exception as e:
            import traceback
            print(f"Error in add_to_mask_mappings: {e}")
            print(f"Error details: {traceback.format_exc()}")
            print(f"Original text: {original_text}")
            print(f"Masked text: {masked_text}")
            print(f"Mask type: {mask_type}")
            return False

    def set_custom_terms_as_map(self, custom_terms: Dict[str, Any]) -> bool:
        """Set custom terms in database"""
        try:
            # Convert term to lowercase for consistent comparison
            term_lower = custom_terms.get('term', '').lower()
            
            # Get existing terms
            existing_terms = self.get_custom_terms()
            
            # Check for duplicates and update if exists
            term_exists = False
            for existing in existing_terms:
                if self.config.debugMode:
                    print(f"existing: {existing.get('term')} {existing.get('replacement')}")
                
                existing_lower = existing.get('term', '').lower()
                if existing_lower == term_lower:
                    # Update existing term
                    existing.update({
                        'replacement': custom_terms.get('replacement'),
                        'enabled': custom_terms.get('enabled'),
                        'spacyModelId': custom_terms.get('spacyModelId')
                    })
                    term_exists = True
                    break
            
            # If term doesn't exist, add it
            if not term_exists:
                existing_terms.append(custom_terms)
            
            # Save all terms
            if self.config.debugMode:
                print("saving custom terms")
                for term in existing_terms:
                    print(f"existingTerms: {term.get('id')} {term.get('spacyModelId')} {term.get('term')} {term.get('replacement')} {term.get('enabled')}")
            
            return self.db.save_custom_terms(existing_terms)
            
        except Exception as e:
            print(f"Error setting custom terms: {e}")
            return False

    def get_custom_terms(self) -> List[Dict[str, Any]]:
        """Get custom terms from database"""
        try:
            return self.db.get_custom_terms()
        except Exception as e:
            print(f"Error getting custom terms: {e}")
            return []

    def set_custom_terms(self, path: str) -> bool:
        """Set custom terms from file"""
        try:
            if self.config.debugMode:
                print(f"setCustomTerms: {path}")
            
            # Read the file line by line and add to database
            with open(path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if ',' in line:
                        term = line[:line.find(",")].strip()
                        replacement = line[line.find(",") + 1:].strip()
                        
                        # Make term lowercase
                        term_lower = term.lower()
                        
                        # Check if term already exists
                        if self.db.is_custom_term_already_in_database(term_lower):
                            continue
                        
                        if self.config.debugMode:
                            print(f"saving custom term with path: {path} {term_lower} {replacement}")
                        
                        custom_term = {
                            'id': -1,
                            'term': term_lower,
                            'replacement': replacement,
                            'spacyModelId': 0,
                            'enabled': True
                        }
                        self.db.save_custom_terms([custom_term])
            
            return True
            
        except Exception as e:
            print(f"Error setting custom terms from file: {e}")
            return False

    def get_should_erase_list(self) -> List[str]:
        """Get list of patterns that should be erased from mask mappings"""
        should_erase_list = []
        
        # Add AI processing types - convert integers to string patterns
        ai_processing_types = self.config.aiProcessingTypes
        for ai_type in ai_processing_types:
            mask_option = ai_type.get('aiMaskOption', '')
            if mask_option is not None:
                # Convert integer mask option to string pattern
                pattern = self.string_to_ai_mask_option(str(mask_option))
                if pattern:
                    should_erase_list.append(pattern)
        
        # Add code protection patterns
        should_erase_list.extend([
            "METHOD_NAME_",
            "PARAMETER_CLASS_NAME_", 
            "CLASS_NAME_"
        ])
        
        return should_erase_list

    def string_to_ai_mask_option(self, mask_option: str) -> str:
        """Convert AI mask option to string representation"""
        # Convert AI mask option numbers to string patterns
        # Based on the AI processing types in the database
        mask_option_map = {
            '0': 'PERSON',
            '1': 'ORG', 
            '2': 'GPE',
            '3': 'DATE',
            '4': 'LOC',
            '5': 'PRODUCT',
            '6': 'EVENT',
            '7': 'WORK_OF_ART',
            '8': 'LAW',
            '9': 'LANGUAGE',
            '10': 'TIME',
            '11': 'PERCENT',
            '12': 'MONEY',
            '13': 'QUANTITY',
            '14': 'ORDINAL',
            '15': 'CARDINAL',
            '16': 'NORP',
            '17': 'FAC'
        }
        
        return mask_option_map.get(mask_option, f"AI_{mask_option}")

    def get_current_timestamp(self) -> str:
        """Return current timestamp as string"""
        import datetime
        return datetime.datetime.now().isoformat() 