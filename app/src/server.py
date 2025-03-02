from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from src.data_process_tools import overall_process, remove_useless_data
from src.variables import *
from starlette.responses import StreamingResponse
from src.llm_tools import stream_llm_response, invoke_llm_response, build_llm_chain
import shutil
import asyncio
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
    print("Running API Analyze")
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        process_results = await asyncio.to_thread(overall_process, file_path)

        return {
            "message": "Processing complete",
            "results": remove_useless_data(process_results)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/hr-analyze/")
async def stream_hr_analyze(request:Request):
    try:
        data = await request.json()
        chain = build_llm_chain(template=hr_analysis_template, input_vars=hr_input_variables)
        heart_rate = data.get("heart_rate", raise Exception("No Heart Rate provided"))
        query = {"heart_rate": heart_rate}
        if data.get("stream", True):
            return StreamingResponse(stream_llm_output(chain, query), media_type="text/plain")
        else:
            return invoke_llm_output(chain, query)
    expect Exception as e:
        raise HTTPException(status_code=500, detail=f"Get Heart Rate Analysis failed: {str(e)}")


@app.post("/hrv-analyze/")
async def stream_hr_analyze(request:Request):
    try:
        data = await request.json()
        chain = build_llm_chain(template=hr_analysis_template, input_vars=hr_input_variables)
        hrv = data.get("hrv", raise Exception("No HRV provided"))
        query = {"heart_rate": heart_rate}
        if data.get("stream", True):
            return StreamingResponse(stream_llm_output(chain, query), media_type="text/plain")
        else:
            return invoke_llm_output(chain, query)
    expect Exception as e:
        raise HTTPException(status_code=500, detail=f"Get HRV Analysis failed: {str(e)}")


@app.post("/stress-analyze/")
async def stream_hr_analyze(request:Request):
    try:
        data = await request.json()
        chain = build_llm_chain(template=hr_analysis_template, input_vars=hr_input_variables)
        stress = data.get("stress", raise Exception("No stress provided"))
        query = {"stress": stress}
        if data.get("stream", True):
            return StreamingResponse(stream_llm_output(chain, query), media_type="text/plain")
        else:
            return invoke_llm_output(chain, query)
    expect Exception as e:
        raise HTTPException(status_code=500, detail=f"Get Stress Analysis failed: {str(e)}")


@app.post("/overall-analyze/")
async def stream_hr_analyze(request:Request):
    try:
        data = await request.json()
        chain = build_llm_chain(template=overall_analysis_template, input_vars=overall_input_variables)
        stress = data.get("stress", raise Exception("No stress provided"))
        query = {"stress": stress}
        if data.get("stream", True):
            return StreamingResponse(stream_llm_output(chain, query), media_type="text/plain")
        else:
            return invoke_llm_output(chain, query)
    expect Exception as e:
        raise HTTPException(status_code=500, detail=f"Get Stress Analysis failed: {str(e)}")