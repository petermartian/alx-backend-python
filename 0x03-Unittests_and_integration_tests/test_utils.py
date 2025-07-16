#!/usr/bin/env python3
"""Unit and integration tests for utils.py."""
import unittest
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize
from unittest.mock import patch


class TestAccessNestedMap(unittest.TestCase):
    """Test suite for the utils.access_nested_map function."""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """access_nested_map returns the correct value for a given path."""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_key):
        """access_nested_map raises a KeyError and reports the missing key."""
        with self.assertRaises(KeyError) as ctx:
            access_nested_map(nested_map, path)
        self.assertEqual(ctx.exception.args[0], expected_key)


class TestGetJson(unittest.TestCase):
    """Test suite for the utils.get_json function."""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json(self, test_url, test_payload):
        """get_json calls requests.get and returns the parsed JSON payload."""
        with patch("utils.requests.get") as mock_get:
            mock_get.return_value.json.return_value = test_payload
            result = get_json(test_url)
            mock_get.assert_called_once_with(test_url)
            self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Test suite for the utils.memoize decorator."""

    def test_memoize(self):
        """memoize caches the result of a single-call method."""
        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        test_obj = TestClass()
        with patch.object(
            TestClass,
            "a_method",
            return_value=42
        ) as mock_method:
            first = test_obj.a_property
            second = test_obj.a_property

        mock_method.assert_called_once()
        self.assertEqual(first, 42)
        self.assertEqual(second, 42)


if __name__ == "__main__":
    unittest.main()
