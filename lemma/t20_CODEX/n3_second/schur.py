"""Exact reduction of projector matrices by the fixed 29-vertex base.

For a positive principal block K, write H=D*K^-1 with D>0 integral.
The range conditions at every omitted (zero-pivot) base coordinate are
checked exactly. The remaining matrix is D*C - B^T*H*B. Thus its PSD
is equivalent to that of the full projector block. No rank bound is assumed.
"""
from fractions import Fraction as F
from math import lcm
from model import projector_blocks


class Reduction:
    def __init__(self, matrix):
        self.matrix = matrix
        n = len(matrix)
        a = [[F(v) for v in row] for row in matrix]
        pivots = []
        for k in range(n):
            assert a[k][k]>=0
            if not a[k][k]:
                assert not any(a[k][j] for j in range(k+1,n))
                continue
            pivots.append(k)
            for i in range(k+1,n):
                for j in range(i,n):
                    a[i][j]-=a[i][k]*a[k][j]/a[k][k]
                    a[j][i]=a[i][j]
        self.pivots=pivots
        self.omitted=[i for i in range(n) if i not in pivots]
        m=len(pivots)
        aug=[[F(matrix[i][j]) for j in pivots]+[F(k==h) for h in range(m)]
             for k,i in enumerate(pivots)]
        for k in range(m):
            d=aug[k][k]
            assert d>0
            aug[k]=[x/d for x in aug[k]]
            for i in range(m):
                if i==k:continue
                x=aug[i][k]
                aug[i]=[v-x*w for v,w in zip(aug[i],aug[k])]
        inv=[row[m:] for row in aug]
        self.D=lcm(*(v.denominator for row in inv for v in row))
        self.H=[[int(v*self.D) for v in row] for row in inv]

    def project(self, column, diagonal):
        b=tuple(column[i] for i in self.pivots)
        hb=tuple(sum(x*y for x,y in zip(row,b)) for row in self.H)
        for i in self.omitted:
            if self.D*column[i] != sum(self.matrix[i][j]*x for j,x in zip(self.pivots,hb)):
                return None
        q=self.D*diagonal-sum(x*y for x,y in zip(b,hb))
        if q<0:return None
        return b,hb,q


class BaseReduction:
    def __init__(self,rows):
        self.reductions=[Reduction(m) for m in projector_blocks(rows)]
        self.rep_count=10+(len(rows)-21)//2

    def project(self,extended_rows):
        data=[]
        for k,(red,matrix) in enumerate(zip(self.reductions,projector_blocks(extended_rows))):
            i=self.rep_count
            col=matrix[i][:i]
            if k&1: col=col+[matrix[i][-1]] # p is last in the even basis
            item=red.project(col,matrix[i][i])
            if item is None:return None
            data.append(item)
        return tuple(data)

    def offsets(self,a,b):
        constants=(0,4,0,-8)
        return tuple(red.D*constant-sum(x*y for x,y in zip(da[0],db[1]))
                     for red,constant,da,db in zip(self.reductions,constants,a,b))

    def entries(self,offsets,pattern):
        direct,cross=pattern&1,(pattern>>1)&1
        coeff=(-direct+cross,-18*(direct+cross),direct-cross,22*(direct+cross))
        return tuple(offset+red.D*c for offset,red,c in zip(offsets,self.reductions,coeff))
