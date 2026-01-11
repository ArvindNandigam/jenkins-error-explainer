from sentence_transformers import SentenceTransformer

print("Downloading model...")
MODEL = SentenceTransformer(
    "paraphrase-MiniLM-L3-v2",
    cache_folder="./model_cache"
)

print("Model cached successfully!")