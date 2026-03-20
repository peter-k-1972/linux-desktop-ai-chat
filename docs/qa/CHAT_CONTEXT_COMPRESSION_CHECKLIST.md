# Chat-Kontext – Compression-Checkliste

**Stand:** 2026-03-17  
**Ziel:** Compression und Budgeting als Teil der Systemarchitektur prüfbar machen.

---

## Checkliste

| # | Prüfpunkt | Status |
|---|-----------|--------|
| 1 | Truncation getestet? | |
| 2 | Line limit getestet? | |
| 3 | Header-only verhindert? | |
| 4 | Marker-only verhindert? | |
| 5 | Policy budgets korrekt? | |
| 6 | Trace enthält Limits? | |
| 7 | Debug zeigt Budgetquelle? | |

---

## Referenzen

| Prüfpunkt | Referenz |
|-----------|----------|
| Truncation | tests/chat/test_context_limits.py, truncate_text |
| Line limit | tests/chat/test_context_limits.py, enforce_line_limit |
| Header-only | tests/chat/test_context_failsafe_limits.py, _has_content_lines |
| Marker-only | tests/chat/test_context_failsafe_limits.py, inject_chat_context_into_messages |
| Policy budgets | tests/chat/test_context_policy_limits.py, resolve_limits_for_policy |
| Trace Limits | tests/chat/test_context_policy_limits.py::test_trace_contains_resolved_limits |
| Budgetquelle | ChatContextResolutionTrace.limits_source, DEBUG-Log |

---

## Verweise

- Governance: CHAT_CONTEXT_GOVERNANCE.md §9
- Failsafe: CHAT_CONTEXT_FAILSAFE_POLICY.md
- Audit: AUDIT_REPORT.md §4.3
