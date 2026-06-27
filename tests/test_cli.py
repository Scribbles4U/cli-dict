import json
import unittest
from unittest.mock import patch

import requests
from click.testing import CliRunner

from main import dict_lookup


class FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


SAMPLE_RESPONSE = [
    {
        "word": "test",
        "phonetic": "/test/",
        "phonetics": [{"audio": "https://example.com/test.mp3"}],
        "meanings": [
            {
                "partOfSpeech": "noun",
                "synonyms": ["trial"],
                "antonyms": ["certainty"],
                "definitions": [
                    {
                        "definition": "A procedure intended to establish quality.",
                        "example": "The test passed.",
                    },
                    {
                        "definition": "An event used to measure skill.",
                    },
                ],
            },
            {
                "partOfSpeech": "verb",
                "definitions": [
                    {
                        "definition": "To examine something.",
                        "example": "Test the release before shipping.",
                    }
                ],
            },
        ],
    }
]


class CliDictionaryTests(unittest.TestCase):
    def test_plain_all_output_lists_all_definitions_and_omits_empty_examples(self):
        runner = CliRunner()

        with patch("main.requests.get", return_value=FakeResponse(200, SAMPLE_RESPONSE)):
            result = runner.invoke(dict_lookup, ["test", "--plain", "--all"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Word: test", result.output)
        self.assertIn("Phonetic: /test/", result.output)
        self.assertIn("Audio: https://example.com/test.mp3", result.output)
        self.assertIn("[1] noun", result.output)
        self.assertIn("[2] noun", result.output)
        self.assertIn("[3] verb", result.output)
        self.assertIn("A procedure intended to establish quality.", result.output)
        self.assertIn("An event used to measure skill.", result.output)
        self.assertIn("To examine something.", result.output)
        self.assertNotIn("Example: None", result.output)
        self.assertIn("Synonyms: trial", result.output)
        self.assertIn("Antonyms: certainty", result.output)

    def test_json_output_returns_normalized_lookup_payload(self):
        runner = CliRunner()

        with patch("main.requests.get", return_value=FakeResponse(200, SAMPLE_RESPONSE)):
            result = runner.invoke(dict_lookup, ["test", "--json", "--all"])

        self.assertEqual(result.exit_code, 0)
        payload = json.loads(result.output)
        self.assertEqual(payload["word"], "test")
        self.assertEqual(payload["phonetic"], "/test/")
        self.assertEqual(payload["audio"], "https://example.com/test.mp3")
        self.assertEqual(
            [entry["part_of_speech"] for entry in payload["definitions"]],
            ["noun", "noun", "verb"],
        )

    def test_not_found_uses_api_resolution_and_exits_nonzero(self):
        runner = CliRunner()
        payload = {
            "title": "No Definitions Found",
            "message": "Sorry pal, we couldn't find definitions.",
            "resolution": "You can try the search again at later time or head to the web instead.",
        }

        with patch("main.requests.get", return_value=FakeResponse(404, payload)):
            result = runner.invoke(dict_lookup, ["zzzzzz"])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Word not found: zzzzzz", result.output)
        self.assertIn(payload["resolution"], result.output)

    def test_network_errors_exit_nonzero_with_readable_message(self):
        runner = CliRunner()

        with patch("main.requests.get", side_effect=requests.exceptions.Timeout("slow")):
            result = runner.invoke(dict_lookup, ["test"])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Request failed: slow", result.output)
