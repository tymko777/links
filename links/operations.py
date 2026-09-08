"""Pure document operations shared by the UI and tests."""

from __future__ import annotations

from collections.abc import MutableSequence
from typing import TypeVar

Item = TypeVar("Item")


def move_by_id(
    items: MutableSequence[Item],
    source_id: str,
    target_id: str,
    get_id,
) -> bool:
    """Move one item before the target item.

    Returns ``True`` only when the sequence changed.  Keeping this operation
    pure and identity-based means UI drag-and-drop cannot accidentally depend
    on filtered visual positions.
    """

    if source_id == target_id:
        return False

    source_index = next(
        (index for index, item in enumerate(items) if get_id(item) == source_id),
        None,
    )
    target_index = next(
        (index for index, item in enumerate(items) if get_id(item) == target_id),
        None,
    )
    if source_index is None or target_index is None:
        return False

    item = items.pop(source_index)
    items.insert(target_index, item)
    return True