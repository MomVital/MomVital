# README

# Description
> This is the backend for a maternal health solution for low-income mom. It requires user to record a 30s video and will generate an health data report with actionable suggestions.
>
> It uses pyVHR and pyHRV to calculate data (heart rate, HRV, pn50, sdnn, etc.) and uses Vector Database to provide solid guideance and uses GPT-4.5-preview to generate suggestions

# How to run it
1. Ensure your linux system have cupy 11.8 and able to connect to the internet
2. Ensure Anaconda or Miniconda installed on the system
3. Go to app and run this command
```bash
conda env create -f codefest_env.yml
conda activate codefest
nohup uvicorn src.video_server:app --host:0.0.0.0 --port=3000 > video_server.log 2>&1 &
```
4. Now your video server is running
5. Then run this command:
```bash
conda env create -f llm_env.yml
conda activate llm
nohup uvicorn src.llm_server:app --host:0.0.0.0 --port=3001 > llm_server.log 2>&1 &
```
6. Now your llm server is also running. The backend development is now finished, go to frontend and run the UI to use the app.


