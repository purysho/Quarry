from __future__ import annotations
import threading, tkinter as tk
from tkinter import ttk,filedialog,messagebox
from pathlib import Path
from quarry_core import scan,largest_files,export_json,layout_treemap
BG='#0d0c09'; PANEL='#17140d'; TEXT='#f4efe3'; MUTED='#a89e8e'; GOLD='#d9a74e'; ORE='#f4c76d'; ROCK='#6f6554'
def fmt(n):
    n=float(n)
    for u in ['B','KB','MB','GB','TB']:
        if n<1024 or u=='TB':return f'{n:.1f} {u}'
        n/=1024
class QuarryApp(tk.Tk):
    def __init__(self):
        super().__init__(); self.title('Quarry — Disk Space Explorer'); self.geometry('1240x800'); self.minsize(960,640); self.configure(bg=BG); self.result=None; self.root_var=tk.StringVar(); self._style(); self._build()
    def _style(self):
        s=ttk.Style(self); s.theme_use('clam'); s.configure('.',background=BG,foreground=TEXT,fieldbackground=PANEL); s.configure('TButton',background='#272116',foreground=TEXT,padding=8); s.configure('Treeview',background=PANEL,fieldbackground=PANEL,foreground=TEXT,rowheight=27); s.configure('Treeview.Heading',background='#211b11',foreground=TEXT)
    def _build(self):
        h=tk.Frame(self,bg=BG);h.pack(fill='x',padx=24,pady=(18,10));tk.Label(h,text='QUARRY',bg=BG,fg=TEXT,font=('Segoe UI Semibold',28)).pack(side='left');tk.Label(h,text='  expose where the space went',bg=BG,fg=MUTED).pack(side='left',pady=(12,0))
        r=tk.Frame(self,bg=BG);r.pack(fill='x',padx=24,pady=8);ttk.Entry(r,textvariable=self.root_var).pack(side='left',fill='x',expand=True);ttk.Button(r,text='Browse',command=self.browse).pack(side='left',padx=8);ttk.Button(r,text='Excavate',command=self.run).pack(side='left');ttk.Button(r,text='Export JSON',command=self.export).pack(side='right')
        self.status=tk.Label(self,bg=BG,fg=GOLD,anchor='w',font=('Consolas',10));self.status.pack(fill='x',padx=24,pady=(2,10))
        body=tk.Frame(self,bg=BG);body.pack(fill='both',expand=True,padx=24,pady=(0,20));body.grid_columnconfigure(0,weight=3);body.grid_columnconfigure(1,weight=2);body.grid_rowconfigure(0,weight=1)
        left=tk.Frame(body,bg=PANEL,highlightbackground='#2c261c',highlightthickness=1);left.grid(row=0,column=0,sticky='nsew',padx=(0,8));right=tk.Frame(body,bg=PANEL,highlightbackground='#2c261c',highlightthickness=1);right.grid(row=0,column=1,sticky='nsew',padx=(8,0))
        tk.Label(left,text='SPACE STRATA',bg=PANEL,fg=ORE,font=('Segoe UI Semibold',10)).pack(anchor='w',padx=14,pady=(12,4));self.canvas=tk.Canvas(left,bg='#100e0a',highlightthickness=0);self.canvas.pack(fill='both',expand=True,padx=12,pady=(0,12));self.canvas.bind('<Configure>',lambda e:self.draw())
        tk.Label(right,text='LARGEST FILES',bg=PANEL,fg=ORE,font=('Segoe UI Semibold',10)).pack(anchor='w',padx=14,pady=(12,4));self.tree=ttk.Treeview(right,columns=('size','path'),show='headings');self.tree.heading('size',text='SIZE');self.tree.heading('path',text='PATH');self.tree.column('size',width=90);self.tree.column('path',width=420);self.tree.pack(fill='both',expand=True,padx=12,pady=(0,12))
    def browse(self):
        p=filedialog.askdirectory();
        if p:self.root_var.set(p)
    def run(self):
        p=self.root_var.get();
        if not Path(p).is_dir():messagebox.showerror('Quarry','Choose a folder or drive.');return
        self.status.config(text='Excavating directory tree…');threading.Thread(target=self._run,args=(p,),daemon=True).start()
    def _run(self,p):
        try:r=scan(p)
        except Exception as e:self.after(0,lambda:messagebox.showerror('Quarry',str(e)));return
        self.after(0,lambda:self.show(r))
    def show(self,r):
        self.result=r;self.tree.delete(*self.tree.get_children());
        for f in largest_files(r,150):self.tree.insert('','end',values=(fmt(f.size),f.relpath))
        self.status.config(text=f'{r.file_count:,} files  ·  {fmt(r.total_bytes)} total  ·  largest top-level item: {next(iter(r.by_top),"—")}');self.draw()
    def draw(self):
        c=self.canvas;c.delete('all');
        if not self.result:return
        w=max(c.winfo_width(),10);h=max(c.winfo_height(),10);items=list(self.result.by_top.items())[:14];rects=layout_treemap(items,0,0,w,h)
        palette=['#2c2417','#3a2d18','#4a381c','#5d451e','#6e5121','#806026','#93702c','#a98035','#be9340','#d2a74b','#e3b85a','#f0c86a','#f7d77d','#ffe69a']
        for i,(name,val,x,y,rw,rh) in enumerate(rects):
            c.create_rectangle(x+2,y+2,x+rw-2,y+rh-2,fill=palette[min(i,len(palette)-1)],outline='#d6b268' if i<4 else '#4f4638')
            if rw>80 and rh>42:
                c.create_text(x+10,y+12,anchor='nw',fill='#fff7e8',font=('Segoe UI Semibold',10),text=name[:28]);c.create_text(x+10,y+31,anchor='nw',fill='#e9d1a0',font=('Consolas',9),text=fmt(val))
    def export(self):
        if not self.result:messagebox.showinfo('Quarry','Run a scan first.');return
        p=filedialog.asksaveasfilename(defaultextension='.json',filetypes=[('JSON','*.json')]);
        if p:export_json(self.result,p);self.status.config(text=f'Exported {Path(p).name}')
if __name__=='__main__':QuarryApp().mainloop()