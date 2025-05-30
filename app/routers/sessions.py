import os
from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.auth import get_or_create_session_token
from cozepy import Coze # 移除 Auth

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

    # Load COZE_BOT_ID from environment variable
    COZE_BOT_ID = os.getenv("COZE_BOT_ID")
    if not COZE_BOT_ID:
        print("Warning: COZE_BOT_ID environment variable not set. Using default or expect error.")
        # You might want to set a default or raise an error if it's critical
        # COZE_BOT_ID = "your_default_bot_id_here" 

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
        "coze_bot_id": COZE_BOT_ID,  # Pass bot_id to the template
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
            "access_token": session_data["access_token"], # Include the access token
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

@router.get("/sessions/{session_name}/bug_info")
async def get_bug_info(session_name: str):
    try:
        session_data = get_or_create_session_token(session_name)
        # Use the COZE_BOT_ID from environment
        bot_id = COZE_BOT_ID 
        if not bot_id:
            raise HTTPException(status_code=500, detail="COZE_BOT_ID is not configured in the environment.")
        
        coze_client: Coze = session_data["coze_client"]

        # Call the Get variable values API
        # Fetching all variables for now, frontend will pick what it needs
        # Changed from .list to .retrieve and added keywords parameter
        variables_response = coze_client.variables.retrieve(
            bot_id=bot_id,
            connector_id='999', # Assuming None for default connector
            connector_uid=session_name, # Use session_name as connector_uid
            keywords=[] # Assuming empty list fetches all variables
        )

        # Process the response and extract relevant bug info
        bug_info = {}
        if variables_response and variables_response.data and variables_response.data.items:
            for item in variables_response.data.items:
                # Assuming variable names in Coze match the form field IDs
                if item.keyword in ["bug-title", "bug-description", "steps-to-reproduce"]:
                     # Convert keyword to use underscores for consistency with frontend JS
                    js_key = item.keyword.replace('-', '_')
                    bug_info[js_key] = item.value
                # Also include variables with underscores if they exist
                elif item.keyword in ["bug_title", "bug_description", "steps_to_reproduce"]:
                    bug_info[item.keyword] = item.value


        return bug_info

    except HTTPException as e:
        raise e # Re-raise FastAPI HTTPExceptions
    except Exception as e:
        print(f"Error fetching bug info for session {session_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch bug information from Coze.")
