import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel
from PyQt5.QtCore import QThread, pyqtSignal
import speech_recognition as sr
import subprocess
import asyncio

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

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Conversation display
        self.conversation = QTextEdit()
        self.conversation.setReadOnly(True)
        layout.addWidget(self.conversation)

        # Listen button
        self.listen_button = QPushButton("Start Listening")
        self.listen_button.clicked.connect(self.start_listening)
        layout.addWidget(self.listen_button)

        # Status label
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # Initialize recognizer
        self.recognizer = sr.Recognizer()

    async def query_ollama(self, prompt):
        try:
            result = await asyncio.create_subprocess_exec(
                "ollama", "run", "mistral", prompt,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            if result.returncode == 0:
                return stdout.decode().strip()
            else:
                return f"Error running Ollama: {stderr.decode()}"
        except Exception as e:
            return f"Exception occurred: {e}"

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