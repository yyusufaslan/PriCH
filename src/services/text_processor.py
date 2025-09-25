import re
import json
from typing import List, Dict, Any, Tuple
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
        """
        Main processing pipeline that separates code and text segments,
        then applies appropriate processors to each segment type.
        """
        try:
            processed_text = text
            mask_mappings = []
            timestamp = self.get_current_timestamp()

            # If masking is disabled, just record the text and return it
            if getattr(self.config, 'disable_masking', False):
                self.db.add_entry(text, processed_text, active_window, timestamp, mask_mappings)
                return processed_text

            if self.config.debugMode:
                print(f"=== Starting text processing pipeline ===")
                print(f"Input text length: {len(text)}")
                print(f"Active window: {active_window}")

            # Step 1: Detect and separate code and text segments
            segments = self.segment_text(text)
            
            if self.config.debugMode:
                stats = self.get_segment_statistics(segments)
                print(f"Segmentation stats: {stats}")
            
            # Step 2: Process each segment with appropriate processors
            processed_segments = []
            for i, segment in enumerate(segments):
                if self.config.debugMode:
                    print(f"Processing segment {i+1}/{len(segments)}: {segment['type']}")
                
                processed_segment = self.process_segment(segment, mask_mappings)
                processed_segments.append(processed_segment)
            
            # Step 3: Validate processing
            if not self.validate_segment_processing(text, processed_segments):
                print("Warning: Segment processing validation failed, using original text")
                return text
            
            # Step 4: Reconstruct the final text
            processed_text = self.reconstruct_text(processed_segments)
            
            # Step 5: Apply custom regex patterns (global processing)
            processed_text = self.process_custom_regex(processed_text, mask_mappings)
            
            if self.config.debugMode:
                print(f"Final processed text length: {len(processed_text)}")
                print(f"Total mask mappings: {len(mask_mappings)}")
                print(f"=== Text processing pipeline completed ===")
            
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

    def segment_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect and separate code and text segments from the input text.
        Returns a list of segments with their type, content, and position information.
        """
        segments = []
        
        # Split text into potential blocks (by double newlines or significant whitespace)
        blocks = self.split_into_blocks(text)
        
        if not blocks:
            # If no blocks found, classify the entire text
            if self.code_checker.model_available and self.code_checker.code_classifier:
                classification = self.code_checker.code_classifier.predict_with_confidence(text)
            else:
                classification = self.code_checker.manual_code_checker.predict_with_confidence(text)
            segment_type = "CODE" if classification["is_code"] else "TEXT"
            
            segment = {
                "type": segment_type,
                "content": text,
                "start_pos": 0,
                "end_pos": len(text),
                "confidence": classification["confidence"],
                "processed": False
            }
            segments.append(segment)
            return segments
        
        current_position = 0
        
        for block in blocks:
            block_text = block.strip()
            if not block_text:
                continue
                
            # Classify the block as code or text
            if self.code_checker.model_available and self.code_checker.code_classifier:
                classification = self.code_checker.code_classifier.predict_with_confidence(block_text)
            else:
                classification = self.code_checker.manual_code_checker.predict_with_confidence(block_text)
            
            # Use model prediction if confidence is high enough, otherwise use heuristics
            if classification["confidence"] > 0.7:
                segment_type = "CODE" if classification["is_code"] else "TEXT"
            else:
                # Fallback to heuristic-based classification
                segment_type = self.heuristic_code_detection(block_text)
                classification["confidence"] = 0.6  # Lower confidence for heuristic
            
            # Find the actual position of this block in the original text
            start_pos = text.find(block_text, current_position)
            if start_pos == -1:  # Fallback if not found
                start_pos = current_position
            end_pos = start_pos + len(block_text)
            
            segment = {
                "type": segment_type,
                "content": block_text,
                "start_pos": start_pos,
                "end_pos": end_pos,
                "confidence": classification["confidence"],
                "processed": False
            }
            
            segments.append(segment)
            current_position = end_pos
            
            if self.config.debugMode:
                print(f"Segment: {segment_type} (confidence: {classification['confidence']:.2f})")
                print(f"Content: {block_text[:100]}{'...' if len(block_text) > 100 else ''}")
        
        return segments

    def split_into_blocks(self, text: str) -> List[str]:
        """
        Split text into logical blocks for classification.
        Uses double newlines, code block markers, and other heuristics.
        """
        # Handle empty or very short text
        if not text.strip():
            return []
        
        # Split by double newlines first
        blocks = re.split(r'\n\s*\n', text)
        
        # Further split large blocks that might contain mixed content
        refined_blocks = []
        for block in blocks:
            block = block.strip()
            if not block:
                continue
                
            if len(block) > 500:  # Large block, try to split further
                # Split by single newlines for large blocks
                sub_blocks = [b.strip() for b in block.split('\n') if b.strip()]
                refined_blocks.extend(sub_blocks)
            else:
                refined_blocks.append(block)
        
        # If no blocks found, treat the entire text as one block
        if not refined_blocks:
            refined_blocks = [text.strip()]
        
        return refined_blocks

    def process_segment(self, segment: Dict[str, Any], mask_mappings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a single segment based on its type (CODE or TEXT).
        Returns the processed segment with updated content.
        """
        segment_type = segment["type"]
        content = segment["content"]
        
        if segment_type == "CODE":
            return self.process_code_segment(segment, mask_mappings)
        else:  # TEXT
            return self.process_text_segment(segment, mask_mappings)

    def process_code_segment(self, segment: Dict[str, Any], mask_mappings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a code segment using code-specific processors.
        """
        content = segment["content"]
        processed_content = content
        
        # Only process if code protection is enabled
        if self.config.code_protection_enabled:
            try:
                code_protection_types = getattr(self.config, 'codeProtectionTypes', [])
                
                # Detect language for the code segment
                language = self.code_checker.detect_language(content)
                
                # Process code using the code checker
                replacement_map = self.code_checker.process_code(content, code_protection_types)
                
                # Apply replacements and track mappings
                for original, replacement in replacement_map.items():
                    if self.add_to_mask_mappings(mask_mappings, original, replacement, f"CODE_{language.upper()}"):
                        processed_content = processed_content.replace(original, replacement)
                        if self.config.debugMode:
                            print(f"Code masking: {original} -> {replacement}")
            except Exception as e:
                print(f"Error processing code segment: {e}")
                # Continue with unprocessed content if there's an error
        
        # Mark segment as processed
        segment["content"] = processed_content
        segment["processed"] = True
        return segment

    def process_text_segment(self, segment: Dict[str, Any], mask_mappings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a text segment using text-specific processors.
        """
        content = segment["content"]
        processed_content = content
        
        # Step 1: AI-based NER processing (spaCy)
        if self.config.ai_enabled:
            processed_content = self.process_ai_on_text(processed_content, mask_mappings)
        
        # Step 2: Email processing
        if self.config.email_enabled:
            processed_content = self.process_emails_on_text(processed_content, mask_mappings)
        
        # Step 3: Phone number processing
        if self.config.phone_enabled:
            processed_content = self.process_phone_numbers_on_text(processed_content, mask_mappings)
        
        # Mark segment as processed
        segment["content"] = processed_content
        segment["processed"] = True
        return segment

    def process_ai_on_text(self, text: str, mask_mappings: List[Dict[str, Any]]) -> str:
        """
        Apply AI-based NER processing only to text segments.
        """
        try:
            # Try to load spaCy model if not already loaded
            if not self.spacy_checker.nlp and not self.spacy_checker.nlp_models:
                self.spacy_checker.load_spacy_model("en_core_web_sm")
            
            # Use AI processing if available
            if self.spacy_checker.nlp or self.spacy_checker.nlp_models:
                replacement_map = self.spacy_checker.analyze_and_replace_entities(text)
                
                if replacement_map:
                    # Process the AI mappings
                    for original, replacement in replacement_map.items():
                        if self.add_to_mask_mappings(mask_mappings, original, replacement, "Spacy"):
                            if self.config.debugMode:
                                print(f"AI masking: {original} -> {replacement}")
                            
                            # Replace all occurrences
                            text = text.replace(original, replacement)
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
        
        return text

    def process_emails_on_text(self, text: str, mask_mappings: List[Dict[str, Any]]) -> str:
        """
        Apply email masking only to text segments.
        """
        email_mask_type = self.config.email_mask_type  # 0 = NONE
        if email_mask_type != 0 and self.email_checker.contains_email(text):
            
            email_matches = self.email_checker.find_emails(text)
            if self.config.debugMode:
                print(f"Email matches found: {email_matches}")
            
            for match in email_matches:
                email_defined_text = self.config.email_defined_text
                masked_email = self.email_checker.mask_email(match, email_mask_type, email_defined_text)
                
                # Replace in text
                text = text.replace(match, masked_email)
                
                # Add to mappings
                if self.add_to_mask_mappings(mask_mappings, match, masked_email, "EMAIL"):
                    if self.config.debugMode:
                        print(f"Email masking: {match} -> {masked_email}")
        
        return text

    def process_phone_numbers_on_text(self, text: str, mask_mappings: List[Dict[str, Any]]) -> str:
        """
        Apply phone number masking only to text segments.
        """
        phone_mask_type = self.config.phone_mask_type  # 0 = NONE
        if phone_mask_type != 0 and self.phone_checker.contains_phone(text):
            
            phone_matches = self.phone_checker.find_phone_numbers(text)
            for match in phone_matches:
                phone_defined_text = self.config.phone_defined_text
                masked_phone = self.phone_checker.mask_phone(match, phone_mask_type, phone_defined_text)
                
                # Replace in text
                text = text.replace(match, masked_phone)
                
                # Add to mappings
                if self.add_to_mask_mappings(mask_mappings, match, masked_phone, "PHONE"):
                    if self.config.debugMode:
                        print(f"Phone masking: {match} -> {masked_phone}")
        
        return text

    def reconstruct_text(self, segments: List[Dict[str, Any]]) -> str:
        """
        Reconstruct the final text from processed segments.
        Maintains the original structure and spacing.
        """
        if not segments:
            return ""
        
        # Sort segments by their original position
        sorted_segments = sorted(segments, key=lambda x: x["start_pos"])
        
        # Reconstruct text with proper spacing
        reconstructed_parts = []
        for i, segment in enumerate(sorted_segments):
            reconstructed_parts.append(segment["content"])
            
            # Add spacing between segments (but not after the last one)
            if i < len(sorted_segments) - 1:
                # Check if there should be spacing based on original positions
                current_end = segment["end_pos"]
                next_start = sorted_segments[i + 1]["start_pos"]
                
                if next_start > current_end:
                    # There was original spacing, preserve it
                    reconstructed_parts.append("")
        
        return "\n\n".join(reconstructed_parts)

    def process_custom_regex(self, processed_text: str, mask_mappings: List[Dict[str, Any]]) -> str:
        """Process custom regex patterns if enabled - applied globally to final text"""
        
        # Check if custom regex is enabled
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
                                
                                if self.config.debugMode:
                                    print(f"Custom regex masking: {original_text} -> {replacement}")
                                
                    except re.error as e:
                        print(f"Invalid regex pattern: {e}")
                    except Exception as e:
                        print(f"Error processing custom regex: {e}")
        
        return processed_text

    def get_segment_statistics(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about the segmented text for debugging and monitoring.
        """
        stats = {
            "total_segments": len(segments),
            "code_segments": 0,
            "text_segments": 0,
            "total_code_length": 0,
            "total_text_length": 0,
            "average_confidence": 0.0
        }
        
        if segments:
            total_confidence = 0.0
            for segment in segments:
                if segment["type"] == "CODE":
                    stats["code_segments"] += 1
                    stats["total_code_length"] += len(segment["content"])
                else:
                    stats["text_segments"] += 1
                    stats["total_text_length"] += len(segment["content"])
                total_confidence += segment["confidence"]
            
            stats["average_confidence"] = total_confidence / len(segments)
        
        return stats

    def heuristic_code_detection(self, text: str) -> str:
        """
        Heuristic-based code detection as fallback when model confidence is low.
        """
        # Code indicators
        code_indicators = [
            r'\b(def|class|function|var|let|const|public|private|protected|static|final|abstract|interface|enum|struct|union)\b',
            r'\b(if|else|elif|for|while|do|switch|case|break|continue|return|throw|try|catch|finally)\b',
            r'\b(import|from|export|require|include|using|namespace|package)\b',
            r'[{}()\[\]]',  # Brackets
            r'[=+\-*/%<>!&|^~]',  # Operators
            r'[;:]',  # Semicolons and colons
            r'^\s*(def|class|function|var|let|const|public|private|protected)',  # Start of line
            r'print\(|console\.log\(|System\.out\.println\(',  # Print statements
            r'^\s*[a-zA-Z_]\w*\s*\([^)]*\)\s*[:{=]',  # Function calls/definitions
        ]
        
        # Text indicators
        text_indicators = [
            r'\b(the|and|or|but|in|on|at|to|for|of|with|by|from|about|like|as|is|are|was|were|be|been|being)\b',
            r'[.!?]',  # Sentence endings
            r'\b[a-z]+\s+[a-z]+\s+[a-z]+',  # Multiple lowercase words
            r'[A-Z][a-z]+',  # Capitalized words (proper nouns)
        ]
        
        code_score = 0
        text_score = 0
        
        # Count code indicators
        for pattern in code_indicators:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            code_score += matches
        
        # Count text indicators
        for pattern in text_indicators:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            text_score += matches
        
        # Additional heuristics
        if re.search(r'^\s*[#<>]', text):  # Comments or HTML
            code_score += 2
        
        if len(text.split()) > 20:  # Long text is more likely to be natural language
            text_score += 3
        
        if re.search(r'[A-Z]{3,}', text):  # ALL CAPS words are often code
            code_score += 1
        
        # Decision
        if code_score > text_score:
            return "CODE"
        else:
            return "TEXT"

    def validate_segment_processing(self, original_text: str, processed_segments: List[Dict[str, Any]]) -> bool:
        """
        Validate that all segments have been processed and the reconstruction is valid.
        """
        # Check that all segments are processed
        for segment in processed_segments:
            if not segment.get("processed", False):
                print(f"Warning: Segment not processed: {segment['type']}")
                return False
        
        # Check that reconstruction maintains reasonable length
        reconstructed = self.reconstruct_text(processed_segments)
        if len(reconstructed) < len(original_text) * 0.5:  # Should not lose more than 50% of content
            print(f"Warning: Reconstructed text is too short: {len(reconstructed)} vs {len(original_text)}")
            return False
        
        return True

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