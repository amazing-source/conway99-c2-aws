# Exact model and the decision question

## 1. Fixed coordinates

Let the 21 cells be the unordered pairs c={i,j} with 1<=i<j<=7, ordered lexicographically.
Each cell contains two orbit indices (c,+), (c,-), in that order.
The 42x7 integer matrix R has rows

    r_(c,+) = e_i+e_j,
    r_(c,-) = e_i-e_j.

Set M=|R| entrywise. I_n is the n-dimensional identity; J_(a,b) is the all-ones a-by-b matrix; J_n=J_(n,n).
Every product below is ordinary matrix multiplication, except the explicit entrywise absolute value and entrywise support conditions.

## 2. Signed candidate set S

A complete N is in S exactly when

    N is a symmetric 42x42 integer matrix;
    diag N=0;
    N_uv is in {-1,0,1};
    NR=0;
    N^2=N+12I_42-RR^T.

No candidate in S is supplied. Nonemptiness of S is not established by the handoff or the reviewer transcript.

For N in S define

    B=|N|,
    T=2J_(42,7)-M-(BM)/2,
    E=(8I_42+4J_42-MM^T-B^2-B)/2.

The canonical signs are important. They fix chi by R 1_7=2 chi, where chi selects the plus index in each cell.

## 3. The real-linear completion system L_N

D is a REAL 42x42 matrix. Impose exactly

    D=D^T;
    D_uv>=0 for all u,v;
    diag D=0;
    D 1_42=1_42;
    D_uv=0 whenever B_uv=1;
    DM=T;
    BD+DB+D=E.

Do not impose integrality or D^2=I when invoking the real-linear theorem; those are conclusions of T4 under the stated N hypotheses.

For fixed N these are linear equalities/inequalities in D. They are not jointly a linear problem in unknown N and D. In particular B=|N| and B^2, BD are not fixed coefficients while N is varying.

## 4. T4 — working theorem, independently hand-reviewed according to the supplied transcript

For every complete N in S, L_N is either empty or a singleton. If nonempty, its sole D is an integral fixed-point-free perfect matching: symmetric, binary, one 1 per row, zero diagonal, D^2=I, and disjoint from B.

The supplied reviewer reports an independent derivation and no gap in this theorem. See AUDIT_STATUS.md. This packet does not claim formal verification.

## 5. Reconstruction and extraction

For N in S and D in L_N, set

    Q=B+2D,
    a=(Q-N)/2,
    b=(Q+N)/2,
    H_ext=[[a,b],[b,a]].

The canonical R specifies the two inner neighbours of every exterior representative, and their sign-reversed neighbours for its involution mate. Add the fixed vertex, fourteen inner vertices, seven inner matching edges, and H_ext on the 84 exterior vertices.

The reconstruction in reference/GRAPH_RECONSTRUCTION.md gives a symmetric binary 99x99 A with zero diagonal satisfying

    A 1=14 1,
    A^2+A=12I_99+2J_99,

and the prescribed involution fixing exactly the added vertex.

Conversely, every graph with these SRG parameters and an involution fixing exactly one vertex can be put in these canonical coordinates and gives a pair (N,D) as above.

## 6. The actual target

Decide the statement

    EX := exists N in S such that L_N is nonempty.

This is NOT the question whether T4 is true. T4 is the bridge used to interpret EX.

- Explicit N,D satisfying the exact conditions give an explicit Conway graph with a one-fixed-point involution. Verify A directly before a positive announcement. No F0 input is required for this direction.
- A proof that EX is false excludes all one-fixed-point involutions.
- F0 states that every involution of an srg(99,14,1,2) fixes exactly one vertex. With F0, a negative EX result excludes every involution, hence C2.
- A negative C2 result alone does not exclude a graph without an involution. Other automorphism exclusions must be cited separately if used.

A proof that S is empty would suffice, but is stronger than needed. A condition derived from L_N cannot automatically be used to claim S is empty.

## 7. Quantifier distinctions

    one N rejected != every N rejected;
    no symmetric N != no N;
    partial row/star/skeleton != complete N;
    unique integral completion when feasible != feasibility;
    two-completion contradiction != contradiction from one graph;
    a property needed by a global solution != already satisfied by every prefix.

One verified explicit positive witness suffices. Negative evidence must cover all candidates, by a theorem or an exhaustive justified partition and complete certificates. Timeouts and sampled failures do not do this.
