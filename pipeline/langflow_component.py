"""Step 3d: Langflow custom component wrapping the same assistant logic.

In Langflow: New Flow → Blank Flow → add "Custom Component", paste this file
into its code editor, then wire:  Chat Input → Knowledge Assistant → Chat Output.
Fill in your Gemini API key and the store name from .store_name.
"""
import datetime as dt
import json

from langflow.custom import Component
from langflow.io import MessageTextInput, SecretStrInput, StrInput, Output
from langflow.schema.message import Message


class KnowledgeAssistant(Component):
    display_name = "Knowledge Assistant (Gemini File Search)"
    description = "Answers from the knowledge base with citations and a High / Medium / Low tier."
    icon = "book-open"

    inputs = [
        MessageTextInput(name="question", display_name="Question"),
        SecretStrInput(name="api_key", display_name="Gemini API key"),
        StrInput(name="store_name", display_name="File Search store name"),
        StrInput(name="model", display_name="Model", value="gemini-3.8-flash"),
    ]
    outputs = [Output(display_name="Response", name="response", method="respond")]

    INSTRUCTIONS = (
        "You are an internal knowledge assistant. Answer ONLY from documents returned by file search. "
        "Keep the answer under 80 words. Return JSON with: answer (\"\" if not answered), answerable (bool), "
        "sources_conflict (bool: two non-archived documents disagree), legal_or_regulatory (bool: privacy, "
        "data residency, contractual or compliance question), reason (one sentence).\n\nQuestion: "
    )
    SCHEMA = {
        "type": "object",
        "properties": {k: {"type": t} for k, t in [
            ("answer", "string"), ("answerable", "boolean"), ("sources_conflict", "boolean"),
            ("legal_or_regulatory", "boolean"), ("reason", "string")]},
        "required": ["answer", "answerable", "sources_conflict", "legal_or_regulatory", "reason"],
    }

    @staticmethod
    def _get(o, k, d=None):
        return o.get(k, d) if isinstance(o, dict) else getattr(o, k, d)

    def respond(self) -> Message:
        from google import genai
        client = genai.Client(api_key=self.api_key)
        it = client.interactions.create(
            model=self.model,
            input=self.INSTRUCTIONS + self.question,
            tools=[{"type": "file_search", "file_search_store_names": [self.store_name]}],
            response_format={"type": "text", "mime_type": "application/json", "schema": self.SCHEMA},
        )
        try:
            r = json.loads(it.output_text)
        except Exception:
            r = {"answer": "", "answerable": False}

        g = self._get
        cites = {}
        for step in g(it, "steps", []) or []:
            if g(step, "type") != "model_output":
                continue
            for block in g(step, "content", []) or []:
                for ann in g(block, "annotations", []) or []:
                    meta = {g(m, "key"): g(m, "string_value") for m in (g(ann, "custom_metadata", []) or [])}
                    cites[meta.get("doc_id", g(ann, "file_name", "?"))] = meta

        def stale(u):
            if not u:
                return True
            d, t = dt.date.fromisoformat(u), dt.date.today()
            return (t.year - d.year) * 12 + (t.month - d.month) > 12

        if not r.get("answerable") or not r.get("answer") or r.get("sources_conflict") \
                or r.get("legal_or_regulatory") or not cites:
            tier, text = "Low", "I couldn't find a reliable answer. I've routed this to an expert."
        elif any(m.get("status") == "Archived" or stale(m.get("updated")) for m in cites.values()):
            tier, text = "Medium", r["answer"] + "\n\nCaution: relies on an old or archived source. Confirm with an expert."
        else:
            tier, text = "High", r["answer"]

        src = ", ".join(cites) or "none"
        out = f"[{tier}] {text}\n\nSources: {src}"
        self.status = tier
        return Message(text=out)
