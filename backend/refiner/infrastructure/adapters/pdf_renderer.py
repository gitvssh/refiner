from __future__ import annotations

import textwrap


def _pdf_escape(value: str) -> str:
    ascii_value = value.encode("ascii", errors="replace").decode("ascii")
    return ascii_value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


class MinimalPdfRenderer:
    """Render an English demo draft using PDF's built-in Helvetica font."""

    def render(self, rewritten_resume: str) -> bytes:
        lines: list[str] = []
        for source_line in rewritten_resume.splitlines():
            lines.extend(textwrap.wrap(source_line, width=82) or [""])
        commands = ["BT", "/F1 10 Tf", "50 760 Td", "14 TL"]
        for line in lines[:48]:
            commands.append(f"({_pdf_escape(line)}) Tj")
            commands.append("T*")
        commands.append("ET")
        stream = "\n".join(commands).encode("ascii")

        objects = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            (
                b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>"
            ),
            b"<< /Length "
            + str(len(stream)).encode("ascii")
            + b" >>\nstream\n"
            + stream
            + b"\nendstream",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        ]

        document = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for index, item in enumerate(objects, start=1):
            offsets.append(len(document))
            document.extend(f"{index} 0 obj\n".encode())
            document.extend(item)
            document.extend(b"\nendobj\n")
        xref_offset = len(document)
        document.extend(f"xref\n0 {len(objects) + 1}\n".encode())
        document.extend(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            document.extend(f"{offset:010d} 00000 n \n".encode())
        document.extend(
            (
                f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
                f"startxref\n{xref_offset}\n%%EOF\n"
            ).encode()
        )
        return bytes(document)
