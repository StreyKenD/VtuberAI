import subprocess
import platform
import time
import requests

_ollama_process = None  # Track the subprocess globally (internal use)

def is_ollama_running(host="http://localhost:11434") -> bool:
    try:
        r = requests.get(host, timeout=1)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False

def start_ollama():
    global _ollama_process

    if is_ollama_running():
        print("[✓] Ollama is already running.")
        return

    system = platform.system()
    print(f"[•] Starting Ollama on {system}...")
    try:
        if system == "Windows":
            _ollama_process = subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            _ollama_process = subprocess.Popen(["ollama", "serve"])
    except FileNotFoundError:
        print("[✗] Could not find 'ollama' command in PATH.")
        return

    # Wait up to 10 seconds for it to respond
    for _ in range(10):
        if is_ollama_running():
            print("[✓] Ollama started successfully.")
            return
        time.sleep(1)

    print("[✗] Ollama did not respond in time.")

def get_ollama_exit_code() -> int | None:
    """
    Returns the exit code of the Ollama subprocess if it has exited,
    or None if it's still running or was never started.
    """
    global _ollama_process
    if _ollama_process is None:
        return None
    return _ollama_process.poll()  # None if still running, int if finished
