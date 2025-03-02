from duckduckgo_search import DDGS
from swarm import Swarm, Agent
from datetime import datetime
from dotenv import load_dotenv
import argparse

load_dotenv()

current_date = datetime.now().strftime("%Y-%m")

# Initialize Swarm client
client = Swarm()


def get_news_articles(topic=None, **kwargs):
    """
    Duckduckgo search based on topic.
    """
    # Ensure topic is a string
    if isinstance(topic, dict):
        topic = topic.get("topic", "")
    elif isinstance(topic, str) and current_date in topic:
        topic = topic.replace(current_date, "").strip()

    print(f"Using Duckduckgo search for: {topic}")
    ddg_api = DDGS()
    results = ddg_api.text(f"{topic} {current_date}", max_results=5)

    if not results:
        return f"Could not find news results for {topic}."

    # Format articles with URLs included
    formatted_articles = []
    for result in results:
        article = (
            f"Title: {result['title']}\n"
            f"Description: {result['body']}\n"
            f"URL_EXACT: {result['href']}\n"
        )
        formatted_articles.append(article)

    # Join articles with clear separators
    news_text = "\n\n===ARTICLE===\n".join(formatted_articles)
    return news_text


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
    instructions="""Rewrite the news articles into one publishing-ready article.
    For each article, look for the line starting with 'URL_EXACT:' and use that EXACT URL (don't modify it).

    Format each article as:
        ## [HEADLINE]
        [PASTE THE EXACT URL HERE, removing the 'URL_EXACT:' prefix]
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

    # Step 1: Fetch news using the news_agent
    news_response = client.run(
        agent=news_agent,
        messages=[{"role": "user", "content": f"Get me the latest news about {topic}"}],
    )

    # Extract the news content from the response
    raw_news = news_response.messages[-1]["content"]

    # Check if we got an error message
    if "Could not find news results" in raw_news:
        return raw_news

    # Step 2: Pass news to editor
    edited_news_response = client.run(
        agent=editor_agent,
        messages=[{"role": "user", "content": raw_news}],
    )

    edited_news = edited_news_response.messages[-1]["content"]

    return edited_news


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Fetch and process news articles on specified topics."
    )
    parser.add_argument(
        "--topic", type=str, default="AI", help="Topic to search for news (default: AI)"
    )
    parser.add_argument(
        "--output",
        type=str,
        choices=["print", "file"],
        default="print",
        help="Output method: print to console or save to file (default: print)",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default="news_output.txt",
        help="Output file name when using file output (default: news_output.txt)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    results = run_news_workflow(args.topic)

    if args.output == "print":
        print(results)
    else:
        with open(args.output_file, "w", encoding="utf-8") as f:
            f.write(results)
        print(f"Results saved to {args.output_file}")
