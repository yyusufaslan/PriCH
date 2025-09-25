import re
from typing import Dict, List, Any

class ManualCodeChecker:
    """
    Manual code checker that uses heuristics and pattern matching
    as a fallback when the trained model fails to load.
    """
    
    def __init__(self):
        self._setup_language_patterns()
        self._setup_code_indicators()
    
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
    
    def _setup_code_indicators(self):
        """Setup patterns that strongly indicate code content"""
        self.code_indicators = [
            # Function/method definitions
            r'\b(def|function|class|interface|struct|enum)\s+\w+',
            r'\b(public|private|protected|static|final|abstract)\s+\w+',
            r'\b(int|float|double|char|bool|string|void|var|let|const)\s+\w+',
            
            # Control structures
            r'\b(if|else|elif|for|while|do|switch|case|try|catch|finally)\s*\(',
            r'\b(return|break|continue|throw|yield|await|async)\b',
            
            # Operators and symbols
            r'[{}();]',  # Braces, parentheses, semicolons
            r'[=+\-*/%<>!&|^~]',  # Common operators
            r'[\[\]]',  # Square brackets
            
            # Comments
            r'//.*$',  # Single line comments
            r'/\*.*?\*/',  # Multi-line comments
            r'#.*$',  # Hash comments (Python, shell)
            
            # Imports and includes
            r'\b(import|from|include|using|namespace|package)\s+',
            
            # String literals with quotes
            r'["\'`].*["\'`]',
            
            # Numbers and variables
            r'\b\d+\.?\d*\b',  # Numbers
            r'\b[a-zA-Z_]\w*\s*[=\(]',  # Variable assignments or function calls
        ]
    
    def detect_language(self, text: str) -> str:
        """Detect programming language from code text using heuristics"""
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
        """Check if text contains code patterns using heuristics"""
        # Count how many code indicators are present
        indicator_count = 0
        total_indicators = len(self.code_indicators)
        
        for pattern in self.code_indicators:
            if re.search(pattern, text, re.MULTILINE | re.DOTALL):
                indicator_count += 1
        
        # If more than 30% of indicators are present, consider it code
        threshold = 0.3
        return (indicator_count / total_indicators) >= threshold
    
    def get_code_blocks(self, text: str) -> List[Dict[str, Any]]:
        """Get code blocks from text using heuristics"""
        code_blocks = []
        
        # Split text into potential blocks (by double newlines or significant whitespace)
        blocks = re.split(r'\n\s*\n', text)
        
        for i, block in enumerate(blocks):
            if self.contains_code(block.strip()):
                # Calculate approximate start/end positions
                start_pos = text.find(block)
                end_pos = start_pos + len(block)
                
                code_blocks.append({
                    "start": start_pos,
                    "end": end_pos,
                    "text": block.strip()
                })
        
        return code_blocks
    
    def process_code(self, text: str, code_protection_types: List[Dict[str, Any]]) -> Dict[str, str]:
        """Process code and apply masking based on protection types"""
        code_blocks = self.get_code_blocks(text)
        replacement_map = {}
        
        print("🔍 Processing code blocks (Manual Mode)")
        print(f"code block len: {len(code_blocks)}")
        print(f"code_blocks: {code_blocks}")
        
        for block in code_blocks:
            block_text = block["text"]
            language = self.detect_language(block_text)
            block_replacements = self.process_code_blocks(block_text, code_protection_types, language)
            replacement_map.update(block_replacements)
        
        return replacement_map
    
    def process_code_blocks(self, text: str, code_protection_types: List[Dict[str, Any]], language: str = 'python') -> Dict[str, str]:
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
    
    def _extract_method_names(self, text: str, language: str) -> Dict[str, str]:
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
    
    def _extract_parameter_names(self, text: str, language: str) -> Dict[str, str]:
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
    
    def _extract_parameter_types(self, text: str, language: str) -> Dict[str, str]:
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
    
    def _extract_return_types(self, text: str, language: str) -> Dict[str, str]:
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
    
    def predict_with_confidence(self, text: str) -> Dict[str, Any]:
        """Predict with confidence scores using heuristics"""
        is_code = self.contains_code(text)
        
        # Calculate a confidence score based on the number of code indicators found
        indicator_count = 0
        for pattern in self.code_indicators:
            if re.search(pattern, text, re.MULTILINE | re.DOTALL):
                indicator_count += 1
        
        # Normalize confidence (0.5 to 1.0 range)
        confidence = min(0.5 + (indicator_count / len(self.code_indicators)) * 0.5, 1.0)
        
        return {
            "prediction": "CODE" if is_code else "TEXT",
            "confidence": confidence,
            "is_code": is_code
        }
