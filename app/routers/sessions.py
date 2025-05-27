import os
from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.auth import get_or_create_session_token

router = APIRouter()

# Path setup for templates
# sessions.py is in app/routers/
# project_root is two levels up from app/routers/ (e.g., e:\soc_ingame_feedback)
# templates_dir is project_root/template/
try:
    current_script_path = os.path.abspath(__file__)
    app_routers_dir = os.path.dirname(current_script_path)
    app_dir = os.path.dirname(app_routers_dir)
    project_root = os.path.dirname(app_dir)
    templates_dir = os.path.join(project_root, "template")

    if not os.path.isdir(templates_dir):
        # Fallback for safety, though the above should be robust
        templates_dir = os.path.join(os.getcwd(), "template") # Assumes running from project root if above fails
        if not os.path.isdir(templates_dir): # one last attempt if structure is flatter
             templates_dir = os.path.join(os.path.dirname(os.getcwd()), "template")


    if not os.path.isdir(templates_dir):
        print(f"Warning: Templates directory not found at {templates_dir} or fallback paths.")
        # Provide a default path or raise an error if critical
        # For now, Jinja2Templates might fail if the path is incorrect.
        # Defaulting to a relative path that might work if CWD is project root.
        templates_dir = "template"


except Exception as e:
    print(f"Error determining template directory: {e}")
    templates_dir = "template" # Fallback

templates = Jinja2Templates(directory=templates_dir)


@router.get("/sessions/{session_name}", response_class=HTMLResponse)
async def get_session_page(
    request: Request,
    session_name: str,
    server_name: str | None = Query(None, alias="serverName"),
    version: str | None = Query(None),
    user_id: str | None = Query(None, alias="userId"),
    map_name: str | None = Query(None, alias="mapName"),
):
    try:
        # Attempt to initialize session. index.html will fetch /status for details.
        get_or_create_session_token(session_name)
    except HTTPException as e:
        print(f"HTTPException during initial token check for session page {session_name}: {e.detail}")
        # Allow page to load; client-side will fetch status and show error if needed.
    except Exception as e:
        print(f"Unexpected exception during initial token check for session page {session_name}: {str(e)}")
        # Allow page to load; client-side will fetch status and show error if needed.

    context = {
        "request": request,
        "session_name": session_name,
        "server_name": server_name,
        "version": version,
        "user_id": user_id,
        "map_name": map_name,
    }
    try:
        return templates.TemplateResponse("index.html", context)
    except Exception as e:
        print(f"Error rendering template index.html: {e}")
        return HTMLResponse(content=f"<html><body><h1>Error loading page</h1><p>Could not render template. Details: {e}</p></body></html>", status_code=500)


@router.get("/sessions/{session_name}/status")
async def get_session_status_api(session_name: str):
    try:
        session_data = get_or_create_session_token(session_name) # Ensures session is init'd
        return {
            "session_name": session_name,
            "initialized": True,
            "access_token_expires_at": session_data["expires_at"],
            "message": "Session is active."
        }
    except HTTPException as e:
        return {
            "session_name": session_name,
            "initialized": False,
            "error": e.detail,
            "status_code": e.status_code
        }
    except Exception as e:
        print(f"Unexpected error in /status for session {session_name}: {str(e)}")
        return {
            "session_name": session_name,
            "initialized": False,
            "error": "An unexpected error occurred while fetching session status."
        }

