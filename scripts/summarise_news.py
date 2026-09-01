import os
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def summarise(text, title=""):
    prompt = f"Summarise this news article about AI in 4 to 6 sentences, highlighting the key takeaways in the last sentence:\n\nTitle: {title}\n\n{text}"
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )
    return response.text.strip()

if __name__ == "__main__":
    # quick manual test
    test_text = "Testing 1 2 3"
    print(summarise(test_text, title="Test Article"))