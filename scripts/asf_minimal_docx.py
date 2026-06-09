from __future__ import annotations

import argparse
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape


CONTENT_TYPES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" '
    'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    "</Types>"
)

RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" '
    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
    'Target="word/document.xml"/>'
    "</Relationships>"
)


def build_document(text: str) -> str:
    paragraphs = []
    for line in text.splitlines() or [""]:
        paragraphs.append(
            '<w:p><w:r><w:t xml:space="preserve">'
            + escape(line)
            + "</w:t></w:r></w:p>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>"
        + "".join(paragraphs)
        + "<w:sectPr/></w:body></w:document>"
    )


def write_docx(output: Path, text: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", CONTENT_TYPES)
        archive.writestr("_rels/.rels", RELS)
        archive.writestr("word/document.xml", build_document(text))


def main() -> int:
    parser = argparse.ArgumentParser(description="Write a minimal valid DOCX file.")
    parser.add_argument("--output", required=True)
    parser.add_argument("--input", required=True)
    args = parser.parse_args()

    text = Path(args.input).read_text(encoding="utf-8")
    write_docx(Path(args.output), text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
