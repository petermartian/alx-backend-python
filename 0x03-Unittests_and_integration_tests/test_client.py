# test_client.py
#!/usr/bin/env python3
"""Unit tests for GithubOrgClient in client.py."""
import unittest
from parameterized import parameterized
from unittest.mock import patch
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    @parameterized.expand([
        ("google", {"payload": True}),
        ("abc", {"payload": False}),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, test_payload, mock_get_json=None):
        """GitHubOrgClient.org should call get_json once and return its result."""
        mock_get_json.return_value = test_payload
        client = GithubOrgClient(org_name)
        result = client.org()
        mock_get_json.assert_called_once_with(
            GithubOrgClient.ORG_URL.format(org=org_name)
        )
        self.assertEqual(result, test_payload)


if __name__ == "__main__":
    unittest.main()
