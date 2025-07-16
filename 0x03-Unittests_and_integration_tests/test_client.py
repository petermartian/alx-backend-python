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
            fixtures.ORG_PAYLOAD,
            fixtures.REPOS_PAYLOAD,
            fixtures.EXPECTED_REPOS,
            fixtures.APACHE2_REPOS
        ),
    ]
)
class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient methods."""

    @parameterized.expand([
        ("google", {"login": "google", "repos_url": "url"}),
        ("abc",    {"login": "abc",    "repos_url": "url2"})
    ])
    @patch("client.get_json")
    def test_org(self, org_name, payload, mock_get_json):
        """org() calls get_json with correct URL and returns its data."""
        mock_get_json.return_value = payload
        client = GithubOrgClient(org_name)
        result = client.org()
        mock_get_json.assert_called_once_with(
            GithubOrgClient.ORG_URL.format(org=org_name)
        )
        self.assertEqual(result, payload)

    def test_public_repos_url(self):
        """_public_repos_url returns the repos_url from org payload."""
        client = GithubOrgClient(self.org_payload["login"])
        self.assertEqual(
            client._public_repos_url(),
            self.org_payload["repos_url"]
        )

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """public_repos returns a list of repository names."""
        mock_get_json.return_value = self.repos_payload
        client = GithubOrgClient(self.org_payload["login"])
        repos = client.public_repos()
        mock_get_json.assert_called_once_with(
            self.org_payload["repos_url"]
        )
        self.assertListEqual(repos, self.expected_repos)

    def test_public_repos_with_license(self):
        """public_repos(license) filters repos by license key."""
        client = GithubOrgClient(self.org_payload["login"])
        with patch("client.get_json", return_value=self.repos_payload):
            filtered = client.public_repos("apache-2.0")
        self.assertListEqual(filtered, self.apache2_repos)

    @parameterized.expand([
        ({"license": {"key": "apache-2.0"}}, "apache-2.0", True),
        ({"license": {"key": "bsd-3-clause"}}, "apache-2.0", False)
    ])
    def test_has_license(self, repo, key, expected):
        """has_license returns True iff license key matches."""
        self.assertEqual(
            GithubOrgClient.has_license(repo, key),
            expected
        )


class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos."""

    @classmethod
    def setUpClass(cls):
        """Patch requests.get so public_repos hits our fixtures."""
        def fake_get(url, *args, **kwargs):
            response = Mock()
            org_url = GithubOrgClient.ORG_URL.format(
                org=fixtures.ORG_PAYLOAD["login"]
            )
            if url == org_url:
                response.json.return_value = fixtures.ORG_PAYLOAD
            else:
                response.json.return_value = fixtures.REPOS_PAYLOAD
            return response

        cls.get_patcher = patch(
            "client.requests.get",
            side_effect=fake_get
        )
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """Stop patching requests.get."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Integration: public_repos returns all repos from fixtures."""
        client = GithubOrgClient(fixtures.ORG_PAYLOAD["login"])
        self.assertListEqual(
            client.public_repos(),
            fixtures.EXPECTED_REPOS
        )

    def test_public_repos_with_license(self):
        """Integration: public_repos filters by license correctly."""
        client = GithubOrgClient(fixtures.ORG_PAYLOAD["login"])
        self.assertListEqual(
            client.public_repos("apache-2.0"),
            fixtures.APACHE2_REPOS
        )


if __name__ == "__main__":
    unittest.main()
