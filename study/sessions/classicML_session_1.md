Let's switch gears to Module 2.1 — Classical ML Foundations. This is the 5-year rust zone, and a data scientist interviewer at Sanofi will likely probe here.

  ---
  Question 1 (Level 1):
  Explain bias-variance trade-off in your own words. What happens when you have too much of each?

❯ yes, totally, 5 year rust zone... and my LTM-like decay algorithm is pretty good ^^. Let's try top remember, thois is the goal, no shame to have (I try to convince myself). High bias means the model detects nothing... huge
underfitting. Low bias is the contrary, it does a good job. Variance is linked to overfitting, high variance causes a model to break if the data is not exactly the training data.

● Grade: solid! You got the core right — bias = underfitting, variance = overfitting. The rust isn't as bad as you feared! Let me sharpen it.

  Bias = how far your model's average predictions are from the truth. High bias means the model is too simple to capture the real pattern. It's wrong consistently in the same direction.
  - Example: fitting a straight line to clearly curved data

  Variance = how much your predictions change if you train on different data. High variance means the model is too sensitive to the specific training set. It memorizes noise.
  - Example: a deep decision tree that perfectly fits training data but fails on new data

  The trade-off:
  Simple model (few params)  →  high bias, low variance  →  underfitting
  Complex model (many params) →  low bias, high variance  →  overfitting
                      ↕
                Sweet spot in the middle

  Analogy: You're drawing a portrait. High bias = you draw stick figures for everyone (too simple, misses the person). High variance = you draw every pore and wrinkle from one photo, but the portrait looks wrong from any other angle
  (memorized one view). Good portrait = captures the essence without overfitting to one photo.

  Interview-ready sentence: "Bias measures systematic error from oversimplified assumptions; variance measures sensitivity to training data noise. The goal is the sweet spot — complex enough to capture real patterns, simple enough to
  generalize. Regularization, cross-validation, and ensemble methods are how we navigate this trade-off."

  ---
  Question 2 (Level 1):
  Speaking of which — what is regularization and name two common techniques?

❯ ouch... I think Relu, Sigmoid... so they are mathematical tricks to get the model output to give an answer between 0 and 1 but in a way it represents well the trust in the prediction?

● Grade: rusty — No shame! Those are activation functions, not regularization. Different concept entirely. Let's fix this.

  Activation functions (what you described): ReLU, Sigmoid, etc. — they introduce non-linearity into neural networks. Sigmoid squashes to [0,1], ReLU clips negatives to zero. Important, but not regularization.

  Regularization = techniques to prevent overfitting by penalizing model complexity. You're telling the model: "don't get too clever, keep it simple."

  Two classic techniques:

  1. L1 / L2 regularization (Ridge / Lasso)
  - Add a penalty term to the loss function based on the size of the weights
  - L2 (Ridge): loss + λ × (sum of weights²) — pushes weights toward small values
  - L1 (Lasso): loss + λ × (sum of |weights|) — pushes some weights to exactly zero (feature selection!)
  - Analogy: "You can use any features you want, but each one costs you. Big weights cost more." Forces the model to only keep features that really matter.

  2. Dropout (neural networks)
  - During training, randomly turn off X% of neurons each batch
  - Forces the network to not rely on any single neuron — builds redundancy
  - Analogy: training a football team where random players sit out each practice. The team learns to function no matter who's missing.

  Other regularization you might hear in interviews:
  - Early stopping: stop training before the model starts memorizing
  - Data augmentation: more varied training data = harder to overfit
  - Cross-validation: not strictly regularization, but detects overfitting

  How they connect to bias-variance:
  - No regularization → low bias, high variance (overfitting)
  - Too much regularization → high bias, low variance (underfitting)
  - λ (the regularization strength) is the dial between the two

  Interview-ready sentence: "Regularization constrains model complexity to prevent overfitting. L2 penalizes large weights to keep the model smooth, dropout forces redundancy in neural networks, and the regularization strength controls
   the bias-variance trade-off."

  ---
  Question 3 (Level 2):
  Your Sanofi interviewer shows you a classification model predicting whether a drug compound will cross the blood-brain barrier (your pharma-catalyst task!). The model has 95% accuracy. Is that good? What would you ask before
  answering?

❯ ah... yeah I remember now... thanks for re-generating my internal embeddings!

● Ha! Dr Falken's transfer learning pipeline working on your brain — freeze the old knowledge, re-activate with a small LoRA update!

  Still waiting for your answer on Question 3 though — 95% accuracy on BBB prediction, good or not?

❯ I would day showing only the accuracy is not enough, and based on what the training data only? after cross-validation? on the testing dataset? and I want to see other metrics like the F1-score, the recall, the precision, the
confusion matrix...

● Grade: solid! That's exactly the right reflex — "95% accuracy means nothing without context." An interviewer wants to hear you push back, not accept the number.

  What you nailed:
  - Don't trust accuracy alone
  - Need to know: training vs test data?
  - Want F1, precision, recall, confusion matrix

  The key thing to add — why accuracy specifically lies:

  Class imbalance. If 95% of compounds do NOT cross the BBB, a model that always predicts "no" gets 95% accuracy while being completely useless. This is extremely common in pharma datasets.

  The metrics that matter and when:

```
  ┌──────────────────┬───────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────┐
  │      Metric      │               What it measures                │                             When it matters                             │
  ├──────────────────┼───────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────┤
  │ Precision        │ Of predicted positives, how many are correct? │ When false positives are expensive (e.g., approving a toxic drug)       │
  ├──────────────────┼───────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────┤
  │ Recall           │ Of actual positives, how many did we catch?   │ When false negatives are dangerous (e.g., missing a promising compound) │
  ├──────────────────┼───────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────┤
  │ F1               │ Harmonic mean of precision & recall           │ When you need to balance both                                           │
  ├──────────────────┼───────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────┤
  │ AUC-ROC          │ Performance across all thresholds             │ When you want threshold-independent evaluation                          │
  ├──────────────────┼───────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────┤
  │ Confusion matrix │ Full breakdown of TP/TN/FP/FN                 │ Always — it tells the whole story                                       │
  └──────────────────┴───────────────────────────────────────────────┴─────────────────────────────────────────────────────────────────────────┘
```

  The complete interview answer would be:

  1. "What's the class distribution?" (if 95/5 split, accuracy is meaningless)
  2. "Is this on the test set, and how was it split?" (random split vs scaffold split for molecules — pharma-specific!)
  3. "Show me AUC-ROC and the confusion matrix"
  4. "What's the baseline?" (random, majority class, simple model)
  5. "What's the cost of false positives vs false negatives?" (in drug discovery, missing a good compound is usually worse than testing a bad one)

  Your pharma-catalyst connection: Your agents improved BBBP ROC-AUC from 0.895 to 0.942. You reported AUC, not accuracy — that was already the right instinct!


First rusty answer of the session (activation vs regularization), but you recovered strong. That's actually how interviews go — stumble, recover, show depth. Save the session whenever you want, or keep going?

❯ keep going!

● Question 4 (Level 2):
  You mentioned cross-validation. Explain how k-fold cross-validation works and why it's better than a single train/test split.

❯ train/test if a rigid split, and that's hard to split it right (usually it could be "as dumb" as 80/20) but hard to tell if both dataset are balanced and so on. Cross-validation is like shuffling the cards but k times between
training and testing dataset to have more chances to get proper splits

● Grade: partial — Right intuition about "shuffling" and doing it multiple times, but the mechanism needs precision.

  How k-fold actually works:

  Dataset: [A][B][C][D][E]   (split into k=5 equal folds)

  Round 1: Train on [B][C][D][E], test on [A] → score₁
  Round 2: Train on [A][C][D][E], test on [B] → score₂
  Round 3: Train on [A][B][D][E], test on [C] → score₃
  Round 4: Train on [A][B][C][E], test on [D] → score₄
  Round 5: Train on [A][B][C][D], test on [E] → score₅

  Final score = average(score₁...score₅)

  The key: every data point gets to be in the test set exactly once. No data point is ever in both train and test in the same round.

  Why it's better than a single split:

  1. Every sample gets tested — no lucky/unlucky split. With 80/20, your test set might accidentally contain all the easy cases.
  2. You get a confidence measure — not just "accuracy = 92%" but "92% ± 3%". If the variance across folds is high, your model is unstable.
  3. Uses all data for both training and testing — crucial when data is small (very common in pharma — your ESOL dataset was only 1,128 molecules!)

  What you said that was right: multiple rounds, better chance of proper representation.

  What was imprecise: it's not random shuffling — it's systematic rotation. Each fold takes a turn as the test set. That's the guarantee.

  Pharma-specific twist for interviews: In molecular data, standard k-fold can cheat — similar molecules end up in both train and test. That's why scaffold split exists: split by molecular structure so the model must generalize to
  truly different compounds. You used this in pharma-catalyst!

  ---
```  
  Question 5 (Level 2):
  Name three ensemble methods and explain why combining multiple models often beats a single model.
```

> yeah right shuffling was wrong, that's not random. Ok I need to check about scaffolding split... how does it work? Q5: believe it or not but the beauty of my Schneider model to detect failures on oil pumps worked thanks to a smart
> ensembling I have done!!!! And believe it or not I forgot all the various ensembling strategies... I think I remember prdiction results could be simply averagered (bad), or weighted per model based on their > strength on a given class
> (what I did), I forgot the other ones.... it often beats "in real life" because real data are not training data and models can be more or less sensitive to new data, can be better or worse to generalize, can > have their own strenght
> and weakness,... so combining multipe ones is a better chance to generalize.

● Grade: solid! Your real-world experience carries you — weighted ensemble based on per-class strength is actually a sophisticated approach, not a basic one. And your reasoning about why ensembles work is spot on.

  Scaffold split (your side question):
  Molecules have a "scaffold" — the core ring structure. Scaffold split groups molecules by their core structure, then splits groups (not individual molecules) into train/test. So if aspirin-like molecules are in training, no
  aspirin-like molecules appear in test. Forces the model to generalize to genuinely new chemistry, not just variations of what it's seen. Standard k-fold on molecules is like testing on synonyms — scaffold split tests on a new
  language.

  The three main ensemble strategies:

  1. Bagging (Bootstrap Aggregating) — Random Forest
  - Train many models on random subsets of data (with replacement)
  - Average their predictions (regression) or vote (classification)
  - Reduces variance — each model overfits differently, averaging cancels out the noise
  - Analogy: ask 100 people to estimate the weight of a cow. Individual guesses are wrong, average is surprisingly accurate (wisdom of crowds)

  2. Boosting — XGBoost, AdaBoost, GradientBoosting
  - Train models sequentially, each one focusing on what the previous ones got wrong
  - Each new model pays more attention to the hard examples
  - Reduces bias — iteratively corrects systematic errors
  - Analogy: each tutor specializes in the student's weakest subject. First tutor fixes math, second fixes what's still wrong in physics, third handles the remaining gaps
  - XGBoost is still the king of tabular data and Kaggle competitions

  3. Stacking
  - Train diverse models (different algorithms), then train a meta-model that learns how to combine their outputs
  - Your weighted approach was close to this! You weighted models by per-class strength — stacking automates that weighting
  - Analogy: a panel of experts (cardiologist, radiologist, general practitioner) + a senior doctor who learns which expert to trust for which symptom

  What you described (weighted per-class) is actually closer to stacking than simple averaging — give yourself more credit!

```
  ┌──────────┬───────────────────────────────────┬──────────┬─────────────────────────┐
  │  Method  │                How                │ Reduces  │        Best for         │
  ├──────────┼───────────────────────────────────┼──────────┼─────────────────────────┤
  │ Bagging  │ Parallel, random subsets, average │ Variance │ Unstable models (trees) │
  ├──────────┼───────────────────────────────────┼──────────┼─────────────────────────┤
  │ Boosting │ Sequential, focus on errors       │ Bias     │ Structured/tabular data │
  ├──────────┼───────────────────────────────────┼──────────┼─────────────────────────┤
  │ Stacking │ Diverse models + meta-learner     │ Both     │ Maximum performance     │
  └──────────┴───────────────────────────────────┴──────────┴─────────────────────────┘
```

  Interview-ready sentence: "Ensembles work because they exploit model diversity — different models make different errors, and combining them cancels out individual weaknesses. Bagging reduces variance through averaging, boosting
  reduces bias by sequentially correcting errors, and stacking learns the optimal combination. At Schneider, I used weighted ensembles based on per-class performance to improve pump failure detection on imbalanced industrial data."

  That last sentence — use it. It connects theory to your real experience with a concrete result.