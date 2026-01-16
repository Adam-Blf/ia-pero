# L'IA Pero

![Status](https://img.shields.io/badge/status-in%20development-yellow)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.35+-red)

Explorez la similarite semantique entre vos textes grace aux embeddings Sentence-Transformers.

## Features

- [x] Interface Streamlit moderne
- [x] Support de plusieurs modeles SBERT
- [x] Matrice de similarite interactive
- [x] Detection des paires les plus similaires
- [ ] Upload de fichiers CSV/TXT
- [ ] Visualisation t-SNE/UMAP

## Installation

```bash
# Clone the repository
git clone https://github.com/Adam-Blf/ia-pero.git
cd ia-pero

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

L'application sera disponible sur http://localhost:8501

## Tech Stack

- **Python** 3.9+
- **Streamlit** >= 1.35 - Interface web interactive
- **Sentence-Transformers** >= 2.2.0 - Embeddings SBERT
- **PyTorch** >= 2.0.0 - Backend ML
- **Transformers** >= 4.34.0 - HuggingFace models
- **Pandas** - Data manipulation
- **NumPy** - Numerical operations

## Models disponibles

| Modele | Dimensions | Description |
|--------|------------|-------------|
| `all-MiniLM-L6-v2` | 384 | Rapide et leger (default) |
| `all-mpnet-base-v2` | 768 | Meilleure qualite |
| `paraphrase-multilingual-MiniLM-L12-v2` | 384 | Support multilingue |

## Project Structure

```
ia-pero/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .gitignore
├── README.md
├── src/
│   ├── __init__.py
│   ├── embeddings.py        # SBERT logic
│   └── utils.py             # Utility functions
├── data/
│   └── .gitkeep
└── .streamlit/
    └── config.toml          # Theme configuration
```

## Changelog

### 2026-01-16
- Initial project setup
- Streamlit interface with SBERT integration
- Similarity matrix visualization
- Multi-model support

## License

MIT
