from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import torch
import os
import datasets
import json
import glob
from typing import List, Dict, Any

class ModelTrainer:
    def __init__(self, model_name="distilbert-base-uncased", 
                 save_dir="model/saved_model", 
                 data_dir="model/data/code_text_pairs"):
        self.model_name = model_name
        self.save_dir = save_dir
        self.data_dir = data_dir
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def load_data_from_directory(self):
        """Load data from all language files in the data directory"""
        texts, labels = [], []
        
        # Find all language files
        pattern = os.path.join(self.data_dir, "*_code_text_pairs.jsonl")
        language_files = glob.glob(pattern)
        
        if not language_files:
            print(f"❌ No data files found in {self.data_dir}")
            print(f"💡 Expected pattern: {pattern}")
            return []
        
        print(f"📁 Found {len(language_files)} language files:")
        for file in language_files:
            print(f"   - {os.path.basename(file)}")
        
        total_questions = 0
        total_segments = 0
        
        for file_path in language_files:
            language = os.path.basename(file_path).replace("_code_text_pairs.jsonl", "")
            print(f"\n📖 Loading {language} data from {os.path.basename(file_path)}...")
            
            file_questions = 0
            file_segments = 0
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        try:
                            data = json.loads(line.strip())
                            segments = data.get("segments", [])
                            
                            file_questions += 1
                            file_segments += len(segments)
                            
                            # Extract each segment as a separate training example
                            for segment in segments:
                                text = segment.get("text", "").strip()
                                segment_type = segment.get("type", "TEXT")
                                
                                # Skip empty text
                                if not text:
                                    continue
                                
                                # Convert segment type to label (CODE=1, TEXT=0)
                                label = 1 if segment_type == "CODE" else 0
                                
                                texts.append(text)
                                labels.append(label)
                                
                        except json.JSONDecodeError as e:
                            print(f"⚠️  Warning: Skipping invalid JSON line {line_num} in {language}: {e}")
                            continue
                        except Exception as e:
                            print(f"⚠️  Warning: Error processing line {line_num} in {language}: {e}")
                            continue
                
                total_questions += file_questions
                total_segments += file_segments
                
                print(f"   ✅ {language}: {file_questions} questions, {file_segments} segments")
                
            except Exception as e:
                print(f"❌ Error loading {language} data: {e}")
                continue
        
        print(f"\n📊 Data Loading Summary:")
        print(f"   Total questions: {total_questions:,}")
        print(f"   Total segments: {total_segments:,}")
        print(f"   Training examples: {len(texts):,}")
        print(f"   Code examples: {sum(labels):,}")
        print(f"   Text examples: {len(labels) - sum(labels):,}")
        
        if len(texts) == 0:
            print("❌ No training data found!")
            return []
        
        return [{"text": t, "label": l} for t, l in zip(texts, labels)]

    def load_data(self):
        """Backward compatibility method - now uses directory loading"""
        return self.load_data_from_directory()

    def tokenize_batch(self, batch):
        return self.tokenizer(batch["text"], padding=True, truncation=True, max_length=256)
    
    def get_optimal_batch_size(self):
        """Determine optimal batch size based on GPU memory"""
        if not torch.cuda.is_available():
            return 8  # Default for CPU
        
        gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
        
        if gpu_memory_gb >= 8:  # 8GB+ GPU
            return 16
        elif gpu_memory_gb >= 4:  # 4GB+ GPU
            return 12
        else:  # Smaller GPU
            return 8

    def run(self):
        # Check GPU availability
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🚀 Using device: {device}")
        if torch.cuda.is_available():
            print(f"📊 GPU: {torch.cuda.get_device_name(0)}")
            print(f"💾 GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        
        # Load data from organized directory structure
        data = self.load_data_from_directory()
        
        if not data:
            print("❌ No training data available. Please run the scraper first.")
            return
        
        # Create train/test split
        dataset_dict = datasets.Dataset.from_list(data).train_test_split(test_size=0.2)
        dataset_dict = dataset_dict.map(self.tokenize_batch, batched=True)
        dataset_dict.set_format("torch", columns=["input_ids", "attention_mask", "label"])

        model = AutoModelForSequenceClassification.from_pretrained(self.model_name, num_labels=2)
        # Move model to GPU if available
        model = model.to(device)

        # Get optimal batch size based on GPU memory
        optimal_batch_size = self.get_optimal_batch_size()
        print(f"📦 Using batch size: {optimal_batch_size}")
        
        training_args = TrainingArguments(
            output_dir=self.save_dir,
            per_device_train_batch_size=optimal_batch_size,
            per_device_eval_batch_size=optimal_batch_size,
            num_train_epochs=3,
            save_strategy="epoch",
            logging_dir="./logs",
            logging_steps=100,
            # GPU/CUDA settings
            no_cuda=False,  # Enable CUDA
            dataloader_pin_memory=True,  # Faster data loading with GPU
            dataloader_num_workers=2,  # Parallel data loading
            # Memory optimization
            gradient_accumulation_steps=2,  # Accumulate gradients for larger effective batch size
            fp16=torch.cuda.is_available(),  # Use mixed precision if GPU available
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=dataset_dict["train"],
            eval_dataset=dataset_dict["test"],
            tokenizer=self.tokenizer,
        )

        trainer.train()
        model.save_pretrained(self.save_dir)
        self.tokenizer.save_pretrained(self.save_dir)
        print(f"✅ Model saved to {self.save_dir}")

    def get_data_statistics(self):
        """Get statistics about available training data"""
        print(f"\n📊 Analyzing training data in {self.data_dir}...")
        
        pattern = os.path.join(self.data_dir, "*_code_text_pairs.jsonl")
        language_files = glob.glob(pattern)
        
        if not language_files:
            print(f"❌ No data files found in {self.data_dir}")
            return
        
        total_stats = {
            "languages": 0,
            "total_questions": 0,
            "total_segments": 0,
            "code_segments": 0,
            "text_segments": 0
        }
        
        print(f"\n📊 Language Statistics:")
        print(f"{'='*60}")
        
        for file_path in sorted(language_files):
            language = os.path.basename(file_path).replace("_code_text_pairs.jsonl", "")
            
            language_stats = {
                "questions": 0,
                "segments": 0,
                "code_segments": 0,
                "text_segments": 0
            }
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        data = json.loads(line)
                        segments = data.get("segments", [])
                        
                        language_stats["questions"] += 1
                        language_stats["segments"] += len(segments)
                        
                        for segment in segments:
                            seg_type = segment.get("type", "UNKNOWN")
                            if seg_type == "CODE":
                                language_stats["code_segments"] += 1
                                total_stats["code_segments"] += 1
                            elif seg_type == "TEXT":
                                language_stats["text_segments"] += 1
                                total_stats["text_segments"] += 1
                
                total_stats["languages"] += 1
                total_stats["total_questions"] += language_stats["questions"]
                total_stats["total_segments"] += language_stats["segments"]
                
                print(f"  {language}:")
                print(f"    Questions: {language_stats['questions']:,}")
                print(f"    Segments: {language_stats['segments']:,}")
                print(f"    Code: {language_stats['code_segments']:,}")
                print(f"    Text: {language_stats['text_segments']:,}")
                
            except Exception as e:
                print(f"❌ Error analyzing {language}: {e}")
        
        print(f"\n📊 Total Statistics:")
        print(f"{'='*60}")
        print(f"  Languages: {total_stats['languages']}")
        print(f"  Total Questions: {total_stats['total_questions']:,}")
        print(f"  Total Segments: {total_stats['total_segments']:,}")
        print(f"  Code Segments: {total_stats['code_segments']:,}")
        print(f"  Text Segments: {total_stats['text_segments']:,}")
        
        if total_stats['total_segments'] > 0:
            code_percentage = (total_stats['code_segments'] / total_stats['total_segments']) * 100
            text_percentage = (total_stats['text_segments'] / total_stats['total_segments']) * 100
            print(f"  Code/Text Ratio: {code_percentage:.1f}% / {text_percentage:.1f}%")


if __name__ == "__main__":
    print("🚀 Starting Model Training with Organized Data")
    print("=" * 60)
    
    # Check CUDA availability
    if torch.cuda.is_available():
        print("✅ CUDA is available - GPU training enabled!")
        print(f"📊 GPU: {torch.cuda.get_device_name(0)}")
        print(f"💾 GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    else:
        print("⚠️  CUDA not available - using CPU (training will be slower)")
    
    print("-" * 60)
    
    # Create trainer with organized data directory
    trainer = ModelTrainer(
        save_dir="model/saved_model",
        data_dir="model/data/code_text_pairs"
    )
    
    # Show data statistics before training
    trainer.get_data_statistics()
    
    print("-" * 60)
    
    # Start training
    trainer.run()
    
    print("✅ Training completed!")
    print(f"📁 Model saved to: {trainer.save_dir}")
