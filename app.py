from duckduckgo_search import DDGS
from swarm import Swarm, Agent
from datetime import datetime
from dotenv import load_dotenv
import argparse

load_dotenv()

current_date = datetime.now().strftime("%Y-%m")

# Initialize Swarm client
client = Swarm()


def get_news_articles(topic, *args):
    """
    Duckduckgo search based on topic.
    Added *args to handle any additional parameters the agent might try to pass
    """
    # Ensure topic is a string and handle cases where it might be passed as a dict or with date
    if isinstance(topic, dict):
        topic = topic.get("topic", "")
    elif isinstance(topic, str) and current_date in topic:
        topic = topic.replace(current_date, "").strip()
    print(f"Using Duckduckgo search for: {topic}")
    ddg_api = DDGS()
    results = ddg_api.text(f"{topic} {current_date}", max_results=5)

    if not results:
        return f"Could not find news results for {topic}."

    # Store URLs separately to maintain order
    urls = []
    formatted_articles = []

    for result in results:
        urls.append(result["href"])
        article = f"Title: {result['title']}\n" f"Description: {result['body']}"
        formatted_articles.append(article)

    # Join articles with clear separators
    news_text = "\n\n===ARTICLE===\n".join(formatted_articles)

    return {"text": news_text, "urls": urls}


# News Agent to fetch news
news_agent = Agent(
    name="News Assistant",
    instructions="""You provide the latest news articles for a given topic using DuckDuckGo search.""",
    functions=[get_news_articles],
    model="llama3.2",
)

# Editor Agent to edit news
editor_agent = Agent(
    name="Editor Assistant",
    instructions="""Rewrite the news articles in a publishing-ready format. 
    For each article:
    1. Create a clear headline
    2. Summarize the content

    Format each article as:

    ## [HEADLINE]
    [Your summarized content]

    In the end write:

    ***Key Takeaways***
    [Your key takeaways content]

    ***Trend Analysis***
    [Your trend analysis content]
    """,
    model="llama3.2",
)


def run_news_workflow(topic):
    print("Running news Agent workflow...")

    # Step 1: Fetch news
    news_data = get_news_articles(topic)

    if isinstance(news_data, str):  # Error message
        return news_data

    raw_news = news_data["text"]
    urls = news_data["urls"]

    # Step 2: Pass news to editor
    edited_news_response = client.run(
        agent=editor_agent,
        messages=[{"role": "user", "content": raw_news}],
    )

    edited_news = edited_news_response.messages[-1]["content"]

    # Add URLs to headlines
    lines = edited_news.split("\n")
    url_index = 0

    for i, line in enumerate(lines):
        if line.startswith("##") and url_index < len(urls):
            lines[i] = f"{line} (Source: {urls[url_index]})"
            url_index += 1

    return "\n".join(lines)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Fetch and process news articles on specified topics.'
    )
    parser.add_argument(
        '--topic', 
        type=str, 
        default='AI',
        help='Topic to search for news (default: AI)'
    )
    parser.add_argument(
        '--output', 
        type=str, 
        choices=['print', 'file'],
        default='print',
        help='Output method: print to console or save to file (default: print)'
    )
    parser.add_argument(
        '--output-file', 
        type=str, 
        default='news_output.txt',
        help='Output file name when using file output (default: news_output.txt)'
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    results = run_news_workflow(args.topic)

    if args.output == 'print':
        print(results)
    else:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(results)
        print(f"Results saved to {args.output_file}")