#!/usr/bin/env python3
"""Prove ouvrir()/consulter() call flock LOCK_EX then LOCK_UN. .lock existing is not enough."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import mesure  # noqa: E402


class FlockOuvrirConsulter(unittest.TestCase):
    def test_ouvrir_calls_flock_ex(self):
        if mesure.fcntl is None:
            self.skipTest("fcntl absent")
        mock = MagicMock()
        mock.LOCK_EX = getattr(mesure.fcntl, "LOCK_EX", 2)
        mock.LOCK_UN = getattr(mesure.fcntl, "LOCK_UN", 8)
        orig = mesure.fcntl
        mesure.fcntl = mock
        try:
            with tempfile.TemporaryDirectory() as d:
                p = Path(d) / "c.mesure.json"
                mesure.ouvrir("figure", 1, p)
                calls = [c.args[1] for c in mock.flock.call_args_list]
                self.assertGreaterEqual(len(calls), 2)
                self.assertEqual(calls[0], mock.LOCK_EX)
                self.assertEqual(calls[-1], mock.LOCK_UN)
        finally:
            mesure.fcntl = orig

    def test_consulter_calls_flock_ex(self):
        if mesure.fcntl is None:
            self.skipTest("fcntl absent")
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "c.mesure.json"
            mesure.ouvrir("figure", 1, p)
            mock = MagicMock()
            mock.LOCK_EX = getattr(mesure.fcntl, "LOCK_EX", 2)
            mock.LOCK_UN = getattr(mesure.fcntl, "LOCK_UN", 8)
            orig = mesure.fcntl
            mesure.fcntl = mock
            try:
                mesure.consulter(p)
                calls = [c.args[1] for c in mock.flock.call_args_list]
                self.assertGreaterEqual(len(calls), 2)
                self.assertEqual(calls[0], mock.LOCK_EX)
                self.assertEqual(calls[-1], mock.LOCK_UN)
            finally:
                mesure.fcntl = orig


if __name__ == "__main__":
    unittest.main()
