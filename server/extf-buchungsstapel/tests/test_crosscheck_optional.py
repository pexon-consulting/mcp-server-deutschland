"""Optional cross-checks against material that is not shipped with this repository.

EXTF_MUSTERDATEI: path to EXTF_Buchungsstapel.csv from the DATEV sample data
    (developer.datev.de, Tools > Musterdaten DATEV-Format).
EXTF_TS_PROJEKT: folder with node_modules/@seamless-engineering/datev-extf installed
    (independent TypeScript implementation, MIT).
Both are skipped when the variables are not set.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
from conftest import FIXTURES

from extf_buchungsstapel_mcp import columns as C
from extf_buchungsstapel_mcp.reader import read_extf

MUSTER = os.environ.get("EXTF_MUSTERDATEI")
TS = os.environ.get("EXTF_TS_PROJEKT")


@pytest.mark.skipif(not MUSTER, reason="EXTF_MUSTERDATEI nicht gesetzt")
def test_datev_sample_file_has_no_errors():
    data = Path(MUSTER).read_bytes()
    r = read_extf(data, Path(MUSTER).name)
    assert r.errors == []
    assert len(r.columns) == 125
    assert len(r.rows) > 10
    assert r.header is not None and r.header.marker == "EXTF"


VALIDATE_JS = """
import { readFileSync } from "node:fs";
import { decodeBytes, validateExtf, BUCHUNGSSTAPEL_COLUMNS } from "@seamless-engineering/datev-extf";
const out = { columns: BUCHUNGSSTAPEL_COLUMNS.map(c => c.name ?? c), files: {} };
for (const f of process.argv.slice(2)) {
  const rep = validateExtf(decodeBytes(readFileSync(f)));
  out.files[f] = rep.findings.map(x => [x.severity, x.code]);
}
console.log(JSON.stringify(out));
"""


@pytest.mark.skipif(not TS or not shutil.which("node"), reason="EXTF_TS_PROJEKT oder node fehlt")
def test_independent_typescript_validator_accepts_our_files(tmp_path):
    script = Path(TS) / "_crosscheck_tmp.mjs"
    script.write_text(VALIDATE_JS, encoding="utf-8")
    try:
        files = sorted(str(p) for p in FIXTURES.glob("EXTF_golden_*.csv"))
        out = subprocess.run(["node", str(script), *files], capture_output=True, text=True, check=True, cwd=TS, timeout=60)
    finally:
        script.unlink()
    result = json.loads(out.stdout)
    assert result["columns"] == list(C.BOOKING_COLUMNS_V13)
    for f, findings in result["files"].items():
        assert [x for x in findings if x[0] == "error"] == [], f
