import re
from src.services.code_classifier.model_predictor import CodeClassifier

class CodeChecker:
    def __init__(self):
        self.code_classifier = CodeClassifier()
        self._setup_language_patterns()

    def _setup_language_patterns(self):
        """Setup language-specific patterns for accurate code parsing"""
        self.language_patterns = {
            'python': {
                'method_names': [
                    r'\bdef\s+(\w+)\s*\(',
                    r'\bclass\s+(\w+)',
                ],
                'parameter_names': [
                    r'\bdef\s+\w+\s*\(([^)]*)\)',
                    r'\bclass\s+\w+\s*\(([^)]*)\)',
                ],
                'parameter_types': [
                    r':\s*(\w+)\s*[=)]',  # Type hints in parameters
                    r'->\s*(\w+)',  # Return type hints
                ],
                'return_types': [
                    r'->\s*(\w+)',  # Return type hints
                ]
            },
            'javascript': {
                'method_names': [
                    r'\bfunction\s+(\w+)\s*\(',
                    r'\b(\w+)\s*\([^)]*\)\s*\{',  # Method definitions
                    r'\b(\w+)\s*:\s*function\s*\(',
                ],
                'parameter_names': [
                    r'\bfunction\s+\w+\s*\(([^)]*)\)',
                    r'\b(\w+)\s*\(([^)]*)\)\s*\{',
                ],
                'parameter_types': [
                    r':\s*(\w+)\s*[=)]',  # TypeScript type annotations
                ],
                'return_types': [
                    r':\s*(\w+)\s*[=)]',  # TypeScript return types
                ]
            },
            'java': {
                'method_names': [
                    r'\b(public|private|protected|static|final|abstract)?\s*\w+\s+(\w+)\s*\(',
                    r'\bclass\s+(\w+)',
                ],
                'parameter_names': [
                    r'\b\w+\s+\w+\s*\(([^)]*)\)',
                ],
                'parameter_types': [
                    r'\b(int|float|double|char|boolean|String|void|long|short|byte|List|Map|Set)\b',
                ],
                'return_types': [
                    r'\b(public|private|protected|static|final|abstract)?\s*(\w+)\s+\w+\s*\(',
                ]
            },
            'cpp': {
                'method_names': [
                    r'\b\w+\s+(\w+)\s*\(',
                    r'\bclass\s+(\w+)',
                ],
                'parameter_names': [
                    r'\b\w+\s+\w+\s*\(([^)]*)\)',
                ],
                'parameter_types': [
                    r'\b(int|float|double|char|bool|string|void|long|short|unsigned)\b',
                ],
                'return_types': [
                    r'\b(\w+)\s+\w+\s*\(',
                ]
            },
            'c_sharp': {
                'method_names': [
                    r'\b(public|private|protected|internal)?\s*\w+\s+(\w+)\s*\(',
                    r'\bclass\s+(\w+)',
                ],
                'parameter_names': [
                    r'\b\w+\s+\w+\s*\(([^)]*)\)',
                ],
                'parameter_types': [
                    r'\b(int|float|double|char|bool|string|void|long|short|byte|List|Dictionary|HashSet)\b',
                ],
                'return_types': [
                    r'\b(public|private|protected|internal)?\s*(\w+)\s+\w+\s*\(',
                ]
            },
            'go': {
                'method_names': [
                    r'\bfunc\s+(\w+)\s*\(',
                    r'\bfunc\s*\([^)]*\)\s*(\w+)\s*\(',
                ],
                'parameter_names': [
                    r'\bfunc\s+\w+\s*\(([^)]*)\)',
                ],
                'parameter_types': [
                    r'\b(int|float64|float32|string|bool|byte|rune)\b',
                ],
                'return_types': [
                    r'\bfunc\s+\w+\s*\([^)]*\)\s*(\w+)',
                ]
            },
            'ruby': {
                'method_names': [
                    r'\bdef\s+(\w+)',
                    r'\bclass\s+(\w+)',
                ],
                'parameter_names': [
                    r'\bdef\s+\w+\s*\(([^)]*)\)',
                ],
                'parameter_types': [],  # Ruby is dynamically typed
                'return_types': [],  # Ruby doesn't have explicit return types
            },
            'typescript': {
                'method_names': [
                    r'\bfunction\s+(\w+)\s*\(',
                    r'\b(\w+)\s*\([^)]*\)\s*:\s*\w+',
                ],
                'parameter_names': [
                    r'\bfunction\s+\w+\s*\(([^)]*)\)',
                ],
                'parameter_types': [
                    r':\s*(\w+)\s*[=)]',
                ],
                'return_types': [
                    r':\s*(\w+)\s*[=)]',
                ]
            }
        }

    def detect_language(self, text: str) -> str:
        """Detect programming language from code text"""
        # Simple language detection based on keywords
        if re.search(r'\bdef\s+\w+\s*\(|import\s+\w+|from\s+\w+', text):
            return 'python'
        elif re.search(r'\bfunction\s+\w+\s*\(|const\s+\w+|let\s+\w+', text):
            return 'javascript'
        elif re.search(r'\bpublic\s+class|\bprivate\s+\w+|\bprotected\s+\w+', text):
            return 'java'
        elif re.search(r'#include\s*<|std::|namespace\s+\w+', text):
            return 'cpp'
        elif re.search(r'\bnamespace\s+\w+|\bpublic\s+class|\busing\s+System', text):
            return 'c_sharp'
        elif re.search(r'\bfunc\s+\w+\s*\(|package\s+\w+', text):
            return 'go'
        elif re.search(r'\bdef\s+\w+\s*\(|class\s+\w+|module\s+\w+', text):
            return 'ruby'
        elif re.search(r'\binterface\s+\w+|\btype\s+\w+|\bimport\s+\w+', text):
            return 'typescript'
        else:
            return 'python'  # Default fallback

    def contains_code(self, text: str) -> bool:
        """Check if text contains code patterns"""
        # Use the existing code classifier for initial detection
        return self.code_classifier.predict(text)

    def get_code_blocks(self, text: str) -> list:
        """Get code blocks from text, code block has start and end index in text"""
        code_blocks = []
        for i, block in enumerate(text.split("\n\n")):
            prediction = self.code_classifier.predict_with_confidence(block)
            print(f"prediction: {prediction}")
            if prediction["is_code"]:
                code_blocks.append({"start": i, "end": i+len(block), "text": block})
        return code_blocks

    def process_code(self, text: str, code_protection_types: list) -> dict:
        """Process code and apply masking based on protection types"""
        code_blocks = self.get_code_blocks(text)
        result_text = text
        print("🔍 Processing code blocks")
        print(f"code block len: {len(code_blocks)}")
        print(f"code_blocks: {code_blocks}")
        
        for block in code_blocks:
            block_text = block["text"]
            language = self.detect_language(block_text)
            replacement_map = self.process_code_blocks(block_text, code_protection_types, language)
            
            # Apply replacements in reverse order to avoid conflicts
            for original, replacement in sorted(replacement_map.items(), key=lambda x: len(x[0]), reverse=True):
                result_text = result_text.replace(original, replacement)
        
        return replacement_map

    def process_code_blocks(self, text: str, code_protection_types: list, language: str = 'python') -> dict:
        """
        Process code and return replacement map based on protection types
        Returns dict of {original_text: replacement}
        """
        replacement_map = {}
        
        for protection_type in code_protection_types:
            if not protection_type.get('enabled', False):
                continue
                
            type_name = protection_type.get('typeName', '')
            
            if type_name == 'METHOD_NAME':
                replacement_map.update(self._extract_method_names(text, language))
            elif type_name == 'PARAMETER_NAMES':
                replacement_map.update(self._extract_parameter_names(text, language))
            elif type_name == 'PARAMETER_TYPES':
                replacement_map.update(self._extract_parameter_types(text, language))
            elif type_name == 'RETURN_TYPE':
                replacement_map.update(self._extract_return_types(text, language))
        
        return replacement_map

    def _extract_method_names(self, text: str, language: str) -> dict:
        """Extract method names using language-specific patterns"""
        replacements = {}
        patterns = self.language_patterns.get(language, {}).get('method_names', [])
        
        for i, pattern in enumerate(patterns):
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for j, match in enumerate(matches):
                # Handle different group patterns
                if match.groups():
                    method_name = match.group(1) if match.group(1) else match.group(2) if len(match.groups()) > 1 else None
                else:
                    method_name = match.group(0)
                
                if method_name and method_name not in replacements and not self._is_reserved_keyword(method_name, language):
                    replacement = f"METHOD_NAME_{i+1}_{j+1}"
                    replacements[method_name] = replacement
        
        return replacements

    def _extract_parameter_names(self, text: str, language: str) -> dict:
        """Extract parameter names using language-specific patterns"""
        replacements = {}
        patterns = self.language_patterns.get(language, {}).get('parameter_names', [])
        
        for i, pattern in enumerate(patterns):
            matches = re.finditer(pattern, text)
            for j, match in enumerate(matches):
                params_text = match.group(1) if match.groups() else match.group(0)
                if params_text:
                    # Split by comma and process each parameter
                    params = [p.strip() for p in params_text.split(',') if p.strip()]
                    for k, param in enumerate(params):
                        # Extract parameter name (last word in parameter)
                        param_parts = param.split()
                        if param_parts:
                            param_name = param_parts[-1]
                            if param_name and not self._is_reserved_keyword(param_name, language):
                                replacement = f"PARAMETER_NAME_{i+1}_{j+1}_{k+1}"
                                replacements[param_name] = replacement
        
        return replacements

    def _extract_parameter_types(self, text: str, language: str) -> dict:
        """Extract parameter types using language-specific patterns"""
        replacements = {}
        patterns = self.language_patterns.get(language, {}).get('parameter_types', [])
        
        for i, pattern in enumerate(patterns):
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for j, match in enumerate(matches):
                type_name = match.group(1) if match.groups() else match.group(0)
                if type_name and type_name not in replacements:
                    replacement = f"PARAMETER_TYPE_{i+1}_{j+1}"
                    replacements[type_name] = replacement
        
        return replacements

    def _extract_return_types(self, text: str, language: str) -> dict:
        """Extract return types using language-specific patterns"""
        replacements = {}
        patterns = self.language_patterns.get(language, {}).get('return_types', [])
        
        for i, pattern in enumerate(patterns):
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for j, match in enumerate(matches):
                return_type = match.group(1) if match.groups() else match.group(0)
                if return_type and return_type not in replacements and not self._is_reserved_keyword(return_type, language):
                    replacement = f"RETURN_TYPE_{i+1}_{j+1}"
                    replacements[return_type] = replacement
        
        return replacements

    def _is_reserved_keyword(self, word: str, language: str) -> bool:
        """Check if a word is a reserved keyword in the given language"""
        reserved_keywords = {
            'python': {
                'def', 'class', 'import', 'from', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'with', 'as',
                'return', 'pass', 'break', 'continue', 'raise', 'yield', 'lambda', 'and', 'or', 'not', 'in', 'is'
            },
            'javascript': {
                'function', 'var', 'let', 'const', 'if', 'else', 'for', 'while', 'try', 'catch', 'class', 'import', 'export',
                'return', 'break', 'continue', 'throw', 'yield', 'async', 'await', 'new', 'delete', 'typeof', 'instanceof'
            },
            'java': {
                'public', 'private', 'protected', 'static', 'final', 'abstract', 'class', 'interface', 'enum', 'extends', 'implements',
                'return', 'break', 'continue', 'throw', 'try', 'catch', 'finally', 'if', 'else', 'for', 'while', 'switch', 'case'
            },
            'cpp': {
                'int', 'float', 'double', 'char', 'bool', 'string', 'void', 'class', 'struct', 'namespace', 'using',
                'return', 'break', 'continue', 'throw', 'try', 'catch', 'if', 'else', 'for', 'while', 'switch', 'case'
            }
        }
        
        return word.lower() in reserved_keywords.get(language, set()) 