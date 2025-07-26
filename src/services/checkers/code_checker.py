import re

class CodeChecker:
    def __init__(self):
        # Code detection patterns
        self.code_patterns = [
            r'\b(public|private|protected|static|final|abstract|class|interface|enum|extends|implements)\b',  # Java
            r'\b(def|class|import|from|if|else|elif|for|while|try|except|with|as)\b',  # Python
            r'\b(function|var|let|const|if|else|for|while|try|catch|class|import|export)\b',  # JavaScript
            r'\b(public|private|protected|static|class|interface|namespace|using|if|else|for|while|try|catch)\b',  # C#
            r'\b(#include|#define|int|float|double|char|void|if|else|for|while|try|catch|class|struct)\b',  # C/C++
            r'\b(func|var|let|const|if|else|for|while|defer|import|package|struct|interface)\b',  # Go
            r'\b(def|class|module|require|include|if|else|elsif|for|while|begin|rescue|end)\b',  # Ruby
            r'\b(function|class|interface|namespace|import|export|if|else|for|while|try|catch)\b',  # TypeScript
        ]

    def contains_code(self, text: str) -> bool:
        """Check if text contains code patterns"""
        for pattern in self.code_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def process_code(self, text: str, code_protection_types: list) -> dict:
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
                replacement_map.update(self._mask_method_names(text))
            elif type_name == 'PARAMETER_NAMES':
                replacement_map.update(self._mask_parameter_names(text))
            elif type_name == 'PARAMETER_TYPES':
                replacement_map.update(self._mask_parameter_types(text))
            elif type_name == 'RETURN_TYPE':
                replacement_map.update(self._mask_return_types(text))
        
        return replacement_map

    def _mask_method_names(self, text: str) -> dict:
        """Mask method names in code"""
        replacements = {}
        
        # Method name patterns for different languages
        method_patterns = [
            r'\b(public|private|protected|static|final|abstract)?\s+\w+\s+(\w+)\s*\(',  # Java/C#
            r'\bdef\s+(\w+)\s*\(',  # Python
            r'\bfunction\s+(\w+)\s*\(',  # JavaScript
            r'\b(\w+)\s*\([^)]*\)\s*\{',  # General function pattern
        ]
        
        for pattern in method_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for i, match in enumerate(matches):
                method_name = match.group(1) if match.groups() else match.group(0)
                if method_name and method_name not in ['public', 'private', 'protected', 'static', 'final', 'abstract', 'def', 'function']:
                    replacement = f"METHOD_NAME_{i+1}"
                    replacements[method_name] = replacement
        
        return replacements

    def _mask_parameter_names(self, text: str) -> dict:
        """Mask parameter names in code"""
        replacements = {}
        
        # Parameter patterns
        param_patterns = [
            r'\(\s*([^)]+)\s*\)',  # Parameters in parentheses
        ]
        
        for pattern in param_patterns:
            matches = re.finditer(pattern, text)
            for i, match in enumerate(matches):
                params_text = match.group(1)
                # Split by comma and process each parameter
                params = [p.strip() for p in params_text.split(',') if p.strip()]
                for j, param in enumerate(params):
                    # Extract parameter name (before type or after type)
                    param_name = param.split()[-1] if ' ' in param else param
                    if param_name and not param_name.startswith('*') and not param_name.startswith('&'):
                        replacement = f"PARAMETER_NAME_{i+1}_{j+1}"
                        replacements[param_name] = replacement
        
        return replacements

    def _mask_parameter_types(self, text: str) -> dict:
        """Mask parameter types in code"""
        replacements = {}
        
        # Type patterns
        type_patterns = [
            r'\b(int|float|double|char|bool|string|void|long|short|byte)\b',  # Basic types
            r'\b(List|Map|Set|ArrayList|HashMap|HashSet)\b',  # Collection types
            r'\b(String|Integer|Float|Double|Boolean|Long|Short|Byte)\b',  # Wrapper types
        ]
        
        for pattern in type_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for i, match in enumerate(matches):
                type_name = match.group(0)
                replacement = f"PARAMETER_TYPE_{i+1}"
                replacements[type_name] = replacement
        
        return replacements

    def _mask_return_types(self, text: str) -> dict:
        """Mask return types in code"""
        replacements = {}
        
        # Return type patterns
        return_patterns = [
            r'\b(public|private|protected|static|final|abstract)?\s+(\w+)\s+\w+\s*\(',  # Method with return type
            r'\bdef\s+(\w+)\s*\(',  # Python function (implicit return type)
        ]
        
        for pattern in return_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for i, match in enumerate(matches):
                return_type = match.group(1) if match.groups() else "void"
                if return_type and return_type not in ['public', 'private', 'protected', 'static', 'final', 'abstract']:
                    replacement = f"RETURN_TYPE_{i+1}"
                    replacements[return_type] = replacement
        
        return replacements 