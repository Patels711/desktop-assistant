import os
from google import genai

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("GEMINI_API_KEY is not set.")
    exit()

client = genai.Client(api_key=api_key)

interaction = client.interactions.create(
    model="gemini-3.6-flash",
    input="Say hello to my desktop assistant in one short sentence."
)

print(interaction.output_text)
