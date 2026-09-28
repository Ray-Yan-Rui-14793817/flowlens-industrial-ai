# FlowLens Industrial AI — W03-C07 HGT Binding Contract

## Protected input validation

Before metrics, C07 independently and fail-closed validates:

1. the scenario dataset ID equals HGT `scenario_dataset_version_id`;
2. recomputed scenario business content hash equals both stored scenario hash
   and the scenario packet run hash;
3. scenario packet run dataset ID equals both scenario dataset and HGT ID;
4. recomputed baseline business hash equals its stored hash;
5. baseline dataset ID equals HGT `baseline_dataset_version_id`;
6. paired baseline packet dataset ID/hash equals the baseline dataset;
7. reconstructed frozen W2 HGT semantics reproduce `hgt_hash` and `hgt_id`;
8. every supplied packet and nested artifact passes its unchanged C01 identity
   and frozen C05 provenance/binding boundary;
9. the effectful scenario packet order belongs to the protected derived set of
   HGT-affected Sales Orders.

C07 reuses `canonical_content_hash` and the existing W2
`HiddenGroundTruth`/`canonical_hgt_payload` identity. It defines no second
canonicalizer or HGT identity.

## Affected-order derivation

Order mappings are frozen:

```text
fact_sales_order.sales_order_id -> sales_order_id
fact_work_order.work_order_id -> sales_order_id
fact_operation.operation_id -> work_order_id -> sales_order_id
fact_material_requirement.material_requirement_id -> work_order_id -> sales_order_id
fact_quality_inspection.inspection_id -> work_order_id -> sales_order_id
fact_rework.rework_id -> work_order_id -> sales_order_id
fact_delivery.delivery_id -> sales_order_id
```

Every HGT affected ID on a mapped table must resolve to a scenario row. Missing
or cross-bound rows fail closed. Purchase orders, inventory, materials,
suppliers, products and work centers do not alone establish an affected order.

## Baseline pairing

If the scenario order exists in the baseline, a baseline packet is required
and must match order, decision time, contract bundle, and tool registry.

If the order was created only by a Capacity arrival scenario, the baseline
dataset is still required and the baseline packet must be absent. That mode is
non-observable unless the HGT for that order also proves a queue-observable
path. A baseline packet must never be fabricated for a nonexistent order.

## Isolation

HGT is admitted only after the runtime packet is frozen. It never enters C01-C06
builders, runtime provenance, `DecisionPacket`, operational rows, a public
artifact, or any normal runtime import graph.
