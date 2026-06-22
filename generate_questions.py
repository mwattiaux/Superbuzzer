import sys
import json
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv('openai_key'))

def generate_quiz(count, subject):
    schema = {
        "type": "object",
        "properties": {
            "questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["question", "choices", "valid"],
                    "properties": {
                        "question": {"type": "string"},
                        "choices": {
                            "type": "array", 
                            "minItems": 4, 
                            "maxItems": 4, 
                            "items": {"type": "string"}
                        },
                        "valid": {"type": "string"}
                    },
                    "additionalProperties": False
                }
            }
        },
        "required": ["questions"],
        "additionalProperties": False
    }

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Generate {count} quizz questions with the following subject : {subject}"}],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "quiz", "schema": schema, "strict": True}
        }
    )
    return json.loads(completion.choices[0].message.content)
