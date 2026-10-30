# C01 recovery A1 context lock

Readback before authoring/proof: main -> A -> B''' -> C2 -> G3 -> C01-I.
main=2f1627342ff2b04d8324fbffec3db2e230b302e0;
A=e61c7b1139e5bf3020f0d79994a3be0aea8072b5;
B'''=416a3ab9c1075cefe5944b7440a47c6d9740373e;
C2=2af8fcd9c3f2fce5121b1b7a3ecead6067eb8aec;
G3=01be49cf51a45b8ea1b0910cb8c615a1dfc441c5;
G3 tree=5e47b452d57be9de0bc138fe019b76598c0a2c37.
PR12/13/14 remain open/ready/unmerged with2/18,3/23,4/31 commits/files respectively.
G3 native40827247539/CI160 attempt1 SUCCESS and actual UNKNOWN/FULL measured R46 PASS.
G3 source state ADMISSION_STAGED, product absent. C01-I is NOT_CREATED at authoring.

Current controlling task W05_C01_PREFREEZE_STOP_RECOVERY_RESUME_R3_TASK_AMENDMENT_A1,
SHA256 f627c4528fa6c9a7b458145405c50af24eb51ff954816a7174674f5e0ea5f46f.
Parent unamended task8f25d1e30f93036cb1c87646983f2b82e16101ae8f3a34f241d895755f7226b6 is superseded.
Deep Review R2 c3b87ac8889a94c3536d28ea05ba9a5d735339f031fb2f34f93fbb0d6b263e3a controls the two
task findings; previous Review R1 PASS_REVOKED_BY_NEW_EVIDENCE stays preserved.
A1 design10be32829b504c755dff3be712699c4e2314a4939d04ded4bb360812a2523d60;
A1 review425b68932b9ebaa5f04b0e62eac1a20b8d17b468d30371544fbb86238660f326;
Human PASS/ACCEPTED/APPROVED_FOR_THIS_TASK_ONLY. No additional acceptance is needed for this task.

Old C01 STOPPED_PREFREEZE_W04_INVARIANT_FAILURE is preserved, not repaired retroactively.
Original evidence2d7e7a0b9ebbe517985c201d33af8e0a12fd67b19bfe42922885812734857aea;
manifest158d20c888e6115828fe73814cdb88d512fdd13418e1664edb4939573d01c214;
full original source map049c7d6a21a5cc1d4403ff21aa40ed4b692e74d6e36f6bab2f115cecc347537c.
188/188 original evidence and15/15 actual source bytes must validate before copying.
G3 post-native evidencec2d0ca7bb7904c08af71d571c88427a65c9a62803652e90aaf19906dd2359f69,
169/169 exact root manifest, is predecessor proof only.

The eight immutable paths are the three semantic docs, three product source files and two product
test files. Their old manifest hashes stay exact. The seven rebased files are the two G3-based
state docs plus secondary review, authorization, context, harness and GPT checklist. Exact scope
is enumerated by the authorization contract; no sixteenth file. Both state docs preserve all12
Frozen G0 lines exact-once with a historical G0 referent and13 current authority lines exact-once
outside that block. Never repurpose the frozen NOT_AUTHORIZED projection as current C01 authority.

Prefreeze126 product tests and quality/schema/vectors/capability proof -> candidate freeze ->
SHADOW_C01_I -> full committed shadow proof -> actual C01-I exact shadow tree -> fresh full actual
proof -> first new PR/nativeattempt1 -> measured C01-I R46 -> reports/review. Source materialization
must be BOOTSTRAP_MATERIALIZED at each validated exact head, not at G3. Policy and admitted blobs
match across shadow/actual; expected_head/head_sha/materialization_sha/proof_sha256 rebind to each.

FULL_RAW_PLAN minus exactly head_sha and plan_sha256 is the normalized object. Compare every
remaining field, including complete files/shards, weights, collection and historical identities.
Independently validate each raw head and its own seal. No copied shadow seal, total-node acceptance
constant or fixed successor test count. Shadow SHA need not equal or differ from actual SHA.

All formal/native/review proof is pending at authoring. First material formal failure STOPs;
no patch/retry/replacement/second commit. Isolated task-only _test DBs; no inherited GIT_CONFIG;
command-local Git only. New target branch feat/w05-c01-product-surface-contract-r3, one normal push
and one ready/unmerged PR to main, expected5commits44files after recomputation. Preserve predecessors.
No closeout/C02/merge/auto-merge/queue/branch deletion/W06/release or automatic advancement.
