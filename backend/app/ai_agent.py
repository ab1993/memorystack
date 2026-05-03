#
# Copyright (c) 2026 Abhishek Sharma. All rights reserved.
# This code is part of the MemoryStack project.
# Unauthorized copying or distribution of this file via any medium is strictly prohibited.
# Proprietary and confidential.
#

import os
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class ContentAgent:
    @staticmethod
    def generate_note(topic_name: str):
        prompt = f"""
        You are an expert technical interview coach. Generate a structured revision note for the topic: "{topic_name}".
        
        CRITICAL CATEGORY: Choose ONLY between "Data Structures" or "System Design".
        
        Follow this 3-Layer Hierarchy strictly:
        Layer 1 (Gist): A simple STRING (2-3 sentence high-level summary).
        Layer 2 (Pattern): A simple STRING (When to use this, common keywords, and the core logic/trade-offs).
        Layer 3 (Challenges): A LIST of strings (3-4 highly frequent LeetCode or System Design questions).

        Return the response ONLY as a valid JSON object with these keys:
        "topic", "category", "layer_1_gist", "layer_2_pattern", "layer_3_questions"
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )

        return json.loads(response.choices[0].message.content)