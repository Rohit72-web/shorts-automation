import requests

API_KEY = 'cfb7e04cb0274aafba953bfbc045aa1c'
URL = f"https://newsapi.org/v2/everything?q=india&language=en&sortBy=publishedAt&pageSize=10&apiKey={API_KEY}"

response = requests.get(URL)

if response.status_code == 200:
    data = response.json()
    articles = data.get('articles', [])

    if articles:
        print("\n📰 Latest 10 News Articles About India:\n")
        for idx, article in enumerate(articles, 1):
            print(f"{idx}. {article['title']}")
    else:
        print("❌ No news articles found.")
else:
    print("❌ API request failed:", response.status_code, response.text)
