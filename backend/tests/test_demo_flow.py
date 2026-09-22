"""Real HTTP routes against an isolated demo database; no live AI calls."""

import json
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import get_db
from app.routes import comments, likes, media, stories, users
from demo_setup import BACKEND_DIR, bootstrap


class DemoFlowTests(unittest.TestCase):
    def setUp(self):
        resources = ExitStack()
        self.addCleanup(resources.close)
        temporary = resources.enter_context(tempfile.TemporaryDirectory())
        self.backend = Path(temporary)
        bootstrap(self.backend)
        accounts = json.loads((self.backend / ".demo-accounts.json").read_text(encoding="utf-8"))["accounts"]
        self.admin_account = next(row for row in accounts if row["role"] == "admin")
        self.user_account = next(row for row in accounts if row["role"] == "user")
        engine = create_engine(
            f"sqlite:///{(self.backend / 'storymap.db').as_posix()}",
            connect_args={"check_same_thread": False},
        )
        resources.callback(engine.dispose)
        session_factory = sessionmaker(bind=engine)

        def temporary_database():
            with session_factory() as session:
                yield session

        resources.enter_context(patch.object(media, "UPLOADS_DIR", self.backend / "uploads"))
        resources.enter_context(patch.object(stories, "AUTO_APPROVE_NEW_STORIES", False))
        self.assessment = resources.enter_context(patch.object(
            stories.ai_client, "assess_story_sensitivity",
            return_value=SimpleNamespace(flagged=False, reason="Test assessment only"),
        ))
        # Mount the production routers without importing app.main, which performs
        # production database initialization as an import side effect.
        app = FastAPI()
        for router in (users.router, stories.router, comments.router, likes.router, media.router):
            app.include_router(router)
        app.mount("/uploads", StaticFiles(directory=self.backend / "uploads"), name="uploads")
        app.dependency_overrides[get_db] = temporary_database
        self.client = resources.enter_context(TestClient(app))
        self.admin_headers = self.login(self.admin_account, expected_admin=True)
        self.user_headers = self.login(self.user_account, expected_admin=False)

    def login(self, account, expected_admin):
        response = self.client.post("/login", data={
            "email": account["email"], "password": account["password"],
        })
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["user"]["id"], account["id"])
        self.assertEqual(body["is_admin"], expected_admin)
        return {"Authorization": "Bearer " + body["access_token"]}

    def create_story(self, **extra):
        payload = {
            "title": "Isolated moderation rehearsal",
            "content": "A fictional cultural memory written for automated integration tests.",
            "latitude": 35.174, "longitude": 33.364,
            "category": "oral_history", "is_anonymous": True,
            **extra,
        }
        response = self.client.post("/stories", headers=self.user_headers, json=payload)
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["status"], "pending")
        return response.json()["id"]

    def set_status(self, story_id, status):
        response = self.client.patch(
            f"/stories/{story_id}/status", headers=self.admin_headers,
            json={"status": status},
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["status"], status)

    def test_anonymous_pending_story_requires_admin_and_can_be_rejected_restored(self):
        before = self.client.get("/stories").json()
        self.assertEqual(len(before), 13)
        story_id = self.create_story()
        self.assertEqual(self.client.get(f"/stories/{story_id}").status_code, 404)
        self.assertNotIn(story_id, [row["id"] for row in self.client.get("/stories").json()])
        self.assertEqual(self.client.get("/stories?status=pending").status_code, 401)
        self.assertEqual(self.client.get("/stories?status=pending", headers=self.user_headers).status_code, 403)
        pending = self.client.get("/stories?status=pending", headers=self.admin_headers).json()
        record = next(row for row in pending if row["id"] == story_id)
        self.assertEqual(record["user_id"], self.user_account["id"])
        self.assertFalse(record["ai_flag"])
        self.assertEqual(self.client.patch(
            f"/stories/{story_id}/status", headers=self.user_headers,
            json={"status": "approved"},
        ).status_code, 403)
        self.set_status(story_id, "approved")
        public_story = self.client.get(f"/stories/{story_id}").json()
        self.assertTrue(public_story["is_anonymous"])
        for private_field in ("user_id", "email", "ai_flag", "ai_flag_reason"):
            self.assertNotIn(private_field, public_story)
        self.set_status(story_id, "rejected")
        self.assertEqual(self.client.get(f"/stories/{story_id}").status_code, 404)
        rejected = self.client.get("/stories?status=rejected", headers=self.admin_headers).json()
        self.assertIn(story_id, [row["id"] for row in rejected])
        self.set_status(story_id, "pending")
        self.assertEqual(self.client.get(f"/stories/{story_id}").status_code, 404)
        self.set_status(story_id, "approved")
        self.assertEqual(self.client.get(f"/stories/{story_id}").status_code, 200)

    def test_likes_comments_replies_and_delete_permissions(self):
        story_id = self.create_story()
        self.assertEqual(self.client.post(f"/stories/{story_id}/likes", headers=self.user_headers).status_code, 404)
        self.set_status(story_id, "approved")
        like_url = f"/stories/{story_id}/likes"
        comment_url = f"/stories/{story_id}/comments"
        self.assertEqual(self.client.post(like_url).status_code, 401)
        response = self.client.post(like_url, headers=self.user_headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["count"], 1)
        self.assertTrue(response.json()["liked"])
        self.assertEqual(self.client.post(like_url, headers=self.user_headers).status_code, 409)
        self.assertTrue(self.client.get(like_url, headers=self.user_headers).json()["liked"])
        self.assertEqual(self.client.delete(like_url, headers=self.user_headers).json()["count"], 0)
        parent = self.client.post(comment_url, headers=self.user_headers, json={"content": "Test parent comment"})
        self.assertEqual(parent.status_code, 201, parent.text)
        parent_id = parent.json()["id"]
        reply = self.client.post(comment_url, headers=self.admin_headers, json={
            "content": "Test reply", "parent_id": parent_id,
        })
        self.assertEqual(reply.status_code, 201, reply.text)
        reply_id = reply.json()["id"]
        public_comments = self.client.get(comment_url).json()
        self.assertEqual(len(public_comments), 2)
        self.assertEqual(next(row for row in public_comments if row["id"] == reply_id)["parent_id"], parent_id)
        self.assertEqual(self.client.delete(f"/comments/{reply_id}", headers=self.user_headers).status_code, 403)
        self.assertEqual(self.client.delete(f"/comments/{parent_id}", headers=self.user_headers).status_code, 204)
        remaining = self.client.get(comment_url).json()
        self.assertEqual(len(remaining), 1)
        self.assertIsNone(remaining[0]["parent_id"])
        self.assertEqual(self.client.delete(f"/comments/{reply_id}", headers=self.admin_headers).status_code, 204)
        self.assertEqual(self.client.get(comment_url).json(), [])

    def test_photo_audio_upload_and_public_read(self):
        files = (
            ("image_url", "syrian.jpg", "image/jpeg"),
            ("audio_url", "67f17e5f11ee4c659be4c691a7d4f35c.mp3", "audio/mpeg"),
        )
        urls = {}
        for field, filename, content_type in files:
            data = (BACKEND_DIR / "demo/uploads" / filename).read_bytes()
            unauthorized = self.client.post("/media/upload", files={"file": (filename, data, content_type)})
            self.assertEqual(unauthorized.status_code, 401)
            response = self.client.post(
                "/media/upload", headers=self.user_headers,
                files={"file": (filename, data, content_type)},
            )
            self.assertEqual(response.status_code, 200, response.text)
            urls[field] = response.json()["media_url"]
            download = self.client.get("/" + urls[field])
            self.assertEqual(download.status_code, 200)
            self.assertEqual(download.content, data)
        story_id = self.create_story(**urls)
        self.set_status(story_id, "approved")
        public = self.client.get(f"/stories/{story_id}").json()
        for field, url in urls.items():
            self.assertEqual(public[field], url)
        invalid = self.client.post(
            "/media/upload", headers=self.user_headers,
            files={"file": ("notes.txt", b"not image or audio", "text/plain")},
        )
        self.assertEqual(invalid.status_code, 400)

    def test_registration_and_bad_credentials(self):
        account = {"name": "Integration Test", "email": "integration@example.invalid", "password": "integration-test-password"}
        registration = self.client.post("/register", data=account)
        self.assertEqual(registration.status_code, 201, registration.text)
        self.assertEqual(registration.json()["user"]["role"], "user")
        self.assertEqual(self.client.post("/register", data=account).status_code, 409)
        login = self.client.post("/login", data={"email": account["email"], "password": account["password"]})
        self.assertEqual(login.status_code, 200)
        self.assertFalse(login.json()["is_admin"])
        bad_login = self.client.post("/login", data={"email": account["email"], "password": "wrong-password"})
        self.assertEqual(bad_login.status_code, 401)

    def test_ai_failure_does_not_block_pending_submission(self):
        self.assessment.side_effect = TimeoutError("Synthetic test timeout; no network call")
        with self.assertLogs("app.routes.stories", level="ERROR"):
            story_id = self.create_story()
        queue = self.client.get("/stories?status=pending", headers=self.admin_headers).json()
        story = next(row for row in queue if row["id"] == story_id)
        self.assertIsNone(story["ai_flag"])
        self.assertEqual(self.client.get(f"/stories/{story_id}").status_code, 404)


if __name__ == "__main__":
    unittest.main()
