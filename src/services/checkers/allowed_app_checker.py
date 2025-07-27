class AllowedAppChecker:
    def __init__(self, config):
        self.config = config

    def is_trusted_app(self, window_title):
        """
        Check if the app with given window title is trusted.
        Returns True if app is trusted, False if untrusted.
        """
        # Clean up window title to match program name
        program_name = window_title
        
        # Remove everything before the last " - " symbol (window title format)
        # This gets the actual app name from the end of the window title
        last_dash = program_name.rfind(" - ")
        if last_dash != -1:
            program_name = program_name[last_dash + 3:]
        
        # Remove file extension if present (like .py, .exe, etc.)
        last_dot = program_name.rfind(".")
        if last_dot != -1:
            program_name = program_name[:last_dot]
        
        if program_name == "":
            if getattr(self.config, 'debugMode', False):
                print("Program name is empty")
            return True  # Allow empty program names
        
        if self.config.debugMode:
            print(f"Extracted program_name: '{program_name}' from window_title: '{window_title}'")
        
        # Check if program is in trusted list
        trusted_programs = getattr(self.config, 'trustedPrograms', [])
        
        # Sort by name length (longest first) to prioritize exact/longer matches
        sorted_trusted_programs = sorted(trusted_programs, 
                                       key=lambda x: len(x.get('programName', '')), 
                                       reverse=True)
        
        for trusted_program in sorted_trusted_programs:
            trusted_name = trusted_program.get('programName', '')
            if program_name.lower() in trusted_name.lower() or trusted_name.lower() in program_name.lower():
                if trusted_program.get('deleted', True):
                    return False  # Program is deleted, not trusted
                if self.config.debugMode:
                    print(f"Program is trusted: {trusted_program.get('enabled')} - {trusted_program.get('programName')}")
                return trusted_program.get('enabled', True)  # Return enabled status
        return False  # Program not found in trusted list, not trusted

    def is_untrusted_app(self, window_title):
        """
        Convenience method - returns True if app is untrusted, False if trusted.
        This is the opposite of is_trusted_app.
        """
        return not self.is_trusted_app(window_title)
