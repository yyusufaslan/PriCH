#!/usr/bin/env python3
"""
PriCH - Clipboard Manager
Main entry point for the application
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import PriCHApp

if __name__ == '__main__':
    app = PriCHApp()
    app.run() 