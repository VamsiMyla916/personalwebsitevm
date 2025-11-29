from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import asyncio

app = FastAPI()

# Mount Static Files and Templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# --- 1. PINNED CONTENT (MANAGE YOUR FAVORITES HERE) ---
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

# --- 2. LIVE NEWS FETCHER (TECHCRUNCH & VERGE) ---
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
                items = data.get("items", [])[:5] # Take top 5 from each
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