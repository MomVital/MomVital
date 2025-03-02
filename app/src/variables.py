import json

with open('config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)

hb_analysis_template = """
According to the given mom's heart beat: {bpms},
give me some suggestions.

Current pregnancy week: {week}

Answer: Let's think step by step within 50 words.
"""
hb_input_variables = ["bpms", "week"]


hrv_analysis_template = """
According to the given sdnn: {sdnn}, rmssd: {rmssd} and pnn50: {pnn50},
give me some suggestions.

Current pregnancy week: {week}

HRV (Heart Rate Variability) metrics reference:
- sdnn: {sdnn} ms (Normal: 50-150 ms; &lt;50 ms indicates high stress or poor autonomic function)
- rmssd: {rmssd} ms (Normal: 20-75 ms; &lt;20 ms suggests increased stress or fatigue)
- pnn50: {pnn50}% (Normal: &gt;3%; &lt;3% suggests reduced parasympathetic activity and higher stress)

Answer: Analyze the HRV results but just give a conclusion of them. Don't analyze the specific metrics. Let's think step by step within 50 words.
"""
hrv_input_variables = ["sdnn", "rmssd", "pnn50", "week"]

stress_analysis_template = """
According to the given stress level: {stress_level},
give me some suggestions.

Current pregnancy week: {week}
average stress level = 60.

Context: {context}

Answer: Let's think step by step within 50 words.
"""
stress_input_variables = ["stress_level", "week", "context"]

overall_analysis_template = """
Based on the provided physiological data and current pregnancy week, provide concise and informative suggestions on four aspects: stress management, physical activity, nutrition, and sleep. The output of each suggestion should be within 50 words. Present the output in JSON format with keys for each aspect (e.g., "stress_management", "physical_activity", "nutrition", "sleep").

Input data:
- Stress level: {stress_level}
- Heartbeat (bpm): {bpms}
- RMSSD: {rmssd}
- PNN50: {pnn50}
- SDNN: {sdnn}
- Current pregnancy week: {week}

HRV (Heart Rate Variability) metrics reference:
- sdnn: {sdnn} ms (Normal: 50-150 ms; &lt;50 ms indicates high stress or poor autonomic function)
- rmssd: {rmssd} ms (Normal: 20-75 ms; &lt;20 ms suggests increased stress or fatigue)
- pnn50: {pnn50}% (Normal: &gt;3%; &lt;3% suggests reduced parasympathetic activity and higher stress)

Context:
{context}
'''
Output the suggestions in JSON format:
```json
{{
  'stress_management': '',
  'physical_activity': '',
  'nutrition': '',
  'sleep': ''
}}
```"""
overall_input_variables = ["stress_level", "bpms", "sdnn", "rmssd", "pnn50", "week", "context"]
