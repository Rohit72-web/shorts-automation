import feedparser
# from script_generator import generate_script_from_headlines
from voice_generator import text_to_voice

def get_top_headlines():
    rss_url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(rss_url)
    headlines = [entry.title for entry in feed.entries[:10]]
    return headlines

if __name__ == "__main__":
    headlines = get_top_headlines()
    print("\nTop 10 Trending Indian News (Google News):\n")
    for idx, title in enumerate(headlines, 1):
        print(f"{idx}. {title}")
