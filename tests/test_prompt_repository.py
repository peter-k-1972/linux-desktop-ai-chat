"""Tests für PromptRepository, Storage-Backends und PromptService."""

import os
import tempfile
import unittest

from app.prompts import (
    Prompt,
    PromptService,
    PromptRepository,
    DatabasePromptStorage,
    DirectoryPromptStorage,
    create_storage_backend,
)


def _temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    return path


def _temp_dir():
    return tempfile.mkdtemp()


class TestPromptRepository(unittest.TestCase):
    def setUp(self):
        self.temp_db = _temp_db()

    def tearDown(self):
        try:
            os.unlink(self.temp_db)
        except OSError:
            pass

    def test_create_and_get(self):
        repo = PromptRepository(self.temp_db)
        p = Prompt(
            id=None,
            title="Test Prompt",
            category="code",
            description="A test",
            content="Write a function",
            tags=["python", "test"],
            prompt_type="user",
            scope="global",
            project_id=None,
            created_at=None,
            updated_at=None,
        )
        pid = repo.create(p)
        self.assertGreater(pid, 0)
        loaded = repo.get(pid)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.title, "Test Prompt")
        self.assertEqual(loaded.category, "code")
        self.assertEqual(loaded.tags, ["python", "test"])

    def test_update(self):
        repo = PromptRepository(self.temp_db)
        p = Prompt.empty()
        p.title = "Original"
        p.content = "Content"
        pid = repo.create(p)
        p.id = pid
        p.title = "Updated"
        p.content = "New content"
        self.assertTrue(repo.update(p))
        loaded = repo.get(pid)
        self.assertEqual(loaded.title, "Updated")
        self.assertEqual(loaded.content, "New content")

    def test_delete(self):
        repo = PromptRepository(self.temp_db)
        p = Prompt.empty()
        p.title = "To delete"
        pid = repo.create(p)
        self.assertTrue(repo.delete(pid))
        self.assertIsNone(repo.get(pid))

    def test_list_all(self):
        repo = PromptRepository(self.temp_db)
        for i in range(3):
            p = Prompt.empty()
            p.title = f"Prompt {i}"
            repo.create(p)
        prompts = repo.list_all()
        self.assertEqual(len(prompts), 3)

    def test_list_filter(self):
        repo = PromptRepository(self.temp_db)
        p1 = Prompt.empty()
        p1.title = "Python Code"
        p1.content = "Write Python"
        repo.create(p1)
        p2 = Prompt.empty()
        p2.title = "Other"
        p2.content = "Something else"
        repo.create(p2)
        found = repo.list_all("Python")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].title, "Python Code")


class TestDatabasePromptStorage(unittest.TestCase):
    def setUp(self):
        self.temp_db = _temp_db()

    def tearDown(self):
        try:
            os.unlink(self.temp_db)
        except OSError:
            pass

    def test_create_and_get(self):
        storage = DatabasePromptStorage(self.temp_db)
        p = Prompt.empty()
        p.title = "DB Test"
        p.content = "Content"
        pid = storage.create(p)
        self.assertGreater(pid, 0)
        loaded = storage.get(pid)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.title, "DB Test")

    def test_update_and_delete(self):
        storage = DatabasePromptStorage(self.temp_db)
        p = Prompt.empty()
        p.title = "To Update"
        pid = storage.create(p)
        p.id = pid
        p.title = "Updated"
        self.assertTrue(storage.update(p))
        self.assertTrue(storage.delete(pid))
        self.assertIsNone(storage.get(pid))


class TestDirectoryPromptStorage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = _temp_dir()

    def tearDown(self):
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except OSError:
            pass

    def test_create_and_get(self):
        storage = DirectoryPromptStorage(self.temp_dir)
        p = Prompt.empty()
        p.title = "Dir Test"
        p.content = "Content"
        pid = storage.create(p)
        self.assertGreater(pid, 0)
        loaded = storage.get(pid)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.title, "Dir Test")

    def test_update_and_delete(self):
        storage = DirectoryPromptStorage(self.temp_dir)
        p = Prompt.empty()
        p.title = "To Update"
        pid = storage.create(p)
        p.id = pid
        p.title = "Updated"
        self.assertTrue(storage.update(p))
        self.assertTrue(storage.delete(pid))
        self.assertIsNone(storage.get(pid))

    def test_list_all_with_filter(self):
        storage = DirectoryPromptStorage(self.temp_dir)
        p1 = Prompt.empty()
        p1.title = "Python"
        p1.content = "Python code"
        storage.create(p1)
        p2 = Prompt.empty()
        p2.title = "Rust"
        p2.content = "Rust code"
        storage.create(p2)
        all_prompts = storage.list_all()
        self.assertEqual(len(all_prompts), 2)
        found = storage.list_all("Python")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].title, "Python")


class TestPromptService(unittest.TestCase):
    def setUp(self):
        self.temp_db = _temp_db()
        self.temp_dir = _temp_dir()

    def tearDown(self):
        try:
            os.unlink(self.temp_db)
        except OSError:
            pass
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except OSError:
            pass

    def test_service_create_db(self):
        svc = PromptService(db_path=self.temp_db)
        p = Prompt.empty()
        p.title = "Service Test"
        p.content = "Content"
        created = svc.create(p)
        self.assertIsNotNone(created)
        self.assertIsNotNone(created.id)
        self.assertEqual(created.title, "Service Test")

    def test_service_duplicate(self):
        svc = PromptService(db_path=self.temp_db)
        p = Prompt.empty()
        p.title = "Original"
        p.content = "Content"
        created = svc.create(p)
        dup = svc.duplicate(created)
        self.assertIsNotNone(dup)
        self.assertNotEqual(dup.id, created.id)
        self.assertIn("Kopie", dup.title)

    def test_service_save_and_load(self):
        svc = PromptService(db_path=self.temp_db)
        p = Prompt.empty()
        p.title = "Save Test"
        p.content = "Content"
        created = svc.create(p)
        loaded = svc.get(created.id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.title, "Save Test")

    def test_service_delete(self):
        svc = PromptService(db_path=self.temp_db)
        p = Prompt.empty()
        p.title = "Delete Test"
        created = svc.create(p)
        self.assertTrue(svc.delete(created.id))
        self.assertIsNone(svc.get(created.id))

    def test_service_directory_backend(self):
        svc = PromptService(storage_type="directory", directory=self.temp_dir)
        p = Prompt.empty()
        p.title = "Dir Service Test"
        p.content = "Content"
        created = svc.create(p)
        self.assertIsNotNone(created)
        loaded = svc.get(created.id)
        self.assertEqual(loaded.title, "Dir Service Test")

    def test_backend_switch(self):
        svc = PromptService(db_path=self.temp_db)
        p = Prompt.empty()
        p.title = "DB Prompt"
        created = svc.create(p)
        self.assertIsNotNone(created)
        svc.refresh_backend(storage_type="directory", directory=self.temp_dir)
        prompts = svc.list_all()
        self.assertEqual(len(prompts), 0)
        p2 = Prompt.empty()
        p2.title = "Dir Prompt"
        created2 = svc.create(p2)
        self.assertIsNotNone(created2)
        self.assertEqual(len(svc.list_all()), 1)
