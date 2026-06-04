#!/usr/bin/env python3
# AWS Bedrock streaming example
# Docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime.html

import boto3
import json
import random

bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'
)

MODEL_ID = "anthropic.claude-3-5-sonnet-20241022-v2:0"

prompts = [
    "Tell me an interesting and lesser-known fact about the Grand Theft Auto game series.",
    "Share a surprising Easter egg or hidden detail from GTA games.",
    "Tell me about a memorable mission or moment from GTA history.",
    "Share an interesting fact about GTA game development or records.",
]

request_body = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 500,
    "messages": [
        {
            "role": "user",
            "content": random.choice(prompts)
        }
    ],
    "temperature": 0.8,
    "top_p": 0.9
}

print("� Generating GTA Fact...\n").

response = bedrock_runtime.invoke_model_with_response_stream(
    modelId=MODEL_ID,
    body=json.dumps(request_body)
)

stream = response.get('body')

for event in stream:
    chunk = event.get('chunk')
    if chunk:
        chunk_data = json.loads(chunk.get('bytes').decode())
        
        if chunk_data['type'] == 'content_block_delta':
            if chunk_data['delta']['type'] == 'text_delta':
                print(chunk_data['delta']['text'], end='', flush=True)

print("\n")
