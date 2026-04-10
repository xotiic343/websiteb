from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="XOTIIC Plaza API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase config
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
OWNER_PASSWORD = os.environ.get("OWNER_PASSWORD",)

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Missing SUPABASE_URL or SUPABASE_KEY environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class Project(BaseModel):
    title: str = ""
    category: str = "website"
    description: str = ""
    tags: str = ""
    link: str = ""
    download: str = ""
    image: str = ""
    order: int = 0

class Skill(BaseModel):
    name: str = ""
    level: int = 80

class SiteData(BaseModel):
    name: str = "XOTIIC"
    bio: str = "Full-stack developer specializing in modern websites and powerful Discord bots."
    status: str = "Building the future"
    projectCount: str = "1"
    downloadCount: str = "1"
    userCount: str = ""
    visitorCount: str = "1"
    email: str = ""
    discord: str = "xotiic._.420"
    github: str = ""
    twitter: str = "@xotiic"
    terminalSkills: str = "HTML/CSS • JavaScript • Python • Discord.js • React"
    projects: List[Project] = []
    skills: List[Skill] = []

def load_data() -> SiteData:
    """Load data from Supabase"""
    try:
        result = supabase.table("site_data").select("data").eq("id", 1).execute()
        if result.data and len(result.data) > 0:
            data = result.data[0]["data"]
            # Convert projects and skills to proper objects
            if "projects" in data:
                data["projects"] = [Project(**p) for p in data["projects"]]
            if "skills" in data:
                data["skills"] = [Skill(**s) for s in data["skills"]]
            return SiteData(**data)
    except Exception as e:
        print(f"Error loading data: {e}")
    return SiteData()

def save_data(data: SiteData):
    """Save data to Supabase"""
    try:
        supabase.table("site_data").upsert({
            "id": 1,
            "data": data.dict(),
            "updated_at": "now()"
        }).execute()
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

def increment_visitor():
    """Increment visitor count"""
    try:
        data = load_data()
        try:
            visitor = int(data.visitorCount) if data.visitorCount and data.visitorCount != '—' else 0
            data.visitorCount = str(visitor + 1)
            save_data(data)
        except:
            pass
    except:
        pass

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/owner", response_class=HTMLResponse)
async def serve_owner():
    with open("index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/api/data")
async def get_data():
    increment_visitor()
    data = load_data()
    return data.dict()

@app.post("/api/data")
async def update_data(data: SiteData, password: str = None):
    if password != OWNER_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    success = save_data(data)
    if success:
        return {"success": True, "message": "Data saved to database"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save data")

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "database": "connected" if SUPABASE_URL else "missing"}
