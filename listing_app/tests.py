from unittest.mock import Mock, patch

from django.test import SimpleTestCase, override_settings

from listing_app import services


class ListingServicesTests(SimpleTestCase):
    @override_settings(PENNYLANE_API_TOKEN="fallback-token")
    def test_get_headers_uses_explicit_token_first(self):
        headers = services._get_headers("session-token")

        self.assertEqual(headers["Authorization"], "Bearer session-token")
        self.assertEqual(headers["Accept"], "application/json")

    @override_settings(PENNYLANE_API_TOKEN="fallback-token")
    def test_get_headers_falls_back_to_settings_token(self):
        headers = services._get_headers(None)

        self.assertEqual(headers["Authorization"], "Bearer fallback-token")

    @override_settings(PENNYLANE_API_BASE_URL="https://api.example.test")
    @patch("listing_app.services.requests.request")
    def test_list_entities_sends_filter_as_json_param(self, mock_request):
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"items": []}
        mock_request.return_value = mock_response

        services.list_entities("products", q='Acme "Plus"', token="tkn")

        mock_request.assert_called_once()
        call_args = mock_request.call_args.args
        call_kwargs = mock_request.call_args.kwargs

        self.assertEqual(call_args[0], "GET")
        self.assertEqual(call_args[1], "https://api.example.test/products")
        self.assertEqual(call_kwargs["headers"]["Authorization"], "Bearer tkn")
        self.assertEqual(call_kwargs["timeout"], services.REQUEST_TIMEOUT_SECONDS)
        self.assertIn('"value":"Acme \\"Plus\\""', call_kwargs["params"]["filter"])

    @override_settings(PENNYLANE_API_BASE_URL="https://api.example.test")
    @patch("listing_app.services.requests.request")
    def test_trial_balance_includes_2026_flag(self, mock_request):
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"trial_balance": []}
        mock_request.return_value = mock_response

        services.get_trial_balance(token="tkn")

        mock_request.assert_called_once_with(
            "GET",
            "https://api.example.test/trial_balance",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer tkn",
            },
            params={"use_2026_api_changes": "true"},
            json=None,
            timeout=services.REQUEST_TIMEOUT_SECONDS,
        )

    @override_settings(PENNYLANE_API_BASE_URL="https://api.example.test")
    @patch("listing_app.services.requests.request")
    def test_import_supplier_invoice_uses_post(self, mock_request):
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"id": "inv_1"}
        mock_request.return_value = mock_response

        payload = {"file_attachment_id": "fa_123"}
        services.import_supplier_invoice(payload, token="tkn")

        mock_request.assert_called_once_with(
            "POST",
            "https://api.example.test/supplier_invoices/import",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer tkn",
            },
            params=None,
            json=payload,
            timeout=services.REQUEST_TIMEOUT_SECONDS,
        )

    @override_settings(PENNYLANE_API_BASE_URL="https://api.example.test")
    @patch("listing_app.services.requests.request")
    def test_validate_supplier_invoice_accounting_uses_put(self, mock_request):
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"status": "validated"}
        mock_request.return_value = mock_response

        services.validate_supplier_invoice_accounting("sup_001", token="tkn")

        mock_request.assert_called_once_with(
            "PUT",
            "https://api.example.test/supplier_invoices/sup_001/validate_accounting",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer tkn",
            },
            params=None,
            json=None,
            timeout=services.REQUEST_TIMEOUT_SECONDS,
        )
