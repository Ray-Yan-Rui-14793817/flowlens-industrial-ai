# FlowLens Industrial AI — W03-C08 GPT Review Checklist

Independent review should verify:

- actual model input is derived only from the supplied DecisionPacket;
- no C07, HGT, evaluation, database, filesystem, or retrieval input exists;
- prompt bytes/hash and output schema are exact;
- the provider is OpenAI Responses API with the frozen model/settings;
- tools are absent and SDK retries are zero;
- recommendation, candidates, ordering, trust, and packet bytes are unchanged;
- grounding rejects invented facts, identifiers, causal upgrades, numeric claims,
  authority expansion, injection behavior, and simulation-efficacy overclaims;
- only schema invalidity receives one repair call;
- deterministic and degraded templates are valid C01 ExplanationRecords;
- all H01-H46 evidence and exact-SHA CI evidence are present;
- no forbidden path, operational mutation, or C09 work occurred.

GPT review and Human acceptance remain pending after the Codex development round.
