"""
Async Behavior Tests – Race Conditions und Event-Loop-Synchronisation.

Prüft typische Async-Probleme:
- Agentwechsel während Stream
- Promptwechsel während Antwort
- Debug Clear während Refresh
- Shutdown während Task

Nutzt: qtbot, waitSignal, Event-Loop-Waits.
Vermeidet: sleep-basierte Tests.
"""
