"""
The Privacy step (P605, the core contract's rule 4): `run_operation` masks each result and the values before the trace
and before any frontend sees them. It passes everything through now, and S10 fills its rules (store and project paths
shortened).
"""


# --- MVP ---
class Privacy:
    """Strategy: what a run may show outside spark. Both methods pass through until S10 gives them rules."""

    def mask_result(self, result):
        """The OperationResult as a frontend and the trace may see it."""
        return result

    def mask_values(self, values):
        """The values of a run as the trace may see them."""
        return values
# --- end MVP ---
