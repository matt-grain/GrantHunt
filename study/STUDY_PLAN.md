# Interview Study Plan — AI/ML Lead (Agentic AI Systems)

> Tailored for: Sanofi AI-ML Lead & Senior Scientist roles (and similar AI Lead positions)
> Created: 2026-03-16
> Method: Interactive Socratic quizzing with spaced repetition

---

## How It Works

1. **Pick a module** (or let Claude pick based on weak spots)
2. **Claude asks 3-5 questions** per session, increasing difficulty
3. **You answer in your own words** (FR or EN)
4. **Claude grades**: `solid` / `partial` / `rusty` — corrects, adds analogies
5. **Progress tracked** in `PROGRESS.md`
6. **Cheat sheets** generated per module in `cheatsheets/`

---

## Module Map

### Tier 1 — Must Nail (asked in 90% of AI Lead interviews)

| # | Module | Topics | Priority |
|---|--------|--------|----------|
| 1.1 | **Transformer Architecture** | Self-attention, multi-head attention, positional encoding, encoder/decoder, KV cache | CRITICAL |
| 1.2 | **LLM Training Pipeline** | Pre-training, SFT, RLHF/DPO, tokenization (BPE/SentencePiece), scaling laws | CRITICAL |
| 1.3 | **LLM Inference & Serving** | Temperature, top-k/p, beam search, KV cache, quantization (GPTQ/AWQ/GGUF), batching | CRITICAL |
| 1.4 | **Fine-tuning Strategies** | Full fine-tuning, LoRA/QLoRA, adapters, prompt tuning, when to use what | CRITICAL |
| 1.5 | **RAG (Retrieval-Augmented Generation)** | Embeddings, vector DBs, chunking, retrieval strategies, reranking, hybrid search | CRITICAL |
| 1.6 | **Agentic AI Architecture** | Tool calling, ReAct, planning/reasoning, memory systems, multi-agent patterns | CRITICAL |
| 1.7 | **Agentic Frameworks** | LangChain/LangGraph, CrewAI, AutoGen — architecture, trade-offs, when to use | CRITICAL |

### Tier 2 — Strong Differentiator (asked in 60% of interviews)

| # | Module | Topics | Priority |
|---|--------|--------|----------|
| 2.1 | **Classical ML Foundations** | Bias/variance, regularization, cross-validation, ensemble methods, metrics | HIGH |
| 2.2 | **Deep Learning Fundamentals** | Backprop, optimizers (Adam/SGD), batch norm, dropout, residual connections | HIGH |
| 2.3 | **NLP Beyond LLMs** | Word embeddings, BERT vs GPT, sequence models, NER, text classification | HIGH |
| 2.4 | **Evaluation & Metrics** | Classification (AUC, F1, precision/recall), regression (RMSE, MAE), LLM evals (BLEU, ROUGE, human eval) | HIGH |
| 2.5 | **MLOps & Production** | Model serving, monitoring, drift detection, CI/CD for ML, experiment tracking | HIGH |
| 2.6 | **AI Safety & Responsible AI** | Hallucination mitigation, guardrails, bias, explainability, pharma compliance | HIGH |

### Tier 3 — Nice to Have (shows depth)

| # | Module | Topics | Priority |
|---|--------|--------|----------|
| 3.1 | **Computer Vision** | CNNs, ResNet, object detection (YOLO/RCNN), segmentation, ViT | MEDIUM |
| 3.2 | **Knowledge Graphs & Ontologies** | Graph DBs, biomedical ontologies, reasoning over graphs | MEDIUM |
| 3.3 | **Distributed Systems & Cloud** | GPU clusters, distributed training, cloud architecture (AWS/Azure/GCP) | MEDIUM |
| 3.4 | **Pharma/Drug Discovery AI** | ADMET, molecular representations (SMILES/fingerprints), clinical trial optimization | MEDIUM |
| 3.5 | **System Design for ML** | End-to-end ML system design, data pipelines, feature stores, A/B testing | MEDIUM |
| 3.6 | **Statistics & Probability** | Distributions, Bayesian thinking, hypothesis testing, causal inference | MEDIUM |

---

## Session Format

### Warm-up (2-3 min)
- 1 quick recall question from a previous session (spaced repetition)

### Main (15-25 min)
- 3-5 questions on the current module, escalating difficulty:
  - **Level 1:** Define/explain the concept
  - **Level 2:** Compare/contrast or explain trade-offs
  - **Level 3:** Apply to a scenario (e.g., "your pharma-agents project needs X, how?")

### Cool-down
- Summary of weak spots
- Cheat sheet update
- Next session recommendation

---

## Existing Materials

| Resource | Covers |
|----------|--------|
| `docs/1 Computer Science.pptx` | CS fundamentals |
| `docs/2 Machine Learning General.pptx` | ML basics |
| `docs/3 Fundamentals for CV and DL.pptx` | CV + DL foundations |
| `docs/4 Selected Topics in CV and DL.pptx` | Advanced CV/DL |
| `docs/5 Large Language Models and Related.pptx` | LLMs |
| `docs/LLMInterviewQuestions.md` | 50 LLM interview Q&A |
| `docs/foundations_of_llm.pdf` | LLM foundations reference |
| `docs/BuildaLargeLanguageModel.epub` | Raschka's LLM book |
| `jobs/Sanofi-AI-ML-Lead/CONCEPT.md` | Pharma-agents project context |
| `jobs/Sanofi-AI-ML-Lead/agentic_frameworks_comparison.md` | Framework trade-offs |

---

## Quick Start

> "Hey Claude, let's study **module 1.1**" or "Quiz me on transformers"
> "I'm rusty on X" → Claude picks relevant module
> "Review session" → Claude picks weakest modules from PROGRESS.md
