"""
Fixed failure type constants for repro cases.

No randomness. No datetime. No hidden defaults.
"""

# Content drift (fragment or context)
CONTEXT_DRIFT = "context_drift"

# Trace drift (policy_chain, etc.)
TRACE_DRIFT = "trace_drift"

# Explainability drift (explanation)
EXPLAINABILITY_DRIFT = "explainability_drift"

# Signature mismatch (content identical but signature differs)
SIGNATURE_MISMATCH = "signature_mismatch"

# Version mismatch (replay_input.system_version != CURRENT_VERSION)
VERSION_MISMATCH = "version_mismatch"

# Combined (multiple drift types)
COMBINED_DRIFT = "combined_drift"
