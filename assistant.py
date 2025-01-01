import speech_recognition as sr
import subprocess
import asyncio

async def query_ollama(prompt):
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
            print(f"Error running Ollama: {stderr.decode()}")
            return "Error communicating with Ollama."
    except Exception as e:
        print(f"Exception occurred: {e}")
        return "Error communicating with Ollama."

async def listen_for_query():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for your query...")
        audio = recognizer.listen(source)
        user_query = recognizer.recognize_google(audio)
        print(f"You said: {user_query}")
        return user_query

async def main():
    user_query = await listen_for_query()
    print("Querying Ollama...")
    response = await query_ollama(user_query)
    print(f"Ollama's response: {response}")

if __name__ == "__main__":
    asyncio.run(main())
