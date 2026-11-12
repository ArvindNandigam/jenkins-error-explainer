from fastapi import FastAPI
from pydantic import BaseModel, Field

from explain_error import explain_error
from langchain_rag import get_rag_chain

app = FastAPI()


class ExplainRequest(BaseModel):
    log_text: str = Field(..., min_length=1)


@app.get("/")
def home():
    return {
        "name": "Jenkins Error Explainer API",
        "status": "ok",
        "endpoints": ["/explain", "/explain-rag"]
    }

@app.post("/explain")
def explain(payload: ExplainRequest):
    return explain_error(payload.log_text)

@app.post("/explain-rag")
def explain_with_rag(payload: ExplainRequest):
    rag_chain = get_rag_chain()
    return rag_chain.explain_error(payload.log_text)
