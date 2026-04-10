import os
import json
import openai

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "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"))

def test_gen():
    with open("content/articles_v2/en/endless-summer-legacy-surfing-ngor.json", "r") as f:
        article = json.load(f)
        
    print("Generating Hero Image...")
    # Generate Hero Image
    try:
        hero_response = client.images.generate(
            model="dall-e-3",
            prompt=article["hero_image_prompt"] + " Minimalist, high-end editorial photography style, vibrant but natural colors.",
            size="1024x1024",
            quality="standard",
            n=1,
        )
        hero_url = hero_response.data[0].url
        print("Hero URL:", hero_url)
    except Exception as e:
        print("Error generating hero:", e)
        hero_url = ""

    print("Generating B&W Image...")
    # Generate B&W Image
    try:
        bw_response = client.images.generate(
            model="dall-e-3",
            prompt=article["hero_image_prompt"] + " Black and white photography, high contrast, minimalist, artistic editorial style.",
            size="1024x1024",
            quality="standard",
            n=1,
        )
        bw_url = bw_response.data[0].url
        print("B&W URL:", bw_url)
    except Exception as e:
        print("Error generating B&W:", e)
        bw_url = ""

    print("Rewriting content...")
    # Rewrite content
    prompt = f"""
    Rewrite the following blog article to make it highly engaging, minimalist, and perfectly aligned with a high-end surf camp brand (Ngor Surfcamp Teranga).
    
    Guidelines:
    - Use Markdown.
    - Include structured visual blocks (e.g., quotes, tips, facts) using blockquotes or custom HTML/Markdown divs if appropriate.
    - Integrate FAQ structured data (JSON-LD) at the end.
    - Include Author markup (JSON-LD) at the end.
    - Keep the tone inspiring, expert, and welcoming.
    - Use the provided reference text if helpful to add depth.
    
    Original Content:
    {article['content_markdown']}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o", # Fallback to 4o as 5.4 might not be accessible via this exact string yet in standard SDK without special headers, but let's try gpt-4o first for safety and speed on the test
        messages=[
            {"role": "system", "content": "You are an expert SEO copywriter and web designer for a premium surf camp."},
            {"role": "user", "content": prompt}
        ]
    )
    
    new_content = response.choices[0].message.content
    article["content_markdown"] = new_content
    article["hero_image_url"] = hero_url
    article["bw_image_url"] = bw_url
    
    with open("test_article_output.json", "w") as f:
        json.dump(article, f, indent=2)
        
    print("Done! Saved to test_article_output.json")

if __name__ == "__main__":
    test_gen()
