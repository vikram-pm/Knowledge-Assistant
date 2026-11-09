# PRD: Agentic Knowledge Assistant

## Problem
Consultants and delivery managers spend ~25 minutes per lookup across SharePoint, Confluence and policy PDFs. Versions conflict, and 4 of 5 interviewees regularly end a lookup by interrupting an expert.

## Goal
One place to ask in plain language and get a short, cited answer, or a clean handoff to the right expert. Target: −40% time to answer.

## Personas
- **Priya, consultant:** 8–12 lookups a day; wants speed and a source link.
- **Marc, delivery manager:** 3–5 high-stakes lookups a day; wants citations and "I don't know" over a guess.

## Scope (MVP)
Delivery policies, playbooks, templates and anonymised case summaries. English. Out of scope: client confidential data, email, HR records, taking actions in other systems.

## Confidence tiers
| Tier | When | What the user sees |
| --- | --- | --- |
| High | Current sources fully support the answer; every claim cited | Answer, citations, source dates |
| Medium | Only old (>12 months) or archived sources | Warning first, answer, "Confirm with an expert" |
| Needs an expert | No answer, conflicting sources, or legal/contractual/regulatory | No generated answer; routed to the right team with context |

Tiers are computed by rules (source age, archive status, agreement, legal flag), not by the model's self-reported confidence.

## User stories
1. Ask in plain language: correct on 4 of 5 rephrased questions.
2. Every claim linked to its source, opening at the right section.
3. A tier badge with a one-line reason on every answer.
4. Low tier never shows a generated answer; the handoff carries the question and sources searched.
5. Thumbs-down feedback logged with query, sources and tier.

## KPIs
| Metric | Baseline | Target |
| --- | --- | --- |
| Time to answer | ~25 min | ≤ 15 min |
| Expert interruptions | 5–6 per manager per day | −30% |
| Answer relevance | n/a | ≥ 85% |
| Hallucination rate | n/a | ≤ 3% of claims |
| Citation accuracy | n/a | ≥ 95% |
| Escalation precision | n/a | ≥ 90% |

## Responsible AI
Every answer shows sources and dates; legal questions always go to a person; no personal or client-confidential data in the corpus (PIPEDA-aligned); every answer is logged for audit; stale sources are flagged.
