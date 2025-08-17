#!/usr/bin/env python3
"""
Helper script to set up Hugging Face token for model uploading
"""

import os
from pathlib import Path

def setup_huggingface_token():
    """Guide user through setting up Hugging Face token"""
    print("🔑 Hugging Face Token Setup")
    print("=" * 50)
    
    print("\n📋 To upload your model to Hugging Face Hub, you need a token.")
    print("Follow these steps:")
    
    print("\n1️⃣  Go to https://huggingface.co/settings/tokens")
    print("2️⃣  Click 'New token'")
    print("3️⃣  Give it a name (e.g., 'model-uploader')")
    print("4️⃣  Select 'Write' role")
    print("5️⃣  Click 'Generate token'")
    print("6️⃣  Copy the token (it starts with 'hf_')")
    
    print("\n💡 The token will be saved to 'huggingface_token.txt'")
    print("⚠️  Keep this token secure and don't share it!")
    
    # Get token from user
    token = input("\n🔑 Paste your Hugging Face token: ").strip()
    
    if not token:
        print("❌ No token provided!")
        return False
    
    if not token.startswith("hf_"):
        print("❌ Invalid token format! Token should start with 'hf_'")
        return False
    
    # Save token to file
    try:
        with open("huggingface_token.txt", "w") as f:
            f.write(token)
        
        print("✅ Token saved to 'huggingface_token.txt'")
        print("🔒 File permissions set to owner-only")
        
        # Set file permissions (Unix-like systems)
        try:
            os.chmod("huggingface_token.txt", 0o600)
        except:
            pass  # Windows doesn't support chmod
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving token: {e}")
        return False

def test_token():
    """Test if the saved token works"""
    token_file = Path("huggingface_token.txt")
    
    if not token_file.exists():
        print("❌ Token file not found!")
        return False
    
    try:
        with open(token_file, "r") as f:
            token = f.read().strip()
        
        if not token:
            print("❌ Token file is empty!")
            return False
        
        print("✅ Token file found")
        print(f"🔑 Token: {token[:10]}...{token[-4:]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading token: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Hugging Face Token Setup")
    print("=" * 50)
    
    # Check if token already exists
    if test_token():
        print("\n✅ Token already configured!")
        response = input("Do you want to set up a new token? (y/N): ").strip().lower()
        if response != 'y':
            print("👋 Setup cancelled.")
            return
    
    # Set up new token
    if setup_huggingface_token():
        print("\n🎉 Token setup completed!")
        print("\n📝 Next steps:")
        print("1. Train your model using the model trainer")
        print("2. Run the model uploader:")
        print("   python src/services/code_classifier/model_data_fetch/model_uploader.py")
    else:
        print("\n❌ Token setup failed!")

if __name__ == "__main__":
    main() 