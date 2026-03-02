import markdown
from weasyprint import HTML

with open('/mnt/c/Users/DivyangSharma/concertiv-poc/ARCHITECTURE_AND_ROADMAP.md', 'r') as f:
    md_content = f.read()

html_body = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'toc'])

full_html = (
    '<!DOCTYPE html><html><head><meta charset="UTF-8"><style>'
    '@page { size: A4; margin: 2cm 2.5cm; @bottom-center { content: counter(page); font-size: 10px; color: #999; } }'
    'body { font-family: -apple-system, Segoe UI, Helvetica, Arial, sans-serif; font-size: 11pt; line-height: 1.6; color: #1a1a1a; }'
    'h1 { color: #1B2A4A; font-size: 22pt; border-bottom: 3px solid #C9A84C; padding-bottom: 10px; margin-top: 30px; }'
    'h2 { color: #1B2A4A; font-size: 16pt; margin-top: 28px; border-bottom: 1px solid #ddd; padding-bottom: 6px; page-break-after: avoid; }'
    'h3 { color: #2a4a7a; font-size: 13pt; margin-top: 20px; page-break-after: avoid; }'
    'h4 { color: #444; font-size: 11pt; margin-top: 16px; }'
    'table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 10pt; page-break-inside: avoid; }'
    'th { background: #1B2A4A; color: white; padding: 8px 12px; text-align: left; font-weight: 600; font-size: 9.5pt; }'
    'td { padding: 7px 12px; border-bottom: 1px solid #e0e0e0; vertical-align: top; }'
    'tr:nth-child(even) td { background: #f8f9fa; }'
    'code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; font-family: Consolas, monospace; font-size: 9.5pt; color: #c7254e; }'
    'pre { background: #1B2A4A; color: #e8e8e8; padding: 14px 18px; border-radius: 6px; font-family: Consolas, monospace; font-size: 8.5pt; line-height: 1.5; white-space: pre-wrap; word-wrap: break-word; page-break-inside: avoid; margin: 12px 0; }'
    'pre code { background: none; color: #e8e8e8; padding: 0; font-size: 8.5pt; }'
    'ul, ol { margin: 8px 0; padding-left: 24px; }'
    'li { margin: 4px 0; }'
    'strong { color: #1B2A4A; }'
    'hr { border: none; border-top: 2px solid #C9A84C; margin: 30px 0; }'
    '</style></head><body>'
    + html_body
    + '</body></html>'
)

output_path = '/mnt/c/Users/DivyangSharma/concertiv-poc/Concertiv_Architecture_and_Roadmap.pdf'
HTML(string=full_html).write_pdf(output_path)
print(f'PDF generated: {output_path}')
