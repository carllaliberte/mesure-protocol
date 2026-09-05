#!/usr/bin/env python3
"""MESURE v0 — consulter consomme. Pas de fork."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

FORMAT = "MESURE-v0"

try:
    import fcntl
except ImportError:
    fcntl = None  # type: ignore


def _load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("format") != FORMAT:
        raise SystemExit("refus: format")
    return data


def _save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(path.suffix + ".lock")
    fh = open(lock_path, "a+", encoding="utf-8")
    if fcntl is not None:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
    return fh


def _unlock(fh) -> None:
    if fcntl is not None:
        fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
    fh.close()


def _sha(objet: str, lectures: int, fichier: Path | None) -> tuple[str, str]:
    if fichier is not None:
        raw = fichier.read_bytes()
        return hashlib.sha256(raw).hexdigest(), "fichier"
    payload = json.dumps({"objet": objet, "lectures": lectures}, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest(), "payload"


def ouvrir(objet: str, lectures: int, dest: Path, fichier: Path | None = None) -> dict:
    if lectures < 1:
        raise SystemExit("refus: lectures")
    fh = _lock(dest)
    try:
        if dest.exists():
            raise SystemExit("refus: ne pas forker une mesure")
        digest, kind = _sha(objet, lectures, fichier)
        card = {
            "format": FORMAT,
            "objet": objet,
            "lectures": lectures,
            "sha256": digest,
            "sha_sur": kind,
            "detruit": False,
        }
        _save(dest, card)
        return card
    finally:
        _unlock(fh)


def consulter(path: Path) -> dict:
    fh = _lock(path)
    try:
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
    finally:
        _unlock(fh)


def lire(path: Path) -> dict:
    return _load(path)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="mesure")
    sub = p.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("ouvrir")
    o.add_argument("--objet", required=True)
    o.add_argument("--lectures", type=int, default=1)
    o.add_argument("--vers", default="carte.mesure.json")
    o.add_argument("--fichier", default=None, help="si fourni, sha256 du fichier réel")
    c = sub.add_parser("consulter")
    c.add_argument("carte")
    r = sub.add_parser("lire")
    r.add_argument("carte")
    args = p.parse_args(argv)
    if args.cmd == "ouvrir":
        src = Path(args.fichier) if args.fichier else None
        card = ouvrir(args.objet, args.lectures, Path(args.vers), src)
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
