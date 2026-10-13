"""Read-only OPD image-slot audit. Python standard library only."""
import hashlib
import argparse
import csv
import html
import io
import json
import posixpath
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
S = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
D = 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'

def relationships(z, source):
    path = posixpath.join(posixpath.dirname(source), '_rels', posixpath.basename(source)+'.rels')
    if path not in z.namelist():
        return {}
    out = {}
    for e in ET.fromstring(z.read(path)):
        target = e.attrib['Target']
        resolved = target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join(posixpath.dirname(source), target))
        out[e.attrib['Id']] = (resolved, e.attrib.get('TargetMode') == 'External')
    return out


def scan_sheet(z, path):
    sheet = ET.fromstring(z.read(path))
    fmt = sheet.find(f'{{{S}}}sheetFormatPr')
    default = float(fmt.get('defaultRowHeight',15)) if fmt is not None else 15
    heights={int(e.get('r')):0 if e.get('hidden')=='1' else float(e.get('ht',default)) for e in sheet.findall(f'.//{{{S}}}row')}
    def y(row): return sum(heights.get(i,default)*12700 for i in range(1,row+1))
    # Zero-based marker row: top of spreadsheet row row+1.
    def marker_y(marker): return y(int(marker.findtext(f'{{{D}}}row','0')))+int(marker.findtext(f'{{{D}}}rowOff','0'))
    bands={'BROADBAND':(y(1),y(16)), 'METRO':(y(17),y(33))}
    result={n:[] for n in bands}; warnings={n:[] for n in bands}
    def warn(message,nets=None):
        for n in nets or bands: warnings[n].append(message)
    if any('vm' in c.attrib or (c.findtext(f'{{{S}}}f','').upper().find('IMAGE(')>=0) for c in sheet.findall(f'.//{{{S}}}c')):
        warn('Ada gambar/data dalam sel yang belum didukung; periksa langsung di Excel.')
    rels=relationships(z,path)
    for e in sheet.findall(f'{{{S}}}drawing'):
        target,external=rels[e.attrib[f'{{{R}}}id']]
        if external: warn('Drawing tertaut ke sumber eksternal.');continue
        drawing=ET.fromstring(z.read(target)); links=relationships(z,target)
        for anchor in drawing:
            pics=anchor.findall(f'.//{{{D}}}pic')
            if not pics: continue  # Lines, comments, and decorative shapes are not report pictures.
            start=anchor.find(f'{{{D}}}from');end=anchor.find(f'{{{D}}}to');ext=anchor.find(f'{{{D}}}ext')
            top=bottom=None
            if start is not None:
                top=marker_y(start)
                if int(start.findtext(f'{{{D}}}col','0'))>=23:continue
                if end is not None: bottom=marker_y(end)
                elif ext is not None: bottom=top+int(ext.get('cy','0'))
            else:
                pos=anchor.find(f'{{{D}}}pos')
                if pos is not None and ext is not None:top=int(pos.get('y','0'));bottom=top+int(ext.get('cy','0'))
            if top is None or bottom is None or bottom<=top:
                warn('Posisi atau ukuran gambar tidak terbaca.');continue
            overlaps={n:max(0,min(bottom,b)-max(top,a))/(bottom-top) for n,(a,b) in bands.items()}
            touched=[n for n,v in overlaps.items() if v>0]
            if not touched:continue
            best=max(overlaps,key=overlaps.get)
            if overlaps[best]<0.8:
                warn('Gambar melintasi batas slot; penempatan jaringan belum pasti.',touched);continue
            for pic in pics:
                if len(pics)>1:
                    warn('Beberapa gambar berada dalam satu grup; periksa penempatannya.',[best]);continue
                blip=pic.find(f'.//{{{A}}}blip');ref=blip.get(f'{{{R}}}embed') if blip is not None else None
                media,external=links.get(ref,('',True))
                if external or media not in z.namelist():warn('Gambar tertaut/hilang, bukan gambar tertanam yang dapat dibaca.',[best]);continue
                data=z.read(media)
                if not data:warn('Data gambar kosong.',[best]);continue
                result[best].append({'media':media,'bytes':data,'reason':f'Gambar berada {overlaps[best]:.0%} di area {best.title()} (baris '+('2–16' if best=='BROADBAND' else '18–33')+').'})
    return result,warnings

def audit_file(path,config):
    before=path.stat();raw=path.read_bytes();after=path.stat()
    if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):raise ValueError('File berubah saat dibaca; ulangi setelah penyimpanan selesai.')
    rows=[]; extras=[]
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        root=ET.fromstring(z.read('xl/workbook.xml'));links=relationships(z,'xl/workbook.xml');sheets=list(root.find(f'{{{S}}}sheets'));used=set()
        for p in config['projects']:
            names={n.strip().casefold() for n in [p['sheet']]+p.get('aliases',[])}
            matches=[s for s in sheets if s.get('name').strip().casefold() in names];used.update(s.get('name') for s in matches)
            found={};warnings={};error=''
            if len(matches)==1:
                try:
                    target,external=links[matches[0].get(f'{{{R}}}id')]
                    if external:raise ValueError('Sheet eksternal')
                    found,warnings=scan_sheet(z,target)
                except Exception as exc:error=str(exc)
            for net in p['networks']:
                imgs=found.get(net,[]);notes=warnings.get(net,[])
                if not matches:status='SHEET_HILANG';reason='Sheet tujuan belum tersedia; slot belum dapat diisi.'
                elif len(matches)>1:status='PERLU_PERIKSA';reason='Lebih dari satu sheet cocok dengan nama/alias project.'
                elif error:status='PERLU_PERIKSA';reason='Sheet gagal diperiksa: '+error
                elif notes:status='PERLU_PERIKSA';reason=' '.join(dict.fromkeys(notes))
                elif len(imgs)>1:status='PERLU_PERIKSA';reason=f'{len(imgs)} gambar berada pada slot yang sama; periksa gambar ganda.'
                elif len(imgs)==1:status='TERISI';reason=imgs[0]['reason']
                else:status='KOSONG';reason='Tidak ada gambar tertanam pada area slot ini.'
                rows.append({'file':path.name,'sheet':matches[0].get('name').strip() if len(matches)==1 else p['sheet'],'jaringan':net,'status':status,'alasan':reason,'images':imgs,'source_hash':hashlib.sha256(raw).hexdigest()})
        extras=[s.get('name') for s in sheets if s.get('name') not in used]
    return rows,extras
