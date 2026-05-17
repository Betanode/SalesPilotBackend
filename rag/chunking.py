from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from rank_bm25 import BM25Okapi

from typing import List, Dict
import re
import os
import pickle
import shutil

from rag.extractor import extract_text


PERSIST_DIR = "./chroma_db"
BM25_PATH = "./bm25.pkl"



embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)



def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    return text.strip()



def chunk_text(text: str, source: str) -> List[Dict]:
    text = clean_text(text)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    raw_chunks = splitter.split_text(text)

    return [
        {
            "id": f"{source}_{i}",
            "content": chunk,
            "metadata": {
                "source": source,
                "chunk_index": i
            }
        }
        for i, chunk in enumerate(raw_chunks)
    ]



def create_vector_store(chunks: List[Dict]):
    texts = [c["content"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]
    ids = [c["id"] for c in chunks]

    db = Chroma.from_texts(
        texts=texts,
        embedding=embedding_model,
        metadatas=metadatas,
        ids=ids,
        persist_directory=PERSIST_DIR
    )

    db.persist()


def load_vector_store():
    return Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embedding_model
    )



def build_and_save_bm25(chunks: List[Dict]):
    tokenized = [c["content"].split() for c in chunks]
    bm25 = BM25Okapi(tokenized)

    with open(BM25_PATH, "wb") as f:
        pickle.dump((bm25, chunks), f)


def load_bm25():
    if not os.path.exists(BM25_PATH):
        raise FileNotFoundError("BM25 index not found. Run ingestion first.")

    with open(BM25_PATH, "rb") as f:
        return pickle.load(f)



def hybrid_retrieve(query: str, k: int = 5):

    # semantic search
    db = load_vector_store()
    semantic_docs = db.similarity_search(query, k=k)

    semantic_results = [
        {
            "content": d.page_content,
            "metadata": d.metadata
        }
        for d in semantic_docs
    ]

    # keyword search
    try:
        bm25, chunks = load_bm25()

        scores = bm25.get_scores(query.split())
        top_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:k]

        keyword_results = [
            {
                "content": chunks[i]["content"],
                "metadata": chunks[i]["metadata"]
            }
            for i in top_indices
        ]
    except Exception:
        keyword_results = []

    # merge + dedup
    seen = set()
    final = []

    for r in semantic_results + keyword_results:
        key = r["content"][:100]
        if key not in seen:
            seen.add(key)
            final.append(r)

    return final[:k]



def ingest_document(file_path: str):

    
    if os.path.exists(PERSIST_DIR):
        shutil.rmtree(PERSIST_DIR)

    if os.path.exists(BM25_PATH):
        os.remove(BM25_PATH)

    
    text = extract_text(file_path)

    
    source = os.path.basename(file_path)
    chunks = chunk_text(text, source)

    
    create_vector_store(chunks)
    build_and_save_bm25(chunks)