"""Prevent privacy leaks from reappearing in tracked or partially staged files."""

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts import check_repo_hygiene as hygiene


class RepoHygieneTests(unittest.TestCase):
    def test_home_paths_include_json_escaping_and_unix_spellings(self):
        for home in ("C:" + "/Users/", "C:" + "\\Users\\", "/home/", "/c/Users/"):
            with self.subTest(home=home):
                text = home + "example" + "/project/input.txt"
                self.assertTrue(hygiene.content_problems("input.json", text.encode()))
                self.assertTrue(hygiene.content_problems(
                    "escaped.json", text.replace("\\", "\\\\").encode()))
        for text in ("docs/home/example", "../input.flyer", "flyers/bank/pl3/example.flyer"):
            self.assertEqual(hygiene.content_problems("example.txt", text.encode()), [])

    def test_potential_secret_values_are_never_printed(self):
        token = "gh" + "p_" + "a" * 36
        key = "-----BEGIN " + "PRIVATE KEY-----"
        for value in (token, key, "https://" + "user:password@example.invalid/path"):
            with self.subTest(kind=value[:3]):
                problems = hygiene.content_problems("settings.txt", ("safe\n" + value).encode())
                self.assertTrue(problems)
                self.assertTrue(all("settings.txt:2" in message for message in problems))
                self.assertTrue(all(value not in message for message in problems))

    def test_guard_and_tests_do_not_match_their_own_patterns(self):
        for path in (Path(hygiene.__file__), Path(__file__)):
            self.assertEqual(hygiene.content_problems(path.name, path.read_bytes()), [])

    @unittest.skipUnless(shutil.which("git"), "Git is required for index checks")
    def test_partially_staged_files_are_checked_from_the_index(self):
        target = Path(__file__).resolve().parents[1] / "target"
        target.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="hygiene-index-", dir=target) as directory:
            root = Path(directory)

            def git(*args):
                subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)

            git("init", "--quiet")
            source = root / "settings.txt"
            source.write_text("C:" + "/Users/" + "example/private.txt\n", encoding="utf-8")
            git("add", "settings.txt")
            source.write_text("safe working copy\n", encoding="utf-8")
            with patch.object(hygiene, "ROOT", root):
                self.assertTrue(hygiene.problems(staged=True))
                self.assertEqual(hygiene.problems(staged=False), [])
            git("add", "settings.txt")
            source.write_text("C:" + "/Users/" + "example/private.txt\n", encoding="utf-8")
            with patch.object(hygiene, "ROOT", root):
                self.assertEqual(hygiene.problems(staged=True), [])
                self.assertTrue(hygiene.problems(staged=False))
