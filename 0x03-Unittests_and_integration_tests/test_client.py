#!/usr/bin/env python3
"""Unit and integration tests for GithubOrgClient in client.py."""
import unittest
from parameterized import parameterized, parameterized_class
from unittest.mock import patch, Mock
import fixtures
from client import GithubOrgClient


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    [
        (
            fixtures.org_payload,
            fixtures.repos_payload,
            fixtures.expected_repos,
            fixtures.apache2_repos
        ),
    ]
)
class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for the methods of GithubOrgClient."""

    @parameterized.expand([
        ("google", {"login": "google", "repos_url": "url"}),
        ("abc",    {"login": "abc",    "repos_url": "url2"}),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, payload, mock_get_json):
        """org() calls get_json with the correct URL and returns its data."""
        mock_get_json.return_value = payload
        client = GithubOrgClient(org_name)
        result = client.org()
        mock_get_json.assert_called_once_with(
            GithubOrgClient.ORG_URL.format(org=org_name)
        )
        self.assertEqual(result, payload)

    def test_public_repos_url(self):
        """_public_repos_url() returns the repos_url from the org payload."""
        client = GithubOrgClient(self.org_payload["login"])
        self.assertEqual(
            client._public_repos_url(),
            self.org_payload["repos_url"]
        )

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """public_repos() returns a list of repository names."""
        mock_get_json.return_value = self.repos_payload
        client = GithubOrgClient(self.org_payload["login"])
        repos = client.public_repos()
        mock_get_json.assert_called_once_with(self.org_payload["repos_url"])
        self.assertListEqual(repos, self.expected_repos)

    def test_public_repos_with_license(self):
        """public_repos(license) filters repos by the given license key."""
        client = GithubOrgClient(self.org_payload["login"])
        # patch get_json a second time for the repos call
        with patch("client.get_json", return_value=self.repos_payload):
            filtered = client.public_repos("apache-2.0")
        self.assertListEqual(filtered, self.apache2_repos)

    @parameterized.expand([
        ({"license": {"key": "apache-2.0"}}, "apache-2.0", True),
        ({"license": {"key": "bsd-3-clause"}}, "apache-2.0", False),
    ])
    def test_has_license(self, repo, key, expected):
        """has_license() returns True only when the license key matches."""
        self.assertEqual(GithubOrgClient.has_license(repo, key), expected)


class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos using real HTTP stubs."""

    @classmethod
    def setUpClass(cls):
        """Patch requests.get so public_repos() can hit fixtures without real HTTP."""
        def fake_get(url, *args, **kwargs):
            response = Mock()
            if url == GithubOrgClient.ORG_URL.format(org=fixtures.org_payload["login"]):
                response.json.return_value = fixtures.org_payload
            else:
                response.json.return_value = fixtures.repos_payload
            return response

        cls.get_patcher = patch("client.requests.get", side_effect=fake_get)
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """Stop patching requests.get."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Integration: public_repos() returns all repo names from fixtures."""
        client = GithubOrgClient(fixtures.org_payload["login"])
        self.assertListEqual(client.public_repos(), fixtures.expected_repos)

    def test_public_repos_with_license(self):
        """Integration: public_repos(license) filters repos by license."""
        client = GithubOrgClient(fixtures.org_payload["login"])
        self.assertListEqual(
            client.public_repos("apache-2.0"),
            fixtures.apache2_repos
        )


if __name__ == "__main__":
    unittest.main()
