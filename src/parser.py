from typing import List, Dict, Union
import json
import re

def escape(body):
    return re.sub(r'([\"])', r'\\\1', body)

class Slide:
    def __init__(self, 
                 idx: int, 
                 overlay: int, 
                 logical_slide: int, 
                 notes: List[Dict[str, Union[int, str]]]):
        '''
        @param idx: Index of the current page in the output pdf file. 
        @param overlay: Index of the current page the slide (as created by #slide)
        @param logical slide: Number of pages for the slide

        NOTE: if the contents in a slide is too long such that it is separated 
        to two pages, the index will be Fed-up. 
        '''
        self.idx = idx
        self.overlay = overlay
        self.logical_slide = logical_slide
        self.notes = notes

    def generate_code(self) -> str:
        res = [ "#slide[\n" ]
        res.append(f"  /* Idx: {self.idx}, overlay: {self.overlay}, slide: {self.logical_slide} */\n")
        for note in self.notes:
            if 'begin' in note and note['begin'] - 1 > self.overlay: 
                continue
            if 'end' in note and note['end'] >= 0 and note['end'] - 1 < self.overlay: 
                continue
            if note['body'].startswith('[('):
                processed_note = note['body'][1:-1]
                processed_note = escape(processed_note)
                res.append(f'  #pdfnote-putcontents("{processed_note}")\n')
            elif "lang" in note:
                res.append(f'{note["text"]}\n')
            else: 
                res.append(f'  #{{{note["body"]}}}')
        res.append("]")
        return '\n'.join(res)

def parse(j: List[Dict[str, Union[int, str]]]) -> List[Slide]:
    res = [ ] 

    to_create = False
    idx = -1
    overlay = -1
    logical_slide = -1
    notes = [ ]
    for meta in j:
        if meta['t'] == "NewSlide":
            if not to_create: 
                to_create = True
            else: 
                res.append(Slide(idx, overlay, logical_slide, notes))
                notes = [ ]
        elif meta['t'] == "Idx":
            idx = meta['v']
        elif meta['t'] == "Overlay":
            overlay = meta['v']
        elif meta['t'] == "Overlay":
            overlay = meta['v']
        elif meta['t'] == "LogicalSlide":
            logical_slide = meta['v']
        elif meta['t'] == "SlideNote":
            notes.append(meta)
    if to_create: 
        res.append(Slide(idx, overlay, logical_slide, notes))

    return res

