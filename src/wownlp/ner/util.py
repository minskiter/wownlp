from typing import List, Tuple, Set


def is_span_intersect(a: Tuple[int,int], b: Tuple[int,int]):
    """
    Determine if two spans intersect.
    a[0]<=b[1] and b[0]<=a[1]

    Args:
        a (Tuple[int,int]): First span
        b (Tuple[int,int]): Second span

    Returns:
        bool: True if intersect, otherwise False.
    """
    return a[0]<=b[1] and b[0]<=a[1]

def is_span_nested(a: Tuple[int,int], b: Tuple[int,int])->bool:
    """
    Determine if two spans nested.
    (b[0]<=a[0] and a[1]<=b[1]) or (a[0]<=b[0] and b[1]<=a[1])

    Args:
        a (Tuple[int,int]): First span
        b (Tuple[int,int]): Second span

    Returns:
        bool: True if nested, otherwise False.
    """
    return (b[0]<=a[0] and a[1]<=b[1]) or (a[0]<=b[0] and b[1]<=a[1])

def decode_sequence_labels(sequence: List[str], offset=0, delimiter="-"):
    """
    decode sequence labels.

    Args:
        sequence (List[str]): Labels sequence.
        offset (int, optional): The offset of start position. Defaults to 0.
        delimiter (str, optional): The delimiter of labels sequence. Defaults to "-".

    Raises:
        ValueError: Invalid labels

    Returns:
        entities (Set[Tuple[int, int, str]]): The set of entities. The range is [l,r].
    """
    entities = set()
    start = -1
    entity = None
    for end in range(len(sequence)):
        if sequence[end].startswith("B") or sequence[end].startswith("S"):
            if start>=0 and entity is not None:
                entities.add((start-offset, end-offset-1, entity))
            start = end
            entity = delimiter.join(sequence[end].split(delimiter)[1:])
        elif sequence[end].startswith("M") or sequence[end].startswith("I"):
            continue
        elif sequence[end].startswith("E"):
            if start>=0 and entity is not None:
                entities.add((start-offset, end-offset, entity))
            start = -1
            entity = None
        elif sequence[end].startswith("O"):
            if start>=0 and entity is not None:
                entities.add((start-offset, end-offset-1, entity))
            start = -1
            entity = None
        else:
            raise ValueError(f"Invalid label {sequence[end]}")
    if start>=0 and entity is not None:
        entities.add((start-offset, len(sequence)-offset-1, entity))
    return entities