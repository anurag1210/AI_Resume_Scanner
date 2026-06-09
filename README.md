# AI Resume Screener 🎯

> Upload a resume, paste a job description — get an instant AI-powered suitability analysis with scores, skill matching, and gap identification.

Built as a learning project to explore **RAG pipelines**, **vector storage**, and **LLM-powered document analysis** using Google Gemini. Demonstrates the full lifecycle of an AI document processing application — from ingestion through retrieval to generation.

---

## What It Does

**Two core capabilities:**

**1. Resume Analysis**
Upload any resume (PDF, DOCX, TXT) alongside a job description and the system returns:
- Suitability score (0–100)
- Skills match breakdown
- Experience alignment summary
- Education alignment summary
- Candidate strengths
- Profile gaps and weaknesses
- Overall two-line assessment

**2. Semantic Resume Query**
Ask natural language questions against a stored resume using RAG:
- *"What programming languages does this candidate know?"*
- *"Does this candidate have team leadership experience?"*
- *"Summarise their fintech domain experience"*

---

## Architecture

```
Resume (PDF/DOCX/TXT)
        │
        ▼
   Document Loader
   (PyPDF / Docx2txt / TextLoader)
        │
        ▼
RecursiveCharacterTextSplitter
   chunk_size=1000, overlap=200
        │
        ├──────────────────────────────────┐
        ▼                                  ▼
  Full Resume Text                   Text Chunks
        │                                  │
        ▼                                  ▼
  Gemini 2.5 Flash              Gemini Embedding-001
  Direct Analysis                    (vectors)
        │                                  │
        ▼                                  ▼
  Suitability Report             ChromaDB Vector Store
                                           │
                                           ▼
                                   MMR Retriever (k=3)
                                           │
                                           ▼
                                  Gemini 2.5 Flash
                                  Query Answering
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| LLM | Gemini 2.5 Flash | Resume analysis and query answering |
| Embeddings | Gemini Embedding-001 | Semantic vector generation |
| Vector Store | ChromaDB | Persistent vector storage and retrieval |
| Retrieval | MMR (Maximal Marginal Relevance) | Diverse, non-redundant chunk retrieval |
| Document Loading | LangChain Loaders | PDF, DOCX, TXT parsing |
| Chunking | RecursiveCharacterTextSplitter | Context-preserving document splitting |
| Framework | LangChain | Pipeline orchestration |
| UI | Streamlit | Interactive web interface |

---

## Key Design Decisions

**Why RecursiveCharacterTextSplitter?**
Resumes are unstructured documents — inconsistent formatting, varied section layouts, mixed content types. Recursive splitting with `chunk_overlap=200` preserves context across chunk boundaries, ensuring skills listed across lines and multi-sentence experience descriptions aren't fragmented.

**Why MMR retrieval?**
Maximal Marginal Relevance retrieves results that are both relevant to the query AND diverse from each other. Without MMR, a resume with repeated similar content (multiple roles with similar descriptions) would return redundant chunks — MMR prevents this, maximising information density in the context window.

**Why direct full-text analysis for scoring?**
For the suitability score, the entire resume is passed to the LLM rather than retrieved chunks. This ensures the model has complete context for a holistic assessment — chunked retrieval would risk missing important sections when making an overall judgement.

**Temperature 0.3**
Low temperature for analytical consistency — suitability scores and gap analysis should be deterministic and repeatable, not creative.

---

## Project Structure

```
resume-screener/
├── app.py                  # Streamlit UI
├── resume_analyzer.py      # Core logic — load, analyze, store, query
├── chroma_store/           # Persisted vector database
├── .env                    # API keys (not committed)
├── requirements.txt
└── README.md
```

---

## Getting Started

**Prerequisites:**
- Python 3.9+
- Google API key with Gemini access

**Installation:**
```bash
git clone https://github.com/anurag1210/resume-screener
cd resume-screener
pip install -r requirements.txt
```

**Environment setup:**
```bash
# .env file
GOOGLE_API_KEY=your_google_api_key_here
```

**Run:**
```bash
streamlit run app.py
```

---

## Core Functions

| Function | Purpose |
|---|---|
| `load_resume(file_path)` | Loads PDF, DOCX, or TXT resume into LangChain Documents |
| `analyze_resume(docs, job_description)` | Full resume vs JD comparison with structured scoring |
| `store_to_vectorstore(docs)` | Chunks, embeds, and persists resume to ChromaDB |
| `run_self_query(query)` | MMR retrieval + Gemini generation for Q&A over stored resume |

---

## What I Learned Building This

- **Document loaders** behave differently across file formats — PDF page boundaries require careful handling
- **Full-text vs RAG** — not every LLM task benefits from retrieval. Holistic scoring needs full context; targeted Q&A benefits from focused retrieval
- **MMR vs similarity search** — for documents with repetitive content, MMR dramatically improves retrieved chunk diversity
- **ChromaDB persistence** — `persist_directory` decouples ingestion from querying, enabling stateful resume storage across sessions
- **Gemini Embedding-001** — Google's latest embedding model, purpose-built for semantic similarity tasks

---

## Roadmap

- [ ] Multi-resume batch processing and comparison
- [ ] Candidate ranking across multiple resumes for one JD
- [ ] Persistent candidate database with search
- [ ] Interview question generation based on gaps identified
- [ ] Export analysis report as PDF
- [ ] Similarity search across stored candidate pool

---

## Related Projects

**[FinSight RAG](https://github.com/anurag1210/finsight)** — Production RAG system over SEC filings with dual-layer evaluation, LLM-as-judge scoring, and Docker deployment.

**[FinSight Agent](https://github.com/anurag1210/finsight-agent)** — LangGraph ReAct agent for autonomous financial research with dynamic tool selection.

---

## Author

**Anurag Gupta** — Senior Software Engineer (17 years) transitioning into AI Engineering.
Building production AI systems alongside an MSc in Data Science at the University of Exeter.

[LinkedIn](https://linkedin.com/in/anurag-gupta) · [FinSight RAG](https://github.com/anurag1210/finsight) · [FinSight Agent](https://github.com/anurag1210/finsight-agent)