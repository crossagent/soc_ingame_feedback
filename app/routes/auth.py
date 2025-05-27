import os
from fastapi import APIRouter, HTTPException

from cozepy import COZE_CN_BASE_URL, Coze, JWTAuth, JWTOAuthApp

# The default access is api.coze.cn, but if you need to access api.coze.com,
# please use base_url to configure the api endpoint to access
coze_api_base = os.getenv("COZE_API_BASE") or COZE_CN_BASE_URL

# client ID
jwt_oauth_client_id = os.getenv("COZE_JWT_OAUTH_CLIENT_ID")
# private key
jwt_oauth_private_key = os.getenv("COZE_JWT_OAUTH_PRIVATE_KEY")
# path to the private key file (usually with .pem extension)
jwt_oauth_private_key_file_path = os.getenv("COZE_JWT_OAUTH_PRIVATE_KEY_FILE_PATH")
# public key id
jwt_oauth_public_key_id = os.getenv("COZE_JWT_OAUTH_PUBLIC_KEY_ID")

if jwt_oauth_private_key_file_path:
    try:
        with open(jwt_oauth_private_key_file_path, "r") as f:
            jwt_oauth_private_key = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"Private key file not found at {jwt_oauth_private_key_file_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading private key file: {e}")


# The sdk offers the JWTOAuthApp class to establish an authorization for Service OAuth.
# Firstly, it is required to initialize the JWTOAuthApp.

# Check if required environment variables are set
if not all([jwt_oauth_client_id, jwt_oauth_private_key, jwt_oauth_public_key_id]):
    raise HTTPException(status_code=500, detail="Missing one or more JWT OAuth environment variables (COZE_JWT_OAUTH_CLIENT_ID, COZE_JWT_OAUTH_PRIVATE_KEY, COZE_JWT_OAUTH_PUBLIC_KEY_ID)")

try:
    jwt_oauth_app = JWTOAuthApp(
        client_id=jwt_oauth_client_id,
        private_key=jwt_oauth_private_key,
        public_key_id=jwt_oauth_public_key_id,
        base_url=coze_api_base,
    )
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error initializing JWTOAuthApp: {e}")


router = APIRouter()

@router.get("/get_coze_client")
async def get_coze_client():
    """
    API endpoint to get an initialized Coze client using JWT authentication.
    """
    try:
        # Generate the authorization token
        # The default ttl is 900s, and developers can customize the expiration time, which can be
        # set up to 24 hours at most.
        oauth_token = jwt_oauth_app.get_access_token(ttl=3600)

        # use the jwt oauth_app to init Coze client
        coze = Coze(auth=JWTAuth(oauth_app=jwt_oauth_app), base_url=coze_api_base)

        # In a real application, you would likely not return the entire client,
        # but rather use it to perform actions and return the results.
        # For demonstration, we'll just indicate success.
        # You might return the access_token or other relevant info to the frontend.
        return {"message": "Coze client initialized successfully", "access_token": oauth_token.access_token}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during JWT authentication or Coze client initialization: {e}")
