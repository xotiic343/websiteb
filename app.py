from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os

app = FastAPI(title="XOTIIC Plaza API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OWNER_PASSWORD = os.environ.get("OWNER_PASSWORD")
DATA_FILE = "data.json"

class Project(BaseModel):
    title: str = ""
    category: str = "website"
    description: str = ""
    tags: str = ""
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
    visitorCount: str = "1337"
    discord: str = "xotiic._.420"
    terminalSkills: str = "HTML/CSS • JavaScript • Python • Discord.js • React"
    projects: List[Project] = []
    skills: List[Skill] = []

def load_data() -> SiteData:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                if 'projects' in data:
                    data['projects'] = [Project(**p) for p in data['projects']]
                if 'skills' in data:
                    data['skills'] = [Skill(**s) for s in data['skills']]
                return SiteData(**data)
        except:
            pass
    return SiteData()

def save_data(data: SiteData):
    with open(DATA_FILE, 'w') as f:
        json.dump(data.dict(), f, indent=2)

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
    data = load_data()
    try:
        visitor = int(data.visitorCount) if data.visitorCount and data.visitorCount != '—' else 0
        data.visitorCount = str(visitor + 1)
        save_data(data)
    except:
        pass
    return data.dict()

@app.post("/api/data")
async def update_data(data: SiteData, password: str = None):
    if password != OWNER_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    save_data(data)
    return {"success": True}

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
