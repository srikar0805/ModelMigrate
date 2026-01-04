from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import shutil
import os
import json
import pandas as pd
from io import BytesIO, StringIO
from . import services

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "ModelMigrate API is running"}

@app.post("/api/encrypt")
async def encrypt_bim(file: UploadFile = File(...)):
    try:
        content = await file.read()
        bim_data = json.loads(content)
        
        modified_bim, changes_log = services.encrypt_logic(bim_data)
        
        # Prepare response
        # We might need to return a zip or a specific structure. 
        # For now, let's return a JSON with the modified BIM and the log as a string (CS).
        
        # Convert log log to CSV string
        df = pd.DataFrame(changes_log)
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        
        return {
            "modified_bim": modified_bim,
            "changes_log_csv": csv_buffer.getvalue()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/decrypt")
async def decrypt_bim(
    encrypted_file: UploadFile = File(...),
    log_file: UploadFile = File(...), 
    original_file: UploadFile = File(...)
):
    try:
        # Read files
        encrypted_content = await encrypted_file.read()
        encrypted_bim = json.loads(encrypted_content)
        
        log_content = await log_file.read()
        log_df = pd.read_csv(BytesIO(log_content))
        
        original_content = await original_file.read()
        original_bim = json.loads(original_content)
        
        # Perform decryption
        decrypted_bim = services.decrypt_logic(encrypted_bim, log_df, original_bim)
        
        return decrypted_bim
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
