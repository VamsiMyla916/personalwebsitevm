import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import asyncio

app = FastAPI()

# --- ROBUST PATH FINDER ---
# Get the folder where this main.py file is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Logic: Check if 'static' is next to main.py, OR one folder up
if os.path.exists(os.path.join(script_dir, "static")):
    # Standard: app/static/
    static_abs_path = os.path.join(script_dir, "static")
    templates_abs_path = os.path.join(script_dir, "templates")
else:
    # Fallback: maybe static is in the root folder?
    parent_dir = os.path.dirname(script_dir)
    static_abs_path = os.path.join(parent_dir, "static")
    templates_abs_path = os.path.join(parent_dir, "templates")

print(f"✅ LOADING FILES FROM: {static_abs_path}")

# Mount the folders we found
app.mount("/static", StaticFiles(directory=static_abs_path), name="static")
templates = Jinja2Templates(directory=templates_abs_path)


# --- 1. PINNED CONTENT ---
pinned_items = [
    {
        "type": "video",
        "title": "Andrew Ng: Opportunities in AI", 
        "link": "https://www.youtube.com/watch?v=5p248yoa3oE",
        "source": "YouTube"
    },
    {
        "type": "article",
        "title": "The Rise of Agentic AI Workflows", 
        "link": "https://www.deeplearning.ai/the-batch/issue-242/",
        "source": "DeepLearning.AI"
    },
    {
        "type": "article",
        "title": "Building RAG from Scratch", 
        "link": "https://www.anthropic.com/news",
        "source": "Anthropic Blog"
    }
]

# --- 2. LIVE NEWS FETCHER ---
async def get_latest_trends():
    rss_urls = [
        "https://api.rss2json.com/v1/api.json?rss_url=https://techcrunch.com/feed/",
        "https://api.rss2json.com/v1/api.json?rss_url=https://www.theverge.com/rss/index.xml"
    ]
    
    news_items = []
    
    async with httpx.AsyncClient() as client:
        # Fetch both feeds in parallel
        tasks = [client.get(url, timeout=5.0) for url in rss_urls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for response in responses:
            if not isinstance(response, Exception) and response.status_code == 200:
                data = response.json()
                items = data.get("items", [])[:5] 
                for item in items:
                    news_items.append({
                        "title": item.get("title"),
                        "link": item.get("link"),
                        "source": "TechPulse",
                        "pubDate": item.get("pubDate", "")[:10]
                    })
    
    # Fallback if API fails
    if not news_items:
        return [
            {"title": "OpenAI releases new reasoning models", "link": "https://openai.com/blog", "source": "OpenAI", "pubDate": "2025-11-27"},
            {"title": "Meta releases Llama 3 for research", "link": "https://ai.meta.com/blog/", "source": "Meta AI", "pubDate": "2025-11-27"},
            {"title": "Google DeepMind's latest Gemini update", "link": "https://blog.google/technology/ai/", "source": "Google", "pubDate": "2025-11-27"},
        ]
        
    return news_items[:10]

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    news_items = await get_latest_trends()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "news_list": news_items,
        "pinned_list": pinned_items
    })