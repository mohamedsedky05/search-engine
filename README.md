# Mini Search Engine with Web Crawler

A simple end-to-end search engine project built in Python.  
It crawls web pages, builds an inverted index, ranks results using TF-IDF, and exposes search through a FastAPI backend with a minimal web interface.

This project is designed as a software engineering portfolio project demonstrating backend development, search algorithms, and system design.

---

## Features

- BFS web crawler starting from seed URLs
- HTML parser using BeautifulSoup
- Inverted index for fast term lookup
- TF-IDF ranking with title and phrase boosts
- Snippet generation with highlighted query terms
- FastAPI REST API
- Simple search UI
- SQLite database
- pytest tests
- Docker support

---

## Architecture

Pipeline:

```
Crawler → Parser → SQLite → Indexer → Ranker → API → Web UI
```

---

## Project Structure

```text
search_engine_project/

├── app/              # Main application code
│   ├── crawler/      # Web crawler
│   ├── indexing/     # Inverted index builder
│   ├── ranking/      # Ranking logic (TF-IDF)
│   ├── search/       # Search service
│   ├── templates/    # HTML templates
│   ├── static/       # CSS
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
│
├── scripts/          # CLI scripts (crawl & build index)
│   ├── crawl.py
│   └── build_index.py
│
├── tests/            # Unit tests
│
├── docs/             # Screenshots
│
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## Setup

```bash
git clone <repo>
cd search_engine_project

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```

---

## Run the pipeline

### 1. Crawl pages

```bash
python scripts/crawl.py
```

### 2. Build index

```bash
python scripts/build_index.py
```

### 3. Start the server

```bash
uvicorn app.main:app --reload
```

Open:

```
http://localhost:8000
```

---

## Screenshots

### Search page

![Search Page](docs/Screenshot-Search.png)

### Results page

![Results Page](docs/Screenshot-Results.png)

---

## Example queries

```
python
search engine
"web crawler"
python "data structure"
```

---

## API

| Endpoint | Description |
|--------|--------|
| `/` | Search page |
| `/api/search` | Search API |
| `/api/status` | System status |
| `/api/health` | Health check |

---

## Tests

```bash
pytest tests/ -v
```

---

## Future Improvements

- BM25 ranking
- robots.txt support
- stemming / lemmatization
- better UI

---

## License

Educational / portfolio project.
