from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict
from typing import Iterable
import json, os, time

DEFAULT_IGNORES={'.git','node_modules','__pycache__','.venv','.cull-quarantine'}

@dataclass(frozen=True)
class FileRecord:
    path:str
    relpath:str
    size:int
    mtime:float
    ext:str

@dataclass(frozen=True)
class ScanResult:
    root:str
    total_bytes:int
    file_count:int
    files:tuple[FileRecord,...]
    by_top:dict[str,int]
    by_ext:dict[str,int]
    by_age:dict[str,int]


def scan(root:str|Path, ignores:Iterable[str]=DEFAULT_IGNORES)->ScanResult:
    root=Path(root).expanduser().resolve(); ignores=set(ignores); files=[]; by_top=defaultdict(int); by_ext=defaultdict(int); by_age=defaultdict(int); now=time.time(); total=0
    for base,dirs,names in os.walk(root):
        dirs[:]=[d for d in dirs if d not in ignores]
        for name in names:
            p=Path(base)/name
            try:
                st=p.stat()
                if not p.is_file() or p.is_symlink(): continue
            except OSError: continue
            rel=p.relative_to(root).as_posix(); size=st.st_size; total+=size
            top=rel.split('/',1)[0]; ext=(p.suffix.lower() or '[no extension]')
            age_days=max(0,(now-st.st_mtime)/86400)
            bucket='≤30d' if age_days<=30 else '31–180d' if age_days<=180 else '181–365d' if age_days<=365 else '>1y'
            by_top[top]+=size; by_ext[ext]+=size; by_age[bucket]+=size
            files.append(FileRecord(str(p),rel,size,st.st_mtime,ext))
    files.sort(key=lambda f:f.size,reverse=True)
    return ScanResult(str(root),total,len(files),tuple(files),dict(sorted(by_top.items(),key=lambda x:x[1],reverse=True)),dict(sorted(by_ext.items(),key=lambda x:x[1],reverse=True)),dict(by_age))


def largest_files(result:ScanResult,n:int=100): return result.files[:n]

def export_json(result:ScanResult,path:str|Path): Path(path).write_text(json.dumps(asdict(result),indent=2),encoding='utf-8')

def layout_treemap(items:list[tuple[str,int]],x:float,y:float,w:float,h:float)->list[tuple[str,int,float,float,float,float]]:
    total=sum(v for _,v in items)
    if total<=0:return []
    out=[]; horizontal=w>=h; cursor=x if horizontal else y
    for name,value in items:
        frac=value/total
        if horizontal:
            sw=w*frac; out.append((name,value,cursor,y,sw,h)); cursor+=sw
        else:
            sh=h*frac; out.append((name,value,x,cursor,w,sh)); cursor+=sh
    return out