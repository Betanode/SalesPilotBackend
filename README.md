# 🚀 Sales AI Coach Backend

An AI-powered backend system that simulates real-world sales coaching using **RAG (Retrieval-Augmented Generation)** and **agent-based workflows**.

---

## 🧠 Overview

This system:

* Conducts multi-turn sales conversations
* Provides feedback after every response
* Asks follow-up questions to improve user performance
* Uses document-based knowledge via RAG

---

## ⚙️ Tech Stack

* **FastAPI** – API layer
* **LangGraph** – Agent workflow orchestration
* **Anthropic Claude** – LLM for reasoning
* **ChromaDB** – Vector database
* **BM25** – Keyword-based retrieval
* **PyMuPDF + OCR** – PDF processing

---

## 🔥 Features

* 🧠 AI Sales Coach (multi-turn conversation)
* 📊 Feedback after every user response
* 🔁 Adaptive questioning using context
* 📚 Hybrid RAG (semantic + keyword search)
* 📄 PDF ingestion pipeline
* 🧩 Modular agent design

---

## 🏗️ Architecture

User Input → Agent → RAG Retrieval → LLM → Feedback + Next Question

---

## 📂 Project Structure

```
backend/
│
├── rag/
│   ├── chunking.py        # RAG pipeline (chunking + hybrid retrieval)
│   └── extractor.py       # PDF + OCR extraction
│
├── services/
│   └── llm.py             # LLM (Anthropic API)
│
├── agent/
│   └── coach.py           # LangGraph agent logic
│
├── chroma_db/             # Vector DB (ignored)
├── bm25.pkl               # BM25 index (ignored)
└── main.py                # FastAPI app (to be added)
```

---

## 🚀 Getting Started

### 1. Clone repo

```
git clone https://github.com/<your-username>/SalesPilotBackend.git
cd SalesPilotBackend
```

---

### 2. Setup environment

```
python -m venv venv
source venv/bin/activate  # mac/linux
```

---

### 3. Install dependencies

```
pip install -r requirements.txt
```

---

### 4. Add API Key

Create `.env` file:

```
ANTHROPIC_API_KEY=your_key_here
```

---

### 5. Run ingestion

```
python rag/chunking.py
```

---

## 🚀 Upcoming Features

* Multi-document support
* Memory persistence (user sessions)
* Streaming responses
* Evaluation metrics for coaching quality

---

## 👨‍💻 Author

**Abhinav Dwivedi**

