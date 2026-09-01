# PromotionRuleEngine

A reusable closed promotion VM where validators tag cart lines with catalog categories and deterministic code executes priority, minimum, exclusivity, stackability, basis-point, and cap rules.

The repository is standalone and the contract is reusable: one deployment can hold multiple independent records for unrelated callers. It has no frontend and moves no funds.

## Native mechanism

semantic multi-tag plan -> category bitmap -> deterministic priority/exclusivity discount VM.

## Actors

merchant, shopper, GenLayer validators.

## Source boundary

No web collection. Category definitions, promotions, terms, cart lines, and source references are public caller declarations.

## Safety boundary

It moves no money, authenticates no merchant, executes no sale, and does not establish price, tax, or consumer-law rights.

All inputs and results are public. Untrusted public data is delimited in prompts and cannot change the closed response schema. A malformed or non-consensus model result fails without committing the intended state transition.

## Verification

    genvm-lint check contracts/promotion_rule_engine.py
    genvm-lint typecheck contracts/promotion_rule_engine.py --strict
    python -m pytest tests/direct -q -p no:cacheprovider
    python tests/run_glsim.py --port 4000 --validators 5 --no-browser
    python -m pytest tests/integration -q -s -p no:cacheprovider

See ARCHITECTURE.md, SECURITY.md, SOURCE_PROVENANCE.md, AUDIT.md, SUBMISSION_CHECKLIST.md, and deployments/studionet.json.

MIT licensed.

<!-- correction-release-start -->
## Corrected release integrity

The full twelve-repository correction audit applied both steward findings to this contract. The validator now canonicalizes the leader's attached line-category plan, recomputes every category mask and the tag digest from those lines, compares that full payload with its independent result, and repeats the binding check after consensus before discount state is written.

The current StudioNet release is `0xf407b36837AE85e92CfF72DE5C9E7ac83c391912`. Its source bytes and full schema were read back from StudioNet and matched this repository exactly. Use `CORRECTION.md`, `REVIEW_RESPONSE.txt`, and the commit-pinned `deployments/studionet.json` for submission evidence; do not reuse the superseded address `0x84f49eB2B5CcD8bcF94DC6780Ce8c071a4Ac7E07`.
<!-- correction-release-end -->
