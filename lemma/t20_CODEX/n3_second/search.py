"""Independent, single-process search on a T20 n3=2 base.

All decisions use integers, including Schur complements of projector matrices.
Complete leaves also undergo full-matrix exact integer Schur elimination.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
from collections import Counter
from dataclasses import dataclass
from itertools import combinations
import time
from model import (BASE_N, PAIR_ID, PAIR_MASKS, X0, X3, conjugate, mate,
                   needs, projector_blocks, psd, vertices,exact_psd)
from schur import BaseReduction


def add_orbit(rows, mask, inner):
    """Add two vertices with sigma-related neighbourhoods; enforce budgets.

    The old induced graph already passes all budgets. Only pairs touched by
    either new vertex need rechecking. Sigma lets us check one new row.
    """
    n = len(rows)
    other = conjugate(mask)
    if mask.bit_count() + inner > 14: return None
    if (mask & other).bit_count() > 2-inner: return None
    for i, row in enumerate(rows):
        adjacent = (mask >> i) & 1
        other_adjacent = (other >> i) & 1
        if row.bit_count() + adjacent + other_adjacent > 14: return None
        common = (row & mask).bit_count() + inner*other_adjacent
        if common > 2-adjacent: return None
    neighbours = list(vertices(mask))
    for a, b in combinations(neighbours, 2):
        extra = 1 + int(bool((other >> a) & 1) and bool((other >> b) & 1))
        if (rows[a] & rows[b]).bit_count() + extra > 2-((rows[a] >> b) & 1):
            return None
    result = list(rows) + [mask | (inner << (n+1)), other | (inner << n)]
    for i in neighbours: result[i] |= 1 << n
    for i in vertices(other): result[i] |= 1 << (n+1)
    return result


@dataclass(frozen=True)
class Candidate:
    u: int
    v: int
    inner: int
    mask: int
    other: int
    target: int
    base_inc: tuple
    schur: tuple


class TimeLimit(Exception): pass


class Search:
    def __init__(self, record, seconds=0):
        self.record = record
        self.base = record['rows']
        self.start = time.monotonic()
        self.deadline = self.start+seconds if seconds else float('inf')
        self.nodes = [0]*13
        self.rejects = Counter()
        self.complete = []
        self.need = needs(self.base, record['U'], record['V'])
        self.h2 = 3 if record['inner'] is None else 4
        self.alpha = int(record['case'] == 'iii')
        # Exact X2 incidences at p,z,z',X0'.
        self.tracked = list(range(20,29))
        self.targets = [2*self.h2,self.alpha,self.alpha] + [
            (self.base[i]&X0).bit_count()+6-2*(self.base[i]&X3).bit_count()
            for i in range(23,29)]
        self.candidates = []
        self.by_unit = [[] for _ in PAIR_MASKS]
        self.compatibility = {}
        self.pair_offsets = {}
        self.reduction = BaseReduction(self.base)
        self.catalog_seconds = 0

    def check_time(self):
        if time.monotonic() >= self.deadline: raise TimeLimit

    def catalog(self):
        started = time.monotonic()
        available = [i for i,need in enumerate(self.need) if need]
        for u,v in combinations(available, 2):
            U,V = PAIR_MASKS[u],PAIR_MASKS[v]
            for inner in (0,1):
                for zmask in ((0,1,2) if self.alpha else (0,)):
                    a3 = int(zmask != 0)
                    for W in range(64):
                        self.check_time()
                        target = W.bit_count()-2*a3
                        if target < 0 or target+inner > (3 if a3 else 5): continue
                        mask = U | (V<<10) | (inner<<20) | (zmask<<21) | (W<<23)
                        other = conjugate(mask)
                        inc = tuple(((mask>>i)&1)+((other>>i)&1) for i in self.tracked)
                        if any(x>y for x,y in zip(inc,self.targets)): continue
                        rows = add_orbit(self.base,mask,inner)
                        if rows is None: continue
                        schur = self.reduction.project(rows)
                        if schur is None: continue
                        c = Candidate(u,v,inner,mask,other,target,inc,schur)
                        cid = len(self.candidates)
                        self.candidates.append(c)
                        self.by_unit[u].append(cid); self.by_unit[v].append(cid)
        self.catalog_seconds = time.monotonic()-started

    def patterns(self, first, second):
        """Allowed edges between two candidate orbits, using the full base.

        Patterns: bit 0 direct, bit 1 cross. They are symmetric in the
        two orbits, so an unordered cache key suffices.
        """
        key = tuple(sorted((first,second)))
        if key in self.compatibility: return self.compatibility[key]
        a,b = self.candidates[first], self.candidates[second]
        offsets = self.reduction.offsets(a.schur,b.schur)
        self.pair_offsets[key] = offsets
        rows = add_orbit(self.base,a.mask,a.inner)
        assert rows is not None
        allowed = []
        for pattern in range(4):
            degree = pattern.bit_count()
            if degree > min(a.target,b.target): continue
            if any(x+y>z for x,y,z in zip(a.base_inc,b.base_inc,self.targets)): continue
            mask = b.mask | ((pattern&1)<<29) | (((pattern>>1)&1)<<30)
            extended = add_orbit(rows,mask,b.inner)
            if extended is None: continue
            entries = self.reduction.entries(offsets,pattern)
            if any(da[2]*db[2] < e*e for da,db,e in zip(a.schur,b.schur,entries)): continue
            allowed.append(pattern)
        self.compatibility[key] = tuple(allowed)
        return tuple(allowed)

    def visit(self, rows, placed, used, residual, degrees, grams):
        self.check_time()
        k = len(placed)
        self.nodes[k] += 1
        if k == 12:
            if any(used[i]!=self.need[i] for i in range(45)): return
            if any(residual): return
            if any(degrees[j]!=self.candidates[cid].target for j,cid in enumerate(placed)): return
            if psd(rows):
                self.complete.append(dict(candidates=placed,rows=rows))
            else: self.rejects['leaf_exact_psd'] += 1
            return
        remaining = 12-k
        # A future orbit contributes at most 2 neighbours to any old vertex.
        if any(r<0 or r>2*remaining for r in residual):
            self.rejects['base_capacity'] += 1; return
        if any(self.candidates[cid].target-d>2*remaining for cid,d in zip(placed,degrees)):
            self.rejects['orbit_capacity'] += 1; return
        # First order units cheaply, then choose the fewest actual viable
        # extensions. A partial scan may stop only after reaching the best
        # known size; such a unit cannot improve the choice.
        valid_by_unit = []
        for unit in range(45):
            if used[unit] == self.need[unit]: continue
            valid = []
            for cid in self.by_unit[unit]:
                c = self.candidates[cid]
                if used[c.u]>=self.need[c.u] or used[c.v]>=self.need[c.v]: continue
                if any(x>r for x,r in zip(c.base_inc,residual)): continue
                if any(not self.patterns(cid,old) for old in placed): continue
                valid.append(cid)
            if not valid:
                self.rejects['unit_empty'] += 1; return
            valid_by_unit.append((len(valid),unit,valid))
        extension_cache = {}
        def extensions(cid):
            if cid in extension_cache:return extension_cache[cid]
            self.check_time()
            result = []
            extension_cache[cid] = result
            c = self.candidates[cid]
            choices = [tuple(p for p in self.patterns(cid,old)
                       if degrees[j]+p.bit_count()<=self.candidates[old].target)
                       for j,old in enumerate(placed)]
            if any(not opts for opts in choices): return result
            minimum = [min(p.bit_count() for p in opts) for opts in choices]
            maximum = [max(p.bit_count() for p in opts) for opts in choices]
            if sum(minimum)>c.target: return result
            if sum(maximum)+2*(11-k)<c.target: return result
            suffix_min = [0]*(k+1)
            suffix_max = [0]*(k+1)
            for j in range(k-1,-1,-1):
                suffix_min[j]=suffix_min[j+1]+minimum[j]
                suffix_max[j]=suffix_max[j+1]+maximum[j]
            picked = [0]*k
            edge_patterns = [0]*k
            def connect(j, mask, degree):
                if degree+suffix_min[j]>c.target: return
                if degree+suffix_max[j]+2*(11-k)<c.target: return
                if j<k:
                    for pattern in choices[j]:
                        picked[j] = pattern.bit_count()
                        edge_patterns[j] = pattern
                        bits = ((pattern&1)<<(29+2*j)) | (((pattern>>1)&1)<<(30+2*j))
                        connect(j+1,mask|bits,degree+picked[j])
                    return
                extended = add_orbit(rows,mask,c.inner)
                if extended is None:
                    self.rejects['budget'] += 1; return
                columns = [self.reduction.entries(self.pair_offsets[tuple(sorted((cid,old)))],pattern)
                           for old,pattern in zip(placed,edge_patterns)]
                new_grams = []
                for block in range(4):
                    column = [entry[block] for entry in columns]
                    new = [row+[v] for row,v in zip(grams[block],column)] + [column+[c.schur[block][2]]]
                    if not exact_psd(new):
                        self.rejects['psd_'+str(block)] += 1; return
                    new_grams.append(new)
                result.append((cid,extended,[d+x for d,x in zip(degrees,picked)]+[degree],new_grams))
            connect(0,c.mask,0)
            return result
        best = None
        for _,unit,valid in sorted(valid_by_unit):
            options = []
            finished = True
            for cid in valid:
                options.extend(extensions(cid))
                if best is not None and len(options)>=len(best):
                    finished = False
                    break
            if finished:
                best = options
                if not best:
                    self.rejects['unit_empty_full'] += 1; return
        assert best is not None
        for cid,extended,new_degrees,new_grams in best:
            c = self.candidates[cid]
            new_used = list(used)
            new_used[c.u]+=1; new_used[c.v]+=1
            self.visit(extended, placed+[cid], new_used,
                       [r-x for r,x in zip(residual,c.base_inc)],new_degrees,new_grams)

    def run(self):
        status = 'complete'
        try:
            self.catalog()
            self.visit(self.base,[],[0]*45,list(self.targets),[],[[],[],[],[]])
        except TimeLimit:
            status = 'timeout'
        return dict(schema=1,base_id=self.record['id'],graph=self.record['graph'],
                    case=self.record['case'],profile='340' if self.record['inner'] is None else '421',
                    status=status,seconds=time.monotonic()-self.start,
                    catalog_seconds=self.catalog_seconds,candidates=len(self.candidates),
                    pair_cache=len(self.compatibility),nodes_per_level=self.nodes,
                    rejections=dict(self.rejects),complete_configurations=len(self.complete),
                    configurations=self.complete)
