# Architecture

Project: PromotionRuleEngine

Reusable primitive: semantic multi-tag plan -> category bitmap -> deterministic priority/exclusivity discount VM.

The contract separates caller-attested public inputs, validator-agreed semantic fields, deterministic state transitions, and role-bound final actions. It stores canonical JSON strings in GenVM maps, validates every identifier and bound before consensus, and keeps source references explicitly unverified.

The mechanism is not a renamed assessment record. Its state transitions, role topology, storage layout, deterministic algorithm, and public ABI are specific to this project.

<!-- correction-release-start -->
## Consensus and storage safety boundary

The validator now canonicalizes the leader's attached line-category plan, recomputes every category mask and the tag digest from those lines, compares that full payload with its independent result, and repeats the binding check after consensus before discount state is written.

The on-chain state transition consumes only the canonical value returned by the post-consensus binding boundary. This contract does not expose a shared permissionless fixed-cap operational registry.
<!-- correction-release-end -->
