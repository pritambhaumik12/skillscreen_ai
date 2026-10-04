import os
from pypdf import PdfReader
out_file = 'd:\\Hacktoberfest 26\\pdfs_content.txt'
with open(out_file, 'w', encoding='utf-8') as out:
    for folder in ['d:\\Hacktoberfest 26\\Project Docs', 'd:\\Hacktoberfest 26\\Project Summary']:
        for file in os.listdir(folder):
            if file.endswith('.pdf'):
                path = os.path.join(folder, file)
                out.write(f'--- {file} ---\n')
                try:
                    reader = PdfReader(path)
                    for page in reader.pages:
                        out.write(page.extract_text() + '\n')
                except Exception as e:
                    out.write(f'Error reading {file}: {e}\n')
                out.write('\n\n')
print("Done")
