from app.core.db import DatabaseManager


def test_db_logic(tmp_path):
    db_path = str(tmp_path / "test_chat_history.db")
    db = DatabaseManager(db_path, ensure_default_project=False)
    
    # 1. Projekt erstellen
    p_id = db.create_project("Test Projekt")
    print(f"Projekt erstellt: {p_id}")
    
    # 2. Datei erstellen und Projekt zuweisen
    f_id = db.get_or_create_file("/tmp/test.txt", "test.txt", "text/plain")
    print(f"Datei erstellt/geholt: {f_id}")
    db.add_file_to_project(p_id, f_id)
    print("Datei dem Projekt zugewiesen.")
    
    # 3. Chat erstellen und Projekt zuweisen
    chat_id = db.create_chat("Test Chat")
    db.add_chat_to_project(p_id, chat_id)
    print(f"Chat {chat_id} dem Projekt {p_id} zugewiesen.")
    
    # 4. Dateien für den Chat abrufen (sollte die Projekt-Datei enthalten)
    files = db.list_files_for_chat(chat_id)
    print(f"Dateien für Chat {chat_id}: {files}")
    
    assert len(files) == 1
    assert files[0][2] == "test.txt"
    
    # 5. Datei direkt dem Chat hinzufügen
    f_id2 = db.get_or_create_file("/tmp/chat_only.txt", "chat_only.txt")
    db.add_file_to_chat(chat_id, f_id2)
    
    files = db.list_files_for_chat(chat_id)
    print(f"Dateien für Chat {chat_id} nach direktem Hinzufügen: {files}")
    assert len(files) == 2
    
    print("DB-Logik Test erfolgreich!")


if __name__ == "__main__":
    from pathlib import Path
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        test_db_logic(Path(td))
