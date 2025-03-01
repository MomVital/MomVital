from fastapi import FastAPI, File, UploadFile, HTTPException
import shutil
import os

app = FastAPI()

# Directory to save uploaded videos
UPLOAD_DIR = "uploaded_videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def hello_world():
    return "Hi"

@app.post("/upload/")
async def upload_video(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "message": "Video uploaded successfully",
            "file_path": file_path,
            "filename": file.filename
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
