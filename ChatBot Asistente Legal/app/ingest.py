from PyPDF2 import PdfReader
import re
from typing import List, Dict

def extract_text_from_pdf(path: str) -> str:
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text += page_text + "\n"
    return text

def normalize_text(text: str) -> str:
    text = re.sub(r'\r', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{2,}', '\n', text)
    return text.strip()

def split_by_articles(text: str) -> List[Dict]:
    pattern = r'(?i)(?:\n|^)(artículo|art\.)\s+(\d+[A-Za-z\.]*)[\.\-–:]?\s*(.*?)(?=\n(?:artículo|art\.)\s+\d+[A-Za-z\.]*|$)'
    matches = re.finditer(pattern, text, flags=re.DOTALL)

    articles = []
    for m in matches:
        number = m.group(2).strip()
        maybe_title = m.group(3).strip()
        parts = maybe_title.split("\n", 1)
        title = parts[0].strip() or "Sin título"
        body = parts[1].strip() if len(parts) > 1 else ""

        inciso_pattern = r'\n([a-z])\.\s*(.*?)(?=\n[a-z]\.|$)'
        incisos = re.finditer(inciso_pattern, body, flags=re.DOTALL)

        found = False
        for inciso in incisos:
            found = True
            letra = inciso.group(1)
            texto = inciso.group(2).strip()
            articles.append({
                "id": f"art_{number}_{letra}",
                "article_number": f"{number}.{letra}",
                "title": f"{title} — Principio {letra}",
                "body": texto
            })

        if not found:
            articles.append({
                "id": f"art_{number}",
                "article_number": number,
                "title": title,
                "body": body
            })

    return articles

def load_legal_articles(pdf_path: str) -> List[Dict]:
    raw = extract_text_from_pdf(pdf_path)
    norm = normalize_text(raw)
    articles = split_by_articles(norm)
    print(f"✅ {len(articles)} artículos extraídos de {pdf_path}")
    return articles