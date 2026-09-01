"""Direct tests for the deterministic promotion VM."""

import json


def _program_json(promotions=None):
    return json.dumps({
        "categories": [{"id": "FOOD", "description": "Packaged pantry food offered by the merchant."}],
        "promotions": promotions or [{"id": "SAVE10", "required_category_mask": 1, "minimum_subtotal": 500, "discount_bps": 1000, "maximum_discount": 1000, "priority": 1, "exclusive_group": "MAIN", "stackable": True}],
    })


CART = json.dumps({"lines": [{"id": "L1", "description": "Two pantry food bundles", "quantity": 2, "unit_price": 1000}]})


def _publish(contract, vm, merchant, program=None):
    vm.sender = merchant
    return contract.publish_program("AUTUMN", program or _program_json(), "Frozen promotion terms for the registered public cart categories.", "merchant-terms-snapshot")


def _evaluate(contract, vm, shopper, program_id, response=None):
    vm.sender = shopper
    vm.mock_llm(r".*Tag public cart lines.*", json.dumps(response or {"line_categories": [{"line_id": "L1", "category_ids": ["FOOD"]}]}))
    return contract.evaluate_cart("CART-1", program_id, CART)


def test_publishes_closed_program(contract, direct_vm, direct_alice):
    program_id = _publish(contract, direct_vm, direct_alice)
    assert contract.get_program(program_id)["program_sha256"].startswith("sha256:")


def test_invalid_priority_collision_rejected(contract, direct_vm, direct_alice):
    promotions = [
        {"id": "A", "required_category_mask": 1, "minimum_subtotal": 0, "discount_bps": 100, "maximum_discount": 10, "priority": 1, "exclusive_group": "A", "stackable": True},
        {"id": "B", "required_category_mask": 1, "minimum_subtotal": 0, "discount_bps": 100, "maximum_discount": 10, "priority": 1, "exclusive_group": "B", "stackable": True},
    ]
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("invalid_promotion"):
        contract.publish_program("BAD", _program_json(promotions), "Frozen promotion terms that are long enough for validation.", "source")


def test_vm_calculates_discount(contract, direct_vm, direct_alice, direct_bob):
    program_id = _publish(contract, direct_vm, direct_alice)
    evaluation_id = _evaluate(contract, direct_vm, direct_bob, program_id)
    evaluation = contract.get_evaluation(evaluation_id)
    assert evaluation["subtotal_units"] == 2000
    assert evaluation["discount_units"] == 200
    assert evaluation["net_units"] == 1800


def test_no_tags_means_no_discount(contract, direct_vm, direct_alice, direct_bob):
    program_id = _publish(contract, direct_vm, direct_alice)
    evaluation_id = _evaluate(contract, direct_vm, direct_bob, program_id, {"line_categories": [{"line_id": "L1", "category_ids": []}]})
    assert contract.get_evaluation(evaluation_id)["discount_units"] == 0


def test_exclusive_group_applies_first_priority(contract, direct_vm, direct_alice, direct_bob):
    promotions = [
        {"id": "FIRST", "required_category_mask": 1, "minimum_subtotal": 0, "discount_bps": 1000, "maximum_discount": 500, "priority": 1, "exclusive_group": "ONE", "stackable": True},
        {"id": "SECOND", "required_category_mask": 1, "minimum_subtotal": 0, "discount_bps": 2000, "maximum_discount": 500, "priority": 2, "exclusive_group": "ONE", "stackable": True},
    ]
    program_id = _publish(contract, direct_vm, direct_alice, _program_json(promotions))
    evaluation_id = _evaluate(contract, direct_vm, direct_bob, program_id)
    assert [item["promotion_id"] for item in contract.get_evaluation(evaluation_id)["applied_promotions"]] == ["FIRST"]


def test_nonstackable_stops_later_rule(contract, direct_vm, direct_alice, direct_bob):
    promotions = [
        {"id": "STOP", "required_category_mask": 1, "minimum_subtotal": 0, "discount_bps": 500, "maximum_discount": 500, "priority": 1, "exclusive_group": "A", "stackable": False},
        {"id": "LATER", "required_category_mask": 1, "minimum_subtotal": 0, "discount_bps": 500, "maximum_discount": 500, "priority": 2, "exclusive_group": "B", "stackable": True},
    ]
    program_id = _publish(contract, direct_vm, direct_alice, _program_json(promotions))
    evaluation_id = _evaluate(contract, direct_vm, direct_bob, program_id)
    assert len(contract.get_evaluation(evaluation_id)["applied_promotions"]) == 1


def test_bad_model_tag_fails_without_evaluation(contract, direct_vm, direct_alice, direct_bob):
    program_id = _publish(contract, direct_vm, direct_alice)
    with direct_vm.expect_revert("[LLM_ERROR] invalid_line_category"):
        _evaluate(contract, direct_vm, direct_bob, program_id, {"line_categories": [{"line_id": "L1", "category_ids": ["NOPE"]}]})
    assert contract.get_evaluation_count() == 0


def test_merchant_deactivates_program(contract, direct_vm, direct_alice):
    program_id = _publish(contract, direct_vm, direct_alice)
    direct_vm.sender = direct_alice
    contract.deactivate_program(program_id)
    assert contract.get_program(program_id)["active"] is False
