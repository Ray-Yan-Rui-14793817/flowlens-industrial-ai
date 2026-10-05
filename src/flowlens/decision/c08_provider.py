"""Bounded OpenAI Responses API transport for W03-C08."""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from dataclasses import dataclass
from importlib import import_module
from typing import Protocol, cast

from flowlens.decision.c08_policy import (
    MAX_OUTPUT_TOKENS,
    PROVIDER_NAME,
    REASONING_EFFORT,
    REQUESTED_MODEL,
    SDK_MAX_RETRIES,
    TIMEOUT_SECONDS,
)

_OPENAI_SDK = import_module("openai")
OpenAI = cast(Callable[..., object], _OPENAI_SDK.OpenAI)
OpenAIError = cast(type[Exception], _OPENAI_SDK.OpenAIError)


@dataclass(frozen=True, slots=True)
class ProviderRequest:
    system_prompt: str
    context_json: str
    output_schema_json: str


@dataclass(frozen=True, slots=True)
class ProviderResponse:
    output_text: str
    resolved_model: str | None


class ExplanationProvider(Protocol):
    def generate(self, request: ProviderRequest) -> ProviderResponse:
        """Return one ephemeral provider response for the bounded request."""


class _ResponsesResource(Protocol):
    def create(self, **kwargs: object) -> object: ...


class _OpenAIClient(Protocol):
    @property
    def responses(self) -> _ResponsesResource: ...


class C08ProviderError(RuntimeError):
    """Expected failure at the bounded C08 provider boundary."""


class C08ProviderTransportError(C08ProviderError):
    """The official provider SDK reported a transport or API failure."""


class C08ProviderRefusal(C08ProviderError):
    """The provider did not return a completed text response."""


class OpenAIExplanationProvider:
    """Official SDK adapter with the exact frozen C08 request surface."""

    provider_name = PROVIDER_NAME
    requested_model = REQUESTED_MODEL

    def __init__(self, api_key: str, *, client: _OpenAIClient | None = None) -> None:
        if not api_key:
            raise ValueError("api_key must be nonempty")
        self._client = client or cast(
            _OpenAIClient,
            OpenAI(
                api_key=api_key,
                timeout=TIMEOUT_SECONDS,
                max_retries=SDK_MAX_RETRIES,
            ),
        )

    @classmethod
    def from_environment(cls) -> OpenAIExplanationProvider | None:
        """Read only the authorized key variable; never read files or persist it."""

        api_key = os.environ.get("FLOWLENS_OPENAI_API_KEY")
        return cls(api_key) if api_key else None

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        schema = json.loads(request.output_schema_json)
        try:
            response = self._client.responses.create(
                model=REQUESTED_MODEL,
                instructions=request.system_prompt,
                input=f"RUNTIME_DATA\n{request.context_json}",
                reasoning={"effort": REASONING_EFFORT},
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "flowlens_w03_c08_output",
                        "strict": True,
                        "schema": schema,
                    }
                },
                tools=[],
                stream=False,
                store=False,
                max_output_tokens=MAX_OUTPUT_TOKENS,
            )
        except OpenAIError as error:
            raise C08ProviderTransportError("official provider SDK request failed") from error
        status = getattr(response, "status", None)
        if status not in (None, "completed"):
            raise C08ProviderRefusal("provider response was not completed")
        for item in getattr(response, "output", ()) or ():
            for content in getattr(item, "content", ()) or ():
                if getattr(content, "type", None) == "refusal" or getattr(content, "refusal", None):
                    raise C08ProviderRefusal("provider refused the request")
        output_text = getattr(response, "output_text", None)
        if type(output_text) is not str or not output_text:
            raise C08ProviderRefusal("provider returned no output text")
        model = getattr(response, "model", None)
        resolved_model = model if type(model) is str and model else None
        return ProviderResponse(output_text=output_text, resolved_model=resolved_model)
