"""
State-Consistency-Tests – Konsistenz zwischen UI, Service, Repository, Persistenz.

Prüft z.B.:
- Prompt in DB gespeichert -> Liste zeigt denselben Prompt -> Editor lädt denselben Inhalt
- Agent bearbeitet -> Profil zeigt neue Werte -> Registry liefert neue Werte
- Taskstatus im Backend -> Debug Panel zeigt denselben Status
"""
