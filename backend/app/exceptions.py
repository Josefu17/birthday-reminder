class DuplicateRuleError(Exception):
    """Raised when a rule constraint is violated."""
    pass


class RuleNotFoundError(Exception):
    """Raised when a rule is not found in the DB."""
    pass
