#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import PyPDF2

def main():
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else 'docs/reports/editais/edital-08737785000191-2026-2.pdf'
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 30

    reader = PyPDF2.PdfReader(pdf_path)
    total = len(reader.pages)
    print(f"Total pages: {total}")

    for i in range(min(max_pages, total)):
        try:
            text = reader.pages[i].extract_text() or ''
        except Exception as e:
            text = f"[ERROR extracting page {i+1}: {e}]"
        if text.strip():
            print(f"\n--- PAGE {i+1} ---")
            # Clean up common PDF extraction artifacts
            clean = text.replace('\x00', '').replace('\ufffd', '?')
            print(clean)

if __name__ == '__main__':
    main()
