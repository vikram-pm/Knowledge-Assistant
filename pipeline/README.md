# Pipeline (Gemini File Search)

1. `pip install -r requirements.txt`
2. Create `.env` in this folder with `GEMINI_API_KEY=your-key` (free key: https://aistudio.google.com/apikey). It's git-ignored.
3. `python setup_store.py`: index the 30 documents with metadata
4. `python assistant.py "your question"`: answer, citations, tier
5. `python run_eval.py`: run the 25-question test set into a results workbook

`langflow_component.py` is the same logic as a Langflow custom component (Chat Input → Knowledge Assistant → Chat Output).
