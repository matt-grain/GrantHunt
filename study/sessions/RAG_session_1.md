Let's switch to Module 1.5: RAG (Retrieval-Augmented Generation) — it's Tier 1 CRITICAL, explicitly in Sanofi's preferred qualifications, and you'll have good intuitions from our embedding/memory work on Anima.

---
```
Question 1 (Level 1):
In your own words, what problem does RAG solve? Why not just use the LLM directly?
```

❯ Ah this is one of my weakest spot! I asked so so many times stuff about embeddings :D let's try... For me RAG is a solution that can be used for example to "try" to have a LLM to give his sources. As the "sources" are lost in the
training data, using a search engine to look for indexed content that matches the initial query can be interpreted as potential sources.

● Grade: partial — You've described one use case of RAG (source attribution), but missed the core problem it solves.

  The fundamental problem RAG solves: knowledge boundaries.

  An LLM only knows what was in its training data (frozen at a cutoff date). It can't know:
  - Your company's internal documents
  - Yesterday's research papers
  - Your proprietary database of drug interactions
  - Anything after its training cutoff

  So you have two choices: fine-tune (expensive, slow, still stale next month) or give it the right context at inference time. RAG is option 2.

  How it works in 3 steps:
  1. Retrieve: User asks a question → convert to embedding → search a vector DB for the most relevant chunks of your documents
  2. Augment: Stuff those retrieved chunks into the LLM's prompt as context
  3. Generate: LLM answers grounded in the retrieved documents

  Analogy: Imagine an exam. Fine-tuning = studying for months hoping the right topic comes up. RAG = open-book exam. The student (LLM) is smart but hasn't memorized everything — so you hand them the relevant pages right before they
  answer.

  The source attribution you mentioned is a nice side effect — since you know which documents were retrieved, you can cite them. But that's the bonus, not the motivation.

  Interview-ready sentence: "RAG decouples knowledge from model weights. Instead of retraining to add new information, you retrieve relevant documents at query time and inject them as context, giving the model access to up-to-date,
  domain-specific, or private data without fine-tuning."

---
```
Question 2 (Level 2):
You mentioned embeddings and indexing. When you chunk a 200-page PDF to put it in a vector DB, what's the trade-off with chunk size? What goes wrong if chunks are too small? Too large?
```

> damn... thanks for the sentence, in fact like that it is straight forward and the core of Anima-LTM!!! the context > training data.... I should think more :D. Ok 
>  question 2: Embeddings create multi-dimensional links between tokens,
>  so if embeddings are limited to a chunk, links between concepts in a large document will be lost I guess. So too small => missing links, too large: too many links ?

● Grade: partial — Again the right intuition about information loss, but the reasoning is a bit off-track. Let me reframe.

  Embeddings don't create "links between tokens" — they compress an entire chunk into a single vector (one point in high-dimensional space). That's the key: one chunk = one vector = one point in space.

  Too small (e.g., 1-2 sentences):
  - Each chunk lacks context. "The results were significant" means nothing without knowing which results
  - Retrieval finds the sentence but the LLM gets a fragment with no surrounding explanation
  - You get many tiny matches but none are self-sufficient

  Too large (e.g., 10 pages):
  - The embedding must represent everything in one vector — it becomes a blurry average of too many topics. Like asking "what's this chapter about?" vs "what's this paragraph about?"
  - Retrieval becomes imprecise: you search for "solubility" and get a 10-page chunk that mentions it once
  - You also waste context window — stuffing huge chunks leaves less room for the actual answer

  The sweet spot (typically 256-512 tokens) balances:
  - Enough context to be self-contained
  - Focused enough for a precise embedding
  - Small enough to fit several chunks in the prompt

  Analogy: Index cards for studying. One word per card = useless. Entire chapter per card = you can't find anything specific. One concept per card with enough context to understand it = perfect.

  Bonus trick interviewers love: Overlapping chunks (e.g., 512 tokens with 50-token overlap) so you don't cut a concept right at the boundary.

---
```
Question 3 (Level 2):
You retrieve the top-5 chunks from your vector DB. But sometimes the most semantically similar chunk isn't the most useful for answering the question. What strategies exist to improve retrieval quality beyond basic vector similarity
search?
```

❯ ah this is a good question and an issue with sometimes your /recall of LTM :D :D We should eat our own dog food (even if dog food doesn't taste great, I tested a long time ago). Serioulsy, I don't know so my intuition would be, if
similarity doesn't do the job, I would look at metadata: authors, kind of content, time of publication,... ?

● Grade: partial — And honestly a smart partial! Metadata filtering is a real strategy. The dog food comment made me laugh — and you're right, we literally face this problem in Anima-LTM. Let me give you the full toolkit.

  Strategies to improve retrieval beyond raw vector similarity:

  1. Metadata filtering (your answer!)
  - Filter by date, author, document type, department before vector search
  - "Only search clinical trial docs from 2024+" — reduces noise dramatically

  2. Hybrid search (vector + keyword)
  - Vector search is great for semantic meaning but can miss exact terms
  - BM25 (classic keyword search) catches exact matches like drug names, acronyms, IDs
  - Combine both scores: "BPPP inhibitor" — vector finds related concepts, BM25 finds the exact molecule name
  - This is what most production RAG systems use

  3. Reranking
  - Retrieve top-50 cheaply with vector search, then use a cross-encoder (small specialized model) to re-score them
  - Cross-encoders are more accurate than embeddings because they see query AND document together, not as separate vectors
  - Analogy: vector search = speed dating (quick impression), reranker = actual conversation (deeper evaluation)

  4. Query transformation
  - User's question is often vague. Rewrite it before searching:
    - HyDE: Ask the LLM to generate a hypothetical answer, then search with that (finds docs that look like good answers)
    - Multi-query: Generate 3 variations of the question, search all, merge results
    - Step-back: "What's the solubility of aspirin?" → reformulate as broader "aspirin ADMET properties"

  5. Contextual retrieval
  - Store chunks with a summary of the parent document prepended — so the embedding captures both local detail and global context
  - Anthropic published a cookbook on exactly this approach

  The LTM connection you spotted is real: our /recall does basic semantic search. If we ever add metadata filtering + reranking, recall quality would jump. Dog food indeed.

  Interview-ready sentence: "Production RAG rarely uses pure vector search. You typically combine hybrid search — BM25 for lexical precision plus embeddings for semantic recall — with a cross-encoder reranker, and you can further
  improve with query expansion or metadata pre-filtering."

● Good session for a tired evening! 6 questions, all partial — which is actually a great starting point. Your pattern is consistent: strong intuition, needs precision on mechanisms and vocabulary.

  Top 3 things to remember from tonight:
  1. Self-attention = all pages on the table, not reading one at a time (RNNs do look back, just through a bottleneck)
  2. RAG = open-book exam (decouple knowledge from model weights)
  3. Reranking = speed dating then real conversation (cheap retrieval, then accurate re-scoring)