import json
import os
import tempfile
import unittest

from scripts.detect_lineage import detect_lineage, load_message_ids, slug_from_filename


def write_dialog(directory, name, message_ids):
    """Write a minimal dialog JSON with the given message_ids."""
    messages = [
        {"role": "user" if i % 2 == 0 else "assistant",
         "content": f"msg-{mid}",
         "message_id": mid}
        for i, mid in enumerate(message_ids)
    ]
    data = {"title": name, "source_file": name, "message_count": len(messages), "messages": messages}
    path = os.path.join(directory, name + ".json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh)
    return path


class TestSlug(unittest.TestCase):
    def test_slug_strips_extension(self):
        self.assertEqual(slug_from_filename("foo_bar.json"), "foo_bar")


class TestDetectLineage(unittest.TestCase):
    def _run(self, files):
        """Create temp dir with dialogs, run detection, return conversations list."""
        with tempfile.TemporaryDirectory() as d:
            for name, ids in files.items():
                write_dialog(d, name, ids)
            index = load_message_ids(d)
            return detect_lineage(index)

    def test_no_overlap(self):
        convs = self._run({
            "A": ["1", "2"],
            "B": ["3", "4"],
        })
        for c in convs:
            self.assertNotIn("lineage", c)

    def test_proper_prefix(self):
        convs = self._run({
            "short": ["a", "b", "c"],
            "long": ["a", "b", "c", "d", "e"],
        })
        by_id = {c["conversation_id"]: c for c in convs}
        self.assertNotIn("lineage", by_id["short"])
        self.assertIn("lineage", by_id["long"])
        parent = by_id["long"]["lineage"]["parents"][0]
        self.assertEqual(parent["conversation_id"], "short")
        self.assertEqual(parent["message_id"], "c")
        self.assertEqual(parent["link_type"], "branch")

    def test_divergence(self):
        convs = self._run({
            "root": ["a", "b"],
            "branch1": ["a", "b", "c1"],
            "branch2": ["a", "b", "c2"],
        })
        by_id = {c["conversation_id"]: c for c in convs}
        self.assertNotIn("lineage", by_id["root"])
        self.assertEqual(by_id["branch1"]["lineage"]["parents"][0]["conversation_id"], "root")
        self.assertEqual(by_id["branch2"]["lineage"]["parents"][0]["conversation_id"], "root")

    def test_identical_files(self):
        convs = self._run({
            "copy1": ["a", "b", "c"],
            "copy2": ["a", "b", "c"],
        })
        # Identical files: neither is a *proper* prefix of the other.
        for c in convs:
            self.assertNotIn("lineage", c)

    def test_single_message_overlap(self):
        convs = self._run({
            "one": ["a"],
            "two": ["a", "b"],
        })
        by_id = {c["conversation_id"]: c for c in convs}
        self.assertEqual(by_id["two"]["lineage"]["parents"][0]["conversation_id"], "one")

    def test_three_way_branch(self):
        convs = self._run({
            "root": ["a", "b"],
            "b1": ["a", "b", "x"],
            "b2": ["a", "b", "y"],
            "b3": ["a", "b", "z"],
        })
        by_id = {c["conversation_id"]: c for c in convs}
        self.assertNotIn("lineage", by_id["root"])
        for name in ("b1", "b2", "b3"):
            self.assertEqual(by_id[name]["lineage"]["parents"][0]["conversation_id"], "root")

    def test_chain(self):
        convs = self._run({
            "v1": ["a"],
            "v2": ["a", "b"],
            "v3": ["a", "b", "c"],
        })
        by_id = {c["conversation_id"]: c for c in convs}
        self.assertNotIn("lineage", by_id["v1"])
        self.assertEqual(by_id["v2"]["lineage"]["parents"][0]["conversation_id"], "v1")
        self.assertEqual(by_id["v3"]["lineage"]["parents"][0]["conversation_id"], "v2")

    def test_idempotent(self):
        files = {"A": ["1", "2"], "B": ["1", "2", "3"]}
        r1 = self._run(files)
        r2 = self._run(files)
        self.assertEqual(r1, r2)


if __name__ == "__main__":
    unittest.main()
