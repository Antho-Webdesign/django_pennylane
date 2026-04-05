from unittest.mock import Mock, patch

from django.test import SimpleTestCase, override_settings

from listing_app import services


class ListingServicesTests(SimpleTestCase):
    @override_settings(PENNYLANE_API_TOKEN="fallback-token")
    def test_get_headers_uses_explicit_token_first(self):
        headers = services._get_headers("session-token")

        self.assertEqual(headers["Authorization"], "Bearer session-token")

    @override_settings(PENNYLANE_API_TOKEN="fallback-token")
    def test_get_headers_falls_back_to_settings_token(self):
        headers = services._get_headers(None)

        self.assertEqual(headers["Authorization"], "Bearer fallback-token")

    @override_settings(PENNYLANE_API_BASE_URL="https://api.example.test")
    @patch("listing_app.services.requests.get")
    def test_list_entities_sends_filter_as_json_param(self, mock_get):
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"items": []}
        mock_get.return_value = mock_response

        services.list_entities("products", q='Acme "Plus"', token="tkn")

        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args.kwargs

        self.assertEqual(mock_get.call_args.args[0], "https://api.example.test/products")
        self.assertEqual(call_kwargs["headers"]["Authorization"], "Bearer tkn")
        self.assertEqual(call_kwargs["timeout"], services.REQUEST_TIMEOUT_SECONDS)
        self.assertIn('"value":"Acme \\"Plus\\""', call_kwargs["params"]["filter"])

    @override_settings(PENNYLANE_API_BASE_URL="https://api.example.test")
    @patch("listing_app.services.requests.get")
    def test_list_customers_uses_sort_parameter(self, mock_get):
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"items": []}
        mock_get.return_value = mock_response

        services.list_customers(token="tkn")

        mock_get.assert_called_once_with(
            "https://api.example.test/customers",
            headers={"Content-Type": "application/json", "Authorization": "Bearer tkn"},
            params={"sort": "-id"},
            timeout=services.REQUEST_TIMEOUT_SECONDS,
        )
