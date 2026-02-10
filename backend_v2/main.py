from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to True Carbon Backend"}

@app.get("/run-phase2")
def run_analysis():
    # This runs your phase2.py script and captures the output
    result = subprocess.run(["python", "phases/phase2.py"], capture_output=True, text=True)
    
    # Return the output to the browser
    return {
        "status": "Success",
        "output": result.stdout,
        "error": result.stderr
    }