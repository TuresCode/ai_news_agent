# News Aggregator and Editor

An automated news aggregation system that fetches and processes news articles using AI. The system uses DuckDuckGo search for gathering news and AI-powered agents for content editing and summarization.

## Features

- Automated news fetching using DuckDuckGo Search
- AI-powered content editing and summarization
- Trend analysis and key takeaways generation
- Source URL tracking and attribution

## Prerequisites

- Python 3.8+
- Local Ollama running adjust the .env file if necessary and install llama3.2
- ollama pull llama3.2

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```
2. Install required dependencies:
```bash
pip install -r requirements.txt
```
3. Configure environment variables by creating a .env file:
```bash
OPENAI_API_KEY=fake-key
OPENAI_MODEL_NAME=llama3.2
OPENAI_BASE_URL=http://localhost:11434/v1
```

## Usage
The system can be run from the command line with various options:
```bash
# Basic usage (defaults to AI topic)
python main.py

# Specify a different topic
python main.py --topic "Climate Change"

# Save output to a file
python main.py --topic "Technology" --output file

# Save output to a custom file
```