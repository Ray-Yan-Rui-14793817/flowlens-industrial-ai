# W03-DEVCTRL-01 → W03-C03 Transition Notice

## Superseded execution path

Do not execute a package that authorizes:

```text
C03 Signal/Diagnosis implementation
+
CI workflow redesign
```

inside the same implementation checkpoint.

The C03 semantic design may be retained as design input, but C03 Codex implementation
must wait until DEVCTRL-01 is closed.

## Required sequence

```text
C02 CLOSED
→ DEVCTRL-01
→ GPT review
→ Human acceptance
→ DEVCTRL-01 closeout
→ C03-A package normalization against closed DEVCTRL baseline
→ Human C03 authorization
→ C03 implementation
```

## C03 after DEVCTRL

C03 must consume:

```text
P/C/I/F deterministic classification
FULL implementation exact-SHA gate
PUBLICATION report exact-SHA gate
stable Verification gate
```

C03 must not redesign those mechanisms unless a separately authorized DEVCTRL repair is
required.
