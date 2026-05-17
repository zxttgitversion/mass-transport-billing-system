class Constants:
    """Manage fare constants centrally."""

    BASE_FEE = 2.00
    PENALTY_FEE = 5.00
    DAY_CAP = 15.00
    MONTH_CAP = 100.00


def zone_cost(zone):
    if not isinstance(zone, int):
        raise TypeError(f"[ERROR] zone must be int, got {zone}")
    if zone == 1:
        return 0.80
    if 2 <= zone <= 3:
        return 0.50
    if 4 <= zone <= 5:
        return 0.30
    if zone > 0:
        return 0.10
    raise ValueError(f"[ERROR] Invalid zone value: {zone}")
