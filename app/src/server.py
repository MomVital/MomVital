from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from src.data_process_tools import overall_process, remove_useless_data
from src.variables import *
from starlette.responses import StreamingResponse
from src.llm_tools import stream_llm_output, invoke_llm_output, build_llm_chain, get_content_by_week
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
            "results": process_results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/hb-analyze/")
async def stream_hr_analyze(request: Request):
    try:
        data = await request.json()
        chain = build_llm_chain(template=hb_analysis_template, input_vars=hb_input_variables)
        
        required_keys = set(hb_input_variables)
        missing_keys = required_keys - data.keys()

        if missing_keys:
            raise Exception(f"Missing required keys: {list(missing_keys)}")
        
        query = {k: data[k] for k in required_keys}
        
        if data.get("stream", True):
            return StreamingResponse(stream_llm_output(chain, query), media_type="text/plain")
        else:
            return invoke_llm_output(chain, query)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Get Heart Rate Analysis failed: {str(e)}")


@app.post("/hrv-analyze/")
async def stream_hrv_analyze(request: Request):
    try:
        data = await request.json()
        chain = build_llm_chain(template=hrv_analysis_template, input_vars=hrv_input_variables)
        
        required_keys = set(hrv_input_variables)
        missing_keys = required_keys - data.keys()

        if missing_keys:
            raise Exception(f"Missing required keys: {list(missing_keys)}")
        
        query = {k: data[k] for k in required_keys}
        
        if data.get("stream", True):
            return StreamingResponse(stream_llm_output(chain, query), media_type="text/plain")
        else:
            return invoke_llm_output(chain, query)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Get HRV Analysis failed: {str(e)}")


@app.post("/stress-analyze/")
async def stream_stress_analyze(request: Request):
    try:
        data = await request.json()
        chain = build_llm_chain(template=stress_analysis_template, input_vars=stress_input_variables)
        
        required_keys = set(stress_input_variables) - {"context"}
        missing_keys = required_keys - data.keys()

        if missing_keys:
            raise Exception(f"Missing required keys: {list(missing_keys)}")
        
        query = {}
        for k in stress_input_variables:
            query[k] = data[k]
        query["context"] = get_content_by_week(int(data['week']))
        
        if data.get("stream", True):
            return StreamingResponse(stream_llm_output(chain, query), media_type="text/plain")
        else:
            return invoke_llm_output(chain, query)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Get Stress Analysis failed: {str(e)}")


@app.post("/overall-analyze/")
async def stream_overall_analyze(request: Request):
    try:
        data = await request.json()
        chain = build_llm_chain(template=overall_analysis_template, input_vars=overall_input_variables)
        
        required_keys = set(overall_input_variables) - {"context"} | {"query"}
        missing_keys = required_keys - data.keys()

        if missing_keys:
            raise Exception(f"Missing required keys: {list(missing_keys)}")
        
        query = {}
        for k in stress_input_variables:
            query[k] = data[k]
        query["context"] = get_content_by_week(int(data['week']))
        
        if data.get("stream", True):
            return StreamingResponse(stream_llm_output(chain, query), media_type="text/plain")
        else:
            return invoke_llm_output(chain, query)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Get Overall Analysis failed: {str(e)}")