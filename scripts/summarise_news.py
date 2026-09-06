import os
import time
from google import genai
from google.genai import errors

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def summarise(text, title="", max_attempts=3):
    prompt = f"Summarize this AI news article in 2-3 sentences:\n\nTitle: {title}\n\n{text}"
    for attempt in range(max_attempts):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
            )
            return response.text.strip()
        except errors.ServerError:
            if attempt < max_attempts - 1:
                wait = 2 ** attempt  # 1s, 2s, 4s
                print(f"503 from Gemini, retrying in {wait}s (attempt {attempt + 1}/{max_attempts})")
                time.sleep(wait)
            else:
                print("Gemini still unavailable after retries, skipping this article")
                return None
        except errors.ClientError as e:
            print(f"Client error (not retryable): {e}")
            return None

if __name__ == "__main__":
    # quick manual test
    test_text = "Testing 1 2 3"
    print(summarise(test_text, title="Test Article"))