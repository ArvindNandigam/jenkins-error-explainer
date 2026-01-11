from fastapi import FastAPI
from pydantic import BaseModel
from explain_error import explain_error

app = FastAPI(title="Jenkins Error Explainer API")

class LogInput(BaseModel):
    log_text: str

@app.post("/explain")
def explain(data: LogInput):
    result = explain_error(data.log_text)
    return result
