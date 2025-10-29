#!/bin/bash

echo "🚀 Starting ETL process..."

python 1-extract_text.py
python 2-transform_load.py
python 3-generate_qa_pairs.py
python 4-create_conversations.py

echo "✅ ETL pipeline finished successfully!"
