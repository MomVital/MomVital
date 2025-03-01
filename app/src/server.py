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

@app.post("/analyze/")
async def analyze(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        process_results = await asyncio.to_thread(overall_process, file_path)

        return {
            "message": "Processing complete",
            "results": process_results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/get-suggest/")
async def get_llm_suggest(data: dict):
    try:
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Get LLM Suggestion failed: {str(e)}")
