import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mesure


class Physics(unittest.TestCase):
    def test_consulter_consomme(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "c.mesure.json"
            mesure.ouvrir("figure", 1, p)
            out = mesure.consulter(p)
            self.assertEqual(out["lectures"], 0)
            self.assertTrue(out["detruit"])
            with self.assertRaises(SystemExit):
                mesure.consulter(p)

    def test_pas_de_fork(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "c.mesure.json"
            mesure.ouvrir("figure", 1, p)
            with self.assertRaises(SystemExit):
                mesure.ouvrir("figure", 1, p)

    def test_interdit_present(self):
        text = Path("INTERDIT.md").read_text(encoding="utf-8")
        self.assertIn("Forker", text)
        self.assertIn("ε = 0", text)

    def test_example_schema_shape(self):
        card = json.loads(Path("examples/figure.mesure.json").read_text())
        self.assertEqual(card["format"], "MESURE-v0")
        self.assertGreaterEqual(card["lectures"], 0)

    def test_schema_accepte_sha_sur(self):
        schema = json.loads(Path("schema/mesure.v0.json").read_text())
        self.assertFalse(schema.get("additionalProperties", True))
        self.assertEqual(schema["properties"]["sha_sur"]["enum"], ["fichier", "payload"])
        card = {
            "format": "MESURE-v0",
            "objet": "figure",
            "lectures": 1,
            "sha256": "a" * 64,
            "sha_sur": "payload",
            "detruit": False,
        }
        allowed = set(schema["properties"])
        self.assertTrue(set(card) <= allowed)
        self.assertIn(card["sha_sur"], schema["properties"]["sha_sur"]["enum"])


if __name__ == "__main__":
    unittest.main()
