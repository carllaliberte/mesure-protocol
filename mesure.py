#!/usr/bin/env python3
"""MESURE v0 — consulter consomme. Pas de fork."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

FORMAT = "MESURE-v0"


def _load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("format") != FORMAT:
        raise SystemExit("refus: format")
    return data


def _save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ouvrir(objet: str, lectures: int, dest: Path) -> dict:
    if lectures < 1:
        raise SystemExit("refus: lectures")
    if dest.exists():
        raise SystemExit("refus: ne pas forker une mesure")
    card = {
        "format": FORMAT,
        "objet": objet,
        "lectures": lectures,
        "sha256": hashlib.sha256(objet.encode()).hexdigest(),
        "detruit": False,
    }
    _save(dest, card)
    return card


def consulter(path: Path) -> dict:
    data = _load(path)
    if data.get("detruit"):
        raise SystemExit("refus: detruit")
    if int(data.get("lectures", 0)) < 1:
        raise SystemExit("refus: lectures")
    data["lectures"] = int(data["lectures"]) - 1
    if data["lectures"] == 0:
        data["detruit"] = True
    _save(path, data)
    return data


def lire(path: Path) -> dict:
    return _load(path)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="mesure")
    sub = p.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("ouvrir")
    o.add_argument("--objet", required=True)
    o.add_argument("--lectures", type=int, default=1)
    o.add_argument("--vers", default="carte.mesure.json")
    c = sub.add_parser("consulter")
    c.add_argument("carte")
    r = sub.add_parser("lire")
    r.add_argument("carte")
    args = p.parse_args(argv)
    if args.cmd == "ouvrir":
        card = ouvrir(args.objet, args.lectures, Path(args.vers))
        print(json.dumps(card, ensure_ascii=False))
        return 0
    if args.cmd == "consulter":
        card = consulter(Path(args.carte))
        print(json.dumps(card, ensure_ascii=False))
        return 0
    print(json.dumps(lire(Path(args.carte)), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
