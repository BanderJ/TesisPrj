import re
from docx import Document
from docx.shared import Pt, RGBColor, Inches

doc = Document()

with open('docs/manuales/Manual_Instalacion_CoffeeRen.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

i = 0
in_code_block = False
code_content = []

while i < len(lines):
    line = lines[i].rstrip()
    i += 1

    if line.startswith('```'):
        if not in_code_block:
            in_code_block = True
            code_content = []
        else:
            in_code_block = False
            if code_content:
                p = doc.add_paragraph()
                run = p.add_run('\n'.join(code_content))
                run.font.name = 'Courier New'
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(40, 40, 40)
                p.paragraph_format.left_indent = Inches(0.5)
                p.paragraph_format.space_before = Pt(6)
                p.paragraph_format.space_after = Pt(6)
        continue

    if in_code_block:
        code_content.append(line)
        continue

    if not line.strip():
        continue

    if line.startswith('# '):
        title = line[2:].strip()
        p = doc.add_heading(title, level=0)
        continue

    if line.startswith('## '):
        heading = line[3:].strip()
        doc.add_heading(heading, level=1)
        continue

    if line.startswith('### '):
        heading = line[4:].strip()
        doc.add_heading(heading, level=2)
        continue

    if line.startswith('#### '):
        heading = line[5:].strip()
        doc.add_heading(heading, level=3)
        continue

    if line.startswith('|'):
        table_rows = []
        curr_line = line
        while curr_line.startswith('|'):
            cells = [c.strip() for c in curr_line.split('|')[1:-1]]
            table_rows.append(cells)
            if i < len(lines):
                curr_line = lines[i].rstrip()
                i += 1
            else:
                break

        if table_rows:
            if len(table_rows) > 1 and all(c.startswith('-') for c in table_rows[1]):
                table_rows.pop(1)

            if table_rows:
                table = doc.add_table(rows=len(table_rows), cols=len(table_rows[0]))
                table.style = 'Light Grid Accent 1'

                for row_idx, row in enumerate(table_rows):
                    for col_idx, cell_text in enumerate(row):
                        table.rows[row_idx].cells[col_idx].text = cell_text
        continue

    p = doc.add_paragraph()
    text = line.strip()

    if not text:
        continue

    pattern = r'\*\*(.*?)\*\*|`(.*?)`|\[(.*?)\]\((.*?)\)'

    last_end = 0
    for match in re.finditer(pattern, text):
        if match.start() > last_end:
            p.add_run(text[last_end:match.start()])

        if match.group(1):
            run = p.add_run(match.group(1))
            run.bold = True
        elif match.group(2):
            run = p.add_run(match.group(2))
            run.font.name = 'Courier New'
            run.font.size = Pt(9)
        elif match.group(3):
            run = p.add_run(match.group(3))
            run.font.underline = True
            run.font.color.rgb = RGBColor(0, 0, 255)

        last_end = match.end()

    if last_end < len(text):
        p.add_run(text[last_end:])

doc.save('docs/manuales/Manual_Instalacion_CoffeeRen.docx')
print("Documento mejorado creado exitosamente!")
