from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import requests
import json
import random


app = FastAPI(title="AI-Powered Data Pipeline (Mock)")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Allow any domain
    allow_methods=["*"],      # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],      # Allow all headers
)

@app.get("/")
def home():
    return {"message": "AI Pipeline is running! Go to /docs to test the endpoint."}

# -------------------------------
# Request Model
# -------------------------------
class PipelineRequest(BaseModel):
    email: str
    source: str

# -------------------------------
# Helper Functions
# -------------------------------

def fetch_posts(limit=3):
    """Fetch first N posts from JSONPlaceholder"""
    try:
        response = requests.get("https://jsonplaceholder.typicode.com/posts", timeout=5)
        response.raise_for_status()
        posts = response.json()[:limit]
        return posts, None
    except Exception as e:
        return [], str(e)

def analyze_post_mock(text):
    """Mock AI analysis: generates fake insights and sentiment"""
    sample_insights = [
        "This post seems very informative.",
        "The author appears optimistic.",
        "Some points might be confusing.",
        "Balanced perspective with some humor."
    ]
    analysis = " ".join(random.sample(sample_insights, 2))
    sentiment = random.choice(["optimistic", "pessimistic", "balanced"])
    return analysis, sentiment

def store_results(items, filename="processed_posts.json"):
    """Store results in a JSON file"""
    try:
        with open(filename, "w") as f:
            json.dump(items, f, indent=2)
        return True
    except Exception as e:
        return False

def send_notification(email):
    """Mock notification (prints to console)"""
    try:
        print(f"Notification sent to {email}")
        return True
    except Exception as e:
        return False

# -------------------------------
# API Endpoint
# -------------------------------
@app.post("/pipeline")
def run_pipeline(request: PipelineRequest):
    posts, fetch_error = fetch_posts()
    errors = []
    if fetch_error:
        errors.append(fetch_error)

    items = []
    for post in posts:
        try:
            analysis, sentiment = analyze_post_mock(post["body"])
            item = {
                "original": post["body"],
                "analysis": analysis,
                "sentiment": sentiment,
                "stored": True,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            items.append(item)
        except Exception as e:
            errors.append(str(e))
            continue

    stored = store_results(items)
    notification_sent = send_notification(request.email)

    return {
        "items": items,
        "notificationSent": notification_sent,
        "processedAt": datetime.utcnow().isoformat() + "Z",
        "errors": errors
    }

# -------------------------------
# Run locally (optional)
# -------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
