"""Command line: extf-buchungsstapel prüfen | lesen | erstellen | erklären (each with an ASCII alias)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .explain import explain
from .importer import InputError, header_from_dict, load_csv, load_json
from .model import ExtfValidationError, Finding
from .reader import read_extf, row_to_booking_dict
from .writer import build_extf, write_new_file


def _print_findings(findings: list[Finding]) -> None:
    for f in findings:
        where = f"Zeile {f.line}" if f.line else "Datei"
        field = f", {f.field}" if f.field else ""
        print(f"{f.severity.upper():8} {f.code:34} {where}{field}: {f.message}")


def cmd_pruefen(args: argparse.Namespace) -> int:
    path = Path(args.datei)
    report = read_extf(path.read_bytes(), path.name)
    if args.json:
        print(json.dumps({
            "datei": path.name,
            "gueltig": report.valid,
            "zeichensatz": report.encoding,
            "kopf": report.header.to_dict() if report.header else None,
            "buchungen": len(report.rows),
            "befunde": [f.to_dict() for f in report.findings],
        }, ensure_ascii=False, indent=2))
    else:
        _print_findings(report.findings)
        print(f"{path.name}: {len(report.rows)} Buchungen, {report.error_count} Fehler, "
              f"{report.warning_count} Warnungen, {report.note_count} Hinweise, Zeichensatz {report.encoding}")
    return 0 if report.valid else 1


def cmd_lesen(args: argparse.Namespace) -> int:
    path = Path(args.datei)
    report = read_extf(path.read_bytes(), path.name)
    rows = [row_to_booking_dict(r, report.header) for r in report.rows[args.offset: args.offset + args.limit]]
    if args.json:
        print(json.dumps({"kopf": report.header.to_dict() if report.header else None, "buchungen": rows},
                         ensure_ascii=False, indent=2))
    else:
        for r in rows:
            print(f"{r['zeile']:>5} {r['belegdatum_iso'] or r['belegdatum']:>10} {r['umsatz']:>14} {r['soll_haben']} "
                  f"{r['konto']:>9} {r['gegenkonto']:>9} {r['bu_schluessel']:>4} {r['belegfeld1']:<20} {r['buchungstext']}")
    return 0


def cmd_erstellen(args: argparse.Namespace) -> int:
    src = Path(args.eingabe)
    text = src.read_text(encoding="utf-8-sig")
    try:
        if src.suffix.lower() == ".json":
            header, bookings = load_json(text)
        else:
            header, bookings = None, load_csv(text)
        if args.kopf:
            header = header_from_dict(json.loads(Path(args.kopf).read_text(encoding="utf-8")))
        if header is None:
            print("Fehler: Kopfdaten fehlen. Geben Sie sie im JSON unter 'kopf' oder mit --kopf an.", file=sys.stderr)
            return 2
        data = build_extf(header, bookings)
    except (InputError, ExtfValidationError) as exc:
        _print_findings(exc.findings)
        print(f"Keine Datei geschrieben: {len(exc.findings)} Befund(e).", file=sys.stderr)
        return 1
    out = Path(args.ausgabe)
    try:
        write_new_file(out, data)
    except FileExistsError:
        print(f"Fehler: {out} existiert bereits und wird nicht überschrieben.", file=sys.stderr)
        return 2
    print(f"{out}: {len(bookings)} Buchungen, {len(data)} Bytes geschrieben (Windows-1252, CR/LF).")
    return 0


def cmd_erklaeren(args: argparse.Namespace) -> int:
    hits = explain(args.begriff)
    if not hits:
        print(f"Kein Treffer für {args.begriff!r}.", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(hits, ensure_ascii=False, indent=2))
        return 0
    for h in hits:
        head = f"{h['art']} {h.get('nummer') or ''} {h['name']}".replace("  ", " ")
        print(head)
        print(f"  {h['beschreibung']}")
        if h.get("format"):
            print(f"  Format: {h['format']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="extf-buchungsstapel", description="Buchungsstapel im DATEV-Format (EXTF) schreiben, lesen und prüfen. Lokal, ohne Netzwerk. Kein Produkt der DATEV eG.")
    p.add_argument("--version", action="version", version=f"extf-buchungsstapel {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("prüfen", aliases=["pruefen"], help="Datei prüfen")
    s.add_argument("datei")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_pruefen)
    s = sub.add_parser("lesen", help="Buchungen anzeigen")
    s.add_argument("datei")
    s.add_argument("--limit", type=int, default=100)
    s.add_argument("--offset", type=int, default=0)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_lesen)
    s = sub.add_parser("erstellen", help="Datei aus JSON oder CSV erzeugen (überschreibt nie)")
    s.add_argument("eingabe", help="JSON mit kopf und buchungen oder CSV mit Buchungen")
    s.add_argument("-o", "--ausgabe", required=True, help="Zieldatei, z. B. EXTF_Buchungsstapel.csv")
    s.add_argument("--kopf", help="JSON-Datei nur mit den Kopfdaten, ohne umschließendes kopf (Pflicht bei CSV-Eingabe), z. B. tests/fixtures/kopf_beispiel.json")
    s.set_defaults(func=cmd_erstellen)
    s = sub.add_parser("erklären", aliases=["erklaeren"], help="Feld oder Prüfcode erklären")
    s.add_argument("begriff")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_erklaeren)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
