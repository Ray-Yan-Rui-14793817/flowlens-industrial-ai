# FlowLens Industrial AI — W03-C08 Authorization Contract

```text
checkpoint = W03-C08
task = W03-C08-I/H/R
contract_version = W03-C08-A-v1
entry_branch = feat/w03-ai-decision-loop
entry_sha = c89a2cc5b24a53897ec0d8085293445c18fd2675
main_sha = 9d18ddde9fe933952a2661ee1419f13c8577605d
status = IMPLEMENTATION_AUTHORIZED
```

## Authorized outcome

C08 adds a bounded explanation layer over one already-finalized C05
`DecisionPacket`. The deterministic system remains the sole recommendation and
candidate authority. The LLM may explain validated packet-derived data only.

The final artifact remains the frozen C01 `ExplanationRecord` with
`schema_version = explanation-record.v1` and one of:

```text
DETERMINISTIC_TEMPLATE
BOUNDED_LLM
DEGRADED_TEMPLATE
```

## Frozen boundary

```text
MODEL EXPLAINS; SYSTEM DECIDES
LLM TOOL ACCESS = NONE
LLM DATABASE ACCESS = NONE
LLM FILESYSTEM ACCESS = NONE
LLM RETRIEVAL/RAG = NONE
LLM HGT ACCESS = NONE
LLM CANDIDATE AUTHORITY = NONE
LLM RECOMMENDATION AUTHORITY = NONE
LLM OPERATIONAL WRITE = NONE
```

The only authorized runtime network I/O is the host application's bounded
OpenAI Responses API inference transport. It gives the model no tool or network
capability.

## Frozen versions

```text
context_schema = w03-c08-context-v1
output_schema = w03-c08-output-v1
explainer_version = w03-c08-explainer-v1
template_version = w03-c08-template-v1
prompt_version = w03-c08-runtime-prompt-v1
prompt_sha256 = 426b061d79d2a8dfa4ac2959a604e77e6ef8dbcc04759bf7860ec9f012d185fc
provider_policy = w03-c08-openai-v1
```

## Stop conditions

Stop rather than adapt if implementation requires a C01 schema/identity change,
C05 recommendation-policy change, C06 semantic change, C07/HGT input, database
or migration change, provider/model substitution, prompt/schema weakening, new
runtime capability, operational mutation, or any dependency other than the
official OpenAI Python SDK.

C09 is not authorized. PR #6 must remain open, draft, and unmerged.
