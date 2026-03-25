# app.py - Entry point for HuggingFace Spaces
import sys
sys.path.insert(0, ".")

from main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
