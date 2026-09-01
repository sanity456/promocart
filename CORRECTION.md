# Correction and release record

Repository: promocart

Contract: PromotionRuleEngine

Corrected release verified: 2026-09-01T08:54:12.515110Z

## Findings applied

This repository was checked against both steward findings from the rejected Boxcomplete and Baggate submissions:

1. A leader-provided digest is not proof of its attached substantive payload. Every result that affects state must be canonicalized, independently compared, and rebound after consensus.
2. A shared permissionless registry with fixed global capacity can be captured or exhausted. Operational catalogs must be explicitly owner-scoped, bounded per catalog, or safely reclaimable.
3. Corrected repository source is insufficient when the submitted Studio/Explorer address still runs an earlier build. The active address, deployed source, ABI, transaction, and evidence URLs must identify one release.

## Contract-specific correction

The validator now canonicalizes the leader's attached line-category plan, recomputes every category mask and the tag digest from those lines, compares that full payload with its independent result, and repeats the binding check after consensus before discount state is written.

## Verified release lock

Current StudioNet address: 0xf407b36837AE85e92CfF72DE5C9E7ac83c391912

Deployment transaction: 0x5ac09126af2dcb7540b4e01f8a896220e326e91d66fc30a061a24bd8a92bb5fa

Source SHA-256: 64ab022ce7ffe5d3e786094384270aa4366c92efba2a0bba624d84296a6d6b4d

Superseded address: 0x84f49eB2B5CcD8bcF94DC6780Ce8c071a4Ac7E07

The deployment manifest records exact byte-for-byte source readback, exact full ABI/schema equality, successful finalized execution for all 3 release transactions, role-separated external wallets, and the final state observed from StudioNet. The superseded address is historical only and must not be used in a new submission.

## Regression evidence

GenVM lint and strict typecheck: pass

Direct tests: 12 pass

Five-validator integration tests: 1 pass

Leader-payload or post-consensus injection regression tests: pass

Registry isolation and reclaim tests: not applicable

## Review boundary

No web collection. Category definitions, promotions, terms, cart lines, and source references are public caller declarations.

It moves no money, authenticates no merchant, executes no sale, and does not establish price, tax, or consumer-law rights.

This record documents the implemented controls and verified release. It does not promise a particular human review outcome.
