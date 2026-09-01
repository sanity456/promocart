import hashlib
import json
from pathlib import Path

from gltest import get_contract_factory, get_validator_factory
from gltest.accounts import create_accounts
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionStatus
from gltest.utils import extract_contract_address


def _ok(receipt):
    assert tx_execution_succeeded(receipt), json.dumps(receipt, default=str)


def _context(fragment, response):
    validators = get_validator_factory().batch_create_mock_validators(
        5,
        mock_llm_response={"nondet_exec_prompt": {fragment: json.dumps(response)}},
    )
    return {
        "validators": [validator.to_dict() for validator in validators],
        "genvm_datetime": "2026-08-25T12:00:00Z",
    }


def _deploy(contract_file, owner_account):
    factory = get_contract_factory(
        contract_file_path=Path(__file__).resolve().parents[2] / "contracts" / contract_file
    )
    receipt = factory.deploy_contract_tx(
        args=[],
        account=owner_account,
        wait_transaction_status=TransactionStatus.FINALIZED,
    )
    _ok(receipt)
    return factory, extract_contract_address(receipt)


def _send(method, args, context=None):
    if context is None:
        receipt = method(args=args).transact(
            wait_transaction_status=TransactionStatus.FINALIZED
        )
    else:
        receipt = method(args=args).transact(
            transaction_context=context,
            wait_transaction_status=TransactionStatus.FINALIZED,
        )
    _ok(receipt)
    return receipt


def test_five_validator_tagging_and_promotion_vm_flow():
    merchant_account, shopper_account = create_accounts(2)
    factory, address = _deploy("promotion_rule_engine.py", merchant_account)
    merchant = factory.build_contract(address, account=merchant_account)
    shopper = factory.build_contract(address, account=shopper_account)
    program_id = f"{str(merchant_account.address).lower()}:AUTUMN"
    evaluation_id = f"{str(shopper_account.address).lower()}:CART-1"
    program = json.dumps({
        "categories": [{"id": "FOOD", "description": "Packaged pantry food offered by the merchant."}],
        "promotions": [{"id": "SAVE10", "required_category_mask": 1, "minimum_subtotal": 500, "discount_bps": 1000, "maximum_discount": 1000, "priority": 1, "exclusive_group": "MAIN", "stackable": True}],
    })
    cart = json.dumps({"lines": [{"id": "L1", "description": "Two pantry food bundles", "quantity": 2, "unit_price": 1000}]})
    _send(merchant.publish_program, ["AUTUMN", program, "Frozen promotion terms for the registered public cart categories.", "merchant-terms-snapshot"])
    _send(
        shopper.evaluate_cart,
        ["CART-1", program_id, cart],
        _context("Tag public cart lines", {"line_categories": [{"line_id": "L1", "category_ids": ["FOOD"]}]}),
    )
    evaluation = shopper.get_evaluation(args=[evaluation_id]).call()
    assert evaluation["discount_units"] == 200
    assert evaluation["net_units"] == 1800
