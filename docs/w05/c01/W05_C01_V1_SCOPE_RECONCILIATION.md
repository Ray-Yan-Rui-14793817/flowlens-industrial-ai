# Original v1 scope reconciliation

docs/01_scope.md remains unchanged. W05 is the single active v1 productization
line; roadmap alignment does not merge checkpoints or authorize W06.
~~~text
P0.1 Industrial Data Foundation = COMPLETE / VERIFIED
P0.2 Manufacturing Analytics = V1_RELEASE_DISPOSITION_REQUIRED
P0.3 Delivery Risk Prediction = V1_RELEASE_DISPOSITION_REQUIRED / NO_VALIDATED_DELAY_PROBABILITY_CLAIM
P0.4 Evidence-Grounded Investigation = CORE_COMPLETE / PRODUCTIZATION_ACTIVE
P0.5 Process & Transformation / ROI = V1_RELEASE_DISPOSITION_REQUIRED
P0.6 Evaluation = SUBSTANTIAL_FOUNDATION_COMPLETE / FINAL_PRODUCT_E2E_SECURITY_VALIDATION_REMAINS
P0.7 Deployable Demo = REQUIRED / NOT_COMPLETE
~~~
P0.2 retains OTD, Delay Rate, Cycle Time, WIP, Material Availability,
Supplier On-Time Rate, FPY and Rework Rate with canonical definition, range,
filters, sample size, limitations and evidence identity. C01 does not implement them.
P0.3 retains original prediction outputs as unresolved release scope; no validated
delay probability or risk score is claimed from current deterministic signals.
P0.4 retains Observed Facts, Hypotheses, Contradicting Evidence, Unknowns and
Next Investigation grounded in evidence without unsupported causal truth.
P0.5 retains Process Bottleneck -> Technology Fit -> AI Opportunity -> ROI ->
Human Approval -> Mock Action and original technology-fit distinctions.
C01 provides neither ROI nor action authority.
P0.6 retains numeric/ML/retrieval/citation/unsupported-claim/security/HGT-isolation/
failure-recovery controls; final product E2E/security acceptance remains.
P0.7 retains one-command startup, fixed seed, README, API documentation,
reproducible demo, final regression and limitations.

Later Human dispositions: IMPLEMENT, EXPLICITLY_DEFER_BY_HUMAN, or
EXPLICITLY_REMOVE_FROM_V1_BY_HUMAN. C01 cannot decide P0.2/P0.3/P0.5 or silently
delete any P0 promise. C02 application service, C03 API, C04 UI, C05 E2E/demo,
C06 release hardening/scope reconciliation/business acceptance remain roadmap.
