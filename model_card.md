# Model Card — PawPal+ AI Advisor

## Model Used

Anthropic API (`claude-haiku-4-5-20251001`) for structured JSON generation of pet care task suggestions.

---

## Limitations and Biases

**Species coverage is uneven.** The training data behind any general-purpose model skews toward common pets (dogs, cats). For less common species — reptiles, birds, exotic mammals — suggestions may be generic or miss important care requirements (e.g., UV lighting for reptiles, social stimulation for parrots).

**Duration estimates are rough.** The model has no way to know the owner's pace, the pet's individual energy level, or local context (apartment vs. yard). A suggested "30-minute walk" may be wrong by a factor of two.

**No memory across sessions.** The advisor has no access to the pet's history, health records, or prior schedules. Each call is stateless.

**JSON schema compliance is ~90%.** In testing, roughly 1 in 10 tasks came back with a malformed field. The validator drops those, but it means a user asking for 5 suggestions might only see 4.

---

## Misuse Potential

**Medical advice.** The `medical` category exists for reminders like "give medication" or "vet checkup," but the system could suggest tasks that sound like medical guidance. The system does not claim to be a vet and no medical rationale is provided — but a user could misread a suggestion as authoritative. Mitigation: adding a disclaimer in the UI ("These are general suggestions, not veterinary advice") would reduce this risk.

**Over-reliance.** A user who clicks "Get AI Suggestions" and immediately generates a schedule without reviewing may follow a plan that doesn't fit their pet's actual needs. The confidence score and manual "Add" step both require the user to stay in the loop.

---

## Testing Surprises

- The model almost always returns valid JSON when the prompt includes an explicit schema example. Prompt engineering (the `Respond ONLY with a JSON object` instruction) reduced parse failures from ~20% to ~5% during development.
- Senior cats (age 10+) consistently received `medical` category tasks, while puppies did not — an emergent, reasonable behavior that wasn't explicitly prompted.
- One test run returned a task with `"priority": "urgent"` instead of `"high"` — a hallucinated priority value not in the schema. The validator correctly dropped it and confidence was 0.75.

---

## AI Collaboration

**Helpful suggestion:** When designing the confidence scoring, the AI suggested using the *fraction of valid tasks out of total returned tasks* rather than a binary pass/fail flag. This was the right call — it gives users meaningful signal when 4 out of 5 suggestions are valid rather than hiding that nuance.

**Flawed suggestion:** The AI initially suggested adding a `retry` loop that would call the API again automatically if confidence was below 0.8. This was a bad idea: silent retries would double API costs without the user knowing, and a low-confidence response is often caused by a prompt issue that won't improve on retry. The better solution (which I used) is to show the lower confidence score and let the user decide whether to regenerate.

---

## Portfolio Reflection

Adding AI to an existing system turned out to be mostly about what happens around the model — validation, logging, and keeping the human in control. The JSON schema in the prompt, the field-level validator, and the confidence score mattered more than the model choice itself.
