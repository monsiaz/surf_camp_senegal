import os
import openai

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "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"))

prompt = "Black and white digital illustration, minimalist flat vector style, elegant and premium editorial surf aesthetic. High contrast, clean lines, negative space. Subject: A surfer at Ngor point with a classic longboard silhouette, island reef wave glowing at sunset. No text, sophisticated art."

try:
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    print("DA Image URL:", response.data[0].url)
except Exception as e:
    print("Error:", e)
