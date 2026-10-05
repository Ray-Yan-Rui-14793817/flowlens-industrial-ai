"""Official SDK adapter request-shape and configuration tests for W03-C08."""

from __future__ import annotations

import json

import pytest
from pydantic import SecretStr

from flowlens.config import Settings
from flowlens.decision.c08_context import build_explanation_context
from flowlens.decision.c08_explanation import explain_decision_packet
from flowlens.decision.c08_policy import (
    MAX_OUTPUT_TOKENS,
    REASONING_EFFORT,
    REQUESTED_MODEL,
    RUNTIME_SYSTEM_PROMPT,
    SDK_MAX_RETRIES,
    TIMEOUT_SECONDS,
)
from flowlens.decision.c08_provider import (
    C08ProviderRefusal,
    C08ProviderTransportError,
    OpenAIError,
    OpenAIExplanationProvider,
    ProviderRequest,
)
from flowlens.decision.enums import ExplanationMode
from flowlens.decision.serialization import canonical_json_text
from test_c08_explanation import make_packet


class FakeSDKResponse:
    status = "completed"
    model = "gpt-5.6-terra-2026-09-01"
    output: tuple[object, ...] = ()

    def __init__(self, output_text: str) -> None:
        self.output_text = output_text


class FakeResponsesResource:
    def __init__(self, response: object) -> None:
        self.response = response
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


class FakeSDKClient:
    def __init__(self, response: object) -> None:
        self.responses = FakeResponsesResource(response)


def test_openai_adapter_uses_exact_bounded_responses_request() -> None:
    client = FakeSDKClient(FakeSDKResponse("{}"))
    provider = OpenAIExplanationProvider("test-key", client=client)
    request = ProviderRequest(
        system_prompt=RUNTIME_SYSTEM_PROMPT,
        context_json='{"schema_version":"w03-c08-context-v1"}',
        output_schema_json=json.dumps(
            {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
            separators=(",", ":"),
        ),
    )

    response = provider.generate(request)

    assert response.output_text == "{}"
    assert response.resolved_model == "gpt-5.6-terra-2026-09-01"
    assert len(client.responses.calls) == 1
    payload = client.responses.calls[0]
    assert payload["model"] == REQUESTED_MODEL
    assert payload["instructions"] == RUNTIME_SYSTEM_PROMPT
    assert payload["input"] == f"RUNTIME_DATA\n{request.context_json}"
    assert payload["reasoning"] == {"effort": REASONING_EFFORT}
    assert payload["tools"] == []
    assert payload["stream"] is False
    assert payload["store"] is False
    assert payload["max_output_tokens"] == MAX_OUTPUT_TOKENS
    assert "temperature" not in payload
    assert "previous_response_id" not in payload
    text = payload["text"]
    assert isinstance(text, dict)
    assert text["format"]["type"] == "json_schema"
    assert text["format"]["strict"] is True


def test_adapter_rejects_noncompleted_or_empty_response() -> None:
    failed = FakeSDKResponse("")
    failed.status = "failed"
    provider = OpenAIExplanationProvider("test-key", client=FakeSDKClient(failed))
    request = ProviderRequest(
        system_prompt=RUNTIME_SYSTEM_PROMPT,
        context_json="{}",
        output_schema_json=json.dumps({"type": "object"}),
    )

    with pytest.raises(C08ProviderRefusal):
        provider.generate(request)


def test_adapter_wraps_official_sdk_failure_as_stable_transport_error() -> None:
    provider = OpenAIExplanationProvider(
        "test-key",
        client=FakeSDKClient(OpenAIError("sdk failure")),
    )
    request = ProviderRequest(
        system_prompt=RUNTIME_SYSTEM_PROMPT,
        context_json="{}",
        output_schema_json=json.dumps({"type": "object"}),
    )

    with pytest.raises(C08ProviderTransportError) as caught:
        provider.generate(request)

    assert isinstance(caught.value.__cause__, OpenAIError)


def test_settings_default_and_opt_in_surface(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FLOWLENS_C08_EXPLAINER_MODE", raising=False)
    monkeypatch.delenv("FLOWLENS_OPENAI_API_KEY", raising=False)
    database_url = SecretStr("postgresql+psycopg://flowlens:flowlens@localhost/flowlens")

    default = Settings(database_url=database_url, _env_file=None)
    assert default.c08_explainer_mode == "template"
    assert default.openai_api_key is None

    monkeypatch.setenv("FLOWLENS_C08_EXPLAINER_MODE", "openai")
    monkeypatch.setenv("FLOWLENS_OPENAI_API_KEY", "test-secret")
    enabled = Settings(database_url=database_url, _env_file=None)
    assert enabled.c08_explainer_mode == "openai"
    assert enabled.openai_api_key is not None
    assert enabled.openai_api_key.get_secret_value() == "test-secret"
    assert "test-secret" not in repr(enabled)


def test_official_sdk_constructor_policy_is_frozen(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: dict[str, object] = {}

    class StubClient:
        responses = FakeResponsesResource(FakeSDKResponse("{}"))

    def fake_openai(**kwargs: object) -> object:
        observed.update(kwargs)
        return StubClient()

    monkeypatch.setattr("flowlens.decision.c08_provider.OpenAI", fake_openai)
    OpenAIExplanationProvider("test-key")

    assert observed == {
        "api_key": "test-key",
        "timeout": TIMEOUT_SECONDS,
        "max_retries": SDK_MAX_RETRIES,
    }


def test_provider_receives_no_hidden_input() -> None:
    packet = make_packet()
    context = build_explanation_context(packet)

    from test_c08_explanation import FakeProvider, responses, valid_output

    provider = FakeProvider(responses([valid_output(context)]))
    result = explain_decision_packet(packet, provider=provider, mode="openai")

    assert result.mode is ExplanationMode.BOUNDED_LLM
    request = provider.calls[0]
    assert request.system_prompt == RUNTIME_SYSTEM_PROMPT
    assert request.context_json == canonical_json_text(context)
    assert set(json.loads(request.output_schema_json)) == {
        "$id",
        "$schema",
        "additionalProperties",
        "properties",
        "required",
        "title",
        "type",
    }
