import requests
import time
import json
import os
from bs4 import BeautifulSoup
import asyncio
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

class StackOverflowScraper:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.stackexchange.com/2.3"
        self.session = requests.Session()
        self.request_count = 0
        self.max_requests = 10000
        self.rate_limit_delay = 0.1 if api_key else 1.5  # Faster with API key
        
        # Create directories for organized data storage
        self.model_root = "model"
        self.data_dir = os.path.join(self.model_root, "data")
        self.raw_data_dir = os.path.join(self.data_dir, "raw_data")
        self.processed_data_dir = os.path.join(self.data_dir, "code_text_pairs")
        self.saved_model_dir = os.path.join(self.model_root, "saved_model")
        self.create_directories()
        
        # Languages to fetch (prioritized by popularity)
        self.languages = [
            "python", "javascript", "java", "cpp", "csharp", "go", "ruby", 
            "typescript", "php", "swift", "kotlin", "rust", "scala", "r", 
            "matlab", "perl", "haskell", "lua", "dart", "elixir"
        ]
        
        # Calculate requests per language (distribute evenly)
        self.requests_per_language = self.max_requests // len(self.languages)
        print(f"📊 API Key: {'✅ Present' if api_key else '❌ Not provided'}")
        print(f"📊 Total requests available: {self.max_requests}")
        print(f"📊 Languages to fetch: {len(self.languages)}")
        print(f"📊 Requests per language: {self.requests_per_language}")
        print(f"📊 Rate limit delay: {self.rate_limit_delay}s")
        print(f"📁 Model root: {self.model_root}")
        print(f"📁 Data directory: {self.data_dir}")
        print(f"📁 Raw data directory: {self.raw_data_dir}")
        print(f"📁 Processed data directory: {self.processed_data_dir}")
        print(f"📁 Saved model directory: {self.saved_model_dir}")

    def create_directories(self):
        """Create necessary directories for data storage"""
        directories = [
            self.model_root,
            self.data_dir,
            self.raw_data_dir,
            self.processed_data_dir,
            self.saved_model_dir
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"📁 Created directory: {directory}")

    def load_api_key(self, key_file: str = "stackoverflow_api_key.txt") -> bool:
        """Load API key from file"""
        try:
            if os.path.exists(key_file):
                with open(key_file, "r") as f:
                    self.api_key = f.read().strip()
                print(f"✅ API key loaded from {key_file}")
                self.rate_limit_delay = 0.1  # Faster with API key
                return True
            else:
                print(f"❌ API key file not found: {key_file}")
                return False
        except Exception as e:
            print(f"❌ Error loading API key: {e}")
            return False

    def make_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict]:
        """Make API request with rate limiting and error handling"""
        if self.request_count >= self.max_requests:
            print(f"⚠️  Reached maximum request limit ({self.max_requests})")
            return None
        
        # Add API key if available
        if self.api_key:
            params["key"] = self.api_key
        
        try:
            url = f"{self.base_url}/{endpoint}"
            response = self.session.get(url, params=params, timeout=30)
            
            self.request_count += 1
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for API errors
                if "error_id" in data:
                    print(f"❌ API Error: {data.get('error_message', 'Unknown error')}")
                    return None
                
                # Check rate limiting
                if "backoff" in data:
                    backoff_time = data["backoff"]
                    print(f"⏳ Rate limited, waiting {backoff_time} seconds...")
                    time.sleep(backoff_time)
                
                return data
            else:
                print(f"❌ HTTP Error {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            return None
        finally:
            time.sleep(self.rate_limit_delay)

    def save_questions_continuously(self, questions: List[Dict], language: str):
        """Save questions to language-specific file continuously"""
        filename = os.path.join(self.raw_data_dir, f"{language}_raw_data.jsonl")
        
        try:
            with open(filename, "a", encoding="utf-8") as f:
                for question in questions:
                    json.dump(question, f, ensure_ascii=False)
                    f.write("\n")
            
            print(f"💾 Saved {len(questions)} questions to {filename}")
        except Exception as e:
            print(f"❌ Error saving questions for {language}: {e}")

    def fetch_questions(self, tag: str, pagesize: int = 100, max_pages: Optional[int] = None) -> List[Dict]:
        """Fetch questions for a specific language tag with continuous saving"""
        all_data = []
        
        # Calculate max pages based on requests per language
        if max_pages is None:
            max_pages = self.requests_per_language
        
        print(f"\n🔍 Fetching {tag} questions...")
        print(f"   Max pages: {max_pages}")
        print(f"   Page size: {pagesize}")
        print(f"   Expected questions: {max_pages * pagesize}")
        
        for page in range(1, max_pages + 1):
            if self.request_count >= self.max_requests:
                print(f"⚠️  Reached request limit while fetching {tag}")
                break
            
            params = {
                "order": "desc",
                "sort": "votes",
                "tagged": tag,
                "site": "stackoverflow",
                "filter": "withBody",  # include question body
                "pagesize": pagesize,
                "page": page
            }
            
            data = self.make_request("questions", params)
            
            if not data or "items" not in data:
                print(f"⚠️  No data received for {tag} page {page}")
                break
            
            items = data.get("items", [])
            if not items:
                print(f"✅ No more questions for {tag} (page {page})")
                break
            
            # Process and save this page's questions immediately
            page_questions = []
            for item in items:
                question_data = {
                    "question_id": item["question_id"],
                    "title": item["title"],
                    "body": item["body"],
                    "score": item.get("score", 0),
                    "answer_count": item.get("answer_count", 0),
                    "view_count": item.get("view_count", 0),
                    "creation_date": item.get("creation_date", 0),
                    "language": tag
                }
                page_questions.append(question_data)
                all_data.append(question_data)
            
            # Save this page's questions immediately
            self.save_questions_continuously(page_questions, tag)
            
            print(f"   📄 Page {page}: {len(items)} questions (Total: {len(all_data)})")
            
            # Check if we have more pages
            if not data.get("has_more", False):
                print(f"✅ No more pages for {tag}")
                break
        
        print(f"✅ Fetched {len(all_data)} questions for {tag}")
        return all_data

    def fetch_all_languages(self) -> List[Dict]:
        """Fetch questions for all languages with continuous saving"""
        all_questions = []
        start_time = datetime.now()
        
        print(f"\n🚀 Starting data collection at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Requests used: {self.request_count}/{self.max_requests}")
        
        for i, language in enumerate(self.languages, 1):
            print(f"\n{'='*60}")
            print(f"🌐 Language {i}/{len(self.languages)}: {language}")
            print(f"{'='*60}")
            
            try:
                questions = self.fetch_questions(tag=language)
                all_questions.extend(questions)
                
                # Progress update
                elapsed = datetime.now() - start_time
                remaining_languages = len(self.languages) - i
                avg_time_per_lang = elapsed / i if i > 0 else 0
                estimated_remaining = avg_time_per_lang * remaining_languages
                
                print(f"📊 Progress: {i}/{len(self.languages)} languages")
                print(f"📊 Total questions: {len(all_questions)}")
                print(f"📊 Requests used: {self.request_count}/{self.max_requests}")
                print(f"⏱️  Elapsed: {elapsed}")
                print(f"⏱️  Estimated remaining: {estimated_remaining}")
                
                if self.request_count >= self.max_requests:
                    print("⚠️  Reached maximum request limit")
                    break
                    
            except Exception as e:
                print(f"❌ Error fetching {language}: {e}")
                print(f"⚠️  Continuing with next language...")
                continue
        
        end_time = datetime.now()
        total_time = end_time - start_time
        
        print(f"\n{'='*60}")
        print(f"✅ Data collection completed!")
        print(f"📊 Total questions: {len(all_questions)}")
        print(f"📊 Total requests: {self.request_count}")
        print(f"⏱️  Total time: {total_time}")
        print(f"📁 Raw data saved to: {self.raw_data_dir}/")
        
        return all_questions

    def process_language_data(self, language: str):
        """Process raw data for a specific language"""
        raw_file = os.path.join(self.raw_data_dir, f"{language}_raw_data.jsonl")
        processed_file = os.path.join(self.processed_data_dir, f"{language}_code_text_pairs.jsonl")
        
        if not os.path.exists(raw_file):
            print(f"⚠️  No raw data file found for {language}")
            return
        
        print(f"\n🔄 Processing {language} data...")
        
        processed_count = 0
        skipped_count = 0
        
        try:
            with open(raw_file, "r", encoding="utf-8") as infile, \
                 open(processed_file, "w", encoding="utf-8") as outfile:

                for line_num, line in enumerate(infile, 1):
                    try:
                        data = json.loads(line)
                        body = data.get("body", "")
                        
                        if not body.strip():
                            skipped_count += 1
                            continue

                        segments = self.extract_code_and_text(body)

                        # Skip if no segments found
                        if not segments:
                            skipped_count += 1
                            continue

                        result = {
                            "raw_content": body.strip(),
                            "language": language,
                            "question_id": data.get("question_id"),
                            "title": data.get("title"),
                            "score": data.get("score", 0),
                            "answer_count": data.get("answer_count", 0),
                            "view_count": data.get("view_count", 0),
                            "creation_date": data.get("creation_date", 0),
                            "segments": segments
                        }

                        outfile.write(json.dumps(result, ensure_ascii=False) + "\n")
                        processed_count += 1
                        
                        if line_num % 100 == 0:
                            print(f"   📄 Processed {line_num} lines...")
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON error on line {line_num}: {e}")
                        skipped_count += 1
                    except Exception as e:
                        print(f"❌ Error processing line {line_num}: {e}")
                        skipped_count += 1
            
            print(f"✅ {language} processing completed!")
            print(f"📊 Processed: {processed_count} items")
            print(f"📊 Skipped: {skipped_count} items")
            print(f"📁 Output: {processed_file}")
            
        except Exception as e:
            print(f"❌ Error processing {language}: {e}")

    def process_all_languages(self):
        """Process all language data files"""
        print(f"\n🔄 Processing all language data...")
        
        for language in self.languages:
            self.process_language_data(language)
        
        print(f"\n✅ All language processing completed!")
        print(f"📁 Processed data saved to: {self.processed_data_dir}/")

    def extract_code_and_text(self, html: str) -> List[Dict]:
        """Extract code and text segments from HTML"""
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

    def get_data_statistics(self):
        """Get comprehensive statistics about all processed data"""
        print(f"\n📊 Analyzing all processed data...")
        
        total_stats = {
            "total_questions": 0,
            "total_segments": 0,
            "languages": {},
            "segment_types": {"CODE": 0, "TEXT": 0}
        }
        
        for language in self.languages:
            processed_file = os.path.join(self.processed_data_dir, f"{language}_code_text_pairs.jsonl")
            
            if not os.path.exists(processed_file):
                continue
            
            language_stats = {
                "questions": 0,
                "segments": 0,
                "code_segments": 0,
                "text_segments": 0
            }
            
            try:
                with open(processed_file, "r", encoding="utf-8") as f:
                    for line in f:
                        data = json.loads(line)
                        segments = data.get("segments", [])
                        
                        language_stats["questions"] += 1
                        language_stats["segments"] += len(segments)
                        
                        for segment in segments:
                            seg_type = segment.get("type", "UNKNOWN")
                            if seg_type == "CODE":
                                language_stats["code_segments"] += 1
                                total_stats["segment_types"]["CODE"] += 1
                            elif seg_type == "TEXT":
                                language_stats["text_segments"] += 1
                                total_stats["segment_types"]["TEXT"] += 1
                
                total_stats["languages"][language] = language_stats
                total_stats["total_questions"] += language_stats["questions"]
                total_stats["total_segments"] += language_stats["segments"]
                
            except Exception as e:
                print(f"❌ Error analyzing {language}: {e}")
        
        # Display comprehensive statistics
        print(f"\n{'='*60}")
        print("📊 COMPREHENSIVE DATA STATISTICS")
        print(f"{'='*60}")
        print(f"📊 Total questions: {total_stats['total_questions']:,}")
        print(f"📊 Total segments: {total_stats['total_segments']:,}")
        print(f"📊 Languages: {len(total_stats['languages'])}")
        
        print(f"\n📊 Segment Types:")
        for seg_type, count in total_stats["segment_types"].items():
            print(f"  {seg_type}: {count:,}")
        
        print(f"\n📊 Language Distribution:")
        sorted_languages = sorted(
            total_stats["languages"].items(), 
            key=lambda x: x[1]["questions"], 
            reverse=True
        )
        
        for lang, stats in sorted_languages:
            percentage = (stats["questions"] / total_stats["total_questions"]) * 100 if total_stats["total_questions"] > 0 else 0
            print(f"  {lang}: {stats['questions']:,} questions ({percentage:.1f}%)")
            print(f"    - Code segments: {stats['code_segments']:,}")
            print(f"    - Text segments: {stats['text_segments']:,}")

    def read_sample_data(self, language: str, max_items: int = 3):
        """Read and display sample data for a specific language"""
        processed_file = os.path.join(self.processed_data_dir, f"{language}_code_text_pairs.jsonl")
        
        if not os.path.exists(processed_file):
            print(f"❌ No processed data found for {language}")
            return
        
        print(f"\n📊 Sample data for {language}:")
        print(f"{'='*60}")
        
        count = 0
        with open(processed_file, "r", encoding="utf-8") as f:
            for line in f:
                if count >= max_items:
                    break
                    
                data = json.loads(line)
                segments = data.get("segments", [])
                
                print(f"\nQuestion ID: {data.get('question_id')}")
                print(f"Title: {data.get('title', 'N/A')}")
                print(f"Score: {data.get('score', 0)}")
                print(f"Segments: {len(segments)}")
                
                for i, seg in enumerate(segments[:3]):  # Show first 3 segments
                    print(f"  [{i+1}] {seg['type']}: {seg['text'][:100]}...")
                
                count += 1


def main():
    """Main function to run the scraper"""
    scraper = StackOverflowScraper()
    
    # Try to load API key
    if not scraper.load_api_key():
        print("⚠️  No API key found. Using slower rate limits.")
        print("💡 Create 'stackoverflow_api_key.txt' file with your API key for faster scraping.")
    
    print(f"\n🚀 Starting StackOverflow data collection...")
    
    # Fetch all languages (data is saved continuously)
    scraper.fetch_all_languages()
    
    # Process all language data
    scraper.process_all_languages()
    
    # Display comprehensive statistics
    scraper.get_data_statistics()
    
    # Show sample data for first few languages
    for language in scraper.languages[:3]:
        scraper.read_sample_data(language, max_items=2)
    
    print(f"\n✅ All operations completed successfully!")
    print(f"📁 Model root: {scraper.model_root}/")
    print(f"📁 Raw data: {scraper.raw_data_dir}/")
    print(f"📁 Processed data: {scraper.processed_data_dir}/")
    print(f"📁 Saved model: {scraper.saved_model_dir}/")


if __name__ == "__main__":
    main()
