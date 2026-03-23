```
Question 1 (Level 1): 
In your own words, what problem does the self-attention mechanism solve that previous architectures (RNNs, LSTMs) couldn't handle well?
```

> going in the "past", RNN and LSTM cannot go back, no feedback mechansim, to explore the impact of previously seen words/tokens

● Grade: partial — Right intuition, but the framing needs sharpening.

  RNNs do look at the past — that's their whole point! The hidden state carries information forward. LSTMs even added gates specifically to remember longer. The real problems are:

  1. Information bottleneck: Everything about the past must squeeze through a fixed-size hidden state vector. Token 1's info gets diluted by the time you reach token 500 — like a game of telephone.
  2. No direct access: To connect "cat" (token 3) with "it" (token 450), the signal must flow through every intermediate step. Long path = vanishing gradients = lost connections.
  3. Sequential = slow: Each step depends on the previous one. Can't parallelize.

  Self-attention fixes all three by letting every token look directly at every other token in one operation. The path length between any two tokens is always 1 — no telephone game, no bottleneck.

  Analogy to remember: RNN is like reading a book and trying to remember everything by keeping a single post-it note that you update after each page. Self-attention is like spreading all pages on a table and highlighting connections
  between any two pages at once.

---
```
Question 2 (Level 1):
The attention formula is often written as Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V. What are Q, K, V conceptually, and why do we divide by sqrt(d_k)?
```

> query, key and value. Query represents the token we are looking at, key is the pointer and the value is the token itself, kind of hashmap. Softmax converts scores to percentages so I guess sqrt is used to weight the score byt based
> on the distance of the token we are looking at. The farer, the less important?

● Grade: partial — The hashmap analogy is actually excellent! Let me refine what's right and fix what's off.

  Q, K, V — your hashmap intuition is spot on:
  - Query: "What am I looking for?" (the current token asking a question)
  - Key: "What do I contain?" (each token advertising its relevance)
  - Value: "Here's my actual content" (what gets returned if the key matches)

  Just like a dictionary: Q is your search term, K is what's indexed, V is what you retrieve. The dot product QK^T computes "how well does my query match each key?" — a relevance score.

  But sqrt(d_k) has nothing to do with distance! This is a common misconception. Here's what actually happens:

  - d_k is the dimension of the key vectors (e.g., 64 or 128)
  - When you dot-product two high-dimensional vectors, the result grows proportionally to the dimension — larger d_k means larger raw scores
  - Large scores push softmax into saturation zones where gradients vanish (everything becomes 0 or 1, like a hard argmax)
  - Dividing by sqrt(d_k) rescales the scores to keep softmax in its useful, gradient-friendly range

  Analogy: Imagine grading exams on different scales — one out of 10, another out of 1000. Before comparing them, you normalize. sqrt(d_k) is that normalization so softmax doesn't freak out regardless of dimension size.

  Key takeaway for interviews: "It's a scaling factor to prevent softmax saturation as embedding dimensions grow. Without it, gradients vanish and attention becomes effectively hard rather than soft."

---
Question 3 (Level 2 — slightly harder):
Why multi-head attention instead of a single attention? What does having multiple heads actually buy you?

❯ due to the random weights, when training an attention head, it will "randomly" focus on different aspects of the sentences: the grammar, synonyms,... so using multi-head attentions retrieve the useful values of the embeddings to improve the token prediction

● Grade: partial — You've got the right idea (multiple perspectives) but the mechanism is a bit fuzzy. Let me clarify.

  What you got right: Multiple heads do capture different "aspects" of relationships between tokens. That's the core insight.

  What needs sharpening:

  It's not really about randomness. Each head operates on a different learned linear projection of Q, K, V into a smaller subspace. If your model dimension is 512 and you have 8 heads, each head works in a 64-dimensional space,
  learning its own "question to ask."

  In practice, heads specialize:
  - Head 3 might learn syntactic relationships ("what's the subject of this verb?")
  - Head 7 might learn coreference ("what does 'it' refer to?")
  - Head 1 might learn positional patterns ("what's the next word in this phrase?")

  Then the outputs of all heads are concatenated and projected back to the full dimension. The model gets a richer, multi-faceted view of relationships.

  Why not just one big attention? A single head computes one attention pattern — one weighted average. That's like looking at a painting with one lens. If "bank" needs to attend to both "river" (meaning) and "went" (grammar)
  simultaneously, a single head must compromise. Multiple heads can each capture one relationship cleanly.

  Analogy: It's like a panel of experts reviewing the same document. One focuses on legal language, another on financial figures, another on dates. Each produces a summary from their angle. Then you combine all summaries for the full
  picture. One generalist reviewer would miss nuances.

  Interview-ready sentence: "Multi-head attention lets the model jointly attend to information from different representation subspaces. Each head learns a different type of relationship — syntactic, semantic, positional — and their
  concatenation gives a richer representation than any single attention could."

---
Good session for a tired evening! Here's your calibration:

```
┌─────┬───────────────────────┬─────────┐
│  #  │       Question        │  Grade  │
├─────┼───────────────────────┼─────────┤
│ 1   │ Self-attention vs RNN │ partial │
├─────┼───────────────────────┼─────────┤
│ 2   │ Q/K/V + sqrt(d_k)     │ partial │
├─────┼───────────────────────┼─────────┤
│ 3   │ Multi-head attention  │ partial │
└─────┴───────────────────────┴─────────┘
```

Diagnosis: Your intuitions are solid — you grasp the why behind these mechanisms. What's rusty is the precision: mixing up what sqrt(d_k) does, saying RNNs "can't go back" when they do but poorly. In an interview with a data
scientist, that precision is what separates "this person understands deeply" from "this person read a blog post."

The good news: you're partial across the board, not rusty. A couple more sessions on Tier 1 and you'll be sharp.

When you're ready for the next round, just say "quiz me" or pick a module. I'd suggest:
- 1.1 again with harder questions (positional encoding, encoder vs decoder, KV cache) to lock it in
- 1.6 Agentic AI where you'll crush it given your pharma-agents work — easy confidence boost
- 2.1 Classical ML if you want to shake off the 5-year rust on basics