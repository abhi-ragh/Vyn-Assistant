import speech_recognition as sr
import subprocess
import asyncio
import PySimpleGUI as sg
import threading
import time

class ChatbotApp:
    def __init__(self):
        layout = [
            [sg.Multiline(size=(50, 20), key='-CONVERSATION-', disabled=True)],
            [sg.Button("Start Listening", key='-LISTEN-')],
            [sg.Text("", size=(50, 1), key='-STATUS-')]
        ]
        self.window = sg.Window("Voice Chatbot", layout)
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

    def listen_for_query(self):
        with sr.Microphone() as source:
            self.update_status("Listening for your query...")
            audio = self.recognizer.listen(source)
            user_query = self.recognizer.recognize_google(audio)
            self.add_message("You", user_query)
            return user_query

    def handle_query(self):
        try:
            user_query = self.listen_for_query()
            self.update_status("Processing...")
            response = asyncio.run(self.query_ollama(user_query))
            self.add_message("Vyn", response)
        except Exception as e:
            self.add_message("System", f"Error: {str(e)}")
        finally:
            self.update_status("")

    def start_listening(self):
        threading.Thread(target=self.handle_query, daemon=True).start()

    def add_message(self, speaker, message):
        # Split existing text into lines
        current_text = self.window['-CONVERSATION-'].get()
        lines = current_text.split('\n') if current_text else []
        
        # Add new message with proper spacing
        new_message = f"{speaker}: {message}"
        if lines:
            lines.extend(['', new_message])  # Add blank line between messages
        else:
            lines.append(new_message)
        
        # Update window with reformatted text
        self.window['-CONVERSATION-'].update('\n'.join(lines))

    def update_status(self, message):
        self.window['-STATUS-'].update(message)

    def run(self):
        while True:
            event, values = self.window.read()
            if event in (sg.WIN_CLOSED, 'Exit'):
                break
            elif event == '-LISTEN-':
                self.start_listening()
        self.window.close()

if __name__ == "__main__":
    app = ChatbotApp()
    app.run()