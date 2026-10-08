"""One bounded official Responses request; no investigation graph or action capability."""

from __future__ import annotations

from os import getenv
from typing import cast

from openai import DefaultHttpxClient, OpenAI
from openai.types.responses import ResponseTextConfigParam

from flowlens.investigation.c07_policy import (
    C07_PROVIDER_OUTPUT_INVALID,
    PROVIDER_AUTH_ENV,
    PROVIDER_BASE_URL,
    PROVIDER_MAX_OUTPUT_TOKENS,
    PROVIDER_MAX_RETRIES,
    PROVIDER_MODEL,
    PROVIDER_TIMEOUT_SECONDS,
    SYSTEM_PROMPT,
    fail,
    provider_output_schema,
    validate_provider_runtime,
)


class OpenAIInvestigationSummaryProvider:
    """Caller-injected transport. Importing the pure renderer never loads this SDK."""

    def generate(self, runtime_data: str) -> str:
        try:
            validate_provider_runtime(runtime_data)
            key = getenv(PROVIDER_AUTH_ENV)
            if type(key) is not str or not key or key != key.strip():
                fail(C07_PROVIDER_OUTPUT_INVALID)
            with OpenAI(
                api_key=key,
                admin_api_key="",
                organization="",
                project="",
                webhook_secret="",
                base_url=PROVIDER_BASE_URL,
                max_retries=PROVIDER_MAX_RETRIES,
                timeout=PROVIDER_TIMEOUT_SECONDS,
                http_client=DefaultHttpxClient(
                    trust_env=False,
                    follow_redirects=False,
                    timeout=PROVIDER_TIMEOUT_SECONDS,
                ),
            ) as client:
                # The locked SDK folds ambient custom headers into this field.
                # Discard them before sending so they cannot replace auth/routing.
                client._custom_headers = {}
                response = client.responses.create(
                    model=PROVIDER_MODEL,
                    instructions=SYSTEM_PROMPT,
                    input="DETERMINISTIC_BASELINE_DATA\n" + runtime_data,
                    tools=[],
                    tool_choice="none",
                    stream=False,
                    store=False,
                    background=False,
                    reasoning={"effort": "none"},
                    max_output_tokens=PROVIDER_MAX_OUTPUT_TOKENS,
                    text=cast(
                        ResponseTextConfigParam,
                        {
                            "format": {
                                "type": "json_schema",
                                "name": "w04_c07_summary",
                                "strict": True,
                                "schema": provider_output_schema(),
                            }
                        },
                    ),
                )
                if response.status != "completed" or response.error is not None:
                    fail(C07_PROVIDER_OUTPUT_INVALID)
                texts: list[str] = []
                for item in response.output:
                    if item.type == "reasoning":
                        continue  # Opaque SDK metadata; never summary text or evidence.
                    if item.type != "message":
                        fail(C07_PROVIDER_OUTPUT_INVALID)
                    for content in item.content:
                        if content.type != "output_text" or type(content.text) is not str:
                            fail(C07_PROVIDER_OUTPUT_INVALID)
                        texts.append(content.text)
                if len(texts) != 1 or not texts[0] or texts[0] != texts[0].strip():
                    fail(C07_PROVIDER_OUTPUT_INVALID)
                return texts[0]
        except Exception:
            fail(C07_PROVIDER_OUTPUT_INVALID)
