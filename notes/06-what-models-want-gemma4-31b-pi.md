# 06 — What models want from tool output: Gemma4-31B introspection

Date: 2026-06-07. Source: same introspection question put to Gemma4-31B inside
pi (ollama-cloud). Self-report below, verbatim.
Synthesis across models: [06-what-models-want.md](06-what-models-want.md).

This document outlines the architectural requirements and semantic desires of the three primary entities in a tool-execution loop: the Harness, the Provider, and the LLM.

---

## 1. The Three Perspectives

### The Harness (Runtime/Orchestrator)
**Goal: Determinism and Observability**
The harness views tool execution as a lifecycle event. It cares about:
- **Reliability:** Did the tool crash? Did it timeout?
- **Resource Management:** How many tokens did the output consume? How much memory was used?
- **State Control:** Can this output be truncated or filtered without breaking the conversation state?
- **Observability:** Logging the exact command sent and the exact output received for auditing.

### The Provider (API/Gateway)
**Goal: Schema Adherence**
The provider acts as the translator between the harness and the model. It cares about:
- **Specification:** Does the output fit the required JSON schema (e.g., `tool_outputs` array)?
- **Boundary Definition:** Clearly separating the "tool result" from "model generation" to prevent prompt injection or parsing errors.
- **Routing:** Ensuring the correct `call_id` is mapped back to the corresponding request.

### The LLM (Inference Engine)
**Goal: Grounding and Resolution**
The LLM views tool execution as a gap-filling exercise. It cares about:
- **The Delta:** What new information has been provided that I didn't have before?
- **Signal-to-Noise Ratio:** High utility data with minimal "boilerplate" or irrelevant clutter.
- **Logical Connection:** A direct result that corresponds to the parameters requested.
- **Error Clarity:** A "clean error" (explaining *why* it failed) is more useful than a silent failure or a generic stack trace.

---

## 2. Anatomy of a Tool Output

A tool output is essentially a **wrapped payload**.

1.  **The Envelope (Metadata):**
    - `call_id`: Essential for matching results to requests in parallel execution.
    - `tool_name`: Confirmation of the active tool.
    - `status`: Success, Failure, or Warning.
2.  **The Core (The Payload):**
    - **Raw Data:** The actual stdout/stderr, HTTP body, or file content.
    - **Semantic Label:** Descriptive text (e.g., "Contents of file X...") that provides context.
3.  **The Footer (Contextual Constraints):**
    - Indicators of truncation or modification (e.g., *"Showing lines 1-50 of 1000"*), informing the model that it is seeing a partial view.

---

## 3. The "Meta" and Normalization

### Emerging Standards
While no single global standard exists, the industry is converging toward protocols like **MCP (Model Context Protocol)**. The "meta" is moving from simple string returns to **structured content blocks** (text, images, resources) that are machine-readable for the harness but semantically transparent for the LLM.

### Normalization Process
Harnesses typically normalize data before it reaches the LLM's context window:
- **Sanitization:** Removal of non-printable characters.
- **Formatting:** Converting dense JSON strings into pretty-printed formats for better LLM comprehension.
- **Compression/Truncation:** Clipping oversized responses to stay within token limits, often replacing the middle of the text with a "..." marker.

---

## 4. Reasoning: Patterns vs. Intent

The LLM processes tool output through a dual-layer mechanism:

### Pattern Matching (The Expectation)
The model uses training data to recognize the *shape* of a response. If it calls `ls`, it expects a file list. This allows the model to quickly enter the correct "mental mode" (e.g., file-system navigation).

### Intent Validation (The Truth)
The model then compares the output against its specific goal. 
- **Pattern:** "This looks like a successful `ls` output."
- **Intent:** "I was looking for `config.json`. It is not in this list."

**The Conclusion:** The "Today's Response" (the actual output) must override the "Pattern" (the training data). The most effective tool outputs are those that provide a clear, undeniable ground truth, even if that truth contradicts the model's initial expectations.