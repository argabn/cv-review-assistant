"""Bounded local document ingestion; ZIP members are never extracted to paths."""
import io
import zipfile
from pathlib import Path

MAX_BYTES = 10 * 1024 * 1024


def text_from_bytes(name, data):
    if len(data) > MAX_BYTES:
        raise ValueError('Dokumen melebihi 10 MB')
    if Path(name).suffix.lower() == '.txt':
        return data.decode('utf-8-sig')
    if Path(name).suffix.lower() != '.pdf':
        raise ValueError('Format harus PDF atau TXT')
    from pypdf import PdfReader
    pdf = PdfReader(io.BytesIO(data))
    if pdf.is_encrypted:
        raise ValueError('PDF terenkripsi memerlukan penanganan manual')
    if len(pdf.pages) > 10:
        raise ValueError('PDF melebihi batas demo 10 halaman')
    pages = [page.extract_text() or '' for page in pdf.pages]
    if any(not page.strip() for page in pages):
        raise ValueError('Ada halaman tanpa teks; pemeriksaan manual/OCR diperlukan agar tidak ada halaman terlewat')
    return '\n'.join(pages)


def read_document(path):
    path = Path(path)
    if path.stat().st_size > MAX_BYTES:
        raise ValueError('Dokumen melebihi 10 MB')
    return text_from_bytes(path.name, path.read_bytes())


def documents(path, limit=1):
    path = Path(path)
    if not 1 <= limit <= 10:
        raise ValueError('Batas batch demo antara 1 dan 10')
    if path.suffix.lower() != '.zip':
        try:
            yield path.name, read_document(path), None
        except Exception as exc:
            yield path.name, '', str(exc)
        return
    with zipfile.ZipFile(path) as archive:
        selected = [x for x in archive.infolist() if not x.is_dir()
                    and Path(x.filename).suffix.lower() in {'.txt','.pdf'}
                    and '__MACOSX' not in x.filename and not Path(x.filename).name.startswith('._')][:limit]
        if not selected:
            raise ValueError('ZIP tidak berisi PDF/TXT yang didukung')
        if sum(x.file_size for x in selected) > 20 * 1024 * 1024:
            raise ValueError('Batch terpilih melebihi 20 MB terurai')
        for entry in selected:
            try:
                if entry.file_size > MAX_BYTES:
                    raise ValueError('Dokumen melebihi 10 MB')
                with archive.open(entry) as stream:
                    data = stream.read(MAX_BYTES + 1)
                yield entry.filename, text_from_bytes(entry.filename, data), None
            except Exception as exc:
                yield entry.filename, '', str(exc)
