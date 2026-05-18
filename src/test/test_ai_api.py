import json
import os
import unittest
from unittest.mock import MagicMock, patch

from src.main import ai_api


class TestAiApi(unittest.TestCase):

    def test_extract_output_text_from_sdk_style_response(self):
        payload = {
            "output": [
                {
                    "type": "message",
                    "content": [
                        {"type": "output_text", "text": "  hello there  "}
                    ],
                }
            ]
        }

        self.assertEqual(ai_api._extract_output_text(payload), "hello there")

    def test_generate_text_requires_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ai_api.OpenAIAPIError):
                ai_api.generate_text("Hello")

    @patch("src.main.ai_api.request.urlopen")
    def test_generate_text_posts_request_and_returns_output(
        self,
        mock_urlopen,
    ):
        response_payload = {
            "output": [
                {
                    "type": "message",
                    "content": [
                        {"type": "output_text", "text": "Done"}
                    ],
                }
            ]
        }

        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(response_payload).encode(
            "utf-8"
        )
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = ai_api.generate_text(
            "Summarize this project",
            instructions="Be brief.",
            api_key="test-key",
            model="gpt-test",
        )

        self.assertEqual(result, "Done")
        request_sent = mock_urlopen.call_args[0][0]
        self.assertEqual(request_sent.full_url, ai_api.OPENAI_RESPONSES_URL)
        self.assertEqual(request_sent.get_method(), "POST")
        self.assertEqual(
            json.loads(request_sent.data.decode("utf-8")),
            {
                "model": "gpt-test",
                "input": "Summarize this project",
                "instructions": "Be brief.",
            },
        )
        self.assertIn(
            ("Authorization", "Bearer test-key"),
            request_sent.header_items(),
        )


if __name__ == '__main__':
    unittest.main()
