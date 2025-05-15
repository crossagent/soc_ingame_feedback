from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os

app = FastAPI()

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

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
