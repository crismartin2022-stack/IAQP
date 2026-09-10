import importlib
import os
import sys
import unittest
from unittest.mock import AsyncMock, patch

import httpx


class Connection:
    async def execute(self, query):
        self.query = query


class Acquire:
    def __init__(self, connection):
        self.connection = connection

    async def __aenter__(self):
        return self.connection

    async def __aexit__(self, exc_type, exc, traceback):
        return False


class Pool:
    def __init__(self, connection):
        self.connection = connection

    def acquire(self):
        return Acquire(self.connection)


def import_main(app_env="staging", allowed_origins="https://approved.example"):
    old_env = os.environ.copy()
    if app_env is None:
        os.environ.pop("APP_ENV", None)
    else:
        os.environ["APP_ENV"] = app_env
    if allowed_origins is None:
        os.environ.pop("ALLOWED_ORIGINS", None)
    else:
        os.environ["ALLOWED_ORIGINS"] = allowed_origins
    sys.modules.pop("main", None)
    try:
        return importlib.import_module("main")
    finally:
        os.environ.clear()
        os.environ.update(old_env)


class RuntimeReadinessTests(unittest.IsolatedAsyncioTestCase):
    async def request(self, app, path, headers=None):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport,
                                     base_url="http://testserver") as client:
            return await client.get(path, headers=headers)

    async def test_approved_origin_receives_cors_header(self):
        main = import_main()

        response = await self.request(
            main.app, "/salud", {"Origin": "https://approved.example"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["access-control-allow-origin"],
                         "https://approved.example")

    async def test_unapproved_origin_receives_no_cors_header(self):
        main = import_main()

        response = await self.request(
            main.app, "/salud", {"Origin": "https://unapproved.example"})

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("access-control-allow-origin", response.headers)

    async def test_ready_probes_database(self):
        main = import_main()
        connection = Connection()

        with patch.object(main, "get_pool", AsyncMock(return_value=Pool(connection))):
            response = await self.request(main.app, "/ready")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"ok": True})
        self.assertEqual(connection.query, "SELECT 1")

    async def test_ready_failure_is_generic_and_logs_error_class(self):
        main = import_main()
        secret = "postgresql://user:secret@database.example/iaqp"

        with patch.object(main, "get_pool", AsyncMock(side_effect=RuntimeError(secret))):
            with self.assertLogs("iaqp", level="ERROR") as logs:
                response = await self.request(main.app, "/ready")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"ok": False})
        self.assertEqual(logs.output, ["ERROR:iaqp:[READY] RuntimeError"])
        self.assertNotIn(secret, response.text)


class RuntimeConfigurationTests(unittest.TestCase):
    def test_missing_app_env_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "^APP_ENV invalido$"):
            import_main(app_env=None)

    def test_non_local_empty_allowlist_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "^ALLOWED_ORIGINS invalido$"):
            import_main(allowed_origins="")

    def test_non_local_origin_with_path_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "^ALLOWED_ORIGINS invalido$"):
            import_main(allowed_origins="https://approved.example/path")

    def test_local_default_keeps_developer_wildcard(self):
        main = import_main(app_env="local", allowed_origins=None)

        self.assertEqual(main.ORIGENES, ["*"])
