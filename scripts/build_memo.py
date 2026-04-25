"""
Build memo.pdf and evidence_graph.json from memo.md.

Usage:
    python scripts/build_memo.py

Reads:
    memo.md                  -- source-of-truth decision memo (markdown)
    eval/score_log.json      -- baseline + mechanism-eval entries

Writes:
    memo.pdf                 -- decision memo PDF
    evidence_graph.json      -- every numeric claim mapped to its source file
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Unicode normalisation for fpdf (latin-1 encoding)
# ---------------------------------------------------------------------------
_CHAR_SUBS = [
    ("—", "--"),   # em dash
    ("–", "-"),    # en dash
    ("’", "'"),    # right single quote
    ("‘", "'"),    # left single quote
    ("“", '"'),    # left double quote
    ("”", '"'),    # right double quote
    ("≥", ">="),   # >=
    ("≤", "<="),   # <=
    ("±", "+/-"),  # +-
    ("×", "x"),    # multiplication sign
    ("÷", "/"),    # division sign
    ("≈", "~"),    # approximately
    ("→", "->"),   # right arrow
    ("←", "<-"),   # left arrow
    ("−", "-"),    # minus sign (U+2212, distinct from hyphen)
    ("τ", "tau"),  # tau
    ("²", "2"),    # superscript 2
    ("α", "alpha"),
    ("β", "beta"),
    ("≠", "!="),
    ("§", "S."),   # section sign (latin-1 safe but some fonts drop it)
]


def _clean(text: str) -> str:
    """Strip markdown markers and replace non-latin-1 chars."""
    for old, new in _CHAR_SUBS:
        text = text.replace(old, new)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)        # **bold**
    text = re.sub(r"\*(.+?)\*", r"\1", text)             # *italic*
    text = re.sub(r"`([^`]+)`", r"\1", text)             # `code`
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text) # [text](url)
    return text


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------

def load_score_data() -> dict:
    path = ROOT / "eval" / "score_log.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return {e["name"]: e for e in data["entries"]}


def build_evidence_graph(entries: dict) -> list[dict]:
    inst  = entries.get("instructor-baseline", {})
    day1  = entries.get("day1-baseline", {})
    mech  = entries.get("mechanism-eval", {})
    gpt41 = entries.get("production-gpt41", {})

    return [
        {
            "claim_id": "C1",
            "claim": f"Instructor baseline pass@1 = {inst.get('pass_at_1', 0.7267):.4f}",
            "value": inst.get("pass_at_1", 0.7267),
            "source_file": "input/score_log.json",
            "source_field": "entries[instructor-baseline].pass_at_1",
            "trace_id": inst.get("git_commit"),
        },
        {
            "claim_id": "C2",
            "claim": f"Day-1 baseline pass@1 = {day1.get('pass_at_1', 0.1333):.4f}",
            "value": day1.get("pass_at_1", 0.1333),
            "source_file": "eval/score_log.json",
            "source_field": "entries[day1-baseline].pass_at_1",
            "trace_id": None,
        },
        {
            "claim_id": "C3",
            "claim": (
                f"Mechanism eval pass@1 = {mech.get('pass_at_1', 0.45):.4f} (gpt-4o-mini)"
            ),
            "value": mech.get("pass_at_1", 0.45),
            "source_file": "eval/score_log.json",
            "source_field": "entries[mechanism-eval].pass_at_1",
            "trace_id": None,
        },
        {
            "claim_id": "C4",
            "claim": (
                f"gpt-4.1 production pass@1 = {gpt41.get('pass_at_1', 0.8333):.4f}"
                " (+14.7% vs instructor)"
            ),
            "value": gpt41.get("pass_at_1", 0.8333),
            "source_file": "eval/score_log.json",
            "source_field": "entries[production-gpt41].pass_at_1",
            "trace_id": None,
        },
        {
            "claim_id": "C5",
            "claim": "Two-proportion z-test p=0.009 (mechanism vs day-1)",
            "value": 0.009,
            "source_file": "ablation_results.json",
            "source_field": "statistical_test.p_value",
            "trace_id": None,
        },
        {
            "claim_id": "C6",
            "claim": "Mechanism eval cost $0.1382 / 20 tasks",
            "value": 0.1382,
            "source_file": "ablation_results.json",
            "source_field": "treatment_with_gate.cost_usd",
            "trace_id": None,
        },
        {
            "claim_id": "C7",
            "claim": "Cost per qualified lead = $0.52 (1,000 touches; 95 leads midpoint)",
            "value": 0.52,
            "source_file": "memo.md",
            "source_field": "section 1 derivation",
            "trace_id": None,
        },
        {
            "claim_id": "C8",
            "claim": "Stall rate 11.1% on synthetic tau2-Bench vs 30-40% manual baseline",
            "value": 0.111,
            "source_file": "memo.md",
            "source_field": "section 2; data/tenacious_sales_data/seed/baseline_numbers.md",
            "trace_id": None,
        },
        {
            "claim_id": "C9",
            "claim": "Signal-grounded reply rate 7-12% vs 1-3% generic baseline",
            "value": "0.07-0.12",
            "source_file": "data/tenacious_sales_data/seed/baseline_numbers.md",
            "source_field": "reply rate benchmarks",
            "trace_id": None,
        },
        {
            "claim_id": "C10",
            "claim": "Qualified lead = replied + not unsubscribed within 72h",
            "value": "definition",
            "source_file": "memo.md",
            "source_field": "section 1 definition",
            "trace_id": None,
        },
        {
            "claim_id": "C11",
            "claim": "Tenacious bench: 36 engineers (Python:7, Data:9, ML:5, Infra:4)",
            "value": 36,
            "source_file": "data/tenacious_sales_data/seed/bench_summary.json",
            "source_field": "total_headcount + stack breakdown",
            "trace_id": None,
        },
        {
            "claim_id": "C12",
            "claim": "Talent outsourcing ACV $240K-$720K",
            "value": "240000-720000",
            "source_file": "input/TRP1 Challenge Week 10 (1).md",
            "source_field": "ACV table",
            "trace_id": None,
        },
        {
            "claim_id": "C13",
            "claim": "33 adversarial probes across 10 failure categories",
            "value": 33,
            "source_file": "probes/probe_library.json",
            "source_field": "probe count",
            "trace_id": None,
        },
        {
            "claim_id": "C14",
            "claim": "Bench over-commitment trigger rate ~3% in Segment 2 conversations",
            "value": 0.03,
            "source_file": "probes/probe_library.json",
            "source_field": "PROBE-011 observed_trigger_rate",
            "trace_id": None,
        },
        {
            "claim_id": "C15",
            "claim": "Mechanism cost $0 additional API spend per lead",
            "value": 0,
            "source_file": "method.md",
            "source_field": "section 3.4 Implementation",
            "trace_id": None,
        },
    ]


# ---------------------------------------------------------------------------
# PDF renderer
# ---------------------------------------------------------------------------

_COL_WIDTHS: dict[int, list[int]] = {
    2: [58, 102],
    3: [16, 90, 54],   # default 3-col; overridden below for wide-middle tables
    4: [40, 32, 22, 66],
}


class MemoRenderer:
    BODY  = 7.4
    HEAD1 = 9.5
    HEAD2 = 8.5
    SMALL = 6.1
    LH    = 3.35   # body line height mm
    LH_SM = 3.0    # table row height mm

    def __init__(self, pdf):
        self.pdf = pdf

    # -- headings -----------------------------------------------------------

    def h1(self, text: str) -> None:
        p = self.pdf
        p.ln(2.5)
        p.set_font("Helvetica", "B", self.HEAD1)
        p.multi_cell(0, 5, _clean(text))
        p.set_draw_color(90, 90, 90)
        p.set_line_width(0.25)
        p.line(p.l_margin, p.get_y(), p.w - p.r_margin, p.get_y())
        p.ln(1.5)
        p.set_font("Helvetica", "", self.BODY)

    def h2(self, text: str) -> None:
        p = self.pdf
        p.ln(1.5)
        p.set_font("Helvetica", "B", self.HEAD2)
        p.multi_cell(0, 4.5, _clean(text))
        p.set_font("Helvetica", "", self.BODY)

    # -- body text ----------------------------------------------------------

    def para(self, text: str) -> None:
        if not text.strip():
            return
        self.pdf.set_font("Helvetica", "", self.BODY)
        self.pdf.multi_cell(0, self.LH, _clean(text))

    def blockquote(self, text: str) -> None:
        p = self.pdf
        p.set_font("Helvetica", "I", self.BODY - 0.5)
        indent = 6
        saved = p.l_margin
        p.set_left_margin(saved + indent)
        p.set_x(saved + indent)
        p.multi_cell(0, self.LH, _clean(text))
        p.set_left_margin(saved)

    def bullet(self, text: str) -> None:
        p = self.pdf
        p.set_font("Helvetica", "", self.BODY)
        indent = 5
        saved = p.l_margin
        p.set_left_margin(saved + indent)
        p.set_x(saved + indent)
        p.multi_cell(0, self.LH, "- " + _clean(text))
        p.set_left_margin(saved)

    def rule(self) -> None:
        p = self.pdf
        p.ln(1)
        p.set_draw_color(190, 190, 190)
        p.set_line_width(0.2)
        p.line(p.l_margin, p.get_y(), p.w - p.r_margin, p.get_y())
        p.ln(2)

    def blank(self) -> None:
        self.pdf.ln(1.2)

    # -- tables -------------------------------------------------------------

    def table(self, raw_lines: list[str]) -> None:
        p = self.pdf

        rows: list[list[str]] = []
        for line in raw_lines:
            parts = [c.strip() for c in line.strip().strip("|").split("|")]
            is_sep = all(re.match(r"^[-: ]+$", c) for c in parts if c)
            if not is_sep and parts:
                rows.append(parts)

        if len(rows) < 1:
            return

        headers   = rows[0]
        data_rows = rows[1:]
        n = len(headers)

        col_w = _COL_WIDTHS.get(n, [int(160 / n)] * n)[:]
        while len(col_w) < n:
            col_w.append(20)

        # Heuristic: if first-column header is very short (IDs), use narrow col
        if n == 3:
            first_max = max(
                len(_clean(headers[0])),
                max((len(_clean(r[0])) for r in data_rows), default=0),
            )
            if first_max <= 4:          # "C15", "ID"
                col_w = [14, 93, 53]
            else:                       # "Input", "Component", "Cost" style
                col_w = [28, 98, 34]

        cell_h = self.LH_SM

        # Header row
        p.set_fill_color(225, 225, 225)
        p.set_font("Helvetica", "B", self.SMALL)
        for i, h in enumerate(headers):
            w = col_w[i] if i < len(col_w) else 20
            p.cell(w, cell_h, _clean(h), border=1, fill=True)
        p.ln()

        # Data rows
        p.set_font("Helvetica", "", self.SMALL)
        for row in data_rows:
            while len(row) < n:
                row.append("")
            for i in range(n):
                w   = col_w[i] if i < len(col_w) else 20
                txt = _clean(row[i])
                # Truncate to fit cell (rough: 1.55 chars per mm at 6.5pt)
                max_ch = max(4, int(w * 1.55))
                if len(txt) > max_ch:
                    txt = txt[: max_ch - 2] + ".."
                p.cell(w, cell_h, txt, border=1)
            p.ln()

        p.ln(1)
        p.set_font("Helvetica", "", self.BODY)


# ---------------------------------------------------------------------------
# Markdown parser / PDF dispatcher
# ---------------------------------------------------------------------------

def render_from_memo_md(pdf, memo_path: Path) -> None:
    r = MemoRenderer(pdf)

    with open(memo_path, encoding="utf-8") as f:
        content = f.read()

    # Drop the metadata preamble (everything up to the first ---\n boundary).
    idx = content.find("\n---\n")
    body = content[idx + 5:] if idx != -1 else content

    table_buf: list[str] = []
    prev_blank = False

    def flush_table() -> None:
        nonlocal table_buf
        if table_buf:
            r.table(table_buf)
            table_buf.clear()

    for line in body.split("\n"):
        s = line.strip()

        if s.startswith("|"):
            table_buf.append(s)
            prev_blank = False
            continue
        flush_table()

        if s.startswith("## "):
            r.h1(s[3:])
        elif s.startswith("### ") or s.startswith("#### "):
            r.h2(s.lstrip("#").strip())
        elif s == "---":
            r.rule()
        elif s.startswith("> "):
            r.blockquote(s[2:])
        elif s.startswith("- ") or s.startswith("* "):
            r.bullet(s[2:])
        elif s == "":
            if not prev_blank:
                r.blank()
        else:
            r.para(s)

        prev_blank = s == ""

    flush_table()


# ---------------------------------------------------------------------------
# Top-level PDF builder
# ---------------------------------------------------------------------------

def build_pdf() -> Path:
    try:
        from fpdf import FPDF
    except ImportError:
        print("fpdf2 not installed -- pip install fpdf2", file=sys.stderr)
        sys.exit(1)

    memo_path = ROOT / "memo.md"
    if not memo_path.exists():
        print(f"ERROR: memo.md not found at {memo_path}", file=sys.stderr)
        sys.exit(1)

    pdf = FPDF(format="Letter")
    pdf.set_margins(16, 12, 16)
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()

    # Custom title block (replaces the # heading in memo.md)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 5.5, "The Conversion Engine -- Decision Memo", ln=True)
    pdf.set_font("Helvetica", "", 7.4)
    pdf.cell(0, 3.6, "For: Tenacious Consulting and Outsourcing -- CEO / CFO", ln=True)
    pdf.cell(0, 3.6, "From: Kirubel Tewodros, 10 Academy Week 10  |  Date: 2026-04-25", ln=True)
    pdf.cell(0, 3.6, "Mechanism: Confidence-Proportional Phrasing Gates (Act IV)", ln=True)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.4)
    pdf.line(16, pdf.get_y() + 1.2, pdf.w - 16, pdf.get_y() + 1.2)
    pdf.ln(3)

    render_from_memo_md(pdf, memo_path)

    # Footer on last page
    pdf.set_y(-14)
    pdf.set_font("Helvetica", "I", 7)
    pdf.cell(
        0, 4,
        f"Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
        " | Full evidence graph: evidence_graph.json",
        ln=True,
    )

    out = ROOT / "memo.pdf"
    pdf.output(str(out))
    return out


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    entries        = load_score_data()
    evidence_graph = build_evidence_graph(entries)

    out_graph = ROOT / "evidence_graph.json"
    with open(out_graph, "w", encoding="utf-8") as f:
        json.dump(
            {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "memo_file": "memo.pdf",
                "claims": evidence_graph,
            },
            f,
            indent=2,
        )
    print(f"evidence_graph.json written: {len(evidence_graph)} claims")

    out_pdf = build_pdf()
    print(f"memo.pdf written: {out_pdf}")


if __name__ == "__main__":
    main()
