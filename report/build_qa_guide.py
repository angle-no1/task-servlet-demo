# -*- coding: utf-8 -*-
"""把 docs/qa/TEST-GUIDE.md 渲染成排版整齐的 Word 指南。

输出：report/06_测试执行与截图取证指南.docx
用法：python3 report/build_qa_guide.py
"""
import os
import re

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "docs", "qa", "TEST-GUIDE.md")
OUT = os.path.join(ROOT, "report", "06_测试执行与截图取证指南.docx")

CN_FONT = "宋体"
CN_HEAD_FONT = "黑体"
EN_FONT = "Times New Roman"
CODE_FONT = "Consolas"
GRAY = RGBColor(0x59, 0x59, 0x59)


def set_run_font(run, cn=CN_FONT, en=EN_FONT, size=10.5, bold=None, color=None):
    run.font.name = en
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if color is not None:
        run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), en)
    rfonts.set(qn("w:hAnsi"), en)
    rfonts.set(qn("w:eastAsia"), cn)


def shade(element, hex_color):
    pr = element.get_or_add_pPr() if hasattr(element, "get_or_add_pPr") else element
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    pr.append(shd)


def add_bottom_border(paragraph, color="BFBFBF", sz=6):
    ppr = paragraph._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(sz))
    bottom.set(qn("w:space"), "2")
    bottom.set(qn("w:color"), color)
    pbdr.append(bottom)
    ppr.append(pbdr)


def add_page_number_footer(section):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_end)
    set_run_font(run, size=9, color=GRAY)


INLINE = re.compile(r"(`[^`]+`|\*\*.+?\*\*|\[[^\]]+\]\([^)]+\))")


def add_inline(paragraph, text, size=10.5, cn=CN_FONT, base_bold=False, color=None):
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("`") and part.endswith("`") and len(part) > 1:
            run = paragraph.add_run(part[1:-1])
            set_run_font(run, cn=CODE_FONT, en=CODE_FONT, size=size - 0.5, color=RGBColor(0xC7, 0x25, 0x4E))
        elif part.startswith("**") and part.endswith("**"):
            run = paragraph.add_run(part[2:-2])
            set_run_font(run, cn=cn, size=size, bold=True, color=color)
        elif part.startswith("[") and "](" in part:
            label = re.match(r"\[([^\]]+)\]", part).group(1)
            run = paragraph.add_run(label)
            set_run_font(run, cn=cn, size=size, bold=base_bold, color=color)
        else:
            run = paragraph.add_run(part)
            set_run_font(run, cn=cn, size=size, bold=base_bold, color=color)


def body_para(doc, text, size=10.5, indent=0.0, space_after=4, align=None, color=None, bold=False):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(space_after)
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = 1.35
    if indent:
        pf.left_indent = Cm(indent)
    if align is not None:
        p.alignment = align
    add_inline(p, text, size=size, color=color, base_bold=bold)
    return p


def heading(doc, text, level):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    if level == 1:
        pf.space_before = Pt(0)
        pf.space_after = Pt(10)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        set_run_font(run, cn=CN_HEAD_FONT, size=20, bold=True)
        add_bottom_border(p, "1F4E79", 12)
    elif level == 2:
        pf.space_before = Pt(14)
        pf.space_after = Pt(6)
        pf.keep_with_next = True
        run = p.add_run(text)
        set_run_font(run, cn=CN_HEAD_FONT, size=14, bold=True, color=RGBColor(0x1F, 0x3B, 0x63))
        add_bottom_border(p, "D0D7E2", 6)
    else:
        pf.space_before = Pt(9)
        pf.space_after = Pt(4)
        pf.keep_with_next = True
        pf.left_indent = Cm(0.2)
        run = p.add_run(text)
        set_run_font(run, cn=CN_HEAD_FONT, size=11.5, bold=True, color=RGBColor(0x2E, 0x5C, 0x8A))
    # 让标题进导航窗格
    p.style = doc.styles["Heading %d" % level] if level <= 3 else p.style
    for r in p.runs:
        set_run_font(r, cn=CN_HEAD_FONT, size={1: 20, 2: 14, 3: 11.5}[level], bold=True)
    return p


def code_block(doc, lines):
    for i, ln in enumerate(lines):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_before = Pt(6 if i == 0 else 0)
        pf.space_after = Pt(6 if i == len(lines) - 1 else 0)
        pf.left_indent = Cm(0.4)
        pf.line_spacing = 1.15
        run = p.add_run(ln if ln else " ")
        set_run_font(run, cn=CODE_FONT, en=CODE_FONT, size=9)
        shade(p._p, "F4F6F8")


def bullet(doc, text, ordered=False, marker=None):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(3)
    pf.left_indent = Cm(0.9)
    pf.first_line_indent = Cm(-0.5)
    pf.line_spacing = 1.3
    prefix = marker if marker else ("· " if not ordered else "")
    if prefix:
        run = p.add_run(prefix + " ")
        set_run_font(run, size=10.5)
    add_inline(p, text)


def add_table(doc, rows):
    header, body = rows[0], rows[1:]
    table = doc.add_table(rows=1, cols=len(header))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True

    hdr = table.rows[0]
    hdr.cells[0].paragraphs[0].text = ""
    for i, cell_text in enumerate(header):
        cell = hdr.cells[i]
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.space_before = Pt(2)
        add_inline(p, cell_text, size=9, base_bold=True)
        for r in p.runs:
            r.bold = True
        shade(cell._tc.get_or_add_tcPr(), "E8EEF6")

    for row in body:
        cells = table.add_row().cells
        for i, cell_text in enumerate(row[: len(header)]):
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            add_inline(p, cell_text, size=9)

    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return table


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def main():
    text = open(SRC, encoding="utf-8").read()
    lines = text.split("\n")

    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Cm(21)
    sec.page_height = Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(2.2)
    sec.top_margin = Cm(2.2)
    sec.bottom_margin = Cm(2.0)
    add_page_number_footer(sec)

    normal = doc.styles["Normal"]
    normal.font.name = EN_FONT
    normal.font.size = Pt(10.5)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), CN_FONT)

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # 代码块
        if stripped.startswith("```"):
            i += 1
            block = []
            while i < n and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            i += 1
            code_block(doc, block)
            continue

        # 分隔线
        if set(stripped) == {"-"} and len(stripped) >= 3:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            add_bottom_border(p, "D9D9D9", 4)
            i += 1
            continue

        # 标题
        m = re.match(r"^(#{1,3})\s+(.*)$", stripped)
        if m:
            heading(doc, m.group(2).strip(), len(m.group(1)))
            i += 1
            continue

        # 表格
        if stripped.startswith("|") and i + 1 < n and re.match(r"^\|[\s:\-\|]+\|?$", lines[i + 1].strip()):
            rows = [split_row(stripped)]
            i += 2
            while i < n and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i].strip()))
                i += 1
            add_table(doc, rows)
            continue

        # 引用
        if stripped.startswith(">"):
            quote = [stripped.lstrip(">").strip()]
            i += 1
            while i < n and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip().lstrip(">").strip())
                i += 1
            for q in quote:
                if not q:
                    continue
                p = body_para(doc, q, size=9.5, indent=0.5, space_after=2, color=GRAY)
                add_bottom_border(p, "E0E0E0", 2)
            continue

        # 勾选框
        m = re.match(r"^-\s+\[( |x)\]\s+(.*)$", stripped)
        if m:
            bullet(doc, m.group(2), marker="☐" if m.group(1) == " " else "☑")
            i += 1
            continue

        # 无序列表
        if re.match(r"^[-*]\s+", stripped):
            bullet(doc, re.sub(r"^[-*]\s+", "", stripped))
            i += 1
            continue

        # 有序列表
        m = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if m:
            bullet(doc, m.group(2), ordered=True, marker=m.group(1) + ".")
            i += 1
            continue

        body_para(doc, stripped)
        i += 1

    doc.save(OUT)
    print("saved:", OUT)


if __name__ == "__main__":
    main()
