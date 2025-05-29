from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Form
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import shutil
import os
import json
from datetime import datetime
from ast_utils import run_full_pipeline, get_entities_from_tokens

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_DIR = os.path.join(DATA_DIR, "history")
SOURCE_FILE = os.path.join(DATA_DIR, "source.py")
TOKENS_FILE = os.path.join(DATA_DIR, "tokens.json")
AST_FILE = os.path.join(DATA_DIR, "ast.json")
TREE_FILE = os.path.join(DATA_DIR, "ast_output.png")

os.makedirs(HISTORY_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
def home(request: Request, idx: int = -1):
    files = sorted([f for f in os.listdir(HISTORY_DIR) if f.endswith(".py")], reverse=True)
    code = ""
    ast_generation_time = "0.0s"
    if files:
        if idx == -1:
            idx = 0
        idx = max(0, min(idx, len(files)-1))
        with open(os.path.join(HISTORY_DIR, files[idx]), "r", encoding="utf-8") as f:
            code = f.read()
    ast_json = ""
    if os.path.exists(AST_FILE):
        with open(AST_FILE, "r", encoding="utf-8") as f:
            ast_json = f.read()
    tree_exists = os.path.exists(TREE_FILE)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "code": code,
        "ast_json": ast_json,
        "tree_exists": tree_exists,
        "idx": idx,
        "history": files,
        "history_len": len(files),
        "ast_generation_time": ast_generation_time
    })

@app.post("/submit", response_class=HTMLResponse)
def submit_code(request: Request, code: str = Form(...)):
    with open(SOURCE_FILE, "w", encoding="utf-8") as f:
        f.write(code)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(os.path.join(HISTORY_DIR, f"source_{timestamp}.py"), "w", encoding="utf-8") as f:
        f.write(code)
    try:
        run_full_pipeline(SOURCE_FILE)
    except Exception as e:
        return HTMLResponse(f"<h1>Pipeline error: {e}</h1>")
    return RedirectResponse(url="/", status_code=303)

@app.delete("/source")
def delete_source():
    if os.path.exists(SOURCE_FILE):
        os.remove(SOURCE_FILE)
    return {"status": "deleted"}

@app.post("/generate")
def generate_ast():
    try:
        run_full_pipeline(SOURCE_FILE)
        return {"status": "generated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
def get_history():
    files = sorted([f for f in os.listdir(HISTORY_DIR) if f.endswith(".py")], reverse=True)
    return {"history": files}

@app.get("/history/{filename}")
def get_history_file(filename: str):
    file_path = os.path.join(HISTORY_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    with open(file_path, "r", encoding="utf-8") as f:
        return {"code": f.read()}

@app.get("/entities")
def get_entities():
    if not os.path.exists(TOKENS_FILE):
        raise HTTPException(status_code=404, detail="Tokens not found")
    with open(TOKENS_FILE, "r", encoding="utf-8") as f:
        tokens = json.load(f)
    entities = get_entities_from_tokens(tokens)
    return JSONResponse(content=entities)

@app.get("/ast_json")
def get_ast_json():
    if not os.path.exists(AST_FILE):
        raise HTTPException(status_code=404, detail="AST not found")
    return FileResponse(AST_FILE, media_type="application/json")

@app.get("/tree_img")
def get_tree_img():
    if not os.path.exists(TREE_FILE):
        raise HTTPException(status_code=404, detail="Tree image not found")
    return FileResponse(TREE_FILE, media_type="image/png")

@app.post("/end")
def end_session():
    # Optionally clean up files or stop background tasks
    return {"status": "ended"} 