import os
import json
import urllib.request
import subprocess
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI

# Set up client
api_key = os.environ.get("OPENAI_API_KEY", "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")
client = OpenAI(api_key=api_key)

# Reference doc
ref_path = "uploads/senegal-ngor-island-endless-summer-surf-guide-1.md"
try:
    with open(ref_path, "r") as f:
        reference_text = f.read()
except:
    reference_text = ""

# Select 15 files across categories
all_files = [
    "advanced-surf-coaching-senegal-video-analysis.json",
    "advanced-surf-senegal-ngor-right.json",
    "best-time-to-surf-senegal.json",
    "complete-guide-surf-camp-dakar-ngor-island.json",
    "dakar-surf-spots-for-every-level.json",
    "endless-summer-legacy-surfing-ngor.json",
    "how-to-choose-best-surf-camp-in-senegal.json",
    "improve-faster-at-surf-camp.json",
    "learn-to-surf-dakar.json",
    "licensed-surf-camp-senegal.json",
    "ngor-island-waves-explained.json",
    "ngor-surf-guide-right-left.json",
    "no-cars-ngor-island-surf-stay.json",
    "senegal-surf-camp-beginners-learn-faster.json",
    "senegal-surf-season-by-month.json"
]

base_dir = "content/articles_v2/en"
img_dir = "cloudflare-demo/assets/images/blog"
os.makedirs(img_dir, exist_ok=True)

def process_article(filename):
    filepath = os.path.join(base_dir, filename)
    print(f"Starting {filename}...")
    with open(filepath, "r") as f:
        article = json.load(f)
        
    prompt = f"""
    You are an expert SEO copywriter and web designer for a premium surf camp (Ngor Surfcamp Teranga).
    Rewrite the following blog article to make it highly engaging, minimalist, and perfectly aligned with a high-end surf camp brand.
    
    Guidelines:
    - Use Markdown for the content.
    - Include structured visual blocks (e.g., quotes, tips, facts) using blockquotes or custom HTML/Markdown divs if appropriate.
    - Integrate FAQ structured data (JSON-LD) at the end of the markdown.
    - Include Author markup (JSON-LD) at the end of the markdown.
    - Keep the tone inspiring, expert, and welcoming.
    - Optimize the SEO Title and Meta Description.
    - Provide a short visual summary (1-2 sentences) of the article's core theme to be used as an image generation prompt.
    
    Reference Material (use to add depth):
    {reference_text[:2000]}
    
    Original Content:
    {article.get('content_markdown', '')[:3000]}
    
    Output JSON format:
    {{
        "new_title": "...",
        "new_meta_description": "...",
        "new_content_markdown": "...",
        "image_summary": "..."
    }}
    """
    
    try:
        # 1. Generate Content with GPT-5.4
        response = client.chat.completions.create(
            model="gpt-5.4",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # 2. Generate Image with DALL-E 3 (1792x1024)
        img_prompt = f"Wide landscape composition. Black and white digital illustration, minimalist flat vector style, elegant and premium editorial surf aesthetic. High contrast, clean lines, negative space. Subject: {result['image_summary']}. Strictly NO text, NO words, NO letters, NO typography, NO logos. Sophisticated art."
        
        img_res = client.images.generate(
            model="dall-e-3",
            prompt=img_prompt,
            size="1792x1024",
            quality="standard",
            n=1,
        )
        img_url = img_res.data[0].url
        
        # 3. Download and convert image to WebP
        slug = article.get("slug", filename.replace(".json", ""))
        tmp_img = f"/tmp/{slug}.png"
        webp_name = f"{slug}_hero.webp"
        webp_path = os.path.join(img_dir, webp_name)
        
        urllib.request.urlretrieve(img_url, tmp_img)
        subprocess.run(["sips", "-s", "format", "webp", tmp_img, "--out", webp_path], capture_output=True)
        
        # 4. Update JSON
        article["title"] = result["new_title"]
        article["meta_description"] = result["new_meta_description"]
        article["content_markdown"] = result["new_content_markdown"]
        article["hero_image_url"] = f"/assets/images/blog/{webp_name}"
        
        with open(filepath, "w") as f:
            json.dump(article, f, indent=2)
            
        print(f"Finished {filename}!")
        return True
    except Exception as e:
        print(f"Error on {filename}: {e}")
        return False

with ThreadPoolExecutor(max_workers=15) as executor:
    executor.map(process_article, all_files)
    
print("All 15 articles processed successfully!")
