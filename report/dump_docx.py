import sys
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn


def iter_block_items(parent):
    body = parent.element.body
    for child in body.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, parent)
        elif child.tag == qn("w:tbl"):
            yield Table(child, parent)


path = sys.argv[1]
doc = Document(path)
for i, block in enumerate(iter_block_items(doc)):
    if isinstance(block, Paragraph):
        text = block.text.strip()
        if text:
            print(f"{i:03d} [{block.style.name}] {text}")
    else:
        print(f"{i:03d} --- TABLE ({len(block.rows)}x{len(block.columns)}) ---")
        for row in block.rows:
            print("   | " + " | ".join(c.text.replace("\n", " / ").strip() for c in row.cells))
        print("   --- END TABLE ---")
