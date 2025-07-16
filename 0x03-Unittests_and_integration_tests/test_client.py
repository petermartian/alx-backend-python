#!/usr/bin/env python3
"""Unit tests for the GithubOrgClient in client.py."""
import unittest
from parameterized import parameterized, parameterized_class
from unittest.mock import patch
from client import GithubOrgClient


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    [
        (
            # simulate JSON from the GitHub /org endpoint
            {"login": "google",
             "repos_url": "https://api.github.com/orgs/google/repos"},
            # simulate JSON list from repos_url
            [{"name": "repo1", "license": {"key": "apache-2.0"}},
             {"name": "repo2", "license": {"key": "bsd-3-clause"}}],
            # all repo names
            ["repo1", "repo2"],
            # only those matching apache-2.0
            ["repo1"],
        ),
    ]
)
class TestGithubOrgClient(unittest.TestCase):
    """Test suite for all methods of GithubOrgClient."""

    @classmethod
    def setUpClass(cls):
        """Start patching requests.get so no real HTTP calls occur."""
        cls.get_patcher = patch("client.requests.get")
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """Stop the global patch of requests.get."""
        cls.get_patcher.stop()

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
        with patch("client.get_json", return_value=self.repos_payload):
            filtered = client.public_repos("apache-2.0")
        self.assertListEqual(filtered, self.apache2_repos)

    @parameterized.expand([
        ({"license": {"key": "apache-2.0"}}, "apache-2.0", True),
        ({"license": {"key": "bsd-3-clause"}}, "apache-2.0", False),
    ])
    def test_has_license(self, repo, key, expected):
        """has_license() returns True only when the repo’s license matches."""
        self.assertEqual(GithubOrgClient.has_license(repo, key), expected)


if __name__ == "__main__":
    unittest.main()
