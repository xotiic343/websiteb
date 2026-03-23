from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import json
from datetime import datetime

app = FastAPI(title="XOTIIC Plaza API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://website-nu-sable-42.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password
OWNER_PASSWORD = os.environ.get("OWNER_PASSWORD")
DATA_FILE = "data.json"

# Models
class Project(BaseModel):
    title: str = ""
    category: str = "website"
    description: str = ""
    tags: str = ""
    emoji: str = "◈"
    link: str = ""
    download: str = ""

class Skill(BaseModel):
    name: str = ""
    level: int = 80

class SiteData(BaseModel):
    name: str = "XOTIIC"
    bio: str = "Full-stack developer specializing in modern websites and powerful Discord bots."
    status: str = "Building the future"
    projectCount: str = ""
    downloadCount: str = ""
    userCount: str = ""
    visitorCount: str = ""
    email: str = "xotiic@example.com"
    discord: str = "xotiic"
    github: str = "github.com/xotiic"
    twitter: str = "@xotiic"
    terminalSkills: str = "HTML/CSS • JavaScript • Python • Discord.js • React"
    projects: List[Project] = []
    skills: List[Skill] = []

class LoginRequest(BaseModel):
    password: str

# Helper functions
def load_data() -> SiteData:
    """Load data from JSON file"""
    default_data = SiteData()
    
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                # Convert projects and skills to proper objects
                if 'projects' in data:
                    data['projects'] = [Project(**p) for p in data['projects']]
                if 'skills' in data:
                    data['skills'] = [Skill(**s) for s in data['skills']]
                return SiteData(**data)
        except Exception as e:
            print(f"Error loading data: {e}")
            return default_data
    return default_data

def save_data(data: SiteData):
    """Save data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data.dict(), f, indent=2, default=str)

# Routes
@app.get("/")
async def serve_index():
    """Serve the main HTML file"""
    return FileResponse("index.html")

@app.get("/owner")
async def serve_owner():
    """Serve the same HTML, frontend handles owner view"""
    return FileResponse("index.html")

@app.get("/api/data")
async def get_data():
    """Get all site data"""
    data = load_data()
    # Increment visitor count
    try:
        visitor = int(data.visitorCount) if data.visitorCount and data.visitorCount != '—' else 0
        data.visitorCount = str(visitor + 1)
        save_data(data)
    except:
        pass
    return data

@app.post("/api/login")
async def login(login: LoginRequest):
    """Owner login"""
    if login.password == OWNER_PASSWORD:
        return {"success": True, "message": "Logged in"}
    raise HTTPException(status_code=401, detail="Invalid password")

@app.post("/api/data")
async def update_data(data: SiteData, password: str = None):
    """Update site data - requires password"""
    if password != OWNER_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    save_data(data)
    return {"success": True, "message": "Data saved successfully"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# Serve static files
app.mount("/static", StaticFiles(directory="."), name="static")
