from openai import OpenAI
from news1 import get_top_headlines  # Import the function to fetch headlines

client = OpenAI(
    api_key="API_key",  #  API key
    base_url="https://api.chatanywhere.com.cn/v1"  # base URL for ChatAnywhere
)

def generate_script_from_headlines(headlines):
    news_text = "\n".join([f"{i+1}. {h}" for i, h in enumerate(headlines)])
    prompt = (
        "Tum ek professional news anchor ho jo YouTube Shorts ke liye engaging Hinglish news script likhta hai.\n"
        "Har script ko aise banao ki audience ki curiosity bani rahe aur woh pura video dekhe.\n\n"
        "Requirements:\n"
        "1. Script ka start hamesha is line se ho:\n   'Pichle 24 ghante me kya hua hai, aayiye jaldi se dekhte hain badi khabrein!'\n"
        "2. Har headline ke liye ek short engaging Hinglish news line likho (10–15 seconds wali).\n"
        "3. Har news line factual aur crisp ho, entertainment-style delivery ho jisme thoda energy ho.\n"
        "4. Script ka end hamesha is line se ho:\n   'Toh, aaj ke liye itna hi. Hamari team aapko har nai khabar se update rakhti rahegi. Tab tak ke liye, apna khayal rakhen aur surakshit rahen. Namaskar.'\n"
        "5. Output strictly JSON format me ho. Structure:\n   [\n     {\n       'news': 'string',\n       'keywords': ['keyword1', 'keyword2', 'keyword3']\n     }\n   ]\n"
        "6. 'news' field me sirf woh script line ho jo TTS me bolni hai. 'keywords' field me 3–5 relevant keywords ho jo video search ke liye use ho.\n\n"
        f"Headlines:\n{news_text}\n"
    )
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    # Fetch latest headlines from news1.py
    headlines = get_top_headlines()
    script_json = generate_script_from_headlines(headlines)
    print("\nHinglish Script for YouTube Shorts (JSON):\n")
    print(script_json)
    # Save JSON script to file for downstream use
    with open("script.json", "w", encoding="utf-8") as f:
        f.write(script_json)
