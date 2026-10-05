# W03-DEVCTRL-01 Historical Replay Matrix

The classifier must replay accepted W03 history.

At minimum, verify these accepted examples by actual Git diff when objects are present:

| Commit / delta | Expected |
|---|---|
| C01 implementation `f779c9fd77f617e6050d5eefa91f711851c86a4f` | FULL |
| C01 implementation evidence `abc9bf...` | PUBLICATION |
| C01 repair `889f29...` | FULL |
| C01 repair evidence `0930da...` | PUBLICATION |
| C01 closeout `c626126a81fe07b5d1f670deaeaadc809f6bea55` | PUBLICATION if delta is only allowlisted publication paths; otherwise FULL |
| C02 implementation `54e28d03c55a6baed58008210d7175565b4d166e` | FULL |
| C02 harness/test update `d0e6e598afb1d380331619ba02fae95fd872479f` | FULL |
| C02 evidence `af742b7bbc602a66eaea89774e94a69e7825d814` | PUBLICATION |
| C02 repair `90767ae555178db3d7af4cc6555fa7593ac056bf` | FULL |
| C02 repair evidence `e222b85f85ef3d419f22b761457973a167f34231` | PUBLICATION |
| C02 closeout `28173582661bc4bba5f254928ab8a9bbb5de63a0` | FULL if authoritative Sprint control was edited |

Important:

The replay oracle is the **frozen class contract**, not a historical label.

For example, a closeout commit that touched `docs/sprints/**` must now classify as CONTROL/FULL,
even if an earlier optimization proposal called all closeout commits publication.

This prevents history from weakening the final control-path rule.
