class BillingError(Exception):
    """Base class for billing domain errors."""


class UnknownStationError(BillingError):
    """Raised when a journey references a station missing from the zone map."""
