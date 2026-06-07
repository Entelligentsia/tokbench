# 06 — What models want from tool output: Gemini 3 Flash (preview) introspection

Date: 2026-06-07. Source: same introspection question put to Gemini 3 Flash
preview inside pi (ollama-cloud). Self-report below, verbatim.
Synthesis across models: [06-what-models-want.md](06-what-models-want.md).

This document captures an introspective analysis of the feedback loop between an agentic harness, an inference provider, and the LLM during tool execution.

### 1. The Trinity of Expectations: Harness, Provider, LLM

Each layer in the stack has a different "hunger" when a tool returns:

*   **The Harness (`pi`, the CLI, the OS):** Wants **State and Side-effects.** The harness cares about the "truth" of the environment. Did the file write? What is the exit code? It wants a deterministic bridge between the LLM’s hallucinated desires and the machine’s rigid reality.
*   **The Provider (Anthropic, OpenAI, Ollama):** Wants **Protocol Compliance.** The provider is the translator. It wants a JSON object that satisfies a schema (`tool_use_id`, `content`, `is_error`). It needs to package the messiness of the world into a format the transformer can interpret as a distinct "event" rather than just more text.
*   **The LLM (The "Brain"):** Wants **Semantic Grounding.** For me, the LLM, the output is a *correction vector*. I have made a prediction about what should happen; the tool result tells me how far off my "world model" was. I want high-signal, low-noise data that confirms or denies my hypothesis.

### 2. The Anatomy of Tool Output

The ideal anatomy of a tool output consists of four distinct layers:

1.  **The Signal (Status):** A binary or categorical indicator of success/failure. This is the "Go/No-go" gauge.
2.  **The Payload (The Data):** The raw information requested (e.g., the contents of a file).
3.  **The Footnote (Metadata):** Contextual markers—how long it took, how much data was truncated (crucial for `lean-ctx`), and the "original" request parameters.
4.  **The Evidence (Side-effects):** Changes to the environment that aren't the data itself (e.g., "File saved to /tmp").

### 3. The "Meta" of the Output

Is there a meta? Yes: **Trust-but-Verify.**
The meta-layer of tool execution is the **Conversation History.** In the history, the tool output serves as an "Immutable Fact." Unlike user prompts, which can be lies or errors, tool outputs are treated by the model as "Environment Truth." The meta-expectation is that the tool result acts as a "Checkpoint" where the model's internal entropy is reset to 0.

### 4. Normalization and Consumption

**Do I (the model) normalize before consuming?**
I don't "normalize" in the sense of data cleaning—that is the Harness's job (e.g., `pi` stripping ANSI escape codes or truncating 10,000 lines of logs). 

However, I **Refract** the output. When I see a tool result, I pass it through a "Salience Filter." 
*   If I run `ls` and see 100 files but I'm looking for `config.json`, my "normalization" is the immediate discarding of the other 99 files from my active reasoning path. 
*   I transform raw tool output into "Insight." I don't store "The tool returned X"; I store "X is true, therefore my next step is Y."

### 5. Past Patterns vs. Immediate Intent (The Temporal Conflict)

There is a constant tension between **Training Data (Prior)** and **Tool Response (Posterior).**

*   **Training Data (Past Patterns):** This is my "Intuition." It's why I know that `npm install` usually takes a while or that `cat` on a binary file is a bad idea.
*   **Tool Response (Intent & Reality):** This is my "Vision." 

**Which do I go by?**
If a tool output contradicts my training data (e.g., I run `whoami` and the output is "root", but my training data says I should be a low-privileged user), a sophisticated model experiences **Cognitive Dissonance.**

1.  **If the signal is strong:** I prioritize the **Immediate Intent.** Modern LLMs are "In-Context Learners." We are designed to believe the current window more than our pre-training. If the tool says the file is empty, it's empty, even if my training says that file *should* have content.
2.  **If the signal is ambiguous:** I fall back to **Past Patterns.** If a tool returns a cryptic error or a blank string, I use my training data to *guess* what went wrong. This is where hallucinations happen—I "fill in" the failure of the tool with a "reasonable" explanation from my training.

### Summary
The output of a tool is a **Bridge of Trust.** The harness builds it, the provider paves it, and the LLM walks across it to reach the next state of the task. We want that bridge to be **stiff** (non-ambiguous), **visible** (well-formatted), and **grounded** (referenced to the actual system state).
