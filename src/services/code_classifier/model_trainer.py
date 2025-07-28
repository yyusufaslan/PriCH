from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import torch
import os
import datasets
import json

class ModelTrainer:
    def __init__(self, model_name="distilbert-base-uncased", save_dir="saved_model", data_file="C:/Users/aslan/Documents/pythonProjects/PriCH/src/services/code_classifier/model_data_fetch/all_languages_code_text_pairs.jsonl"):
        self.model_name = model_name
        self.save_dir = save_dir
        self.data_file = data_file
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def load_data(self):
        """Load data from JSONL format with segments"""
        texts, labels = [], []
        
        with open(self.data_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    segments = data.get("segments", [])
                    
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
                    print(f"Warning: Skipping invalid JSON line: {e}")
                    continue
                except Exception as e:
                    print(f"Warning: Error processing line: {e}")
                    continue
        
        print(f"Loaded {len(texts)} training examples")
        print(f"Code examples: {sum(labels)}")
        print(f"Text examples: {len(labels) - sum(labels)}")
        
        return [{"text": t, "label": l} for t, l in zip(texts, labels)]

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
        
        data = self.load_data()
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
        print(f"Model saved to {self.save_dir}")

if __name__ == "__main__":
    print("🚀 Starting Model Training with JSONL Data")
    print("=" * 50)
    
    # Check CUDA availability
    if torch.cuda.is_available():
        print("✅ CUDA is available - GPU training enabled!")
        print(f"📊 GPU: {torch.cuda.get_device_name(0)}")
        print(f"💾 GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    else:
        print("⚠️  CUDA not available - using CPU (training will be slower)")
    
    print("-" * 50)
    
    trainer = ModelTrainer()
    trainer.run()
    
    print("✅ Training completed!")
    print(f"📁 Model saved to: {trainer.save_dir}")
