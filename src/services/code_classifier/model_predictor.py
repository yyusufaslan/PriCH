from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import os

class CodeClassifier:
    def __init__(self, model_path="./src/services/code_classifier/saved_model"):
        # Convert to absolute path to avoid path interpretation issues
        if not os.path.isabs(model_path):
            model_path = os.path.abspath(model_path)
        
        try:
            # Try to load the trained model and tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=model_path, local_files_only=True)
            self.model = AutoModelForSequenceClassification.from_pretrained(pretrained_model_name_or_path=model_path, local_files_only=True)
            print(f"Successfully loaded trained model from: {model_path}")
        except Exception as e:
            print(f"Failed to load trained model from {model_path}: {e}")
            print("Falling back to base DistilBERT model")
            # Fallback to base model
            self.tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path="distilbert-base-uncased", local_files_only=True)
            self.model = AutoModelForSequenceClassification.from_pretrained(pretrained_model_name_or_path="distilbert-base-uncased", local_files_only=True)

    def is_code(self, text: str) -> bool:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
        with torch.no_grad():
            logits = self.model(**inputs).logits
        predicted = torch.argmax(logits, dim=-1).item()
        return predicted == 1

    def predict(self, text: str) -> bool:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
        with torch.no_grad():
            logits = self.model(**inputs).logits
        predicted = torch.argmax(logits, dim=-1).item()
        return predicted == 1
    
    def predict_with_confidence(self, text: str) -> dict:
        """Predict with confidence scores"""
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
        with torch.no_grad():
            logits = self.model(**inputs).logits
            probabilities = torch.softmax(logits, dim=-1)
        
        predicted = torch.argmax(logits, dim=-1).item()
        confidence = probabilities[0][predicted].item()
        
        return {
            "prediction": "CODE" if predicted == 1 else "TEXT",
            "confidence": confidence,
            "is_code": predicted == 1
        }

if __name__ == "__main__":
    classifier = CodeClassifier()
    test_texts = [
        "private String shareWithPastie(String selection, int languageDropdownId) throws Exception {",
        "String response = shareAndGetResponse(selection, languageDropdownId);",
        "return extractKeyFrom(response);",
        "}",
        "def hello_world(): print('Hello, World!')",
        "What&#39;s the difference between I am trying to understand the difference between these four methods.",
    ]

    print("Testing CODE vs TEXT Classification:")
    print("=" * 50)
    
    for t in test_texts:
        result = classifier.predict_with_confidence(t)
        print(f"{result}")
