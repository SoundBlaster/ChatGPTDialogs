import json
import unittest
from pathlib import Path

from extract_chatgpt_html import extract_html


REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"
HTML_FIXTURES_DIR = FIXTURES_DIR / "html"
JSON_FIXTURES_DIR = FIXTURES_DIR / "json"
TMP_HTML = FIXTURES_DIR / "regressions" / "tmp_section_tail.html"


def normalized_result(result: dict) -> dict:
    return {
        "title": result["title"],
        "message_count": result["message_count"],
        "messages": result["messages"],
    }


class ExtractChatGPTHtmlTests(unittest.TestCase):
    def test_all_import_html_files_extract_messages(self) -> None:
        html_files = sorted(HTML_FIXTURES_DIR.glob("*.html"))
        self.assertGreater(len(html_files), 0)

        for html_path in html_files:
            with self.subTest(html=html_path.name):
                result = extract_html(html_path)
                self.assertTrue(result["title"])
                self.assertTrue(Path(result["source_file"]).is_absolute())
                self.assertEqual(Path(result["source_file"]), html_path.resolve())
                self.assertGreater(result["message_count"], 0)
                self.assertEqual(result["message_count"], len(result["messages"]))

                for message in result["messages"]:
                    self.assertIn(message["role"], {"user", "assistant"})
                    self.assertTrue(message["content"].strip())

    def test_checked_in_json_matches_html_fixtures(self) -> None:
        json_files = sorted(JSON_FIXTURES_DIR.glob("*.json"))
        self.assertGreater(len(json_files), 0)

        for json_path in json_files:
            html_path = HTML_FIXTURES_DIR / f"{json_path.stem}.html"
            with self.subTest(fixture=json_path.name):
                self.assertTrue(html_path.exists(), f"Missing HTML fixture for {json_path.name}")

                actual = extract_html(html_path)
                expected = json.loads(json_path.read_text(encoding="utf-8"))

                self.assertEqual(normalized_result(actual), normalized_result(expected))
                self.assertTrue(Path(actual["source_file"]).is_absolute())
                self.assertTrue(str(expected["source_file"]).endswith(f"/tests/fixtures/html/{html_path.name}"))

    def test_tmp_html_preserves_tail_after_code_block(self) -> None:
        self.assertTrue(TMP_HTML.exists(), "tmp.html regression fixture is missing")

        result = extract_html(TMP_HTML)
        self.assertEqual(result["message_count"], 1)

        content = result["messages"][0]["content"]
        self.assertIn("mir://passport/sha256/", content)
        self.assertIn("И отдельно:", content)
        self.assertIn("Roadmap", content)
        self.assertIn("Phase 1", content)


if __name__ == "__main__":
    unittest.main()
