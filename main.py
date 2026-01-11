from fastapi import FastAPI
from explain_error import explain_error

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Jenkins Error Explainer API running"}

@app.post("/explain")
def explain(payload: dict):
    log = payload["log_text"]
    return explain_error(log)
