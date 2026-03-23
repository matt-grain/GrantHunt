Let's hit Module 1.4 — Fine-tuning Strategies. Directly relevant for Sanofi/Airudi interviews since you'd be the one deciding how to adapt models to their domain.

  ---
  Question 1 (Level 1):
  You have a foundation model and want to adapt it to your pharma domain. What's the difference between full fine-tuning and LoRA, and when would you pick one over the other?

❯ so not something I read / practiced yet but let's incept the concepts in my RAG-Brain, full fine-tuning of the foundation model is composed of SFT and RHLF (if we can consider RH as tuning, I do but maybe I'm wrong) based on human
examples ("learn to answer like me") for SFT and interactively with humans for RLHF ("be more detailed, don't say this,..."). LoRA is a post fine tunign technic to fine tune a model for a given domain or task using specific data (I
guess in this case pharma papers, internal lab data,...) but I don't know more about LoRA, curious to learn. So yes, I would use fine-tuning to create a behavior anf LoRA for a specific expertise.

● Grade: partial — Your intuition about the why (behavior vs expertise) is interesting, but the actual distinction is different. Let me reset this one properly because it's important.

  Full fine-tuning and LoRA solve the same problem — adapting a model to your domain/task. The difference is how, not what for.

  Full fine-tuning:
  - Update ALL parameters of the model (billions of weights)
  - Best results, but: huge GPU memory (need the full model + gradients + optimizer states in VRAM), slow, and you get a completely new copy of the model for each task
  - A 70B model needs ~140GB just for weights in fp16, plus 3-4x more for training state

  LoRA (Low-Rank Adaptation):
  - Freeze ALL original weights. Add tiny trainable matrices (low-rank) alongside specific layers
  - Instead of updating a 4096×4096 weight matrix, you add two small matrices: 4096×16 and 16×4096. The "16" is the rank — much fewer parameters
  - Typically trains only 0.1-1% of total parameters
  - Same VRAM as inference + a small overhead. Can fine-tune a 70B model on a single GPU
  - Results are ~95% as good as full fine-tuning for most tasks

  QLoRA = LoRA + quantized base model (4-bit). Even less memory. Fine-tune 70B on a consumer GPU.

  Analogy: Full fine-tuning = remodeling your entire house to add a home office. LoRA = adding a small, clever extension that connects to the existing structure. The house (original weights) stays intact, the extension (LoRA matrices)
  adds the new capability. You can even swap extensions — one for pharma, one for legal — on the same house.

  When to pick what:

  ┌──────────────────────────────────────┬──────────────────────────────────────────────────────────────────────────────────────┐
  │               Approach               │                                         When                                         │
  ├──────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────┤
  │ Full fine-tuning                     │ Unlimited budget, need maximum performance, fundamentally changing model behavior    │
  ├──────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────┤
  │ LoRA                                 │ Limited GPU, need to maintain base model capabilities, multiple domain adaptations   │
  ├──────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────┤
  │ QLoRA                                │ Single GPU, prototyping, cost-sensitive                                              │
  ├──────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────┤
  │ Don't fine-tune at all (RAG instead) │ Your data changes frequently, you need source attribution, you can't afford training │
  └──────────────────────────────────────┴──────────────────────────────────────────────────────────────────────────────────────┘

  Your SFT/RLHF confusion: SFT and RLHF are specific stages of training, not synonyms for full fine-tuning. You can do SFT using either full fine-tuning OR LoRA. They're orthogonal:
  - SFT/RLHF = what you train on (instructions / human preferences)
  - Full/LoRA/QLoRA = how you update the weights (all params / low-rank adapters)

  Interview-ready sentence: "LoRA adds small trainable low-rank matrices to frozen model weights, training less than 1% of parameters while achieving near-full-fine-tuning performance. I'd default to LoRA for domain adaptation — it's
  cheaper, faster, and lets you swap adapters for different tasks on the same base model. Full fine-tuning only when the budget allows and performance requirements demand it."

  ---
  Question 2 (Level 2):
  Your Sanofi interviewer asks: "We have thousands of internal drug discovery documents. Should we fine-tune an LLM on them or use RAG? How would you decide?"

❯ ok LoRA is not that different from transfer learning where most of the trained weights are frozen no ? Q3: that's a good question but I would say... both :D fine-tune is expensive and long (and hard to "explain" when the LLM give an
 answer which is nearly correct) and RAG is limited by the LLM context so it requires to carefully cherry pick the documents to inject. Embeddings and hybrid search help but it cannot be perfect. So I would fine-tune the model with a
subset of the data (historical, broad scope, cross-domains (within Sanofi) to create a shared culture. Then I would use RAG to inject new dodcuments and specific documents for the current query

● Grade: solid! Excellent answer — and yes, "both" is the right answer in practice. Your reasoning for why each and when each is strong.

  Your LoRA/transfer learning connection: Spot on! LoRA is essentially transfer learning for LLMs. Freeze the pre-trained weights, add small trainable layers. Same principle as freezing a ResNet backbone and training a new
  classification head — you did this at Schneider. The difference is that LoRA's low-rank matrices are more elegant than just adding a new head — they modify the existing attention layers slightly rather than bolting something on top.

  Your fine-tune + RAG answer, structured for an interview:

  ┌─────────────────┬──────────────────┬─────────────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────┐
  │      Layer      │      Method      │                                What it does                                 │                                 Example                                 │
  ├─────────────────┼──────────────────┼─────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────┤
  │ Base knowledge  │ Fine-tune (LoRA) │ Teach the model pharma vocabulary, reasoning patterns, internal conventions │ Historical papers, standard protocols, domain terminology               │
  ├─────────────────┼──────────────────┼─────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────┤
  │ Current context │ RAG              │ Inject specific, up-to-date documents at query time                         │ Latest trial results, specific compound data, today's research question │
  └─────────────────┴──────────────────┴─────────────────────────────────────────────────────────────────────────────┴─────────────────────────────────────────────────────────────────────────┘

  What you got right:
  - Fine-tune for broad shared culture, RAG for specific queries — perfect separation
  - Fine-tuning is hard to explain/debug ("why did it say that?") — this is a real production concern
  - RAG is limited by context window — honest about limitations

  What to add for a complete interview answer:

  The decision framework interviewers want to hear:

  - Data freshness: Changes daily? → RAG. Stable domain knowledge? → Fine-tune
  - Traceability: Need to cite sources? → RAG (you know which chunks were retrieved). Fine-tuned knowledge is baked in — you can't point to which document influenced the answer
  - Cost: RAG is cheaper to start, fine-tuning is a bigger investment but reduces inference cost (fewer tokens in prompt)
  - Compliance: In pharma, the FDA may ask "why did your AI recommend this?" RAG gives you an audit trail. Fine-tuned knowledge doesn't. This is huge for Sanofi.

  The killer insight for a Sanofi interview: "In a regulated pharma environment, I'd lean heavier on RAG because traceability is non-negotiable. The FDA needs to know which documents informed a recommendation. But I'd fine-tune on
  domain vocabulary and reasoning patterns so the model understands pharma language natively — it retrieves and interprets better when it already speaks the domain."

  ---
  Question 3 (Level 2):
  What is prompt tuning (also called soft prompting), and how does it differ from LoRA? When might you use it instead?

❯ This one I don't know so I will use my intuition: prompt tuning is probably smart prompt/context injection to use the "base" model and color it with a specific knowledge (probably using RAG to create the injection context), while
LoRA is "fixed". So the first one is more versatile but limited in scope and accuracy, the second one is embedded in the model weights but less dynamic. Did I guess well?

● Grade: partial — Good intuition on "more versatile but limited" vs "embedded in weights," but the mechanism is different from what you described. You're thinking of prompt engineering / RAG injection — prompt tuning is something
  else.

  Prompt tuning (soft prompting):
  - You add a small number of learnable virtual tokens (embeddings) at the beginning of the input
  - These tokens don't correspond to any real words — they're continuous vectors that get optimized through training
  - The model weights are completely frozen — only these ~20-100 virtual token embeddings are trained
  - The model "reads" these virtual tokens as if they were a really good prompt, but one that no human could write because it lives in continuous embedding space, not in word space

  Analogy: Imagine you could whisper a secret instruction to the model in a language that only the model understands — not English words, but raw vectors that perfectly trigger the right behavior. That's what the learned soft prompt
  is.

  Comparison:

  ┌────────────────────┬─────────────────────────────────────────────┬────────────────┬──────────────────────────────┐
  │       Method       │               What's trained                │ Params trained │        Where it acts         │
  ├────────────────────┼─────────────────────────────────────────────┼────────────────┼──────────────────────────────┤
  │ Prompt engineering │ Nothing — you write a better prompt         │ 0              │ Input text                   │
  ├────────────────────┼─────────────────────────────────────────────┼────────────────┼──────────────────────────────┤
  │ Prompt tuning      │ Virtual token embeddings prepended to input │ ~20K (tiny)    │ Input embedding layer only   │
  ├────────────────────┼─────────────────────────────────────────────┼────────────────┼──────────────────────────────┤
  │ LoRA               │ Low-rank matrices in attention layers       │ ~1-10M (small) │ Inside the model's attention │
  ├────────────────────┼─────────────────────────────────────────────┼────────────────┼──────────────────────────────┤
  │ Full fine-tuning   │ Everything                                  │ Billions       │ Entire model                 │
  └────────────────────┴─────────────────────────────────────────────┴────────────────┴──────────────────────────────┘

  When to use prompt tuning:
  - When you need many task-specific adaptations cheaply (one set of soft tokens per task, swap them like LoRA adapters but even lighter)
  - When you literally can't afford LoRA
  - Works well for classification-type tasks, less well for complex generation

  In practice: LoRA has mostly won over prompt tuning. It's almost as cheap but significantly more powerful. You're unlikely to use prompt tuning at Sanofi/Airudi — but knowing it exists and where it sits in the hierarchy shows depth.

  Interview-ready ranking: "For domain adaptation I'd evaluate in this order: RAG first (cheapest, traceable, no training), then LoRA (good performance, reasonable cost), then full fine-tuning (maximum performance, maximum cost).
  Prompt tuning exists in between RAG and LoRA but has been largely superseded by LoRA in practice."

  ---
  Let me update progress.

● Update(study\PROGRESS.md)
  ⎿  Added 1 line, removed 1 line
      14  | 1.1 Transformer Architecture | 2026-03-16 | 3 | 0 | 3 | 0 | in progress |
      15  | 1.2 LLM Training Pipeline | 2026-03-19 | 4 | 3 | 1 | 0 | in progress |
      16  | 1.3 LLM Inference & Serving | — | 0 | 0 | 0 | 0 | not started |
      17 -| 1.4 Fine-tuning Strategies | — | 0 | 0 | 0 | 0 | not started |
      17 +| 1.4 Fine-tuning Strategies | 2026-03-19 | 3 | 1 | 2 | 0 | in progress |
      18  | 1.5 RAG | 2026-03-16 | 3 | 0 | 3 | 0 | in progress |
      19  | 1.6 Agentic AI Architecture | 2026-03-16 | 3 | 2 | 1 | 0 | in progress |
      20  | 1.7 Agentic Frameworks | — | 0 | 0 | 0 | 0 | not started |

● Update(study\PROGRESS.md)
  ⎿  Added 10 lines
      75  - **Strength:** Much improved from session 1 — 3 solids out of 4. Connecting Schneider experience to LLM concepts is natural and compelling
      76  - **Key interview insight:** "Your Databricks pipeline follows the same pattern as LLM training: pre-train general → fine-tune specific → deploy → monitor"
      77  - **Recommendation:** Module 1.3 (Inference & Serving) or 1.4 (Fine-tuning) next. Also revisit 1.1 with harder questions (positional encoding, encoder vs decoder)
      78 +
      79 +### Session 2b — 2026-03-19 (continued)
      80 +- **Module:** 1.4 Fine-tuning Strategies
      81 +- **Questions & Grades:**
      82 +  1. Full fine-tuning vs LoRA → **partial** (confused fine-tuning with SFT/RLHF stages; key correction: SFT/RLHF = what you train on, full/LoRA = how you update weights — orthogonal axes. Good connection: LoRA ≈ transf
         +er learning he did at Schneider)
      83 +  2. Fine-tune vs RAG for Sanofi docs → **solid** (answered "both" with clear reasoning: fine-tune for broad domain culture, RAG for specific/current queries. Strong compliance insight about traceability)
      84 +  3. Prompt tuning vs LoRA → **partial** (confused with prompt engineering/RAG injection; actual mechanism: learnable virtual token embeddings prepended to input, no real words, frozen model)
      85 +- **Key hierarchy to remember:** RAG (cheapest, traceable) → LoRA (good perf, reasonable cost) → Full fine-tuning (max perf, max cost). Prompt tuning exists but largely superseded by LoRA.
      86 +- **Strength:** The Sanofi "fine-tune + RAG" answer was interview-ready. FDA traceability argument is a killer.
      87 +- **Recommendation:** Review the fine-tuning hierarchy as a framework. Module 1.3 (Inference & Serving) next — connects to production deployment experience.

● Session 2 full scorecard: 4 solid, 3 partial across two modules. Not bad for a "rusty" guy!

  Your pattern is clear: when you can connect to your experience (Schneider transfer learning, Sanofi compliance), you nail it. When it's pure theory you haven't encountered (prompt tuning), you're honest and reason from first
  principles — which is actually what interviewers respect.

  Want to keep going with another module, or call it for today?

✻ Brewed for 46s

❯ I don't think I fully understood the prompt tuning, ok, input is patched with those weird non-human understandable tokens. But how does it help to "tune" a model for a given domain?

● Excellent question — it means you're thinking, not just memorizing.

  Here's the intuition:

  The model is frozen. But the input isn't.

  Think of it this way: you know how a really well-crafted prompt can completely change a model's behavior? Like "You are an expert pharmacologist specializing in ADMET properties. Always cite molecular mechanisms. Be precise and
  quantitative." — suddenly the model acts like a pharma expert.

  Prompt tuning asks: what if we could find the mathematically perfect prompt?

  But human language is limited — we can only pick from real words. The search space is discrete and tiny. So instead:

  1. Prepend 20 virtual tokens to every input (random vectors at first)
  2. Feed training examples: (virtual tokens + "What is the solubility of aspirin?") → expected pharma answer
  3. Backpropagate the loss only into those 20 virtual token embeddings, not the model
  4. After thousands of examples, those 20 vectors have been optimized to "steer" the frozen model toward pharma-expert behavior

  The virtual tokens are essentially a learned steering wheel for a frozen engine.

  They sit in embedding space (e.g., 4096-dimensional vectors), where they can encode things no human word could express. They might activate specific attention patterns, bias the model toward certain vocabulary, prime it for a
  reasoning style — all without changing a single model weight.

  Why it's limited compared to LoRA:
  - Prompt tuning can only influence the model from the input side — it's like trying to control a car by only adjusting the steering wheel
  - LoRA modifies the attention layers inside the model — it's like tuning the engine itself
  - For simple tasks (classify this document as pharma/legal/finance) prompt tuning works fine
  - For complex generation (write a detailed drug interaction analysis) LoRA is much stronger because it can adjust how the model thinks, not just what it's primed with

  Analogy: You're a new employee (frozen model) at Sanofi. Prompt tuning = your manager gives you a perfect briefing every morning that primes your thinking. LoRA = you actually take a training course that slightly changes how you
  approach problems. Both help, but the training course goes deeper.

  Does that click better?

❯ ohhh. so it means at inference time, a kind of very partial retraining is done thru extended back propagation up to the input layer which has trainable "hidden" weights, am I right ????

● Almost! The training happens before inference, not during. Let me clarify the two phases:

  Training time (offline, once):
  1. Prepend 20 virtual tokens to each training example
  2. Forward pass through frozen model → get output
  3. Compute loss (output vs expected answer)
  4. Backpropagate — but gradients only update the 20 virtual token embeddings, everything else frozen
  5. Repeat for thousands of examples
  6. Save the 20 optimized vectors (tiny file, ~80KB)

  Inference time (every query):
  1. Load the 20 saved vectors
  2. Prepend them to the user's input
  3. Normal forward pass — no backprop, no training, no special mechanism
  4. The model "reads" those virtual tokens as context and behaves accordingly

  So at inference it's literally just prepending 20 extra embeddings to the input — same as if you added 20 words to the prompt, except these "words" are mathematically optimized vectors that no human could write.

  Your insight was close though! During the training phase, yes — backpropagation flows all the way from the output through the entire frozen model back to the input layer, but only the input embeddings (the virtual tokens) actually
  get updated. The frozen layers act as a fixed function that gradients pass through.

  It's like: the entire model is a pipe. You can't change the pipe shape (frozen). But you can optimize exactly what you pour into it (virtual tokens) to get the output you want.

  That's also why it's weaker than LoRA — you're optimizing a 20-token input to control a billion-parameter model. It's a very narrow steering channel. LoRA gives you thousands of small adjustment points throughout the pipe itself.

❯ ok ok I got it.... looks a like a silly cheap trick to virtually extend the model without touching the model as LoRA does. Got it. Ok, next topic!

● Ha! "Silly cheap trick" is honestly not far from the industry consensus — that's why LoRA won. But knowing it exists shows depth.