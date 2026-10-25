from app.market.models import IndexDefinition


INDEX_REGISTRY: dict[str, IndexDefinition] = {
    "NIFTY": IndexDefinition(
        code="NIFTY",
        display_name="NIFTY 50",
        strike_step=50,
    ),
    "BANKNIFTY": IndexDefinition(
        code="BANKNIFTY",
        display_name="BANKNIFTY",
        strike_step=100,
    ),
}


def get_index(code: str) -> IndexDefinition:
    try:
        return INDEX_REGISTRY[code.strip().upper()]
    except KeyError as exc:
        available = ", ".join(sorted(INDEX_REGISTRY))
        raise ValueError(
            f"Unknown index {code!r}. Available indexes: {available}"
        ) from exc