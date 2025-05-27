from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os
from app import auth

app = FastAPI()

# 包含 auth 路由
app.include_router(auth.router, prefix="/auth", tags=["auth"])

# 获取当前文件所在的目录
current_file_path = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录 (假设 main.py 在 app 文件夹下，template 在项目根目录的 template 文件夹下)
project_root = os.path.dirname(current_file_path)
templates_dir = os.path.join(project_root, "template")
static_dir = os.path.join(templates_dir, "static")

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 设置模板目录
templates = Jinja2Templates(directory=templates_dir)

@app.get("/sessions/{session_name}", response_class=HTMLResponse)
async def start_session(
    request: Request,
    session_name: str,
    server_name: str | None = Query(None, alias="serverName"),
    version: str | None = Query(None),
    user_id: str | None = Query(None, alias="userId"),
    map_name: str | None = Query(None, alias="mapName"),
):
    context = {
        "request": request,
        "session_name": session_name,
        "server_name": server_name,
        "version": version,
        "user_id": user_id,
        "map_name": map_name,
    }
    print(f"Accessing session: {session_name}, Server: {server_name}, Version: {version}, User: {user_id}, Map: {map_name}")
    return templates.TemplateResponse("index.html", context)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Session Required</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 50px; text-align: center; }
            .container { max-width: 600px; margin: 0 auto; }
            .error { color: #d32f2f; font-size: 18px; margin: 20px 0; }
            .instruction { color: #555; margin: 20px 0; }
            .example { background: #f5f5f5; padding: 15px; border-radius: 5px; font-family: monospace; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>In-Game Feedback System</h1>
            <div class="error">❌ Session name Required</div>
            <div class="instruction">
                Please access the feedback system with a valid session name using the following URL format:
            </div>
            <div class="example">
                /sessions/{session_name}?serverName=服务器名&version=版本号&userId=用户ID&mapName=地图名
            </div>
            <div class="instruction">
                Example:<br>
                <code>/sessions/abc123?serverName=GameServer&version=1.0.0&userId=player456</code>
            </div>
        </div>
    </body>
    </html>
    """)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
