
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model_name = "microsoft/codebert-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)


class AIChecker:
    def __init__(self):
        pass

    def is_code_block(self, text):
        inputs = tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            logits = model(**inputs).logits
            prediction = torch.argmax(logits, dim=-1).item()
        return prediction == 1  # 1 = code, 0 = text

    def extract_code_blocks(self, content):
        blocks = [block.strip() for block in content.split("\n\n") if block.strip()]
        print(f"found {len(blocks)} blocks................")
        code_blocks = [block for block in blocks if self.is_code_block(block)]
        print(f"code blocks: {code_blocks}")
        return code_blocks
    
    def print_code_blocks(self, content):
        print(f"starting to check for code blocks................")
        code_blocks = self.extract_code_blocks(content)
        print(f"found {len(code_blocks)} code blocks................")
        for i, block in enumerate(code_blocks):
            print(f"\n--- Code Block {i+1} ---\n{block}")