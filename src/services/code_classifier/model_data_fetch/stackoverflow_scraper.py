import requests
import time
import json
from bs4 import BeautifulSoup
import asyncio
import json
import re

def fetch_questions(tag="python", pagesize=10, max_pages=1):
    all_data = []

    for page in range(1, max_pages + 1):
        url = "https://api.stackexchange.com/2.3/questions"
        params = {
            "order": "desc",
            "sort": "votes",
            "tagged": tag,
            "site": "stackoverflow",
            "filter": "withbody",  # include question body
            "pagesize": pagesize,
            "page": page
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        for item in data.get("items", []):
            all_data.append({
                "question_id": item["question_id"],
                "title": item["title"],
                "body": item["body"]
            })

        time.sleep(1.5)  # API rate limit (30 reqs/sec if no key)

    return all_data


def save_jsonl(data, filename="stackoverflow_raw_data.jsonl"):
    with open(filename, "w", encoding="utf-8") as f:
        for item in data:
            json.dump(item, f)
            f.write("\n")


def extract_code_and_text(html):
    soup = BeautifulSoup(html, "html.parser")
    segments = []
    code_texts = set()  # Track code texts to avoid duplicates
    
    # First pass: extract all code segments
    for elem in soup.descendants:
        if elem.name == "code" and len(elem.get_text().strip().split()) > 1:
            text = elem.get_text().strip()
            if text and text not in code_texts:
                segments.append({"type": "CODE", "text": text})
                code_texts.add(text)
        elif elem.name == "pre" and len(elem.get_text().strip().split()) > 1:
            text = elem.get_text().strip()
            if text and text not in code_texts:
                segments.append({"type": "CODE", "text": text})
                code_texts.add(text)
    
    # Second pass: extract text segments, excluding code
    for elem in soup.descendants:
        if elem.name is None and elem.string:
            text = elem.string.strip()
            if text and text not in code_texts:
                # Check if this text is not part of any code block
                is_part_of_code = False
                for code_text in code_texts:
                    if text in code_text or code_text in text:
                        is_part_of_code = True
                        break
                
                if not is_part_of_code:
                    segments.append({"type": "TEXT", "text": text})

    return segments

def read_jsonl(filename="stackoverflow_raw_data.jsonl"):
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            segments = extract_code_and_text(data["body"])
            print(f"\nQuestion: {data['title']}")
            for seg in segments:
                print(f"[{seg['type']}] {seg['text']}")

def read_processed_data(filename="all_languages_code_text_pairs.jsonl", max_items=5):
    """Read and display processed data with language information"""
    count = 0
    language_stats = {}
    
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            if count >= max_items:
                break
                
            data = json.loads(line)
            language = data.get("language", "unknown")
            language_stats[language] = language_stats.get(language, 0) + 1
            
            print(f"\n{'='*60}")
            print(f"Language: {language}")
            print(f"Question ID: {data.get('question_id')}")
            print(f"Title: {data.get('title', 'N/A')}")
            print(f"Segments: {len(data.get('segments', []))}")
            
            for i, seg in enumerate(data.get('segments', [])[:3]):  # Show first 3 segments
                print(f"  [{i+1}] {seg['type']}: {seg['text'][:100]}...")
            
            count += 1
    
    print(f"\n{'='*60}")
    print("Language Statistics:")
    for lang, count in language_stats.items():
        print(f"  {lang}: {count} items")


def fetch_questions_async():
    # fetch all languages
    languages = ["python", "javascript", "java", "cpp", "csharp", "go", "ruby", "typescript"]
    all_questions = []
    
    for language in languages:
        print(f"Fetching questions for {language}...")
        questions = fetch_questions(tag=language, pagesize=20, max_pages=2)
        
        # Add language tag to each question
        for question in questions:
            question["language"] = language
        
        all_questions.extend(questions)
        print(f"Fetched {len(questions)} questions for {language}")
    
    # Save all questions to a single file
    save_jsonl(all_questions, "all_languages_raw_data.jsonl")
    print(f"Total questions saved: {len(all_questions)}")
    return all_questions


def process_stackoverflow_data(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as infile, \
         open(output_path, "w", encoding="utf-8") as outfile:

        for line in infile:
            data = json.loads(line)
            body = data.get("body", "")
            language = data.get("language", "unknown")
            
            if not body.strip():
                continue

            segments = extract_code_and_text(body)

            # Boş segment varsa alma
            if not segments:
                continue

            result = {
                "raw_content": body.strip(),
                "language": language,
                "question_id": data.get("question_id"),
                "title": data.get("title"),
                "segments": segments
            }

            outfile.write(json.dumps(result, ensure_ascii=False) + "\n")
if __name__ == "__main__":
    # Fetch all languages and save to single file
    fetch_questions_async()
    
    # Process the combined data and extract to single file
    process_stackoverflow_data(
        input_path="all_languages_raw_data.jsonl",
        output_path="all_languages_code_text_pairs.jsonl"
    )
    
    print("✅ Data fetching and processing completed!")
    print("📁 Files created:")
    print("   - all_languages_raw_data.jsonl (raw StackOverflow data)")
    print("   - all_languages_code_text_pairs.jsonl (processed code-text pairs)")
    
    # Display sample of processed data
    print("\n📊 Sample of processed data:")
    read_processed_data("all_languages_code_text_pairs.jsonl", max_items=3)