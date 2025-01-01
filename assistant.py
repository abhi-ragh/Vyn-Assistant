import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel
from PyQt5.QtCore import QThread, pyqtSignal
import speech_recognition as sr
import subprocess
import asyncio
import re

class ListenerThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    status = pyqtSignal(str)

    def __init__(self, recognizer):
        super().__init__()
        self.recognizer = recognizer

    def run(self):
        try:
            with sr.Microphone() as source:
                self.status.emit("Listening for your query...")
                audio = self.recognizer.listen(source)
                text = self.recognizer.recognize_google(audio)
                self.finished.emit(text)
        except Exception as e:
            self.error.emit(str(e))

class ChatbotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voice Chatbot")
        self.setGeometry(100, 100, 600, 400)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        self.conversation = QTextEdit()
        self.conversation.setReadOnly(True)
        layout.addWidget(self.conversation)

        self.listen_button = QPushButton("Start Listening")
        self.listen_button.clicked.connect(self.start_listening)
        layout.addWidget(self.listen_button)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.recognizer = sr.Recognizer()

    async def get_install_commands(self, package):
        prompt = f"""Generate only the exact Ubuntu/Debian terminal commands to install {package}. Format as a single command per line with no backticks, quotes, or explanations or numbers like 1. 2.. DO NOT NUMBER THE COMMANDS UNDER ANY CIRCUMSTANCES PLEASEEEEEEEEEEEEEE JUST PRINT OUT THE EXACT COMMANDS WITH NOTHING BEFORE OR AFTER IT ONE BY ONE PLEASEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE. Example format:
wget https://example.com/package.deb
sudo dpkg -i package.deb"""                   ## A little Exaggeration because why not also use the magic word (Please) so AI Overloads will be kinder to you.
        
        process = await asyncio.create_subprocess_exec(
            "ollama", "run", "mistral", prompt,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            return []
            
        commands = []
        for line in stdout.decode().strip().split('\n'):
            line = line.strip()
            if line and not line.startswith('```') and not line.startswith('#'):
                commands.append(line)
        return commands

    async def run_command(self, command):
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return process.returncode, stdout.decode(), stderr.decode()

    async def install_package(self, package):
        commands = await self.get_install_commands(package)
        if not commands:
            return f"Failed to get installation commands for {package}"
            
        results = []
        for cmd in commands:
            results.append(f"Running: {cmd}")
            code, out, err = await self.run_command(cmd)
            if code != 0:
                results.append(f"Error: {err}")
                return "\n".join(results)
            if out:
                results.append(out)
                
        results.append(f"Finished installing {package}")
        return "\n".join(results)

    async def query_ollama(self, prompt):
        try:
            if prompt.lower().startswith("install "):
                package = prompt.split(" ", 1)[1]
                return await self.install_package(package)
                
            process = await asyncio.create_subprocess_exec(
                "ollama", "run", "mistral", prompt,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode == 0:
                return stdout.decode().strip()
            return f"Error: {stderr.decode()}"
        except Exception as e:
            return f"Error: {str(e)}"

    def start_listening(self):
        self.listen_button.setEnabled(False)
        self.listener = ListenerThread(self.recognizer)
        self.listener.finished.connect(self.handle_query)
        self.listener.error.connect(self.handle_error)
        self.listener.status.connect(self.update_status)
        self.listener.start()

    def handle_query(self, text):
        self.add_message("You", text)
        self.update_status("Processing...")
        
        async def process_query():
            response = await self.query_ollama(text)
            self.add_message("Vyn", response)
            self.update_status("")
            self.listen_button.setEnabled(True)

        asyncio.run(process_query())

    def handle_error(self, error_text):
        self.add_message("System", f"Error: {error_text}")
        self.update_status("")
        self.listen_button.setEnabled(True)

    def add_message(self, speaker, message):
        cursor = self.conversation.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(f"{speaker}: {message}\n\n")

    def update_status(self, message):
        self.status_label.setText(message)

def main():
    app = QApplication(sys.argv)
    window = ChatbotApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()