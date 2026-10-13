import argparse,json,re,webbrowser
from collections import Counter
from datetime import date,datetime,timedelta
from pathlib import Path
from audit_engine import audit_file
from report_ui import export_empty_xlsx,write_html
ROOT=Path(__file__).resolve().parent
MONTHS=['JANUARI','FEBRUARI','MARET','APRIL','MEI','JUNI','JULI','AGUSTUS','SEPTEMBER','OKTOBER','NOVEMBER','DESEMBER']
def file_date(name):
    m=re.search(r'(\d{1,2})\s+('+'|'.join(MONTHS)+r')\s+(\d{4})',name,re.I)
    if not m:return None
    try:return date(int(m[3]),MONTHS.index(m[2].upper())+1,int(m[1]))
    except ValueError:return None

def popup(default):
    import tkinter as tk
    from tkinter import ttk,filedialog,messagebox
    root=tk.Tk();root.title('Pilih laporan yang diperiksa');root.resizable(False,False)
    folder=tk.StringVar(value=default);start=tk.StringVar(value=date.today().replace(day=1).isoformat());end=tk.StringVar(value=date.today().isoformat());result=[]
    panel=ttk.Frame(root,padding=20);panel.grid()
    ttk.Label(panel,text='Folder laporan Excel').grid(row=0,column=0,columnspan=2,sticky='w')
    ttk.Entry(panel,textvariable=folder,width=65).grid(row=1,column=0,pady=8)
    def browse():
        chosen=filedialog.askdirectory(parent=root)
        if chosen:folder.set(chosen)
    ttk.Button(panel,text='Pilih folder',command=browse).grid(row=1,column=1,padx=8)
    for row,title,var in [(2,'Dari tanggal (YYYY-MM-DD)',start),(3,'Sampai tanggal (YYYY-MM-DD)',end)]:
        ttk.Label(panel,text=title).grid(row=row,column=0,sticky='w',pady=6);ttk.Entry(panel,textvariable=var,width=16).grid(row=row,column=1)
    def go():
        try:
            a,b=date.fromisoformat(start.get()),date.fromisoformat(end.get())
            if a>b:raise ValueError('Tanggal awal harus sebelum atau sama dengan tanggal akhir.')
            if not Path(folder.get()).is_dir():raise ValueError('Folder tidak ditemukan. Klik Pilih folder.')
            result.append((Path(folder.get()),a,b));root.destroy()
        except ValueError as exc:messagebox.showerror('Periksa isian',str(exc),parent=root)
    ttk.Button(panel,text='Mulai pemeriksaan',command=go).grid(row=4,column=0,columnspan=2,pady=15)
    root.mainloop();return result[0] if result else None

def run(folder,start,end,config,output=None):
    if start>end:raise ValueError('Rentang tanggal terbalik.')
    candidates=[];unknown=[]
    for p in folder.iterdir():
        if not p.is_file() or p.suffix.lower() not in ('.xlsx','.xlsm','.xls','.xlsb') or p.name.startswith(('~$','opd_saving_')):continue
        d=file_date(p.name)
        if d is None:unknown.append(p.name)
        elif start<=d<=end:candidates.append((d,p))
    candidates.sort(key=lambda x:(x[0],x[1].name));counts=Counter(d for d,p in candidates)
    records=[]
    for index,(d,p) in enumerate(candidates,1):
        print(f'[{index}/{len(candidates)}] {p.name}',flush=True)
        rec={'file':p.name,'date':d.isoformat(),'rows':[],'extras':[],'error':'','duplicate':counts[d]>1}
        try:
            if p.suffix.lower() not in ('.xlsx','.xlsm'):raise ValueError('Format belum didukung. Gunakan XLSX/XLSM.')
            if p.with_name('~$'+p.name).exists():raise ValueError('File sedang dibuka di Excel. Tutup lalu ulangi.')
            rec['rows'],rec['extras']=audit_file(p,config)
        except Exception as exc:rec['error']='File gagal diperiksa: '+str(exc)
        records.append(rec)
    missing=[];d=start
    while d<=end:
        if d not in counts:missing.append(d.isoformat())
        d+=timedelta(days=1)
    out=output or ROOT/'hasil_audit'/datetime.now().strftime('%Y-%m-%d_%H%M%S_%f');out.mkdir(parents=True,exist_ok=False)
    allrows=[r for rec in records for r in rec['rows']]
    export_empty_xlsx(out/'slot_belum_terisi.xlsx',allrows)
    write_html(out,records,missing,unknown,folder,start,end)
    (out/'hasil.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Selesai:',out/'hasil.html');return out

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--folder');parser.add_argument('--start');parser.add_argument('--end');parser.add_argument('--no-open',action='store_true');args=parser.parse_args()
    config_path=ROOT/'audit_config.json'
    if not config_path.exists():config_path=ROOT/'audit_config.example.json'
    config=json.loads(config_path.read_text(encoding='utf-8-sig'))
    if args.start and args.end:
        folder=Path(args.folder or config['folder']);start=date.fromisoformat(args.start);end=date.fromisoformat(args.end)
    else:
        selected=popup(args.folder or config['folder'])
        if not selected:return
        folder,start,end=selected
    if not folder.is_dir():raise ValueError('Folder tidak ditemukan: '+str(folder))
    out=run(folder,start,end,config)
    if not args.no_open:webbrowser.open((out/'hasil.html').resolve().as_uri())
if __name__=='__main__':
    try:main()
    except Exception as exc:print('ERROR:',exc);raise SystemExit(1)
