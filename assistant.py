import speech_recognition as sr
import subprocess
import asyncio
import PySimpleGUI as sg
import threading

class ChatbotApp:
    def __init__(self):
        # Define the layout for the GUI
        layout = [
            [sg.Multiline(size=(50, 20), key='-CONVERSATION-', disabled=True)],
            [sg.Button("Start Listening", key='-LISTEN-')],
            [sg.Text("", size=(50, 1), key='-STATUS-')]
        ]

        # Create the window
        self.window = sg.Window("Voice Chatbot", layout)
        self.recognizer = sr.Recognizer()

    async def query_ollama(self, prompt):
        """
        Send a prompt to the Ollama model (e.g., Mistral) and return the response.
        """
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
            self.update_conversation("Listening for your query...")
            audio = self.recognizer.listen(source)
            user_query = self.recognizer.recognize_google(audio)
            self.update_conversation(f"You said: {user_query}")
            return user_query

    def handle_query(self):
        user_query = self.listen_for_query()
        self.update_conversation("Querying Ollama...")
        response = asyncio.run(self.query_ollama(user_query))
        self.update_conversation(f"Ollama's response: {response}")

    def start_listening(self):
        # Run the handle_query function in a separate thread
        threading.Thread(target=self.handle_query).start()

    def update_conversation(self, message):
        # Update the conversation area with the new message
        current_text = self.window['-CONVERSATION-'].get()
        self.window['-CONVERSATION-'].update(current_text + message + "\n")
        self.window['-STATUS-'].update("")  # Clear status message

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