from fastapi import APIRouter, HTTPException
from models.dto import PasswordRequest, PasswordResponse
from db.sqlite import store_password, get_password_by_key, get_decrypted_password

router = APIRouter()

@router.post("/passwords/{key}", response_model=PasswordResponse, summary="Store hashed password")
def store_password_endpoint(key: str, req: PasswordRequest):
    """Accepts a password, encrypts and stores in DB with the given key."""
    if not req.password:
        raise HTTPException(status_code=400, detail="Password is required.")
    
    saved = store_password(key, req.password)
    return PasswordResponse(id=saved['id'], key=key, password=req.password)

@router.get("/passwords/{key}", response_model=PasswordResponse, summary="Get hashed password (decrypted)")
def get_password_endpoint(key: str):
    pw = get_password_by_key(key)
    if not pw:
        # ID is optional in PasswordResponse, so we can return None for it
        return PasswordResponse(key=key, password="")

    decrypted = get_decrypted_password(key)
    if decrypted is None:
        decrypted = ""
    return PasswordResponse(id=pw['id'], key=key, password=decrypted)
