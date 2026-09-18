request_counts: dict[str, int] = {}

FREE_AI_REQUESTS_LIMIT = 3


def check_and_increment(ip: str) -> bool:
    """Проверить и увеличить количество AI-запросов для IP."""
    current_count = request_counts.get(ip, 0)

    if current_count >= FREE_AI_REQUESTS_LIMIT:
        return False

    request_counts[ip] = current_count + 1
    return True