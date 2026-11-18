from dataclasses import asdict, is_dataclass


def _fmt(value) -> str:
    return "" if value is None else str(value)


def print_table(headers, rows):
    """Print rows (list of tuples/lists) as a simple aligned text table."""
    rows = [[_fmt(v) for v in row] for row in rows]
    if not rows:
        print("(no records)")
        return

    widths = [
        max(len(str(h)), *(len(r[i]) for r in rows))
        for i, h in enumerate(headers)
    ]
    line = "-+-".join("-" * w for w in widths)
    print(" | ".join(str(h).ljust(w) for h, w in zip(headers, widths)))
    print(line)
    for row in rows:
        print(" | ".join(v.ljust(w) for v, w in zip(row, widths)))
    print(f"({len(rows)} record(s))")


def print_records(records):
    """Print a list of dataclass objects (models) or dicts as a table."""
    records = list(records)
    if not records:
        print("(no records)")
        return
    dicts = [asdict(r) if is_dataclass(r) else dict(r) for r in records]
    headers = list(dicts[0].keys())
    print_table(headers, [[d[h] for h in headers] for d in dicts])


def print_dict(record):
    """Print one dataclass/dict as 'field: value' lines."""
    data = asdict(record) if is_dataclass(record) else dict(record)
    for key, value in data.items():
        print(f"{key:>24}: {_fmt(value)}")
