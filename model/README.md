# Model Directory

This directory contains the trained model and training data.

## Structure
- `saved_model/` - Trained model files (created by model trainer)
- `data/` - Training data
  - `raw_data/` - Raw StackOverflow data
  - `code_text_pairs/` - Processed training data

## Getting Started
1. Run the data scraper to fetch training data
2. Run the model trainer to train the model
3. The trained model will appear in `saved_model/`
