import sys
import os
import json

# Setup path so it can import utils and agents
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.llm_client import LLMClient
from agents.coordinator import CoordinatorAgent

try:
    print("Testing LLMClient directly...")
    result = LLMClient.generate_response(prompt="Hello", fast=True)
    print("LLM Client Result:", result)
except Exception as e:
    print("LLMClient Error:", e)

try:
    print("Testing CoordinatorAgent...")
    coord = CoordinatorAgent()
    result2 = coord.process_request("Can you give me a python quiz?")
    print("Coordinator Result:", json.dumps(result2))
except Exception as e:
    print("CoordinatorAgent Error:", e)
