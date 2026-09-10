import importlib
import os
import sys
import unittest
from unittest.mock import patch


def import_billetera(app_env, qp_url, allowed_hosts):
    old_env = os.environ.copy()
    os.environ["APP_ENV"] = app_env
    os.environ["QP_URL"] = qp_url
    os.environ["QP_ALLOWED_HOSTS"] = allowed_hosts
    os.environ["IAQP_SERVICE_KEY"] = "test-service-key"
    sys.modules.pop("billetera", None)
    try:
        return importlib.import_module("billetera")
    finally:
        os.environ.clear()
        os.environ.update(old_env)


class WalletGuardTests(unittest.IsolatedAsyncioTestCase):
    async def test_staging_allowed_host_creates_request(self):
        billetera = import_billetera(
            "staging", "https://wallet-staging.example.test",
            "wallet-staging.example.test")
        requests = []

        class Client:
            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, traceback):
                return False

            async def post(self, url, **kwargs):
                requests.append((url, kwargs))
                return type("Response", (), {
                    "status_code": 200,
                    "json": lambda self: {"saldo_centavos": 25},
                })()

        with patch.object(billetera.httpx, "AsyncClient", return_value=Client()):
            response = await billetera._llamar("/api/wallet/saldo", {})

        self.assertEqual(response, {"saldo_centavos": 25})
        self.assertEqual(requests[0][0],
                         "https://wallet-staging.example.test/api/wallet/saldo")

    async def test_staging_unapproved_host_creates_no_client_or_request(self):
        secret_url = "https://user:url-password@production.example.test"
        secret_key = "test-service-key"
        billetera = import_billetera(
            "staging", secret_url, "wallet-staging.example.test")

        with patch.object(billetera.httpx, "AsyncClient") as client:
            with patch.object(billetera.log, "error") as log_error:
                with self.assertRaisesRegex(
                        billetera.ErrorBilletera,
                        "^Destino de billetera invalido$") as error:
                    await billetera._llamar("/api/wallet/saldo", {})

        client.assert_not_called()
        log_error.assert_not_called()
        self.assertTrue(error.exception.definitivo)
        self.assertNotIn(secret_url, str(error.exception))
        self.assertNotIn(secret_key, str(error.exception))

    async def test_staging_non_https_host_creates_no_client(self):
        billetera = import_billetera(
            "staging", "http://wallet-staging.example.test",
            "wallet-staging.example.test")

        with patch.object(billetera.httpx, "AsyncClient") as client:
            with self.assertRaisesRegex(
                    billetera.ErrorBilletera,
                    "^Destino de billetera invalido$"):
                await billetera._llamar("/api/wallet/saldo", {})

        client.assert_not_called()

    async def test_production_keeps_existing_request_behavior(self):
        billetera = import_billetera(
            "production", "http://existing.example.test", "")

        class Client:
            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, traceback):
                return False

            async def post(self, url, **kwargs):
                return type("Response", (), {
                    "status_code": 200,
                    "json": lambda self: {},
                })()

        with patch.object(billetera.httpx, "AsyncClient", return_value=Client()) as client:
            await billetera._llamar("/api/wallet/saldo", {})

        client.assert_called_once_with(timeout=billetera.TIEMPO_ESPERA)
