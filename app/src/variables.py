import json

with open('config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)

hr_analysis_template = """According to the given: {question}
    
Context: {context}
        
Answer: Let's think step by step."""
hr_input_variables = [""]


hrv_analysis_template = """According to the given: {question}
    
Context: {context}
        
Answer: Let's think step by step."""
hrv_input_variables = [""]

stress_analysis_template = """According to the given: {question}
    
Context: {context}
        
Answer: Let's think step by step."""
stress_input_variables = [""]

overall_analysis_template = """"""
overall_input_variables = [""]