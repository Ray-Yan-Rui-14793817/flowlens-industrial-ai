# FlowLens Industrial AI — W03-C08 Provider and Model Policy

```text
policy_version = w03-c08-openai-v1
provider = OpenAI
api = Responses API
requested_model = gpt-5.6-terra
reasoning_effort = none
temperature = OMITTED
tools = NONE
retrieval = NONE
streaming = OFF
store = FALSE where supported
max_output_tokens = 1200
application_timeout_seconds = 15
sdk_automatic_retries = 0
max_provider_calls_per_explanation = 2
```

Only the official OpenAI Python SDK may be added. Its exact resolved version is
locked in `uv.lock`. The API key is read only from
`FLOWLENS_OPENAI_API_KEY`, only by the provider adapter, and is never logged,
persisted, or sent in prompt content.

Default mode is `template`. `openai` mode is opt-in. Missing credentials in
OpenAI mode produce deterministic template output without a provider call and
without failing application startup.

The adapter receives only the exact system prompt, canonical
`ExplanationContextV1`, and strict output schema. It persists or logs no raw
model response. Unit and integration CI use fake providers and make no live
provider call.
