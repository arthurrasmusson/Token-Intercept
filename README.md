# vLLM-Intercept

**vLLM-Intercept** is a Python library and server that allows you to seamlessly port your existing OpenAI API-based applications to use a local vLLM server running models like `facebook/opt-125m`. This enables you to run language models locally, reducing latency and improving privacy, without extensively modifying your existing codebase.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Getting Started](#getting-started)
  - [Setting Up the vLLM Server](#setting-up-the-vllm-server)
  - [Using vllm_intercept in Your Application](#using-vllm_intercept-in-your-application)
- [Usage Example](#usage-example)
- [Directory Structure](#directory-structure)
  - [Source Code Files](#source-code-files)
    - `vllm_intercept.py`
    - `daemon_server.py`
- [Contributing](#contributing)
- [License](#license)

## Features
- **Seamless Integration:** Intercept and redirect OpenAI API calls to your local vLLM server with minimal code changes.
- **FastAPI Server Wrapper:** A daemon server that ensures the vLLM server is running and translates API requests.
- **Model Flexibility:** Run any Hugging Face-compatible model locally with vLLM.
- **Portability:** Keep your existing codebase largely unmodified by simply importing the `vllm_intercept` module.

## Prerequisites
- Python 3.8 or higher
- vLLM installed
- Required Python packages:
  - `fastapi`
  - `uvicorn`
  - `grpcio`
  - `grpcio-tools`
  - `pydantic`
  - `openai`

## Installation

### Clone the Repository

```bash
git clone --recursive-submodules https://github.com/your_username/vLLM-Intercept.git
cd vLLM-Intercept
```

### Run the Install Script
Make the install script executable and run it:

```bash
chmod +x install.sh
./install.sh
```

This script will:

Install the required Python dependencies.
Generate the gRPC code from generation_service.proto.
Set up the daemon_server.py as a systemd service named vllm_intercept.
Start the service and enable it to run on system startup.
Note: The install script must be run with appropriate permissions to create systemd service files.

### Getting Started
Using vllm_intercept in Your Application
Copy vllm_intercept.py to Your Project

Ensure vllm_intercept.py is in your project directory or accessible via your Python path.

Modify Your Application

In your Python script, replace:

```python
import openai
```
With:

```python
import vllm_intercept  # Import the interceptor
import openai
```
Note: Ensure that import vllm_intercept comes before import openai.

### Run Your Application

Run your script as you normally would. The vllm_intercept module will redirect API calls to your local vLLM server.

### Usage Example
Suppose you have the following script using OpenAI's API:

```python
import openai

openai.api_key = "your-api-key-here"

def ask_openai(question):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question}
        ]
    )
    answer = response['choices'][0]['message']['content']
    return answer

if __name__ == "__main__":
    user_question = input("Enter your question: ")
    print("Thinking...")
    answer = ask_openai(user_question)
    print(f"Assistant: {answer}")
```

To use vLLM-Intercept, modify the script as follows:

```python
import vllm_intercept  # Import the interceptor
import openai

def ask_openai(question):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # This will be mapped to "facebook/opt-125m"
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question}
        ]
    )
    answer = response['choices'][0]['message']['content']
    return answer

if __name__ == "__main__":
    user_question = input("Enter your question: ")
    print("Thinking...")
    answer = ask_openai(user_question)
    print(f"Assistant: {answer}")
```
That's it! The rest of your code remains unchanged.

Directory Structure
Your project directory should look like this:

```
vLLM-Intercept/
├── README.md
├── requirements.txt
├── install.sh
├── vllm_intercept.py
├── daemon_server.py
├── generation_service.proto
├── generation_service_pb2.py
├── generation_service_pb2_grpc.py
└── your_application.py
```

README.md: Project documentation.
requirements.txt: List of Python dependencies.
install.sh: Install script that sets up the systemd service.
vllm_intercept.py: Interceptor module to redirect API calls.
daemon_server.py: Daemon server script.
generation_service.proto: Protobuf definition file.
generation_service_pb2.py and generation_service_pb2_grpc.py: Generated gRPC code.
your_application.py: Your existing script modified to use vllm_intercept.
Source Code Files
vllm_intercept.py
Path: /vLLM-Intercept/vllm_intercept.py


daemon_server.py
Path: /vLLM-Intercept/daemon_server.py


install.sh
Path: /vLLM-Intercept/install.sh


### Contributing
Feel free to open an issue or create a pull request if you find a bug or want to add a new feature. Contributions are welcome!

### License
This project is licensed under the GPLv3 License.

### Additional Notes
Ensure All Dependencies Are Installed

The install script (install.sh) installs all required packages listed in requirements.txt.

### Starting the Daemon Server

The install script sets up daemon_server.py as a systemd service named vllm_intercept. It starts automatically on system boot and can be managed using systemctl commands:

### Check Service Status

```bash
sudo systemctl status vllm_intercept
```

### Restart the Service
```bash
sudo systemctl restart vllm_intercept
```

### Stop the Service
```bash
sudo systemctl stop vllm_intercept
```

### Logs

The service logs are stored in the working directory:

Standard Output: vllm_intercept.log
Standard Error: vllm_intercept_error.log

Testing the Setup

After setting up, test your application to ensure that it's correctly communicating with the local vLLM server.