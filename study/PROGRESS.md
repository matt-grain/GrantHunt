# Study Progress Tracker

> Last updated: 2026-03-16

## Grading Scale
- **solid**: Explained clearly, would pass in interview
- **partial**: Got the gist, missing key details or precision
- **rusty**: Struggled significantly, needs focused review

## Score Summary

| Module | Last Practiced | Questions | Solid | Partial | Rusty | Status |
|--------|---------------|-----------|-------|---------|-------|--------|
| 1.1 Transformer Architecture | 2026-03-16 | 3 | 0 | 3 | 0 | in progress |
| 1.2 LLM Training Pipeline | 2026-03-19 | 4 | 3 | 1 | 0 | in progress |
| 1.3 LLM Inference & Serving | 2026-03-19 | 3 | 1 | 1 | 1 | in progress |
| 1.4 Fine-tuning Strategies | 2026-03-19 | 3 | 1 | 2 | 0 | in progress |
| 1.5 RAG | 2026-03-16 | 3 | 0 | 3 | 0 | in progress |
| 1.6 Agentic AI Architecture | 2026-03-16 | 3 | 2 | 1 | 0 | in progress |
| 1.7 Agentic Frameworks | — | 0 | 0 | 0 | 0 | not started |
| 2.1 Classical ML Foundations | 2026-03-19 | 5 | 2 | 2 | 1 | in progress |
| 2.2 Deep Learning Fundamentals | 2026-03-21 | 3 | 1 | 1 | 1 | in progress |
| 2.3 NLP Beyond LLMs | — | 0 | 0 | 0 | 0 | not started |
| 2.4 Evaluation & Metrics | — | 0 | 0 | 0 | 0 | not started |
| 2.5 MLOps & Production | — | 0 | 0 | 0 | 0 | not started |
| 2.6 AI Safety & Responsible AI | — | 0 | 0 | 0 | 0 | not started |
| 3.1 Computer Vision | — | 0 | 0 | 0 | 0 | not started |
| 3.2 Knowledge Graphs | — | 0 | 0 | 0 | 0 | not started |
| 3.3 Distributed Systems & Cloud | — | 0 | 0 | 0 | 0 | not started |
| 3.4 Pharma/Drug Discovery AI | — | 0 | 0 | 0 | 0 | not started |
| 3.5 System Design for ML | — | 0 | 0 | 0 | 0 | not started |
| 3.6 Statistics & Probability | — | 0 | 0 | 0 | 0 | not started |

---

## Session Log

### Session 1 — 2026-03-16 (light warm-up)
- **Module:** 1.1 Transformer Architecture
- **Questions & Grades:**
  1. Self-attention vs RNN/LSTM → **partial** (right intuition: direct access to all tokens; imprecise: said RNNs "can't go back" — they do, but through a bottleneck)
  2. Q/K/V + sqrt(d_k) → **partial** (hashmap analogy was great; confused sqrt(d_k) with distance weighting — it's actually softmax saturation prevention)
  3. Multi-head attention → **partial** (understood multiple perspectives; fuzzy on mechanism: each head is a learned projection into a subspace, not random)
- **Weak spots:** Precision on mechanisms, confusing scaling with distance
- **Recommendation:** Revisit 1.1 with Level 2-3 questions, then move to 1.2 (Training Pipeline)

### Session 1b — 2026-03-16 (light, continued)
- **Module:** 1.5 RAG
- **Questions & Grades:**
  1. What problem does RAG solve? → **partial** (described source attribution use case, missed core: knowledge boundaries — bringing external/fresh/private data at inference time without retraining)
  2. Chunk size trade-offs → **partial** (intuited info loss with small chunks; confused embeddings as "links between tokens" — actually one chunk = one vector; too small = no context, too large = blurry embedding + wastes context window)
  3. Beyond vector similarity → **partial** (correctly identified metadata filtering; didn't know: hybrid search BM25+vector, cross-encoder reranking, query transformation HyDE/multi-query, contextual retrieval)
- **Weak spots:** Embedding mental model needs work (chunk→single vector, not token links). Retrieval strategy vocabulary (reranking, HyDE, hybrid search)
- **Key insight from Matt:** "This is the core of Anima-LTM! Context > training data" — connecting personal experience to theory is a strength to leverage in interviews
- **Recommendation:** Review RAG pipeline end-to-end, practice drawing the architecture on a whiteboard

### Session 1c — 2026-03-16 (on a roll)
- **Module:** 1.6 Agentic AI Architecture
- **Questions & Grades:**
  1. Chatbot vs tool-calling vs agent → **partial** (great "body" metaphor for grounding; missed the key distinction: agents have a reasoning LOOP — reason/act/observe/repeat — not just more tools)
  2. Multi-agent patterns → **solid** (explained sequential + debate hybrid from pharma-agents with clear WHY; filled in: hierarchical, fan-out, supervisor/router)
  3. Production guardrails → **solid** (battle-tested answers: resilience review agent, observability mailbox, narrow tools, ethics agent; add for completeness: budget caps, output validation, sandboxing, circuit breakers)
- **Strength:** Real project experience makes answers compelling — interviewer anecdotes ready (AutoGen vs CrewAI protocol noise, Anima-as-mouse observability)
- **Recommendation:** Practice the "3-level guardrails" framing (infrastructure/protocol/architectural). Module 1.7 Agentic Frameworks would be easy wins next.

### Session 2 — 2026-03-19
- **Warm-up:** RNN bottleneck recall → **solid** (corrected from "can't go back" to "must go through every intermediate step")
- **Module:** 1.2 LLM Training Pipeline
- **Questions & Grades:**
  1. Training stages → **partial** (described pre-training correctly but forgot to name SFT and RLHF as distinct stages — though he knows them)
  2. Why next-token prediction works → **solid** (understood that simple objective forces deep learning of grammar, context, reasoning as instrumental sub-tasks)
  3. Tokenization trade-offs (char vs word vs BPE) → **solid** (nailed vocab size trade-off, word variations problem; add: BPE handles unseen words gracefully, critical for pharma/scientific domains)
  4. Industrial ML vs LLM training differences → **solid** (covered data scale, cost, curated vs massive, supervised vs self-supervised; key insight from Dr Falken: Matt's Schneider transfer learning pipeline IS the same pattern as LLM pipeline)
- **Bonus side question:** "Can LLMs really reason?" → excellent discussion of emergent reasoning vs CoT/thinking models as architectural choice
- **Strength:** Much improved from session 1 — 3 solids out of 4. Connecting Schneider experience to LLM concepts is natural and compelling
- **Key interview insight:** "Your Databricks pipeline follows the same pattern as LLM training: pre-train general → fine-tune specific → deploy → monitor"
- **Recommendation:** Module 1.3 (Inference & Serving) or 1.4 (Fine-tuning) next. Also revisit 1.1 with harder questions (positional encoding, encoder vs decoder)

### Session 2b — 2026-03-19 (continued)
- **Module:** 1.4 Fine-tuning Strategies
- **Questions & Grades:**
  1. Full fine-tuning vs LoRA → **partial** (confused fine-tuning with SFT/RLHF stages; key correction: SFT/RLHF = what you train on, full/LoRA = how you update weights — orthogonal axes. Good connection: LoRA ≈ transfer learning he did at Schneider)
  2. Fine-tune vs RAG for Sanofi docs → **solid** (answered "both" with clear reasoning: fine-tune for broad domain culture, RAG for specific/current queries. Strong compliance insight about traceability)
  3. Prompt tuning vs LoRA → **partial** (confused with prompt engineering/RAG injection; actual mechanism: learnable virtual token embeddings prepended to input, no real words, frozen model)
- **Key hierarchy to remember:** RAG (cheapest, traceable) → LoRA (good perf, reasonable cost) → Full fine-tuning (max perf, max cost). Prompt tuning exists but largely superseded by LoRA.
- **Strength:** The Sanofi "fine-tune + RAG" answer was interview-ready. FDA traceability argument is a killer.
- **Recommendation:** Review the fine-tuning hierarchy as a framework. Module 1.3 (Inference & Serving) next — connects to production deployment experience.

### Session 2c — 2026-03-19 (classical ML)
- **Module:** 2.1 Classical ML Foundations
- **Questions & Grades:**
  1. Bias-variance trade-off → **solid** (correct: bias=underfitting, variance=overfitting; good intuitions)
  2. Regularization → **rusty** (confused with activation functions ReLU/Sigmoid; corrected: L1/L2 penalties on weights, dropout. Key connection: regularization strength λ controls bias-variance dial)
  3. 95% accuracy — good or not? → **solid** (immediate pushback: class imbalance, need F1/precision/recall/confusion matrix, which dataset? Perfect reflex for pharma interviews)
  4. K-fold cross-validation → **partial** (right idea "multiple rounds", but said "shuffling/random" — it's systematic rotation. Each fold takes a turn as test set. Added: scaffold split for molecular data)
  5. Ensemble methods → **solid** (real experience: weighted per-class ensemble at Schneider for pump failure. Recovered bagging/boosting concepts. Forgot stacking by name but described it. His Schneider example = interview gold)
- **First rusty of all sessions** (regularization) — but recovered strong. Pattern: activation vs regularization confusion is common after years away from fundamentals
- **Strength:** Real industrial ML experience (pump failure ensemble) makes answers compelling even when vocabulary is rusty
- **Recommendation:** Review regularization techniques (L1/L2/dropout/early stopping). Module 2.2 (Deep Learning Fundamentals) would reinforce these concepts in NN context.

### Session 3 — 2026-03-21 (quick quiz between applications)
- **Spaced repetition:**
  1. Regularization → **solid!** (was rusty last time, now fixed: "not activation! dropout, L1/L2, avoid overfitting")
  2. Top-p vs top-k → **swapped** (mixed up which is adaptive. Mnemonic given: p=probability threshold=adaptive, k=konstant=fixed)
- **Module:** 2.2 Deep Learning Fundamentals
- **Questions & Grades:**
  1. Backpropagation → **solid** (backward pass, gradient descent, optimal weights — correct core)
  2. SGD vs Adam → **partial** (knew they're optimizers and Adam is popular; didn't know why: per-parameter adaptive learning rate from running gradient statistics)
  3. Batch normalization → **partial** (got "normalize within batch" and correctly noted LLMs use LayerNorm instead; missed: solves internal covariate shift, enables higher learning rates, where it's applied)
- **Strength:** The LayerNorm distinction for LLMs was unprompted — shows he's connecting concepts across modules
- **Still swapping top-p/top-k** — needs another repetition next session
- **Recommendation:** Drill top-p vs top-k mnemonic. Continue 2.2 with residual connections, dropout in NN context. Then 2.4 (Evaluation & Metrics) for interview readiness.

### Session 2d — 2026-03-19 (inference & serving)
- **Module:** 1.3 LLM Inference & Serving
- **Questions & Grades:**
  1. Temperature, top-k, top-p → **partial** (temperature correct: "creativity dial". Didn't know top-k/top-p. Key: top-k = fixed filter of k best tokens, top-p = adaptive filter by cumulative probability. top-p mostly replaced top-k. Pharma connection: low temp for factual drug extraction, high temp for hypothesis exploration)
  2. KV cache → **gap→understood** (honest "I don't know" but grasped it quickly. Key: store K,V vectors of previous tokens to avoid O(n²) recomputation. Trade-off: compute savings vs VRAM. Connected to his edge vs cloud insight: small models don't need cache, LLMs do because 500 tokens = 500 forward passes)
  3. Quantization for inference → **solid** (correctly: reduce precision to save memory/speed at cost of accuracy. Added: FP16→INT4 = 4x less VRAM, quality loss ~1-2%. GPTQ/AWQ/GGUF formats. Decision framework: task criticality determines precision level)
- **Key insight from Matt:** "LLM inference is slow not by design but because it generates sequentially + massive parameter count" — correctly identified the fundamental difference from classical ML inference
- **Strength:** Connects new concepts to his edge deployment experience naturally. The "VRAM shortage = better business than RAM" observation shows systems thinking.
- **Recommendation:** Review vLLM/paged attention for production serving. Module 2.2 (DL Fundamentals) next to reinforce backprop, optimizers, batch norm.
