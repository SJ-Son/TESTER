import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Set dummy environment variables to bypass Settings validation
os.environ["GEMINI_API_KEY"] = "AIzaSyFakeKey"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "fake_service_key"
os.environ["SUPABASE_URL"] = "https://example.supabase.co"
os.environ["SUPABASE_JWT_SECRET"] = "fake_jwt"
os.environ["DATA_ENCRYPTION_KEY"] = "fake_encryption_key" # Might be needed

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

class TestSupabaseSingleton(unittest.TestCase):
    @patch("src.services.supabase_service.create_client")
    @patch("src.services.supabase_service.CacheService")
    def test_singleton(self, mock_cache, mock_create_client):
        # Setup mocks
        mock_create_client.return_value = MagicMock()
        mock_cache.return_value = MagicMock()

        # Import after setting env vars
        from src.services.supabase_service import SupabaseService

        # Reset singleton instance for testing because it might have been initialized by imports
        SupabaseService._instance = None
        SupabaseService._client = None

        print("\nTesting SupabaseService Singleton...")
        s1 = SupabaseService()
        s2 = SupabaseService()

        self.assertIs(s1, s2, "SupabaseService should be a singleton")
        # Ensure client is initialized
        self.assertIsNotNone(s1.client)
        self.assertIs(s1.client, s2.client, "Client should be shared")

        # Verify create_client called only once
        mock_create_client.assert_called_once()
        print("✅ SupabaseService Singleton Verified")

if __name__ == "__main__":
    unittest.main()
