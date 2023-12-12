#!/bin/env python3
'''
Depends on: pdfjam, typst

Limitation: 16x9 screen size only
'''

import argparse
import json
import subprocess
import parser
from pathlib import Path
import sys
from pypdf import PdfReader

PUT_NOTE = """
#let pdfnote-putcontents(body) = {
  let res = eval(body, mode: "code")
  for i in range(res.len()) {
    res.at(i)
  }
}
"""

def parse_args():
    parser = argparse.ArgumentParser(description="pelylux2pdfnote Generating Notes in PDF format")
    parser.add_argument(
            "action", choices=['generate', 'compile', 'join'], 
            help="The action to perform")
    parser.add_argument("file", type=str, help="The location to the typst file")
    parser.add_argument("--typst", default='typst', type=str, help="The typst excutable")
    parser.add_argument("--compress", action='store_true', help="If set, the PDF files will be compressed")
    parser.add_argument('-p', "--preamble", default='', type=str, help="The location of the preamble")
    return parser.parse_args()

def main(args: argparse.Namespace):
    if args.preamble:
        preamble_path = Path(args.preamble) 
    else:
        preamble_path = Path(__file__).parent / 'default_preamble.typ'

    input_path = Path(args.file)
    p = subprocess.run([ 
                        args.typst, 
                        'query',
                        '--format',
                        'json',
                        '--field',
                        'value',
                        args.file,
                        '<pdfpc>'
                        ], capture_output=True)
    if p.returncode:
        print(f'Error: typst-query returns {p.returncode}, with the information:\n{p.stderr.decode()}', file=sys.stderr)
        sys.exit(1)
    j = json.loads(p.stdout)
    res = parser.parse(j)
    note_path = input_path.with_stem(input_path.stem + '.note')
    with open(note_path, 'w') as f:
        with open(preamble_path, 'r') as fr:
            f.write(fr.read())
            f.write('\n\n')
        f.write(PUT_NOTE)
        f.write('\n\n')
        for slide in res:
            f.write(slide.generate_code())
            f.write('\n\n')

    if args.action in ['compile', 'join']:
        p = subprocess.run([ 
                            args.typst, 
                            'compile',
                            str(note_path)
                            ], capture_output=True)
        if p.returncode:
            print(f'Error: typst-compile returns {p.returncode}, with the information:\n{p.stderr.decode()}', file=sys.stderr)
            sys.exit(1)

    def compress(path: Path, opath: Path):
        p = subprocess.run([ 
                            'gs',
                            '-sDEVICE=pdfwrite',
                            '-dCompatibilityLevel=1.4',
                            '-dPDFSETTINGS=/default',
                            '-dNOPAUSE',
                            '-dQUIET',
                            '-dBATCH',
                            '-sOutputFile=' + str(opath),
                            str(path), 
                            ], capture_output=True)
        if p.returncode:
            print(f'Error: gs returns {p.returncode}, with the information:\n{p.stderr.decode()}', file=sys.stderr)

    if args.compress: 
        compressed_input_path = input_path.parent / (input_path.stem + '.compressed.pdf')
        compressed_note_path = note_path.parent / (note_path.stem + '.compressed.pdf')
        compress(input_path.with_suffix('.pdf'), compressed_input_path)
        compress(note_path.with_suffix('.pdf'), compressed_note_path)
        final_input_path = compressed_input_path
        final_note_path = compressed_note_path
    else:
        final_input_path = input_path
        final_note_path = note_path


    if args.action in ['join']:
        p = subprocess.run([ 
                            args.typst, 
                            'compile',
                            str(input_path)
                            ], capture_output=True)
        if p.returncode:
            print(f'Error: typst-compile returns {p.returncode}, with the information:\n{p.stderr.decode()}', file=sys.stderr)
            sys.exit(1)


        reader = PdfReader(final_input_path.with_suffix('.pdf'))
        num_pages = len(reader.pages)

        # The following workarounds are necessary; otherwise, the file size will be huge
        tmp_path = input_path.with_name(input_path.stem + '.tmp.pdf')
        pagelist = [ ]
        for i in range(len(res)):
            # flist.append(str(input_path.with_suffix('.pdf')))
            pagelist.append(f'A{i+1:d}')
            pagelist.append(f'B{i+1:d}')
        # We don't allow a slide taking multiple pages (without increasing 
        # the "Overlay" variable), but we have to consider the "Reference" list. 
        if num_pages > len(res):
            for i in range(num_pages - len(res)):
                pagelist.append(f'A{i + len(res):d}')
                pagelist.append(f'B{len(res):d}')

        p = subprocess.run([ 
                            'pdftk',
                            'A=' + str(final_input_path.with_suffix('.pdf')), 
                            'B=' + str(final_note_path.with_suffix('.pdf')), 
                            'cat',
                            *pagelist, 
                            'output',
                            tmp_path
                            ], capture_output=True)
        if p.returncode:
            print(f'Error: gs returns {p.returncode}, with the information:\n{p.stderr.decode()}', file=sys.stderr)


        p = subprocess.run([ 
                            'pdfjam',
                            tmp_path,
                            '--nup', '2x1', 
                            '--landscape',
                            '--frame',
                            'false',
                            '--papersize',
                            '{9cm,32cm}',
                            '--outfile',
                            str(final_input_path.with_name(final_input_path.stem + '.present.pdf'))
                            ], capture_output=True)
        if p.returncode:
            print(f'Error: pdfjam returns {p.returncode}, with the information:\n{p.stderr.decode()}', file=sys.stderr)
            sys.exit(1)
        # tmp_path.rmtree()


if __name__ == '__main__':
    args = parse_args()
    main(args)
