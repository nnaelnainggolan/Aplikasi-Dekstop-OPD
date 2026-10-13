import json,html,zipfile
from pathlib import Path
from xml.sax.saxutils import escape

def export_empty_xlsx(path,rows):
    """Runtime export of an intentionally small missing-slot list (no source edits)."""
    data=[['File laporan','Sheet / project','Jaringan','Keterangan']]+[[r['file'],r['sheet'],r['jaringan'].title(),'Slot kosong' if r['status']=='KOSONG' else 'Sheet belum tersedia'] for r in rows if r['status'] in ('KOSONG','SHEET_HILANG')]
    body=''
    for i,row in enumerate(data,1):
        body+=f'<row r="{i}">'+''.join(f'<c r="{chr(65+j)}{i}" t="inlineStr"><is><t xml:space="preserve">{escape(str(v))}</t></is></c>' for j,v in enumerate(row))+'</row>'
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
        z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        z.writestr('xl/workbook.xml','<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Slot belum terisi" sheetId="1" r:id="rId1"/></sheets></workbook>')
        z.writestr('xl/_rels/workbook.xml.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>')
        z.writestr('xl/worksheets/sheet1.xml','<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews><cols><col min="1" max="1" width="34" customWidth="1"/><col min="2" max="2" width="38" customWidth="1"/><col min="3" max="3" width="16" customWidth="1"/><col min="4" max="4" width="30" customWidth="1"/></cols><sheetData>'+body+f'</sheetData><autoFilter ref="A1:D{len(data)}"/></worksheet>')

def write_html(out,records,missing,unrecognized,folder,start,end):
    (out/'gambar').mkdir()
    for record in records:
        for r in record['rows']:
            previews=[]
            for img in r.pop('images',[]):
                ext=Path(img['media']).suffix.lower()
                if ext in ('.png','.jpg','.jpeg','.gif','.webp'):
                    name=f'{sum(1 for _ in (out/"gambar").iterdir()):05d}{ext}'
                    (out/'gambar'/name).write_bytes(img['bytes']);previews.append('gambar/'+name)
            r['previews']=previews
    data={'records':records,'missing':missing,'unrecognized':unrecognized,'folder':str(folder),'start':str(start),'end':str(end)}
    template=(Path(__file__).parent/'tampilan.html').read_text(encoding='utf-8')
    (out/'hasil.html').write_text(template.replace('__DATA__',json.dumps(data,ensure_ascii=False).replace('<','\\u003c')),encoding='utf-8')
