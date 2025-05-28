import os
from fastapi import HTTPException
from typing import Dict
import time

from cozepy import COZE_COM_BASE_URL, Coze, JWTAuth, JWTOAuthApp

# The default access is api.coze.cn, but if you need to access api.coze.com,
# please use base_url to configure the api endpoint to access
coze_api_base = os.getenv("COZE_API_BASE") or COZE_COM_BASE_URL

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

# 简单的内存缓存来存储 session 和对应的 access_token
# 格式: {session_name: {"access_token": str, "expires_at": float, "coze_client": Coze}}
session_cache: Dict[str, Dict] = {}

def get_or_create_session_token(session_name: str) -> Dict:
    """获取或创建 session 对应的 access_token 和 Coze 客户端"""
    current_time = time.time()
    
    # 检查是否已有有效的 token
    if session_name in session_cache:
        session_data = session_cache[session_name]
        if session_data["expires_at"] > current_time + 300:  # 提前5分钟刷新
            return session_data
    
    try:
        # 生成新的 access_token (TTL: 1小时)，并传入 session_name
        oauth_token = jwt_oauth_app.get_access_token(ttl=3600, session_name=session_name)

        # 创建 Coze 客户端
        # Note: The Coze client itself doesn't need the session_name here,
        # as the session is tied to the access token generated above.
        coze_client = Coze(auth=JWTAuth(oauth_app=jwt_oauth_app), base_url=coze_api_base)
        
        # 缓存 session 数据
        session_data = {
            "access_token": oauth_token.access_token,
            "expires_at": current_time + 3600,  # 1小时后过期
            "coze_client": coze_client
        }
        session_cache[session_name] = session_data
        
        print(f"Created new session token for: {session_name}，access_token: {oauth_token.access_token}, expires_at: {session_data['expires_at']}")
        return session_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session token: {e}")

def get_coze_client_for_session(session_name: str) -> Coze:
    """获取指定 session 的 Coze 客户端"""
    session_data = get_or_create_session_token(session_name)
    return session_data["coze_client"]
