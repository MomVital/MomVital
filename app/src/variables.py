import json

with open('config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)

hb_analysis_template = """According to the given: {question}
    
Context: {context}
        
Answer: Let's think step by step."""
hb_input_variables = ["bpms", "week"]


hrv_analysis_template = """According to the given: {question}
    
Context: {context}
        
Answer: Let's think step by step."""
hrv_input_variables = ["sdnn", "rmssd", "pnn50", "week"]

stress_analysis_template = """According to the given: {question}
    
Context: {context}
        
Answer: Let's think step by step."""
stress_input_variables = ["stress_level", "week", "context"]

overall_analysis_template = """"""
overall_input_variables = ["stress_level", "bpms", "sdnn", "rmssd", "pnn50", "week", "context"]