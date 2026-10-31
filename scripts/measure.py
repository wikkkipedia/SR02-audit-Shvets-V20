"""Approximate transparent lexical code metrics, NOT official Roslyn/NDepend measures."""
from pathlib import Path
import re,csv,sys,collections,json
ROOT=Path(__file__).resolve().parents[1]
CODES=sorted((ROOT/'src').glob('*.cs'))
TYPES=['Participant','Match','MatchStatus','MatchService','ResultTable','TableRow','TournamentRepository','ReportPrinter','EventLog','ScheduleRequest','RankingRowMapper']

def sanitize(s):
    # Replace comments/quoted strings with spaces while preserving line breaks.
    pat=re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|@"(?:""|[^"])*"|\$?"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')
    def repl(m):return ''.join('\n' if c=='\n' else ' ' for c in m.group())
    return pat.sub(repl,s)

rowlist=[]
for path in CODES:
    original=path.read_text(encoding='utf-8-sig')
    src=sanitize(original)
    src_types=[x for x in TYPES if re.search(r'\b(?:class|record|struct|enum|interface)\s+'+x+r'\b',src)]
    # Scope by class position for types in the same source file.
    typelocations=[(m.start(),m.group(1)) for m in re.finditer(r'\b(?:class|record|struct|enum|interface)\s+(\w+)',src)]
    # Include methods, constructors and expression-bodied methods.
    regex=re.compile(r'(?m)^[ \t]*(?:public|private|protected|internal|static|sealed|virtual|override|async|new|partial|readonly|unsafe|extern|\s)+[\w<>?\[\],. ]+?\s+(\w+)\s*\(([^()]*?)\)\s*(?:\{|=>)')
    for m in regex.finditer(src):
        name=m.group(1)
        if name in ['if','while','for','foreach','switch','catch','using','nameof']:continue
        openchar=m.end()-1
        if src[openchar:openchar+1]=='=':
            end=src.find(';',openchar)+1
            if end<=0:continue
        else:
            depth=0; end=-1
            for k in range(openchar,len(src)):
                if src[k]=='{':depth+=1
                elif src[k]=='}':
                    depth-=1
                    if depth==0:end=k+1;break
            if end<0:continue
        body=src[openchar+1:end-1]
        firstline=src.count('\n',0,m.start())+1
        logical=sum(bool(line.strip()) and line.strip() not in ['{','}'] for line in body.splitlines())
        ccs=1+len(re.findall(r'\b(?:if|for|foreach|while|do|catch|case)\b|&&|\|\||\?\?|\?\.|\?(?=\s*[^:?]+\s*:)',body))
        depth=1;deep=1
        for ch in body:
            if ch=='{':depth+=1;deep=max(deep,depth)
            elif ch=='}':depth-=1
        params=0 if not m.group(2).strip() else len(m.group(2).split(','))
        current=max((t for t in typelocations if t[0]<m.start()),default=(-1,src_types[0] if src_types else path.stem))[1]
        type_count=len({t for t in TYPES if t!=current and re.search(r'\b'+t+r'\b',src)})
        rowlist.append(dict(File=path.name,Class=current,Method=name,Line=firstline,LOC=logical,CC=ccs,Depth=deep,Parameters=params,FanOut=type_count))

# A conservative exact normalized-line clone detector; no claim of semantic clones.
lines=[]
for p in CODES:
    for n,line in enumerate(sanitize(p.read_text(encoding='utf-8-sig')).splitlines(),1):
        normalized=re.sub(r'\s+','',line)
        if normalized and normalized not in ['{','}','};']:
            lines.append((p.name,n,normalized))
clones=collections.defaultdict(list)
for i in range(len(lines)-5):
    window=lines[i:i+6]
    if len({w[0] for w in window})!=1 or any(window[j+1][1]!=window[j][1]+1 for j in range(5)):continue
    clones[tuple(x[2] for x in window)].append((window[0][0],window[0][1]))
clonegroups=[loc for loc in clones.values() if len({k[0]+str(k[1]) for k in loc})>=2]

where=ROOT/'audit'
where.mkdir(exist_ok=True)
phase=sys.argv[1] if len(sys.argv)>1 else 'before'
out=where/f'metrics-{phase}.csv'
with out.open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['File','Class','Method','Line','LOC','CC','Depth','Parameters','FanOut'],delimiter=';')
    w.writeheader();w.writerows(rowlist)
summary={
    'phase':phase,'files':len(CODES),'physical_lines':sum(len(p.read_text(encoding='utf-8-sig').splitlines()) for p in CODES),
    'nonblank_noncomment_lines':sum(sum(bool(line.strip()) for line in sanitize(p.read_text(encoding='utf-8-sig')).splitlines()) for p in CODES),
    'methods_measured':len(rowlist),'max_cc':max((x['CC'] for x in rowlist),default=0),
    'avg_cc':round(sum(x['CC'] for x in rowlist)/len(rowlist),2) if rowlist else 0,
    'longest_method_LOC':max((x['LOC'] for x in rowlist),default=0),
    'max_depth':max((x['Depth'] for x in rowlist),default=0),
    'clone_windows_6':len(clonegroups),
    'max_fan_out':max((x['FanOut'] for x in rowlist),default=0),
}
(where/f'summary-{phase}.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
for x in sorted(rowlist,key=lambda r:r['CC'],reverse=True)[:15]:print(x['Class'],x['Method'],x['CC'],x['LOC'],x['Depth'])
