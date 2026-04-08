from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import base64
import uuid

app = FastAPI(title="XOTIIC Plaza API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.xotiicsplaza.us"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OWNER_PASSWORD = os.environ.get("OWNER_PASSWORD")
DATA_FILE = "data.json"
IMAGES_DIR = "images"

os.makedirs(IMAGES_DIR, exist_ok=True)


class Project(BaseModel):
    id: str = ""
    title: str = ""
    category: str = "website"
    description: str = ""
    tags: str = ""
    link: str = ""
    download: str = ""
    image: str = ""  # base64 data URI or filename
    order: int = 0


class Skill(BaseModel):
    name: str = ""
    level: int = 80


class SiteData(BaseModel):
    name: str = "XOTIIC"
    bio: str = "Full-stack developer specializing in modern websites and powerful Discord bots."
    status: str = "Building the future"
    discord: str = "xotiic._.420"
    terminalSkills: str = "HTML/CSS • JavaScript • Python • Discord.js • React"
    visitorCount: str = "0"
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
        except Exception as e:
            print(f"Load error: {e}")
    return SiteData()


def save_data(data: SiteData):
    with open(DATA_FILE, 'w') as f:
        json.dump(data.dict(), f, indent=2)


def compute_stats(data: SiteData):
    """Auto-compute stats from actual data"""
    project_count = len(data.projects)
    download_count = sum(1 for p in data.projects if p.download)
    return {
        "projectCount": f"{project_count}",
        "downloadCount": f"{download_count}" if download_count > 0 else "0",
    }


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("index.html", "r") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/data")
async def get_data():
    data = load_data()
    # Auto-increment visitors
    try:
        visitor = int(data.visitorCount) if data.visitorCount else 0
        data.visitorCount = str(visitor + 1)
        save_data(data)
    except Exception:
        pass

    result = data.dict()
    stats = compute_stats(data)
    result.update(stats)
    return result


@app.post("/api/data")
async def update_data(data: SiteData, password: str = None):
    if password != OWNER_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    save_data(data)
    stats = compute_stats(data)
    result = data.dict()
    result.update(stats)
    return {"success": True, **stats}


@app.post("/api/upload-image")
async def upload_image(password: str = None, file: UploadFile = File(...)):
    if password != OWNER_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Read file and convert to base64 data URI
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:  # 5MB limit
        raise HTTPException(status_code=413, detail="Image too large (max 5MB)")

    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
    allowed = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    if ext not in allowed:
        raise HTTPException(status_code=400, detail="Invalid image type")

    mime = f"image/{'jpeg' if ext == 'jpg' else ext}"
    b64 = base64.b64encode(contents).decode('utf-8')
    data_uri = f"data:{mime};base64,{b64}"

    return {"dataUri": data_uri, "filename": file.filename}


@app.get("/api/health")
async def health_check():
    data = load_data()
    stats = compute_stats(data)
    return {"status": "ok", **stats}
