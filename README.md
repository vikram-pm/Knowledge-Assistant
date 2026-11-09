# Agentic Knowledge Assistant: AI product case study

A retrieval-augmented assistant that answers delivery questions from approved documents, cites every answer, and routes risky questions to an expert. Concept project for Cognizant Canada, built end to end as an AI Product Manager.

**Case study:** https://vikram-pm.github.io/Knowledge-Assistant/
**Live prototype:** https://vikram-pm.github.io/Knowledge-Assistant/prototype/
**Product demo (73 s):** [media/demo.mp4](media/demo.mp4)

## Results
| | |
| --- | --- |
| Time to a verified answer | 43 s in usability testing, vs ~25 min today |
| Retrieval hit rate (baseline) | 100% (22/22) |
| Tier accuracy (baseline) | 84% (21/25) |
| Escalation precision / recall (baseline) | 100% / 60% |
| ROI, base case | 5.1× in year 1, payback ~2 months |

## Repo
| Folder | Contents |
| --- | --- |
| `index.html` | Case study page |
| `prototype/` | Live prototype (runs in the browser, no API key) |
| `pipeline/` | Gemini File Search pipeline, tier rules, evaluation runner, Langflow component |
| `data/` | 30-document sample knowledge base and the 25-question evaluation test set |
| `docs/` | PRD and measured baseline metrics |

## Method
Discovery (5 interviews) → PRD with confidence tiers → test set written before building → Gemini pipeline → Figma design → evaluation and usability testing → ROI model.

All documents are simulated. No client data is used.
