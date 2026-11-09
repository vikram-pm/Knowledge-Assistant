"""Step 3a: create a Gemini File Search store and index the 30 documents.

Each document is tagged with metadata (doc_id, type, status, updated) so the
assistant can tell current, old and archived sources apart when it scores confidence.

Run once:  python setup_store.py
"""
import pathlib, re, time
from google import genai
from config import EMBEDDING_MODEL, STORE_DISPLAY_NAME, STORE_FILE

client = genai.Client()
CORPUS = pathlib.Path(__file__).parent / "corpus"

def read_header(text):
    def field(name):
        m = re.search(rf"^{name}:\s*(.+)$", text, re.M)
        return m.group(1).strip() if m else ""
    title = text.splitlines()[0].lstrip("# ").strip()
    updated = field("Last updated")                      # e.g. 2026-04-15
    return {
        "doc_id": field("Document ID"),
        "title": title,
        "type": field("Type"),
        "status": field("Status"),                        # Current | Archived
        "updated": updated,
        "updated_num": int(updated.replace("-", "")[:6]),  # 202604, for filtering
    }

store = client.file_search_stores.create(
    config={"display_name": STORE_DISPLAY_NAME, "embedding_model": EMBEDDING_MODEL}
)
print("Created store:", store.name)

for path in sorted(CORPUS.glob("*.md")):
    meta = read_header(path.read_text(encoding="utf-8"))
    display = f'{meta["doc_id"]} · {meta["title"]}'      # shown in citations
    uploaded = client.files.upload(
        file=str(path), config={"display_name": display, "mime_type": "text/markdown"}
    )
    op = client.file_search_stores.import_file(
        file_search_store_name=store.name,
        file_name=uploaded.name,
        config={"custom_metadata": [
            {"key": "doc_id", "string_value": meta["doc_id"]},
            {"key": "type", "string_value": meta["type"]},
            {"key": "status", "string_value": meta["status"]},
            {"key": "updated", "string_value": meta["updated"]},
            {"key": "updated_num", "numeric_value": meta["updated_num"]},
        ]},
    )
    while not op.done:
        time.sleep(3)
        op = client.operations.get(op)
    print("Indexed", display)

pathlib.Path(STORE_FILE).write_text(store.name)
print(f"\nDone. Store name saved to {STORE_FILE}")
