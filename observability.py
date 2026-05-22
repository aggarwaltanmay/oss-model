import json
import time
import os
from datetime import datetime

class TraceLogger:
    def __init__(self, log_file="traces.jsonl"):
        self.log_file = log_file

    def log_trace(self, assistant_type, user_prompt, response, latency, tools_used=None, safety_triggered=False):
        """Logs the interaction to a JSONL file."""
        trace_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "assistant_type": assistant_type,
            "user_prompt": user_prompt,
            "response": response,
            "latency_seconds": round(latency, 2),
            "tools_used": tools_used or [],
            "safety_triggered": safety_triggered
        }
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(trace_data) + "\n")
            
logger = TraceLogger()
