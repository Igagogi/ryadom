request_counts: dict[tuple[str, str], int] = {}

FREE_AI_REQUESTS_LIMIT = 3


def check_and_increment(
    ip: str,
    operation: str,
    limit: int = FREE_AI_REQUESTS_LIMIT,
) -> bool:
    """Проверить и увеличить количество AI-запросов для операции."""

    key = (ip, operation)
    current_count = request_counts.get(key, 0)

    if current_count >= limit:
        return False

    request_counts[key] = current_count + 1
    return True
