"""Step 3b: the knowledge assistant.

ask(question) returns the answer, its citations and a confidence tier:
  High   - every cited source is current (updated within 12 months, not archived)
  Medium - the answer relies on a source that is old or archived
  Low    - escalate: no answer found, sources conflict, legal/regulatory question,
           or the model gave an answer with no citations

The tier is decided by rules in code, not by the model's own sense of confidence.

Try it:  python assistant.py "What's the hotel limit in Toronto?"
"""
import datetime as dt, json, pathlib, sys
from google import genai
from config import MODEL, STORE_FILE, STALE_AFTER_MONTHS

client = genai.Client()

INSTRUCTIONS = """You are an internal knowledge assistant for consultants and delivery managers.
Answer ONLY from the documents returned by file search. Never use outside knowledge.
Keep the answer under 80 words, in plain language.

Return JSON with these fields:
- answer: the answer, or "" if the documents don't answer the question
- answerable: true only if the retrieved documents clearly answer the question
- sources_conflict: true if two retrieved documents give different rules for the same thing
  and neither is marked Archived
- legal_or_regulatory: true if the question is about privacy law, data residency,
  contractual commitments or regulatory compliance
- reason: one short sentence explaining the above

Question: """

SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "answerable": {"type": "boolean"},
        "sources_conflict": {"type": "boolean"},
        "legal_or_regulatory": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "required": ["answer", "answerable", "sources_conflict", "legal_or_regulatory", "reason"],
}


def _get(obj, key, default=None):
    """Read a field from an SDK object or a plain dict."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _citations(interaction):
    """Collect unique cited documents with their metadata from the response annotations."""
    seen = {}
    for step in _get(interaction, "steps", []) or []:
        if _get(step, "type") != "model_output":
            continue
        for block in _get(step, "content", []) or []:
            for ann in _get(block, "annotations", []) or []:
                if _get(ann, "type") not in (None, "file_citation"):
                    continue
                meta = {}
                for m in _get(ann, "custom_metadata", []) or []:
                    meta[_get(m, "key")] = _get(m, "string_value") or _get(m, "numeric_value")
                name = _get(ann, "file_name", "")
                doc_id = meta.get("doc_id") or name.split(" ")[0]
                seen[doc_id] = {
                    "doc_id": doc_id,
                    "title": name,
                    "status": meta.get("status", "Unknown"),
                    "updated": meta.get("updated", ""),
                }
    return list(seen.values())


def _is_stale(updated, today=None):
    if not updated:
        return True
    today = today or dt.date.today()
    d = dt.date.fromisoformat(updated)
    months = (today.year - d.year) * 12 + (today.month - d.month)
    return months > STALE_AFTER_MONTHS


def score_tier(result, citations):
    """The escalation rules from the PRD. Returns (tier, reason)."""
    if result.get("sources_conflict"):
        return "Low", "Sources disagree, so an expert should confirm."
    if result.get("legal_or_regulatory"):
        return "Low", "Legal or regulatory question, so an expert should confirm."
    if not result.get("answerable") or not result.get("answer"):
        return "Low", "No reliable answer in the knowledge base."
    if not citations:
        return "Low", "The answer had no citations, so it was withheld."
    weak = [c for c in citations if c["status"] == "Archived" or _is_stale(c["updated"])]
    if weak:
        ids = ", ".join(c["doc_id"] for c in weak)
        return "Medium", f"Relies on an old or archived source ({ids}). Confirm before using."
    return "High", "Answered from current sources."


def ask(question):
    store = pathlib.Path(STORE_FILE).read_text().strip()
    interaction = client.interactions.create(
        model=MODEL,
        input=INSTRUCTIONS + question,
        tools=[{"type": "file_search", "file_search_store_names": [store]}],
        response_format={"type": "text", "mime_type": "application/json", "schema": SCHEMA},
    )
    try:
        result = json.loads(interaction.output_text)
    except (json.JSONDecodeError, TypeError):
        result = {"answer": "", "answerable": False, "sources_conflict": False,
                  "legal_or_regulatory": False, "reason": "Could not parse model output."}
    citations = _citations(interaction)
    tier, why = score_tier(result, citations)
    return {
        "question": question,
        "tier": tier,
        "tier_reason": why,
        # Low tier never shows a generated answer (PRD user story US4)
        "answer": result["answer"] if tier != "Low" else "",
        "citations": citations,
        "model_reason": result.get("reason", ""),
    }


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "What's the hotel limit per night in Toronto?"
    print(json.dumps(ask(q), indent=2, ensure_ascii=False))
