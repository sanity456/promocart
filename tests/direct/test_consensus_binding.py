"""Adversarial leader-payload and post-consensus binding regressions."""

import hashlib
import json

from tests.direct.test_promotion_rule_engine import CART, _evaluate, _publish


HONEST_LINES = [{"line_id": "L1", "category_ids": ["FOOD"], "category_mask": 1}]


def _hash(lines):
    wire = json.dumps(lines, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return "sha256:" + hashlib.sha256(wire.encode("ascii")).hexdigest()


def _captured(contract, direct_vm, merchant, shopper):
    program_id = _publish(contract, direct_vm, merchant)
    _evaluate(contract, direct_vm, shopper, program_id)
    return program_id


def test_validator_rejects_changed_categories_with_honest_hash(contract, direct_vm, direct_alice, direct_bob):
    _captured(contract, direct_vm, direct_alice, direct_bob)
    forged = {"line_categories": [{"line_id": "L1", "category_ids": [], "category_mask": 0}], "tag_sha256": _hash(HONEST_LINES)}
    assert direct_vm.run_validator(leader_result=forged) is False


def test_validator_rejects_changed_mask_with_honest_hash(contract, direct_vm, direct_alice, direct_bob):
    _captured(contract, direct_vm, direct_alice, direct_bob)
    forged = {"line_categories": [{"line_id": "L1", "category_ids": ["FOOD"], "category_mask": 0}], "tag_sha256": _hash(HONEST_LINES)}
    assert direct_vm.run_validator(leader_result=forged) is False


def test_validator_accepts_honest_complete_payload(contract, direct_vm, direct_alice, direct_bob):
    _captured(contract, direct_vm, direct_alice, direct_bob)
    assert direct_vm.run_validator() is True


def test_post_consensus_forgery_cannot_update_evaluation(contract, direct_vm, direct_alice, direct_bob, monkeypatch):
    from genlayer import gl

    program_id = _publish(contract, direct_vm, direct_alice)
    direct_vm.sender = direct_bob
    forged = {"line_categories": [{"line_id": "L1", "category_ids": [], "category_mask": 0}], "tag_sha256": _hash(HONEST_LINES)}
    monkeypatch.setattr(gl.vm, "run_nondet_unsafe", lambda *args: forged)
    with direct_vm.expect_revert("tag_hash_mismatch"):
        contract.evaluate_cart("CART-1", program_id, CART)
    assert contract.get_evaluation_count() == 0
