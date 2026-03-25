from fastapi import FastAPI
from explain_error import explain_error
from langchain_rag import get_rag_chain

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Jenkins Error Explainer API running"}

@app.post("/explain")
def explain(payload: dict):
    log = payload["log_text"]
    return explain_error(log)

@app.post("/explain-rag")
def explain_with_rag(payload: dict):
    log = payload["log_text"]
    rag_chain = get_rag_chain()
    return rag_chain.explain_error(log)
