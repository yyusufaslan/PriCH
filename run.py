#!/usr/bin/env python3
"""
PriCH - Clipboard Manager
Alternative entry point
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import PriCHApp

def main():
    app = PriCHApp()
    app.run()   

if __name__ == '__main__':
    main() 