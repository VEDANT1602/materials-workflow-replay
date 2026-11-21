"""Independently check expanded catalog headline counts by sorted rational signatures."""
import csv
from fractions import Fraction
from itertools import groupby
from operator import itemgetter
from pathlib import Path

ROOT=Path(__file__).resolve().parent
def read(path):
    with path.open() as file:
        return list(csv.DictReader(file))

def check():
    first=read(ROOT/'catalog.csv')
    later=read(ROOT/'page_catalog.csv')
    orig={r['run'] for r in first}
    rows=first+later
    assert len(orig)==2688 and len(later)==8064 and len({r['run'] for r in rows})==10752
    assert {int(r['task']) for r in rows}=={3,6,12,23,28,31,37}
    formats=[(100,None),(100,10),(1000,None),(1000,100)]
    expected=[(1066,782,3167), (1110,792,3192), (1721,1207,4925), (2216,1634,6706)]
    for (ascale,kscale), totals in zip(formats,expected):
        values=[]
        for r in rows:
            signature=(r['task'],round(Fraction(r['predictive_accuracy'])*ascale))
            if kscale:
                signature+=(round(Fraction(r['kappa'])*kscale),)
            values.append((signature,Fraction(r['area_under_roc_curve']),r['run'] in orig))
        same=expanded=all_covered=0
        for _,group in groupby(sorted(values),key=itemgetter(0)):
            block=list(group)
            aucs=[s[1] for s in block]
            old=[s[1] for s in block if s[2]]
            if max(aucs)-min(aucs)<=Fraction(1,50):
                all_covered+=len(block)
                expanded+=len(old)
            if old and max(old)-min(old)<=Fraction(1,50):
                same+=len(old)
        assert (same,expanded,all_covered)==totals,(same,expanded,all_covered,totals)
    streams=read(ROOT/'page_sources.csv')
    assert len(streams)==63 and all(int(r['returned'])==384 and len(r['source_sha256'])==64 for r in streams)
    joins=read(ROOT/'page_joins.csv')
    assert len(joins)==21 and all(r['joined']==r['union']=='384' for r in joins)
    print('Seven tasks, 10,752 distinct runs, 63 later requests and all 12 Table 1 counts verified.')

if __name__=='__main__':
    check()
