from datetime import datetime, timezone
from unittest.mock import MagicMock, PropertyMock, patch
from uuid import uuid4


def test_get_history_integration_success(client, mock_user_auth):
    """
    Verify /api/history endpoint works correctly with mocked SupabaseService.
    This ensures BaseRepository uses self.client correctly.
    """
    # Mock SupabaseService where it is USED in BaseRepository
    with patch("src.repositories.base_repository.SupabaseService") as MockSupabaseService:
        mock_instance = MockSupabaseService.return_value
        mock_client = MagicMock()
        # Important: SupabaseService().client property must return the mock client
        type(mock_instance).client = (
            PropertyMock(return_value=mock_client)
            if isinstance(mock_instance, MagicMock)
            else mock_client
        )
        # Actually in the code: self.client = SupabaseService().client
        # Mocking the class returns a MagicMock, accessing .client on it returns another MagicMock unless configured.
        mock_instance.client = mock_client

        # Mock the chain: table("generation_history").select("*").eq().order().limit().execute()
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": str(uuid4()),
                "user_id": "test_user_id",
                "input_code": "encrypted_input",
                "generated_code": "encrypted_output",
                "language": "python",
                "model": "gemini-pro",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        ]

        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_response

        # Mock EncryptionService to avoid actual decryption errors
        with patch("src.repositories.generation_repository.EncryptionService") as MockEncryption:
            MockEncryption.return_value.decrypt.side_effect = lambda x: x.replace("encrypted_", "")

            response = client.get("/api/history/")

            assert response.status_code == 200, f"Response 500: {response.text}"
            data = response.json()
            assert len(data) == 1
            assert data[0]["input_code"] == "input"
            assert data[0]["language"] == "python"

            # Verify BaseRepository used self.client
            mock_client.table.assert_called_with("generation_history")
