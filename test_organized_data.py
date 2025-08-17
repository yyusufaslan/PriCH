#!/usr/bin/env python3
"""
Test script for the new organized data structure
"""

import os
import json
import glob
from src.services.code_classifier.model_data_fetch.model_trainer import ModelTrainer

def test_data_structure():
    """Test the new organized data structure"""
    print("🧪 Testing Organized Data Structure")
    print("=" * 50)
    
    # Check if directories exist
    model_root = "model"
    data_dir = os.path.join(model_root, "data")
    raw_dir = os.path.join(data_dir, "raw_data")
    processed_dir = os.path.join(data_dir, "code_text_pairs")
    saved_model_dir = os.path.join(model_root, "saved_model")
    
    print(f"📁 Checking directories...")
    print(f"   Model root: {'✅' if os.path.exists(model_root) else '❌'} {model_root}")
    print(f"   Data directory: {'✅' if os.path.exists(data_dir) else '❌'} {data_dir}")
    print(f"   Raw data: {'✅' if os.path.exists(raw_dir) else '❌'} {raw_dir}")
    print(f"   Processed data: {'✅' if os.path.exists(processed_dir) else '❌'} {processed_dir}")
    print(f"   Saved model: {'✅' if os.path.exists(saved_model_dir) else '❌'} {saved_model_dir}")
    
    if not os.path.exists(processed_dir):
        print("❌ Processed data directory not found!")
        print("💡 Run the scraper first to generate data.")
        return
    
    # Check for language files
    pattern = os.path.join(processed_dir, "*_code_text_pairs.jsonl")
    language_files = glob.glob(pattern)
    
    print(f"\n📁 Found {len(language_files)} language files:")
    for file in sorted(language_files):
        filename = os.path.basename(file)
        language = filename.replace("_code_text_pairs.jsonl", "")
        
        # Count lines in file
        try:
            with open(file, "r", encoding="utf-8") as f:
                line_count = sum(1 for _ in f)
            print(f"   ✅ {filename}: {line_count:,} lines")
        except Exception as e:
            print(f"   ❌ {filename}: Error reading file - {e}")
    
    # Test model trainer
    print(f"\n🧪 Testing Model Trainer...")
    trainer = ModelTrainer(
        save_dir="model/saved_model",
        data_dir="model/data/code_text_pairs"
    )
    
    # Get statistics
    trainer.get_data_statistics()
    
    # Test data loading
    print(f"\n🧪 Testing Data Loading...")
    data = trainer.load_data_from_directory()
    
    if data:
        print(f"✅ Successfully loaded {len(data):,} training examples")
        code_count = sum(1 for item in data if item["label"] == 1)
        text_count = len(data) - code_count
        print(f"   Code examples: {code_count:,}")
        print(f"   Text examples: {text_count:,}")
    else:
        print("❌ No training data loaded!")
    
    print(f"\n✅ Test completed!")

if __name__ == "__main__":
    test_data_structure() 