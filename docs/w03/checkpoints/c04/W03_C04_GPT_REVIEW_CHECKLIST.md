# W03-C04 GPT Review Checklist

The independent reviewer must verify:

- repository and exact-SHA evidence bind the reviewed implementation and report commits;
- only authorized implementation/report paths changed and main remains unchanged;
- registry cardinality, keys, mappings, reasons, limitations, fixed parameters and canonical
  identities match the frozen specs;
- supplied C03 artifacts are canonically rebuilt and tampering fails closed;
- stress probes make no efficacy, benefit, causal, probability or recommendation claim;
- earlier decision times never consume a future-containing full dataset;
- affected entities and measurements are independently derived from business data, not HGT;
- the business-only adapter neither imports nor constructs HGT and legacy W2/HGT behavior is
  byte/canonically compatible;
- runtime capability audits and complete local/CI gates pass;
- the final state is `REVIEW_READY`, not accepted, closed or advanced to C05.

```text
GPT C04 REVIEW = PENDING
HUMAN C04 ACCEPTANCE = PENDING
C04 CLOSED = NO
C05 AUTHORIZED = NO
```
