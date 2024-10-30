# daemon_server.py

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import time
import os
import sys
import grpc
import generation_service_pb2
import generation_service_pb2_grpc
import uuid
import socket

app = FastAPI()

# Pydantic models for request and response
class CompletionRequest(BaseModel):
    model: str = "facebook/opt-125m"
    prompt: str
    max_tokens: int = 16
    temperature: float = 1.0
    top_p: float = 1.0
    n: int = 1
    stream: bool = False
    logprobs: int = None
    stop: list = None  # Accommodate multiple stop tokens
    echo: bool = False
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0

# Check if vLLM server is running on port 8081
def is_vllm_running(port=8081):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(1)
            s.connect(('localhost', port))
            return True
        except socket.error:
            return False

# Start the vLLM server
def start_vllm_server():
    # Command to start the vLLM server
    command = [
        sys.executable,  # Use the same Python interpreter
        '-m', 'vllm.entrypoints.api_server',
        '--model', 'facebook/opt-125m',
        '--port', '8000',  # REST API port (not used here)
        '--grpc-port', '8081',
    ]

    # Start the server as a subprocess
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid  # Ensure the process is properly managed
    )

    return process

# Ensure vLLM server is running, start it if not
def ensure_vllm_server_running():
    if not is_vllm_running():
        print("vLLM server not running. Starting vLLM server...")
        process = start_vllm_server()
        # Wait a bit to ensure the server has time to start
        time.sleep(5)
        # Check again if the server is running
        if not is_vllm_running():
            print("Failed to start vLLM server.")
            sys.exit(1)
        else:
            print("vLLM server started.")
        return process
    else:
        print("vLLM server is already running.")
        return None  # No need to return a process if already running

# Map the OpenAI API parameters to the vLLM gRPC request
def map_request_to_grpc(request: CompletionRequest):
    # Prepare the stop tokens
    stop_sequences = request.stop if request.stop else []
    if isinstance(stop_sequences, str):
        stop_sequences = [stop_sequences]

    # Create the GenerationRequest for vLLM
    gen_request = generation_service_pb2.GenerationRequest(
        prompt=request.prompt,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        top_p=request.top_p,
        num_generations=request.n,
        echo=request.echo,
    )

    # Set stop sequences if any
    gen_request.stop_sequences.extend(stop_sequences)

    # Map penalties if supported by vLLM
    # gen_request.presence_penalty = request.presence_penalty
    # gen_request.frequency_penalty = request.frequency_penalty

    return gen_request

# Endpoint for completions
@app.post("/v1/completions")
async def completions(request: CompletionRequest):
    try:
        # Ensure vLLM server is running
        ensure_vllm_server_running()

        # Connect to the gRPC server
        channel = grpc.insecure_channel('localhost:8081')
        stub = generation_service_pb2_grpc.GenerationServiceStub(channel)

        # Map the request to gRPC
        gen_request = map_request_to_grpc(request)

        # Handle streaming or non-streaming responses
        if request.stream:
            # Implement streaming response if needed
            raise HTTPException(status_code=501, detail="Streaming not implemented.")
        else:
            # Send the request and get the response
            gen_response = stub.Generate(gen_request)

            # Prepare the choices list
            choices = []
            for i, generation in enumerate(gen_response.responses):
                choice = {
                    "text": generation.text,
                    "index": i,
                    "logprobs": None,  # Logprobs not provided by vLLM
                    "finish_reason": None,  # Update if vLLM provides this
                }
                choices.append(choice)

            # Prepare the usage data (if available)
            usage = {
                "prompt_tokens": 0,  # Update if vLLM provides this
                "completion_tokens": 0,  # Update if vLLM provides this
                "total_tokens": 0,  # Update if vLLM provides this
            }

            # Construct the final response
            response = {
                "id": "cmpl-" + str(uuid.uuid4()),
                "object": "text_completion",
                "created": int(time.time()),
                "model": request.model,
                "choices": choices,
                "usage": usage
            }

            return response

    except grpc.RpcError as e:
        # Handle gRPC errors
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")

    except Exception as e:
        # Handle other exceptions
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Start the FastAPI server
    uvicorn.run("daemon_server:app", host="0.0.0.0", port=8000)