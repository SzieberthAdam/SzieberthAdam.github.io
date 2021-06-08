import pathlib
import re
import subprocess
import sys

from hyphen import Hyphenator

mtxrun_args = ["--script", "pattern", "--hyphenate", "--language=hu", "--left=1", "--right=1"]

kezdő_állapotok = ("feladó", "címzett", "tárgymegjelöles", "megszólítás", "főszöveg")
záró_állapotok = ("keltezés", "üdvözlésaláírás")

def contextexceptions(szó, h_szótagok):
    r = []
    h_szó = "=".join(h_szótagok)
    i, hi = 0, 0
    while True:
        szó_betű = szó[i]
        szótag_betű = h_szó[hi]
        if szó_betű == szótag_betű:
            r.append(szó_betű)
        elif szótag_betű == "=" and h_szó[hi+1] == szó_betű:
            if 1 < i:
                utolsó_betű = r.pop()
                első = f'{utolsó_betű}-'
                második = ""
                harmadik = utolsó_betű
                r.append(f'{{{első}}}{{{második}}}{{{harmadik}}}')
            i -= 1
        elif h_szó[hi+1] == "=" and h_szó[hi+2] == r[-1]:  
            utolsó_betű = r.pop()
            első, második = h_szó[hi-1:hi+4].split("=") # ny=ny alak
            első = első + "-"
            harmadik = szó[i-1:i+2]
            r.append(f'{{{első}}}{{{második}}}{{{harmadik}}}')
            i = i + 1
            hi = hi + 3
        else:
            print([szó[i:], h_szó[hi:]])
            raise NotImplementedError()
        i += 1
        hi += 1
        if len(szó) == i:
            break
    return "".join(r)


if __name__ == "__main__":
    h = Hyphenator('hu_HU', lmin=1, rmin=1, compound_lmin=1, compound_rmin=1)
    
    if 1 < len(sys.argv):
        fájlnév = sys.argv[1]
    else:
        fájlnév = "level.txt"
    
    p = pathlib.Path(fájlnév).resolve()
    with p.open(encoding="utf8") as fp:
        sorok = fp.readlines()

    előző_sor = ""
    
    főszöveg = []
    
    kezdő_állapot = 0
    for sor in sorok:
        sor = sor.strip()
        k = kezdő_állapotok[kezdő_állapot]
        if not sor:
            if sor != előző_sor:
                if k != "főszöveg":
                    kezdő_állapot += 1
                    k = kezdő_állapotok[kezdő_állapot]
                if k == "főszöveg":
                    főszöveg.append([])
        else:
            if k == "főszöveg":
                főszöveg[-1].append(sor)
        előző_sor = sor
                
    for k in záró_állapotok:
        főszöveg.pop()
    
    főszöveg_s = "\n\n".join("\n".join(bekezdes) for bekezdes in főszöveg)
    
    szavak = sorted(s2 for s2 in set(re.split(r'\W+', főszöveg_s)) if s2 and not s2.isdecimal())
    elválasztások = []
    
    for szó in szavak:
        print(szó)
        h_szótagok = h.syllables(szó)
        if len(h_szótagok) < 2:
            continue
        mtxrun = subprocess.check_output(['mtxrun'] + mtxrun_args + [szó]).decode("utf8")
        mtx_patterns = [sor for sor in mtxrun.split("\n") if sor.startswith("mtx-patterns")][0]
        mtx1, mtx2 = [s.strip() for s in mtx_patterns.split(":")[-2:]]
        mtx_szótagok = mtx2.split("-")
        if h_szótagok != mtx_szótagok:
            e = contextexceptions(szó, h_szótagok)
            print(f'kivétel: {e}')
            elválasztások.append(e)

    pki = p.parent / f'{p.stem}_hyp.tex'
    
    s_ki00 = "\startenvironment *\n\startexceptions[hu]"
    s_ki99 = "\stopexceptions\stopenvironment"
    
    with pki.open("w", encoding="utf8") as fn:
        fn.write("\n".join([s_ki00] + elválasztások + [s_ki99]) + "\n") 