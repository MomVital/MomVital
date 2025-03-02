from starlette.responses import StreamingResponse
from src.llm_tools import (stream_llm_output, invoke_llm_output, build_llm_chain, 
                           get_content_by_week, search, search_filter)
from src.variables import *
from fastapi import FastAPI, HTTPException, Request
import re, ast


app = FastAPI()

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
        
        query = {k: data[k] for k in required_keys}
        query["context"] = get_content_by_week(int(data['week']))
        
        if data.get("stream", True):
            return StreamingResponse(stream_llm_output(chain, query), media_type="text/plain")
        else:
            return invoke_llm_output(chain, query)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Get Stress Analysis failed: {str(e)}")


@app.post("/overall-analyze/")
async def get_overall_analyze(request: Request):
    try:
        data = await request.json()
        chain = build_llm_chain(template=overall_analysis_template, input_vars=overall_input_variables)
        
        required_keys = set(overall_input_variables) - {"context"} | {"history_result"}
        missing_keys = required_keys - data.keys()

        if missing_keys:
            raise Exception(f"Missing required keys: {list(missing_keys)}")
        
        query = {k: data[k] for k in required_keys}
        query["context"] = search_filter(search(data['history_result'], k=50), week_filter=6)
        
        result = invoke_llm_output(chain, query)
        match = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)

        if match:
            extracted_str = match.group(1)
            json_dict = ast.literal_eval(extracted_str)
            return {
                "message": "LLM Process complete",
                "results": json_dict
            }
        else:
            return {
                "message": "No JSON content found.",
                "results": {}
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Get Overall Analysis failed: {str(e)}")