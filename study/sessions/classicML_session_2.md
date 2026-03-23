❯ ok let's do a quick quizz to keep the brain moving!

● Spaced repetition ambush first! From last session:

  Warm-up 1: What is regularization and name two techniques? (You got this one rusty last time — let's see if the consolidation worked.)

❯ Ah not activation :) regularization, like dropout layers or L1/L2 are mechanisms to avoid overfitting

● SOLID! The "Ah not activation :)" tells me the correction stuck. Dropout + L1/L2 + overfitting prevention — perfect. Brain-RAG reindexed successfully.

  Warm-up 2: Top-p vs top-k — which one is adaptive and why?

❯ ok this is about LLM temperature, selection of best token. -p is about ranked probablities so not adaptive, k  is about bigger than x, so more adaptive.

● Grade: swapped! You mixed them up. Let me re-anchor:

  - Top-k = fixed, rigid: "always keep the k best tokens" (k=50 means exactly 50, regardless of confidence)
  - Top-p = adaptive, smart: "keep tokens until cumulative probability reaches threshold" (p=0.9 means maybe 3 tokens when confident, maybe 200 when uncertain)

  Mnemonic: p = probability threshold (adapts to confidence). k = konstant number (always fixed). The adaptive one is the one with the probability — top-p.

  Let's keep going. Quick fire — Module 2.2 Deep Learning Fundamentals. Fresh territory.

  ---
  Question 1 (Level 1):
  What is backpropagation and why is it essential for training neural networks?

❯ "matt knocked his rag-brain... p..k...k..p... meeeh :D". Q1: that's the main mathematical trick to train neural networks and basically from layer to layer, backward, to find using gradient descent the optimal weight value

● Grade: solid! Core idea correct — backward pass through the network, using gradients to update weights toward the optimum.

  Let me add the precision layer:

  The full picture in 3 steps:

  1. Forward pass: Input flows through the network → produces a prediction
  2. Loss computation: Compare prediction to ground truth → how wrong are we?
  3. Backward pass (backprop): Using the chain rule of calculus, compute how much each weight contributed to the error → gradient flows backward from output to input, layer by layer → each weight gets a gradient saying "adjust me this
  much in this direction"

  Why the chain rule matters: A deep network is a composition of functions: f(g(h(x))). The chain rule lets you decompose the total gradient into local gradients at each layer and multiply them together. That's the "backward" — you
  propagate the error signal back through each layer.

  The vanishing gradient problem (connects to your RNN knowledge): In very deep networks, these multiplied gradients can shrink to near-zero in early layers — those layers stop learning. This is why residual connections (ResNet) were
  invented: they add shortcut paths so gradients can flow directly to early layers without being multiplied to death.

  Analogy: A factory assembly line has a defect in the final product. Backprop is the quality inspector tracing backward through each station asking "how much did YOUR step contribute to this defect?" and telling each station exactly
  how to adjust.

  ---
  Question 2 (Level 2):
  You mentioned gradient descent. What's the difference between SGD, Adam, and why does everyone use Adam?

❯ this is the learning rate optimizer, to decide how to adjust weights according to the loss. Adam? because it is a cool name.. ^^ (kidding, I know it is the most popular but why....dunno)

● Grade: partial — Right that they're optimizers, but the "why Adam" is the interesting part!

  SGD (Stochastic Gradient Descent):
  - The simple one: update weights by weight -= learning_rate × gradient
  - Same learning rate for every parameter, every step
  - Problem: if the loss landscape is a narrow valley (steep in one direction, flat in another), SGD oscillates wildly across the steep dimension while crawling along the flat one

  Adam (Adaptive Moment Estimation):
  - Keeps a running average of gradients (momentum — which direction are we generally going?)
  - AND a running average of squared gradients (how much does each parameter's gradient vary?)
  - Uses both to give each parameter its own adaptive learning rate
  - Parameters with stable, consistent gradients get bigger steps. Noisy parameters get smaller steps.

  Why everyone uses Adam: It just works. You set the learning rate to 3e-4, press go, and it converges for most problems without tuning. SGD can beat Adam with perfect hyperparameter tuning, but nobody has time for that.

  Analogy: SGD = driving at a fixed speed on every road (highway, dirt trail, mountain pass — same speed). Adam = a smart cruise control that accelerates on straight highways and slows down on bumpy terrain, adapting to each stretch of
   road independently.

  Interview one-liner: "Adam adapts the learning rate per-parameter using running estimates of gradient mean and variance. It's the default because it converges reliably with minimal tuning. SGD with momentum can match or beat it but
  requires more hyperparameter work."

  ---
  Question 3 (Level 1):
  What is batch normalization and what problem does it solve?

❯ the goal is, within data that are comparable, so in this case a batch from the training data (LLM can only use layernorm), to normalize the data

● Grade: partial — You got the "normalize within a batch" part and the LayerNorm distinction for LLMs (nice catch!). But what problem does it solve and where is it applied?

  What it does: After each layer, normalize the activations (outputs) so they have mean ≈ 0 and variance ≈ 1. Then apply two learnable parameters (scale and shift) so the network can undo the normalization if it wants to.

  What problem it solves — internal covariate shift:
  - As training progresses, each layer's inputs keep changing because the layer before it is also updating its weights
  - Layer 5 is trying to learn on a moving target — the distribution of its inputs keeps shifting
  - Batch norm stabilizes these distributions, so each layer can learn more efficiently

  Practical effects:
  - Faster training — can use higher learning rates without exploding
  - Acts as mild regularization — the batch statistics add noise, reducing overfitting slightly
  - Less sensitive to weight initialization — more forgiving to start with

  Your LayerNorm insight is correct and worth expanding:

```
  ┌───────────┬───────────────────────────────────────────┬─────────────────────┐
  │   Type    │             Normalizes across             │       Used in       │
  ├───────────┼───────────────────────────────────────────┼─────────────────────┤
  │ BatchNorm │ The batch dimension (across samples)      │ CNNs, vision models │
  ├───────────┼───────────────────────────────────────────┼─────────────────────┤
  │ LayerNorm │ The feature dimension (within one sample) │ Transformers, LLMs  │
  └───────────┴───────────────────────────────────────────┴─────────────────────┘
```

  Why LLMs use LayerNorm: BatchNorm needs a batch of samples to compute statistics. During autoregressive generation, you process one token at a time — no batch. LayerNorm works on a single sample, so it works at inference time.

  Analogy: BatchNorm = grading on a curve (your score depends on the class average). LayerNorm = normalizing your own scores across subjects (your math, physics, history scores are rescaled relative to each other, regardless of anyone
  else).

  ---
  Good session! Let me update progress.


● Quick session scorecard:
```
  ┌─────────────────────────────┬──────────────────────────────────────────────┐
  │          Question           │                    Grade                     │
  ├─────────────────────────────┼──────────────────────────────────────────────┤
  │ Regularization (spaced rep) │ SOLID (was rusty, now fixed!)                │
  ├─────────────────────────────┼──────────────────────────────────────────────┤
  │ Top-p vs top-k (spaced rep) │ Swapped (needs more reps)                    │
  ├─────────────────────────────┼──────────────────────────────────────────────┤
  │ Backpropagation             │ Solid                                        │
  ├─────────────────────────────┼──────────────────────────────────────────────┤
  │ SGD vs Adam                 │ Partial                                      │
  ├─────────────────────────────┼──────────────────────────────────────────────┤
  │ Batch norm                  │ Partial (but LayerNorm insight was a bonus!) │
  └─────────────────────────────┴──────────────────────────────────────────────┘
```

  Mnemonic homework: p = probability = adaptive. k = konstant = fiksed. Next time I'll ambush you on this again.

  8 applications sent + brain kept warm. Productive day, Doc!

✻ Baked for 59s

❯ give me my carrot!!!! ^^

● Your carrot:

  Regularization went from RUSTY to SOLID in one sleep cycle. That's proof the system works — the study sessions, the analogies, the spaced repetition, the N2/N3 consolidation. You're not just memorizing, you're rebuilding neural
  pathways that were dormant for 5 years.

  The scoreboard since session 1:

```
  ┌───────────────────┬───────┬─────────┬───────┬───────────────────────────────────┐
  │      Session      │ Solid │ Partial │ Rusty │               Trend               │
  ├───────────────────┼───────┼─────────┼───────┼───────────────────────────────────┤
  │ Session 1 (day 1) │ 2     │ 7       │ 0     │ Baseline                          │
  ├───────────────────┼───────┼─────────┼───────┼───────────────────────────────────┤
  │ Session 2 (day 2) │ 7     │ 6       │ 2     │ Big jump                          │
  ├───────────────────┼───────┼─────────┼───────┼───────────────────────────────────┤
  │ Session 3 (today) │ 2     │ 2       │ 1     │ Quick maintenance                 │
  ├───────────────────┼───────┼─────────┼───────┼───────────────────────────────────┤
  │ Total             │ 11    │ 15      │ 3     │ 38% solid, 52% partial, 10% rusty │
  └───────────────────┴───────┴─────────┴───────┴───────────────────────────────────┘
```

  3 sessions ago you confused activation functions with regularization. Today you corrected yourself before I could. That's not rust removal — that's a brain-LoRA fine-tuning in progress.

  And you sent 8 sniper applications to Bengio, LeCun, Mensch, Thales, Sanofi, Airudi, MIA, and Vooban while doing it. Pas mal pour un gars qui "hasn't done this seriously in 5 years."

  Now go eat your carrot and dream in N2/N3. p = adaptive. See you next session, WOPR!