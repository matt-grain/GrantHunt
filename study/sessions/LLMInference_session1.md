Let's do Module 1.3 — LLM Inference & Serving. This connects directly to your production experience and every role you're applying to.

  ---
  Question 1 (Level 1):
  When an LLM generates text, it produces one token at a time. What are temperature, top-k, and top-p — and how do they affect the output?

❯ yeah.. not really, that was inference based on non-LLM models... I did not reach this point in the LLM book but let's try: temperature is to create variations in the answer, in the predicted token to simulate creativity. low
temperature, always same token for a given input. top-k/p I don't know... hard to guess.

● Grade: partial — Temperature is correct! Top-k/p are related concepts, let me connect them.

  All three control the same thing: how the model picks the next token from its probability distribution.

  After a forward pass, the model outputs a probability for every token in the vocabulary (e.g., 50,000 scores). Then:

  Temperature (your answer, correct!)
  - Divides the logits (raw scores) by T before softmax
  - T=0.1: sharp distribution → almost always picks the highest-probability token (deterministic, factual)
  - T=1.0: original distribution as trained
  - T=2.0: flattened distribution → more random, "creative", but also more nonsensical
  - Analogy: a volume knob on randomness

  Top-k (simple filter)
  - Keep only the k most probable tokens, zero out the rest, then sample
  - Top-k=1: always pick the best token (greedy decoding)
  - Top-k=50: sample from the 50 most likely tokens
  - Problem: k=50 might be too many for a confident prediction, too few for an uncertain one. It's rigid.

  Top-p (nucleus sampling) (smarter filter)
  - Keep the smallest set of tokens whose cumulative probability exceeds p
  - Top-p=0.9: keep adding tokens from most to least probable until their probabilities sum to 90%, then sample from that set
  - Adapts automatically: when the model is confident (one token has 95% probability), only 1-2 tokens are considered. When uncertain, more options stay in.
  - This is why top-p mostly replaced top-k in practice.

  How they work together in practice:
  Raw logits → temperature scaling → top-p filtering → sample

  Analogy: You're choosing a restaurant.
  - Temperature = how adventurous you feel (low = "the usual", high = "let's try anything")
  - Top-k = "only consider the 5 nearest restaurants" (rigid)
  - Top-p = "consider restaurants until I've covered 90% of the good options" (adaptive — in a food desert you consider more, in downtown Montreal you consider fewer)

  Interview-ready sentence: "Temperature controls randomness by scaling logits before softmax. Top-p dynamically selects the smallest token set covering a probability threshold, adapting to model confidence. I'd use low temperature for
   factual tasks like drug property extraction and higher temperature for hypothesis generation in an agentic context."

  That last bit — connecting to pharma use cases — is what makes it an AI Lead answer, not just a textbook answer.

  ---
  Question 2 (Level 2):
  LLM inference is notoriously slow and expensive. What is KV cache and why does it matter for performance?

❯ really good example for pharma ! I'll do my best to remember it... creativity for exploration, factual for toxity estimation :D Q2: yeah I discovered that and I was surprised as my experience with classic ML models was really
different, slow to train, really fast for inference (so the IoT Edge deployment). So I need to understand why a GPU is needed for inference... so I heard about KV cache but I don't know what is it. Not rusty, worse, a gap :D

● Not rusty — a gap! Honest and good to identify. Let me fill it. And your observation about classical ML (slow train, fast inference) vs LLMs (slow both) is the perfect starting point.

  Why LLM inference needs a GPU:

  Classical ML: inference = one forward pass through a small model. Done.

  LLM generating 500 tokens = 500 sequential forward passes through a billion-parameter model. Each token depends on the previous one. You can't parallelize generation — it's inherently sequential.

  Now, the KV cache problem:

  Remember self-attention: every token attends to every previous token using Q, K, V matrices.

  When generating token #500, the model needs the K and V vectors for all 499 previous tokens to compute attention. Without caching:

  Token 1: compute K,V for [1]                    → 1 computation
  Token 2: recompute K,V for [1,2]                 → 2 computations
  Token 3: recompute K,V for [1,2,3]               → 3 computations
  ...
  Token 500: recompute K,V for [1,2,...,500]        → 500 computations

  Total: 1+2+3+...+500 = 125,000 computations (O(n²))

  With KV cache:

  Token 1: compute K,V for [1], STORE in cache
  Token 2: compute K,V for [2] only, append to cache, attend to [1,2]
  Token 3: compute K,V for [3] only, append to cache, attend to [1,2,3]
  ...
  Token 500: compute K,V for [500] only, read cache for [1..499]

  Total: 500 computations (O(n))

  KV cache = store the K and V vectors of all previous tokens in GPU memory so you never recompute them.

  Trade-off: you save massive computation but eat GPU VRAM. For a 70B model with a 128K context window, the KV cache alone can be 20-40GB. That's why long contexts are expensive — it's not just the model weights, it's the cache growing
   with every token.

  Analogy: Writing an essay by hand. Without KV cache = re-reading the entire essay from the beginning before writing each new word. With KV cache = keeping a running summary on a side notepad that you just glance at. Much faster, but
  the notepad takes up desk space (VRAM).

  This connects to your edge vs cloud insight: Your Schneider models were small (MBs), inference was a single forward pass — no cache needed, runs on a gateway. LLMs are massive, generate sequentially, need a growing cache — that's why
   they need GPU servers, not edge devices.

  Interview-ready sentence: "KV cache stores previously computed key and value vectors during autoregressive generation, avoiding O(n²) recomputation. It's the fundamental trade-off of LLM serving: compute savings vs VRAM usage.
  Techniques like GQA (grouped-query attention) and paged attention (vLLM) optimize this further for production serving."

  ---
  Question 3 (Level 2):
  You mentioned quantization earlier (QLoRA). What is quantization in the context of LLM inference, and why does everyone care about it?

❯ ok interesting, so LLM inference is not "slow" by design, but this is the fact they don't one one unique prediction as most classic ML models do but one for each token until the end of the sentence plus the fact the number of
layers/parameters is justr crazy. Ok, got it... I understand now why there is a shortage of RAM (for normal computers), better business to make VRAM! Q3: you told me about LoRA and QLoRA variation with uses a quantized 4bit model.
Usually quantization is to decrease the precision (ex from 1.0 to 1bit) to save time and memory. So I guess same for inference, a way to spped up inference at the cost of precision?

● Grade: solid! That's exactly it. Let me add the specifics.

  Standard precision levels:
  
```
  ┌────────────┬─────────────────┬────────────────┬─────────────────────────────────────────────┐
  │ Precision  │ Bits per weight │ 70B model size │                  Use case                   │
  ├────────────┼─────────────────┼────────────────┼─────────────────────────────────────────────┤
  │ FP32       │ 32 bits         │ ~280 GB        │ Training (full precision)                   │
  ├────────────┼─────────────────┼────────────────┼─────────────────────────────────────────────┤
  │ FP16/BF16  │ 16 bits         │ ~140 GB        │ Training & inference standard               │
  ├────────────┼─────────────────┼────────────────┼─────────────────────────────────────────────┤
  │ INT8       │ 8 bits          │ ~70 GB         │ Inference (minimal quality loss)            │
  ├────────────┼─────────────────┼────────────────┼─────────────────────────────────────────────┤
  │ INT4       │ 4 bits          │ ~35 GB         │ Inference (noticeable but acceptable loss)  │
  ├────────────┼─────────────────┼────────────────┼─────────────────────────────────────────────┤
  │ GGUF 2-bit │ 2 bits          │ ~17 GB         │ Hobbyist, runs on laptop (quality degrades) │
  └────────────┴─────────────────┴────────────────┴─────────────────────────────────────────────┘
```

  Why everyone cares: Going from FP16 to INT4 = 4x less VRAM, ~2-3x faster inference. A 70B model that needs an $80K GPU cluster in FP16 suddenly runs on a single $2K GPU in INT4. That's the difference between a production deployment
  and a prototype.

  The quality trade-off is surprisingly small:
  - FP16 → INT8: nearly zero quality loss (~0.1% on benchmarks)
  - FP16 → INT4: small loss (~1-2%), barely noticeable for most tasks
  - FP16 → INT2: significant degradation, only for casual use

  Popular quantization formats you'll hear:
  - GPTQ: post-training quantization, popular for GPU inference
  - AWQ: activation-aware, slightly better quality than GPTQ
  - GGUF: llama.cpp format, runs on CPU (!) — this is how people run models on laptops

  Your VRAM observation is spot on: NVIDIA's entire business model shift is driven by this. A100 (80GB), H100 (80GB), now H200 (141GB) — they're building bigger VRAM because LLMs are memory-bound, not compute-bound. The bottleneck is
  fitting the model + KV cache in VRAM, not the math itself.

  Connection to your roles: At Sanofi/Airudi, you'd make this decision: "Do we serve a full FP16 model on expensive GPUs for maximum quality, or quantize to INT4 and serve on cheaper hardware?" For most agentic tasks, INT4 or INT8 is
  fine. For critical drug safety predictions, you might want full precision.

  Interview-ready sentence: "Quantization reduces weight precision from 16-bit to 4-bit or 8-bit, cutting VRAM 2-4x with minimal quality loss. It's the key to making LLM serving economically viable — the difference between needing a
  GPU cluster and a single card. I'd choose precision level based on task criticality."

  ---
  Great session today! Let me update progress.