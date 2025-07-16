--- a/0x03-Unittests_and_integration_tests/test_utils.py
+++ b/0x03-Unittests_and_integration_tests/test_utils.py
@@
-# test_utils.py
 #!/usr/bin/env python3
 """Unit and integration tests for utils.py."""
 import unittest
@@
 class TestAccessNestedMap(unittest.TestCase):
+    """Test suite for the utils.access_nested_map function."""
@@
     @parameterized.expand([
@@
-    def test_access_nested_map(self, nested_map, path, expected):
-        self.assertEqual(access_nested_map(nested_map, path), expected)
+    def test_access_nested_map(self, nested_map, path, expected):
+        """access_nested_map returns the correct value for a given path."""
+        self.assertEqual(access_nested_map(nested_map, path), expected)
@@
     @parameterized.expand([
@@
-    def test_access_nested_map_exception(self, nested_map, path, expected_key):
-        with self.assertRaises(KeyError) as ctx:
-            access_nested_map(nested_map, path)
-        self.assertEqual(ctx.exception.args[0], expected_key)
+    def test_access_nested_map_exception(self, nested_map, path, expected_key):
+        """access_nested_map raises KeyError and reports the missing key."""
+        with self.assertRaises(KeyError) as ctx:
+            access_nested_map(nested_map, path)
+        self.assertEqual(ctx.exception.args[0], expected_key)
@@
 class TestGetJson(unittest.TestCase):
-    @parameterized.expand([
+    """Test suite for the utils.get_json function."""
+
+    @parameterized.expand([
@@
-    def test_get_json(self, test_url, test_payload):
-        # Patch requests.get so no real HTTP calls are made
-        with patch("utils.requests.get") as mock_get:
-            mock_get.return_value.json.return_value = test_payload
-            result = get_json(test_url)
-            mock_get.assert_called_once_with(test_url)
-            self.assertEqual(result, test_payload)
+    def test_get_json(self, test_url, test_payload):
+        """get_json calls requests.get and returns the payload ."""
+        with patch("utils.requests.get") as mock_get:
+            mock_get.return_value.json.return_value = test_payload
+            result = get_json(test_url)
+            mock_get.assert_called_once_with(test_url)
+            self.assertEqual(result, test_payload)
@@
 class TestMemoize(unittest.TestCase):
-    def test_memoize(self):
-        class TestClass:
+    """Test suite for the utils.memoize decorator."""
+
+    def test_memoize(self):
+        """memoize caches the result of a single-call method."""
+        class TestClass:
             def a_method(self):
                 return 42

             @memoize
             def a_property(self):
                 return self.a_method()

         test_obj = TestClass()
-        with patch.object(TestClass, "a_method", return_value=42) as mock_method:
-            first = test_obj.a_property
-            second = test_obj.a_property
+        with patch.object(
+            TestClass,
+            "a_method",
+            return_value=42
+        ) as mock_method:
+            first = test_obj.a_property
+            second = test_obj.a_property

         mock_method.assert_called_once()
         self.assertEqual(first, 42)
         self.assertEqual(second, 42)
