import re
import zlib

pdf_path = 'DVD_2023.pdf'
output_csv = 'DVD_2023.csv'

with open(pdf_path, 'rb') as f:
    data = f.read()

# Find and decompress the first stream
match = re.search(rb'stream\r?\n(.*?)\r?\nendstream', data, re.S)
stream = zlib.decompress(match.group(1))

# Tokenize and build lines based on vertical offsets
tokens = re.findall(rb'(\[(?:[^\]]*)\]\s*TJ|\((?:[^()]|\\.)*\)\s*Tj|TD|Td|[+-]?\d*\.?\d+)', stream)
lines = []
current = ''
last_num = '0'

for token in tokens:
    if token in [b'Td', b'TD']:
        if float(last_num) < 0:
            if current.strip():
                lines.append(current.strip())
            current = ''
    elif token.startswith(b'(') and token.endswith(b')Tj'):
        text = re.findall(rb'\((.*)\)Tj', token)[0].decode('latin-1')
        current += text
    elif token.startswith(b'[') and token.endswith(b']TJ'):
        parts = re.findall(rb'\((.*?)\)', token)
        for p in parts:
            current += p.decode('latin-1')
    else:
        last_num = token.decode('latin-1')

if current.strip():
    lines.append(current.strip())

# Write CSV
import csv
with open(output_csv, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Line'])
    for line in lines:
        writer.writerow([line])

print('Extracted', len(lines), 'lines to', output_csv)
