# Voice Assistant with Package Installation

A PyQt5-based voice assistant that uses Ollama's Mistral model to help Linux users install packages through natural language commands.

## Features
- Voice command recognition
- Natural language package installation
- Dynamic command generation using Mistral LLM
- Real-time conversation display
- System command execution with feedback

## Requirements
- Python 3.8+
- PyQt5
- SpeechRecognition
- Ollama with Mistral model
- Linux 

## Installation
```bash
# Clone repository
git clone https://github.com/yourusername/voice-assistant.git
cd voice-assistant

# Install dependencies
pip install PyQt5 speechrecognition

# Install Ollama and Mistral model
curl https://ollama.ai/install.sh | sh
ollama pull mistral
```

## Usage
1. Launch the application:
```bash
python3 main.py
```

2. Click "Start Listening" and speak commands:
- Install packages: "install firefox"
- Ask questions: "how do I update my system?"
- Get help: "what's the best video editor for Linux?"

## Permissions
The application requires sudo privileges for package installation. Ensure your user has appropriate permissions.

## Contributing
1. Fork the repository
2. Create feature branch
3. Submit pull request

## License
MIT License