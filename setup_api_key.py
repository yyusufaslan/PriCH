#!/usr/bin/env python3
"""
Setup script for StackOverflow API key
"""

def setup_api_key():
    print("🔑 StackOverflow API Key Setup")
    print("=" * 50)
    print()
    print("To get your StackOverflow API key:")
    print("1. Go to https://stackapps.com/apps/oauth/register")
    print("2. Register a new application")
    print("3. Copy your API key")
    print()
    
    api_key = input("Enter your StackOverflow API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Exiting.")
        return False
    
    # Save API key to file
    try:
        with open("stackoverflow_api_key.txt", "w") as f:
            f.write(api_key)
        print("✅ API key saved to 'stackoverflow_api_key.txt'")
        print("🔒 The file contains your API key - keep it secure!")
        return True
    except Exception as e:
        print(f"❌ Error saving API key: {e}")
        return False

if __name__ == "__main__":
    setup_api_key() 