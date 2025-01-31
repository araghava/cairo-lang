from enum import Enum
from typing import Callable, Sequence

from starkware.cairo.common.hash_state import compute_hash_on_elements
from starkware.cairo.lang.vm.crypto import pedersen_hash
from starkware.python.utils import from_bytes
from starkware.starknet.services.api.contract_definition import CONSTRUCTOR_SELECTOR


class TransactionHashPrefix(Enum):
    DEPLOY = from_bytes(b"deploy")
    INVOKE = from_bytes(b"invoke")
    L1_HANDLER = from_bytes(b"l1_handler")


def calculate_transaction_hash_common(
    tx_hash_prefix: TransactionHashPrefix,
    contract_address: int,
    entry_point_selector: int,
    calldata: Sequence[int],
    chain_id: int,
    additional_data: Sequence[int],
    hash_function: Callable[[int, int], int] = pedersen_hash,
) -> int:
    """
    Calculates the transaction hash in the StarkNet network - a unique identifier of the
    transaction.
    The transaction hash is a hash chain of the following information:
        1. A prefix that depends on the transaction type.
        2. Contract address.
        3. Entry point selector.
        4. A hash chain of the calldata.
        5. The network's chain ID.
    Each hash chain computation begins with 0 as initialization and ends with its length appended.
    The length is appended in order to avoid collisions of the following kind:
    H([x,y,z]) = h(h(x,y),z) = H([w, z]) where w = h(x,y).
    """
    calldata_hash = compute_hash_on_elements(data=calldata, hash_func=hash_function)
    data_to_hash = [
        tx_hash_prefix.value,
        contract_address,
        entry_point_selector,
        calldata_hash,
        chain_id,
        *additional_data,
    ]

    return compute_hash_on_elements(
        data=data_to_hash,
        hash_func=hash_function,
    )


def calculate_deploy_transaction_hash(
    contract_address: int,
    constructor_calldata: Sequence[int],
    chain_id: int,
    hash_function: Callable[[int, int], int] = pedersen_hash,
) -> int:
    return calculate_transaction_hash_common(
        tx_hash_prefix=TransactionHashPrefix.DEPLOY,
        contract_address=contract_address,
        entry_point_selector=CONSTRUCTOR_SELECTOR,
        calldata=constructor_calldata,
        chain_id=chain_id,
        additional_data=[],
        hash_function=hash_function,
    )
