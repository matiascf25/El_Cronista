import sys
import unittest
from unittest.mock import patch, MagicMock
from app.components.ai.client import generar_con_ia, get_cache_stats, clear_prompt_cache

class TestAICache(unittest.TestCase):
    def setUp(self):
        clear_prompt_cache()

    @patch('app.components.ai.client.requests.post')
    def test_cache_hit(self, mock_post):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Cached Response", "done": True}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # First call - Should hit API
        print("\n--- Call 1 (Expect MISS) ---")
        result1 = generar_con_ia("Test Prompt", json_mode=False, use_cache=True)
        self.assertEqual(result1, "Cached Response")
        self.assertTrue(mock_post.called)
        self.assertEqual(mock_post.call_count, 1)

        # Check stats
        stats = get_cache_stats()
        self.assertEqual(stats["hits"], 0)
        self.assertEqual(stats["misses"], 1)

        # Second call - Should hit Cache
        print("\n--- Call 2 (Expect HIT) ---")
        result2 = generar_con_ia("Test Prompt", json_mode=False, use_cache=True)
        self.assertEqual(result2, "Cached Response")
        
        # Mock should NOT have been called again
        self.assertEqual(mock_post.call_count, 1)

        # Check stats again
        stats = get_cache_stats()
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 1)
        print(f"Stats after hit: {stats}")

    @patch('app.components.ai.client.requests.post')
    def test_cache_bypass(self, mock_post):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Dynamic Response", "done": True}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Call with use_cache=False
        print("\n--- Call Bypass (Expect BYPASS) ---")
        generar_con_ia("Test Prompt", json_mode=False, use_cache=False)
        
        stats = get_cache_stats()
        self.assertEqual(stats["bypassed"], 1)
        self.assertEqual(stats["hits"], 0)
        self.assertEqual(stats["misses"], 0)

    @patch('app.components.ai.client.requests.post')
    def test_json_caching(self, mock_post):
        # Setup mock response for JSON
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": '{"key": "value"}', "done": True}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Call 1
        result1 = generar_con_ia("JSON Prompt", json_mode=True, use_cache=True)
        self.assertEqual(result1, {"key": "value"})

        # Call 2
        result2 = generar_con_ia("JSON Prompt", json_mode=True, use_cache=True)
        self.assertEqual(result2, {"key": "value"})
        
        self.assertEqual(mock_post.call_count, 1)
        self.assertEqual(get_cache_stats()["hits"], 1)

if __name__ == '__main__':
    unittest.main()
