# Mandat C — transformations exactes, rigidité, symétrie forcée

Session LAP, 9 octobre 2026, 09:29–09:56 UTC. Révision consultée : `amazing-source/conway99-c1`, branche
`codex/c1-arithmetic-audit`, commit `19ec316`. Lus : `AGENTS.md`, `RECHERCHE_ACTIVE_C1.md`, notes 90, 91, 158, 159,
220 (§ transformations), 162 (rigidité GM), annexe D (routes closes).

## 0. Verdict

**Aucun résultat substantiel pour C1.** Je n'ai ni mouvement applicable à tout candidat, ni symétrie forcée sans
hypothèse, ni invariant strictement monotone. Ce qui est obtenu : des théorèmes de rigidité sur les mouvements
(§3), la description exacte du seul mouvement connu de la famille (§4), et un pilote négatif (§5). Ce sont des
résultats sur la méthode ; ils n'excluent aucun candidat.

Ce que ces résultats enlèvent réellement : la possibilité d'un mouvement *local* (toute modification par bloc
orthogonal touche au moins 9 sommets, §3.2), et le mécanisme du 243 comme modèle pour 99 (il ne déplace que des
arêtes de grilles lointaines, qui portent au plus 96 des 240 arêtes lointaines d'un candidat, §4).

## 1. Résultat antérieur le plus proche

- Note 159 : bascule du graphe lointain d'un triangle, BvLS ↔ 243 tordu ; rigide pour 4 types de triangles sur 5
  du graphe tordu. La note demande une description algébrique (« Suite »).
- Note 158 : pour une droite T, Z = ker B_Cᵀ = F₋₄ ⊕ F₃ et A_far = 3P_Z − 7P₈ sur Z.
- Note 162 : aucun ensemble de commutation de Godsil–McKay dans un srg(v,k,1,2), k ≥ 8.
- Note 90 §6 : schéma de B₇ sur les 84 étiquettes, borne de Delsarte locale triviale au premier ordre.

Différence effective : §3.1 et §3.3 s'appliquent à toute paire de candidats et à toute base, pas seulement à une
droite ; §3.2 remplace la matrice particulière de Godsil–McKay par un bloc orthogonal quelconque ; §4 donne la règle
fermée de la bascule ; §5 ajoute la sensibilité au rang (dimensions 30 et 40) que le premier ordre n'avait pas.

## 2. Proposition attaquée

> **Proposition C (cible).** Dans tout srg(99,14,1,2), pour toute droite T, l'étage lointain est déterminé par la
> boule de T et les 60 ombres : il n'existe pas deux candidats distincts ayant la même boule et les mêmes
> incidences proche–lointain.

Conséquence visée : toute symétrie de (boule, ombres) se prolonge en automorphisme, donc est triviale par les
exclusions du programme (dépendance : C2/C3 et ordres 7, 11) ; et la route « transformations » par bascule de
triangle est fermée à 99. **Statut : non démontrée.** Démontrée seulement dans les cas du §3.3.

## 3. Résultats démontrés

Notations : A, A′ deux candidats sur le même ensemble de sommets, D = A′ − A, E et E′ les projecteurs
orthogonaux sur leurs espaces propres −4 (rang 44).

### 3.1 Toute paire de candidats est une paire de projecteurs

**Lemme 1.** D = 7(E − E′). Donc : (a) le spectre de D est symétrique et contenu dans [−7, 7], ses valeurs propres
sont ±7 sin θ_i pour les angles principaux θ_i entre les deux espaces propres −4 ; (b) tr D^(2k+1) = 0 ;
(c) le nombre de paires modifiées vaut 49·Σ sin²θ_i ; (d) D² commute avec A et avec A′.

*Preuve.* A = 3I + J/9 − 7E et de même pour A′. Le reste est la théorie de deux projecteurs de même rang :
(E − E′)² commute avec E et E′, et les espaces propres ±1 de E − E′ ont même dimension. ∎

**Lemme 2 (mouvements de rang 2).** Si D est de rang 2, alors A′ est A avec deux sommets échangés.

*Preuve.* D = xyᵀ + yxᵀ avec x ⊥ y, supports disjoints (diagonale nulle), et x, y à valeurs ±1 sur leurs supports
X, Y. L'équation AD + DA + D² + D = 0 équivaut à : vect(x, y) est stable par A, avec Ax = (α − ½)x + (|x|²/2)y et
Ay = (|y|²/2)x − (α + ½)y. Les valeurs propres sont 3 et −4, d'où |X||Y| = 49 − 4α² avec α ∈ ½ + Z. Les paires de
signes opposés forment un K_{a,b} dans Γ (a = |X|/2, b = |Y|/2), donc (a, b) = (2, 2), exclu car 4α² = 33, ou a = 1,
qui force b = 12 : Y est toute la différence symétrique des voisinages des deux sommets de X. ∎

### 3.2 Aucun mouvement par bloc de moins de 9 sommets

**Théorème 3.** Soit Γ un srg(v,k,1,2), k ≥ 8, C un ensemble de sommets, R une matrice orthogonale réelle sur C,
Q = R ⊕ I. Si QᵀAQ est une matrice 0/1, alors, après retrait des indices où R agit comme une permutation, le bloc
restant C₀ est vide ou vérifie |C₀| ≥ k/2 + 2. Pour 99 : |C₀| ≥ 9. Pour 243 : |C₀| ≥ 13.

*Preuve.* Pour j ∉ C, la colonne a_j ∈ {0,1}^C devient Rᵀa_j, qui doit être 0/1. Si a_j = e_i, Rᵀe_i est un
vecteur unité : i est un indice de permutation. Donc tout voisin extérieur d'un i ∈ C₀ a un autre voisin dans C₀.
Un i' adjacent à i partage au plus 1 voisin avec i, un i' non adjacent au plus 2 : k − k_i ≤ k_i + 2(c₀ − 1 − k_i),
soit c₀ ≥ k/2 + 1. En cas d'égalité, tout sommet extérieur voit 0 ou 2 points de C₀ et toutes les paires
apparaissent, donc Rᵀ(e_i + e_i') est une somme de deux vecteurs unités pour toute paire. L'application
paires → paires ainsi définie est un automorphisme du graphe triangulaire T(c₀), donc induite par une permutation
dès que c₀ ≥ 5 (seul T(4) a des automorphismes exotiques, et c'est le bloc de Godsil–McKay) ; alors R est une
permutation, contradiction. ∎

### 3.3 Bascules à boule fixée

Soit T une droite, F ses 60 lointains, N_F l'incidence proche × lointain. On suppose A et A′ égaux hors de F × F.

**Lemme 4.** N_F D = 0, et toute ligne non nulle de D a au moins 3 entrées +1 et 3 entrées −1.

*Preuve.* (A²)_{proche, lointain} est fixé par la boule et les ombres, d'où N_F D = 0 : pour la ligne de f, la
réunion (avec multiplicités) des ombres des voisins retirés égale celle des voisins ajoutés. Deux lointains
distincts ont au plus 2 voisins communs, donc une ombre de 6 points n'est couverte que par au moins 3 autres. ∎

**Lemme 5.** Si D ≠ 0 et si S est l'ensemble des lointains dont la ligne change, il existe un vecteur propre de A
pour −4 et un autre pour 3, non nuls, à support dans S.

*Preuve.* Pour f ∉ S, De_f = 0 donne Π e_f = Π′e_f ∈ U ∩ U′ (U, U′ les espaces propres −4 nuls sur la boule). Si
D ≠ 0, U ⊄ U′ ; un x ∈ U orthogonal à U ∩ U′ est orthogonal à tous les Πe_f, f ∉ S, donc nul hors de S. Même
argument sur les compléments dans Z. ∎

**Lemme 6 (rang modulo 7).** Si G(T) est connexe et 7 ∤ τ(G(T)), et si r, r′ sont les rangs modulo 7 de A − 3I et
A′ − 3I, alors rang_{F₇}(D) ≤ r + r′ − 74.

*Preuve.* Les sommets ont des images v_i dans un espace quadratique de dimension r − 1 sur F₇, de Gram
3I − A + 4J. Le bloc proche est L + 4J, de déterminant 4·36²·τ ≢ 0. Le complément de Schur du bloc lointain,
Y_fg = (4 − A_fg) − q(n_f, n_g), est de rang r − 37, et q ne dépend que de (G, ombres). Donc D ≡ Y − Y′. ∎

**Théorème 7.** Sous les hypothèses du lemme 6, r + r′ ≥ 78 dès que D ≠ 0. En particulier un candidat de rang 37
n'a pas d'autre complétion de rang 37 (déjà acquis, voir note 230) **ni de rang 39** (nouveau).

*Preuve du cas (37, 39).* Y = 0, donc D ≡ −Y′, symétrique de rang ≤ 2 sur F₇ à diagonale nulle. Rang 1 : impossible
(xxᵀ à diagonale nulle est nul). Rang 2 : Y′ = XBXᵀ, toutes les lignes de X isotropes pour B, donc B hyperbolique
et les lignes sont portées par ses deux droites isotropes. D est alors biparti complet entre deux classes F₁, F₂,
avec D_fg = κ s_f s_g, s = ±1. Les sommes de lignes nulles donnent un K_{a,b} dans Γ avec a = |F₁|/2, b = |F₂|/2.
Le lemme 4 donne a ≥ 3 et b ≥ 3, donc K₃,₃ ⊂ Γ : impossible (μ = 2). ∎

**Corollaire 8 (symétrie forcée, conditionnelle).** Dans un candidat de rang 37, pour toute droite T avec G(T)
connexe et 7 ∤ τ, tout automorphisme de (boule, ombres) est un automorphisme de Γ. Avec les exclusions du programme,
(boule, ombres) est donc sans symétrie. *Preuve :* l'image de A par la symétrie est une complétion de même rang. ∎

**Complément de Codex (message LAB du 9 octobre, 10:41 UTC ; note 232 annoncée, pas encore poussée).** Les cas
(37,41) et (37,43) sont fermés aussi : au rang 37, à droite générique, la complétion est unique parmi tous les
rangs. J'ai relu l'argument, il est correct. *Lemme (Codex).* Si D² ≡ 0 modulo 7 et si les profils des sommets
modifiés sur les sommets non modifiés sont deux à deux distincts, alors D = 0. *Preuve.* Hors diagonale,
(D²)_uv ≤ (A²)_uv + (A′²)_uv ≤ 4, donc un multiple de 7 y est ≤ 0 ; D1 = 0 donne D²1 = 0 : D² est un laplacien à
poids positifs. Pour chaque ligne b de l'incidence non modifiés × modifiés, bD = 0, donc
0 = b D² bᵀ = Σ w_uv (b_u − b_v)² ; un poids non nul forcerait deux profils égaux. Donc D² = 0 et D = 0. ∎
Au rang 37, Y = 0 donne D² ≡ 0 sans hypothèse sur A′ (dans les notations du lemme 6, D² ≡ −(YY′ + Y′Y)).
Remarque de ma part : l'hypothèse des profils distincts est automatique dès que chaque sommet modifié a au moins
3 voisins non modifiés (deux sommets ont au plus 2 voisins communs) ; le lemme vaut donc pour toute paire de
candidats de ce type, pas seulement à boule fixée. Le corollaire 8 ne dépend plus du rang de l'autre complétion.

**Second complément de Codex (message LAB de 10:46 UTC ; note 233, commit local `5054889`, non poussée).** Annoncé :
aucune différence D de rang ≤ 4 sur F₇ entre deux complétions des mêmes boule et ombres ; par le lemme 6 cela ferme
(39,39) quand le bloc proche est inversible. Preuve assistée par un petit calcul exact selon Codex (729 Grams
principaux, une seule géométrie signée survivante de Gram K ⊗ K, quatre supports de 14 à 18 sommets éliminés par
résolution exacte). **Je ne l'ai pas relue : la note n'est pas accessible depuis ce poste.** Conséquence annoncée :
au rang 39 générique, toute symétrie de (boule, ombres) se prolonge au graphe, comme au rang 37.

Cas restants pour la proposition C : droites non génériques (τ ≡ 0 ou G(T) déconnecté), et paires de rangs avec
r + r′ ≥ 80, soit rang de D sur F₇ jusqu'à 6 pour (39,41), 8 pour (39,43) et (41,41), 10 pour (41,43), 12 pour
(43,43). Dans ces cas D² ≡ −(YY′ + Y′Y) n'a pas de signe imposé et l'argument du laplacien ne s'applique pas tel
quel ; il s'applique encore si les espaces colonnes de Y et Y′ sont orthogonaux.

## 4. La bascule du 243 décodée (calcul exact, `flip243*.py`, sortie `pilotes.out`)

BvLS = Cay(F₃⁵, S), T = ⟨e₀⟩, quotient F₃⁴ muni de la quadrique elliptique Q (20 vecteurs singuliers = projection de
S) ; lointains = {Q ≠ 0}, deux classes de 90.

- D a pour spectre (±√45)³², 0¹⁷⁹ ; **D³ = 45 D** : les 32 angles principaux non nuls sont égaux, cos²θ = 4/9.
  A et A′ ne commutent pas ; D² commute avec les deux.
- Les arêtes lointaines entre les deux classes sont conservées. Les 720 arêtes retirées sont exactement celles à
  l'intérieur d'une classe (B(x̄, s̄) = 0).
- **La bascule est la re-réglure simultanée de 80 grilles 3 × 3 lointaines** x + ⟨e₀, s⟩ : chaque grille garde sa
  réglure parallèle à T et échange l'autre contre une des deux réglures diagonales (direction s ± e₀). Chaque
  lointain est dans 4 de ces grilles ; aucune paire modifiée hors de ces grilles.

Portée pour 99 : ce mécanisme ne modifie que des arêtes de droites entièrement lointaines. Dans un candidat il y a
32 − t droites lointaines (t = nombre de triangles transversaux de G(T), 0 ≤ t ≤ 12), soit au plus 96 des 240
arêtes lointaines ; les autres sont dans les étoiles des sommets proches. Une bascule à 99 devrait changer des
couplages d'étoiles, ce que le 243 ne fait jamais. Le 243 ne fournit donc pas de modèle.

**Remarque 9 (re-réglures à 99, hors boule fixée).** Soit une famille de grilles d'un candidat, chacune réunion de
trois droites d'un ensemble 𝒮 de droites disjointes, re-réglées comme ci-dessus, telle que tout sommet x touché soit
dans g grilles de la famille, toutes par sa droite de 𝒮 et ne partageant deux à deux que cette droite, et n'ait pas
d'autre voisin touché. Alors g ≥ 3.
*Preuve.* Soit r un voisin retiré de x. Un voisin non touché z de r n'est pas voisin de x, et l'équation en (x, z)
demande que z soit voisin d'un des 2(g − 1) nouveaux voisins d de x pris dans les autres grilles. Les grilles étant
des codes parfaits (G1), r et d ne sont pas adjacents et ont 2 voisins communs. Donc 12 − 2g ≤ 4(g − 1). ∎
Un tel mouvement demande donc que chaque sommet touché soit dans au moins 3 grilles partageant une droite : il
n'existe pas dans un candidat pauvre en grilles, en particulier pas sous P = 0.

## 5. Pilote local sensible au rang (`local_frames.py`) — négatif

Question : les conditions à deux points sensibles au rang sur les deux repères serrés des 84 seconds voisins d'un
sommet (rangs 30 et 40), c'est-à-dire Gegenbauer en dimensions 30 et 40, leurs produits de Schur, tracés contre les
six idempotents de B₇, coupent-elles le triangle 0 ≤ s ≤ W ≤ 84 des statistiques locales de torsion (note 90) ?
Une coupe en W = 84 aurait signifié « tout sommet est sur un prisme ».

Réponse : **non.** Degrés 0 à 12 pour chaque facteur, 1 008 inégalités linéaires : les 3 655 points entiers du
triangle sont tous admissibles. Constantes retrouvées : 56·Π₃₀ = 20I − 2R_a − R_sh + R_cl + 2R_dj − 8H.

## 6. Obstacle précis

Un mouvement universel doit partir d'une configuration présente dans tout candidat. Les seules connues sont le
sommet, la droite, le quadrangle et le motif de Makhnev. Autour d'un sommet la base a toute la symétrie B₇ mais ne
contient aucune information (toutes les complétions sont des ré-étiquetages). Autour d'une droite, l'existence
d'une seconde complétion équivaut à un second projecteur de rang 8 admissible dans Z, et rien ne la force ; le seul
exemple connu (243) est une re-réglure le long des droites parallèles à T, classe fournie par la translation
d'ordre 3 qui fixe T, et un tel automorphisme est interdit à 99. Par ailleurs une bascule à
boule fixée est involutive : elle ne peut pas faire décroître strictement un invariant dans les deux sens, donc
l'argument extrémal de la note 220 demanderait en plus une raison pour que la bascule existe au maximum.

Je ne vois pas de mécanisme qui lève cet obstacle. La route « transformations » ne donne pas de décision de C1 en
l'état.

## 7. Fichiers

`flip243.py`, `flip243b.py`, `flip243c.py` (structure de la bascule du 243, numpy, quelques secondes) ;
`local_frames.py` (pilote du §5) ; `pilotes.out` (sorties).

## 8. Suite du 9 octobre après 10:48 UTC : symétrie forcée ou données inexistantes au rang 37

Question posée par l'utilisateur : au rang 37, à droite générique (G(T) connexe, 7 ∤ τ), les données (boule, 60
ombres) sont-elles obligées d'avoir une symétrie, ou de ne pas exister ? Chacune des deux réponses « oui » exclurait
les droites génériques au rang 37 (une symétrie se prolonge au graphe par le théorème 7 et le complément de Codex,
ce que les exclusions du programme interdisent). **Aucune des deux n'est démontrée ici.** Ce qui suit est acquis.

**Lemme 10 (scindage entier).** Soit T une droite, G(T) connexe, Z_Λ = ker_Z(N_F) ⊂ Z^60 (rang 26), N_far et K_far
ses sous-réseaux propres pour −4 et 3. Alors 7 Z_Λ ⊂ N_far ⊕ K_far ⊂ Z_Λ, et le quotient Z_Λ/(N_far ⊕ K_far) se
plonge dans N_far^#/N_far. Au rang 37 avec 7 ∤ τ, **Z_Λ = N_far ⊥ K_far** : tout vecteur entier sur les lointains,
de somme nulle sur chaque étoile, est somme d'un vecteur propre entier de valeur −4 et d'un de valeur 3.
*Preuve.* A_F préserve Z_Λ et y vérifie (A_F − 3)(A_F + 4) = 0, d'où 7z = (A_F + 4)z + (3 − A_F)z. Au rang 37,
Π est 7-entier (complément de Schur nul), donc N_far^# = Π Z^60 a un indice premier à 7 sur N_far. ∎

**Corollaire 11.** Au rang 37 générique, tout z ∈ Z_Λ de norme < 14 est un vecteur propre de valeur 3 (car
min N_far ≥ 14, note 165). Un vecteur propre de valeur 3 a un support d'au moins 8 sommets (borne de répartition
des poids : 1 + 14·3/14 + 84/21). Donc Z_Λ n'a aucun vecteur de norme 6 : il n'existe pas trois ombres dont la
réunion avec multiplicités égale celle de trois autres.

**Lemme 12 (discriminants, tout rang, G(T) connexe).** det N_far ≡ τ(G(T)) et det K_far ≡ 35·det(G(T) + 4I)
modulo les carrés rationnels. *Preuve.* det N_far ≡ det(N_0 ∩ E(Q^boule)) ≡ det 63(9L + J) ≡ τ. Le réseau des
étoiles a pour Gram K = 7L − L² + 2J − D, de pseudo-déterminant (15/7)·τ·det(G + 4I), et pour relations les
différences de couches (déterminant 432) ; son saturé a le déterminant de Z_Λ, égal à 7^{−2g} det N_far det K_far. ∎
(Le premier point recoupe la note 217.)

**Cadre du sommet.** Les 99 sommets sont les mots de poids ≤ 2 de F_3^7 (0, les 14 points ±e_i, les 84 racines de
D_7). Au rang 37, les 84 résidus vivent dans un espace W de dimension 22 sur F_7 ; chaque étoile X_u (12 racines
contenant u) a pour Gram 5J − 2(τ_u + P_m), où τ_u ∪ P_m est une réunion de cycles pairs. Son radical a dimension
2·#{cycles de longueur multiple de 4} ; il est nul seulement pour le type (3,3) parmi les quatre types sans prisme
(6), (4,2), (3,3), (2,2,2), qui donnent 2, 4, 0, 6. La matrice des résidus vérifie 𝔐² ≡ 0 : son espace colonne
est un code auto-orthogonal [84, 22] contenu dans ker(H − 3) ∩ ker C.

**Coût d'une exclusion exhaustive (estimation, non mesurée).** Toute base engendrant l'espace de dimension 36
contient l'équivalent d'une boule de droite : environ 1,9·10^11 types au total, 1,4·10^10 sans prisme et connexes.
Le test d'une étoile vaut de l'ordre de 10^6 nœuds (pic à la profondeur 4 : 620^4·7^{−6}), soit 10 à 100 ms au mieux
par boule. Total : de l'ordre de 5 à 50 années-cœur pour la seule classe sans prisme connexe, sans compter les
droites à torsion ni les prismes. Aucune réduction du nombre de boules n'est connue.

## 9. Séries thêta pondérées par un quartique harmonique (9 octobre, 12:30–12:45 UTC)

Idée : étendre l'outil des notes 167–168 (séries thêta de L1 et M, poids 22, niveau 7) en pondérant chaque vecteur
par un polynôme harmonique de degré 4 invariant par renommage. Je n'ai pas trouvé cet outil dans le dépôt (les notes
96 et 110 utilisent le degré 2 de Venkov après complétion unimodulaire).

**Énoncé.** Sur l'espace propre −4 (dimension 44), les polynômes

    P_V(y) = Σ_v y_v⁴ − (2/69)|y|⁴,        P_T(y) = Σ_T y(T)⁴ − (18/161)|y|⁴

sont harmoniques (Δ Σ_v y_v⁴ = (16/3)|y|², Δ Σ_T y(T)⁴ = (144/7)|y|², et Φ − κ|y|⁴/184 est harmonique dès que
ΔΦ = κ|y|²). Donc G_L = Σ_{y∈L1} P(y) q^{|y|²/2} et G_M = Σ_{x∈M} P(x) q^{|x|²/2} sont des formes paraboliques de
poids 26 sur Γ₀(7) (dimension 15), et

    G_L |₂₆ W₇ = −7^{(23−r)/2} G_M      (même facteur que pour θ ; vérifié exactement sur H7 ⊕ H7, `toy_harm.py`).

**Coefficients exacts côté L1.** Tous les vecteurs de norme ≤ 20 sont binaires et coupent chaque droite au plus une
fois (notes 165, 171, 176), avec Σ_T y(T)² = 3|y|². Donc pour la norme 2n : coefficient nul si n ≤ 6, et
(2n − 8n²/69)·a_n pour P_V, (6n − 72n²/161)·a_n pour P_T, si 7 ≤ n ≤ 10.

**Coefficients exacts côté M.** Racines : 82/483 et 66/161 par racine. Vecteurs de droites (462) : −124/1127 chacun
pour P_V ; somme (149688 + 48P − 462·2016/23)/49 pour P_T, P le nombre de prismes. Différences de deux sommets non
adjacents (8316) : 3102/1127 et −534/1127 ; adjacents (1386) : 30712/3381 et −888/1127.

**Premier test (`harm4.py`, bornes de Cauchy–Schwarz pour tous les autres vecteurs ; solveur flottant puis exact).** La base de degré 0
est reproduite : rang 35 infaisable avec les contraintes actives de la note 180, rang 37 faisable. Avec les deux
quartiques, 11 égalités exactes par série et 4 paramètres libres restants : **faisable aux rangs 37, 39, 41** à la
troncature 14–16. Aux troncatures plus hautes et au rang 43 le solveur flottant n'est pas fiable (écarts d'échelle) ;
aucune conclusion n'en est tirée. Tel quel, l'outil n'exclut rien : les bornes sur les vecteurs non catalogués de M
(normes 6, 8, 10) sont trop lâches. Il faudrait les sommes quartiques exactes des familles comptées dans b₃, b₄, b₅
(notes 172–204) et un solveur exact.

Fichiers : `mf7.py` (espaces M_k(Γ₀(7)) par monômes en h², E₄, E₆ et involution de Fricke, contrôlée sur la base
F_j de la note 167), `toy_harm.py`, `harm4.py`.

**Reprise en arithmétique exacte (jusqu'à 12:59 UTC, `exact_lp.py`).** La résolution finale est remplacée par un
simplexe en fractions sur le système de Farkas ; il rend un point exact vérifié sur chaque inégalité, ou un
certificat exact vérifié. Contrôle : rang 35 infaisable, certificat sur a₇ ≤ 990, 7a₇+8a₈ ≤ 55440, b₁ ≤ 44, b₃, b₄
et a₉, a₁₀, a₁₁ ≥ 0. Avec les deux quartiques, troncatures 40 et 84 : **faisable aux rangs 37, 39, 41 et 43**
(points exacts). Les réponses « infaisable, marge −1 » du solveur flottant aux troncatures ≥ 18 étaient des
artefacts d'arrondi (coefficients jusqu'à 7²¹ dans une même ligne).

**Réponse de LAB à la question posée (message du 9 octobre, 12:59 UTC ; commit `e5734c0` de sa branche).** Non : avec son simplexe
exact et les bornes uniformes de Codex sur les vecteurs catalogués de normes 6, 8, 10 (45 964, 3 371 634,
34 087 368), LAB a placé chaque somme quartique inconnue à l'une ou l'autre extrémité de son intervalle : les 64
coins sont faisables au rang 37 (troncatures 14 et 20), et l'ensemble des valeurs faisables est convexe. Les sommes
exactes du catalogue ne peuvent donc pas rendre le rang 37 infaisable dans ce programme linéaire. Raison : quatre
paramètres libres par série, et les vecteurs non catalogués, nombreux au rang 37, portent un jeu proportionnel à
leur nombre. Fichiers de LAB : conway99-c1, branche lab/theta-lp-2026-10-08, `code/lab_theta_lp_2026-10-08/lap_harm/`.
**Cette piste est fermée sous cette forme.**

## 10. Indice du réseau des droites dans M ; nombres forcés rang par rang (9 octobre, 13:28–14:15 UTC)

### 10.1 Proposition 13 (saturation globale du réseau triangulaire)

Notations : N matrice d'incidence points × droites (99 × 231), NNᵀ = 7I + A ; Λ_L = √7·E(N Z²³¹) ⊂ M le réseau
engendré par les 231 vecteurs de droites w_T ; U = {c : V → F₃ de somme nulle sur chaque droite} (chaque droite
monochrome ou arc-en-ciel), e₃ = dim U = 99 − rang_{F₃}(N) ≥ 1 (les constantes).

**Proposition 13.** [M : Λ_L] = 3^(e₃−1), M/Λ_L ≅ F₃^(e₃−1), dét Λ_L = 7^(45−r)·9^(e₃−1).
En particulier Λ_L est saturé dans M en 2, 5 et 7 ; si U ne contient que les constantes, M est engendré par ses
462 vecteurs de droites.

*Preuve.* (i) Dans V = V₋₄, le dual de E(N Z²³¹) est L₂ = {y ∈ V : y(T) ∈ Z pour toute droite T}, puisque
y·E1_T = y(T) ; le dual de E(Z⁹⁹) est L, celui de E(Z⁹⁹₀) (somme ≡ 0 mod 3) est L₁, et L₁ ⊂ L₂.
(ii) Si y ∈ L₂, alors z = Nᵀy ∈ Z²³¹ et Nz = NNᵀy = (7I + A)y = 3y, donc y ∈ ⅓L.
(iii) x ↦ x mod 3 identifie donc L₂/L à {c ∈ L/3L : Nᵀc ≡ 0 mod 3}.
(iv) ker(Nᵀ mod 3) ⊂ ker((7I + A) mod 3) = ker((A + I) mod 3), et ce noyau est exactement L/3L : modulo 3 on a
A(A + I) ≡ 2J ; le sous-espace caractéristique W de la valeur propre −1 est de dimension 45 (multiplicités 1 + 44),
orthogonal à celui de 0, donc non dégénéré ; il contient 1, qui est isotrope (99 ≡ 0), donc il existe x ∈ W avec
1·x ≠ 0, et (A + I)x = 2A⁻¹Jx = (1·x)·1 ≠ 0 ; sur W, A + I est de rang exactement 1, son noyau a dimension 44 et
contient L/3L, de dimension 44. Donc L₂/L ≅ U, [L₂ : L₁] = 3^(e₃−1), et par dualité [M : Λ_L] = [L₂ : L₁]. ∎

**Corollaires.**
(a) Un vecteur de M dont un multiple premier à 3 est dans Λ_L est dans Λ_L. Exemple : pour un support H à 12
sommets, 4-régulier, à 8 triangles (dossier « Convergences »), 2h_H = Σ_{T⊂H} w_T, donc **h_H est une combinaison
entière de vecteurs de droites**. Forme équivalente : aucun vecteur propre entier x ∈ L∖2L (resp. L∖5L) n'a toutes
ses sommes de droites paires (resp. multiples de 5).
(b) Côté valeur propre 3 (Nᵀ y multiplie les normes par 10) : [E₃Z⁹⁹ : E₃N Z²³¹] = 2^(e₂)·5^(e₅), e_p = 99 − rang_{F_p}(N).
Avec dét(NNᵀ) = 3⁴⁵·7·2⁵⁴·5⁵⁴ : e₃ ≤ 22, e₂ ≤ 27, e₅ ≤ 27, et rang_{F₇}(N) = 99.
(c) Une fonction c ∈ U non constante a m ≥ 33 droites monochromes (9m = ζ*(7I + A)ζ ≥ 3·99 pour ζ = ω^c), avec
égalité si et seulement si ζ est vecteur propre pour −4 ; alors les trois classes de couleur ont 33 sommets, chacune
est réunion de 11 droites disjointes, toutes les autres droites sont arc-en-ciel, et ⅓ − 1_{V_i} sont trois vecteurs
fractionnaires de norme 22 de L₁.

Ce que cela vaut : e₃ est un invariant entre 1 et 22 que les paramètres ne fixent pas (notes 70, 96 et 99 du dépôt
c1 laissaient ouverts les premiers 2, 3, 5, 7 pour l'indice ; seul 3 intervient). Aucun rang n'est exclu par là.

### 10.2 Nombres forcés par le programme thêta, en arithmétique exacte (`thetalp.py`, `probe_menu.py`, `probe_patterns.py`)

Programme de degré 0 des notes 167–168 avec les contraintes de la note 180 (a₇ ≤ 990, 7a₇ + 8a₈ ≤ 55440, b₁ ≤ 44,
b₂ ≥ 462 + 41b₁, b₃, b₄, b₅, a₇ₖ ≥ bₖ ; au rang 43 l'égalité a₇ = b₁), simplexe rationnel en mémoire, minimum par
dichotomie ; valeurs identiques aux troncatures 40, 60 et 84. Chaque valeur est une minoration valide.

| rang | vecteurs courts de L₁ forcés | couches pouvant être seules non vides | côté M |
|---|---|---|---|
| 37 | ≥ 380 de norme ≤ 20 | 14 (≥ 380), 16 (≥ 1283), 18 (≥ 4932), 20 (≥ 34523) | b₂ = 462 possible |
| 39 | ≥ 2367 de norme ≤ 24 | 16, 18, 20, 22, 24 (pas 14 seule) | b₂ = 462 possible |
| 41 | ≥ 234 de norme ≤ 24 | 14 (≥ 234), 16, 18, 20, 22, 24 | b₂ = 462 possible, b₄ ≥ 474 941 774 |
| 43 | ≥ 165 de norme ≤ 26 | **18 (≥ 165) ou 26 (≥ 2632) seulement** | b₂ ≥ 913, b₃ ≥ 7 073 772 |

Ces nombres recoupent les notes 177 (identité 2a₈ + 16a₉ + a₁₃ = 2632 + …) et 192 (b₂ ≥ 968 par les cocliques) de
Codex ; l'apport est l'outil (une question = quelques secondes, réponse exacte) et la ligne « supports minimaux ».

## 11. Programme thêta à neuf classes (recollement en 3 séparé) : construit, validé, sans gain (9 octobre, 14:23–15:03 UTC)

**Fait nouveau utilisé.** La partie 3 du recollement du réseau propre est Z/9 (engendrée par 7Ee_v), et chaque classe
a sa propre série thêta. Côté M : O = √7E(Z⁹⁹), classe k = Σψ mod 9, Θ_k = nombre de vecteurs de classe k par norme
(θ_M = Θ₀ + 2Θ₃). Côté L : L₉ = vecteurs propres dont toutes les coordonnées sont ≡ c/9 mod 1, classe c, Ξ_c
(θ_{L₁} = Ξ₀ + 2Ξ₃). Les programmes antérieurs (notes 167–168 ; `theta_pi.py` de LAB, recollement avec A₈) mélangent
ces classes ; LAB avait noté le 8 octobre que l'information de classe était la seule non utilisée.

**Construction.** Avec A₈ (même forme discriminante au signe près), Lam = {(x, a) : classe(x) = classe(a)} est pair, de
rang 52, de niveau 7, et Π = √7·Lam^# = {(y, √7a′) : classe(y) = classe(a′)}. Pour tout harmonique zonal Z_m sur la
partie A₈ (degré m pair, pôle e₁ − e₂ ou e₁ − (1/9)1) :

    g_m = Σ_k w_k Θ_k(τ) ϑ_{k,m}(τ) ∈ M_{26+m}(Γ₀(7)),    ĝ_m = 7^{m/2} Σ_c w_c Ξ_c(τ) ϑ_{c,m}(7τ) = −7^{(19−r)/2} g_m|W₇,

avec w₀ = 1, w_k = 2, et ϑ_{k,m} la série de la classe k de A₈^# pondérée par Z_m. Le cas m = 0 seul est le
programme de LAB ; les degrés 0, 4, 6 (deux pôles), 8 (deux pôles) séparent les cinq classes paires (la matrice 6 × 5
des ϑ est de rang 5 en τ = ρ, i et en un point générique ; le degré 2 est identiquement nul, S₉ étant irréductible).

**Contrôles** (`a8.py`, `z9theta.py`, `z9_test.py`, arithmétique exacte, python-flint) :
classe 0 + 2·classe 3 de A₈^# = E₄ au degré 0, = 0 aux degrés 4, 6, 10 (S₈ = S₁₀ = S₁₄ = 0), = 144Δ au degré 8 ;
sous-cas « classes 1, 2, 4 vides et classe 3 = classe 0 » : exactement 15 paramètres = dim M₂₂(Γ₀(7)) ;
système complet : 71 paramètres (95 moins 24 inconnues de bord de troncature), égal à la dimension donnée par la
formule des formes vectorielles pour la représentation de Weil paire de Z/9 induite à SL₂(Z) ; stable de N = 24 à 48.

**Entrées démontrées** (aucune hypothèse sur le graphe). Côté L : classe 0 : normes 2 à 12 vides ; classe 3 : normes
< 22 ; classe 1 : normes < 178/9 (avec y = 1/9 + m, Σm = −11, Am = −2 − 4m : tout sommet négatif a besoin d'une masse
positive voisine ≥ 2, ce qui exclut Σm² ≤ 19 cas par cas) ; classe 2 : normes < 154/9, l'égalité étant exactement une
coclique de Hoffman de taille 22 ; classe 4 : normes < 220/9, l'égalité étant un ensemble de 44 sommets 4-régulier à
degré extérieur 8. Côté M : 99 sommets en classe 1 (norme 28/9), 693 arêtes en classe 2 (norme 40/9), 231 droites en
classe 3, racines seulement en classe 0, 8316 différences en classe 0 (norme 6), et les bornes connues sur a_n, b_n.
Inégalités croisées Ξ_k[7e] ≥ Θ_k[e]. Il reste 18 paramètres libres (7 dans le programme L₁).

**Résultat** (`z9lp.py`, `z9q.py`, `z9cond.py`, simplexe rationnel exact, N = 32, inégalités jusqu'à l'exposant 23).
Rang 35 : infaisable avec a₇ ≤ 990, faisable sans, comme dans le programme L₁. Rangs 37, 39, 41, 43 : **faisables**.
Nombres forcés identiques à ceux du programme L₁ aux rangs calculés (380 au rang 37, 2367 au rang 39 ; b₂ = 462 et
aucune norme 22 fractionnaire forcée). En ajoutant ensemble huit absences (pas de coclique de taille 22, pas
d'ensemble régulier de 44 sommets, pas de vecteur de classe 1 de norme 178/9, pas de norme 22 fractionnaire, pas de
sommet fantôme, pas de vecteur de M de classe 2 de norme 22/9 ni de classe 4 de norme 34/9, pas de racine) : les
quatre rangs restent faisables. La séparation des classes en 3 n'apporte donc rien au degré 0 ; les 13 paramètres de
la partie nouvelle absorbent toutes les contraintes. Cette piste est fermée au degré 0.

**Variante impaire, non exécutée.** P₃(x) = Σ_v x_v³ est harmonique sur V₋₄ (son laplacien est 6·(28/63)·Σ_v x_v = 0)
et impair, donc ses séries thêta sur les classes ±1, ±2, ±3, ±4 ne sont pas nulles : forme vectorielle parabolique de
poids 25, quatre composantes, sans positivité mais avec des valeurs exactes par profil (norme 28 fractionnaire :
−4/3 pour le profil A, −22/3 pour B, +14/3 pour C ; coclique de taille 22 : −770/81). Décompte : environ 60
dimensions, 43 zéros démontrés, donc environ 17 paramètres libres ; aucune contradiction à en attendre sans majorer
les vecteurs fantômes.

**Variante impaire exécutée (`z9cubic.py`, pôles e₁ − e₂ et e₁ − (1/9)1, degrés zonaux 3, 5, 7, 9).** L'espace des
formes vectorielles impaires de poids 25 a 64 dimensions (88 moins 24 inconnues de bord) ; avec les 45 zéros
démontrés il reste **19 paramètres libres**, qui sont exactement les moments cubiques des couches de O de classes
1 à 4 d'exposant 11/9 à 56/9 (normes 22/9 à 112/9). Tous les moments du côté L (norme 22 fractionnaire, cocliques
de taille 22, ensembles réguliers de 44 sommets) en sont des combinaisons linéaires ; il n'y a aucune relation
entre les premiers moments. Sans classification complète des vecteurs de O de norme ≤ 12 dans ces classes, cette
variante ne donne rien. Fermée.

**Contrôle machine de la proposition 13 sur le graphe de Berlekamp–van Lint–Seidel (`check_prop13.py`, entiers
exacts).** srg(243,22,1,2), valeurs propres 22, 4, −5, NNᵀ = 11I + A, constante 6 sur l'espace propre de −5 :
L = Z²⁴³ ∩ ker(A + 5I) est de rang 110 et de déterminant 3¹⁶⁹ ; les facteurs invariants de NᵀB (B base de L) sont 1
et 3 ; [L₂ : L] = 3¹² = nombre de x ∈ L/6L dont toutes les sommes de droites sont nulles modulo 6 ; ker(Nᵀ mod 3)
est de dimension 12 (valeur de la note 99 du dépôt c1) et entièrement dans L/3L ; ker(Nᵀ mod 2) = 0. Les étapes
(i) à (iii) de la preuve et l'analogue de (iv) sont donc vérifiés sur un exemple qui existe.

## 12. Rang 43 : les 49 classes de L₁/√7M une par une, relations exactes (9 octobre, 15:11–15:34 UTC)

**Fait nouveau utilisé.** Au rang 43, M est pair, de rang 44, de déterminant 49, à plan discriminant anisotrope ;
N₄ = O_K ⊕ O_K (O_K = entiers de Q(√−7), Gram [[2,1],[1,4]]) a la forme discriminante opposée, donc M ⊕ N₄ se recolle
en un réseau unimodulaire pair de rang 48, et pour tout polynôme harmonique h sur la partie N₄ (degré m)

    Σ_d Θ_d(τ) ϑ_{d,h}(τ) ∈ M_{24+m}(SL₂(Z)),

où d parcourt les 49 classes et Θ_d est la série de la classe de L₁/√7M recollée à d (exposant = norme dans L₁ / 14).
Les moyennes radiales redonnent le programme L₁ ; le reste est l'information classe par classe, que ni la note 177
de Codex ni le programme de LAB n'utilisent (ils raisonnent par couche, puis par pigeonnier).

**Calcul** (`w49.py`, exact, harmoniques zonaux de degré 0 à 12 avec dix pôles, 61 fonctionnelles, troncature 7).
L'espace des solutions a 44 dimensions, égal à la dimension donnée par la formule des formes vectorielles pour la
partie paire de la représentation de Weil du plan ; avec les 24 zéros (aucun vecteur de norme < 14 hors de √7M) et
Θ₀[0] = 1 il reste **19 paramètres libres** : b₁, les quatre classes de chacune des normes 16, 18, 20, 22, et deux
des quatre classes de norme 24. **Les quatre classes de norme 26 et deux classes de norme 24 sont déterminées.**

Notation : la classe est repérée par (c₁, c₂) ∈ F₇² modulo signe, avec norme ≡ −4(c₁² + c₂²) mod 14 ; n[c₁,c₂](ν) est
le nombre de vecteurs de L₁ de norme ν dans cette classe (autant dans la classe opposée). L'étiquetage réel n'est
défini qu'à une isométrie du plan près ; l'ensemble des relations est stable par ces isométries.

    n[0,1](24) − n[1,0](24) = (n[1,2] + n[1,5] − n[2,1] − n[2,6])(22) + (n[3,0] − n[0,3])(20)
                              + (n[3,2] + n[3,5] − n[2,3] − n[2,4])(18) + (n[1,3] + n[1,4] − n[3,1] − n[3,6])(16)
    n[2,2](24) − n[2,5](24) = (n[1,5] + n[2,6] − n[1,2] − n[2,1])(22) + (n[1,6] − n[1,1])(20)
                              + (n[2,4] + n[3,5] − n[2,3] − n[3,2])(18) + (n[1,4] + n[3,6] − n[1,3] − n[3,1])(16)
    n[0,2](26) = 329 + 7b₁ + 3n[1,0](24) − 2n[2,5](24) + (2n[1,2] + n[2,1] − n[2,6])(22)
                 + (−8n[0,3] + 7n[1,1] + 5n[1,6] + 3n[3,0])(20) + (−7n[2,3] − 9n[2,4] + n[3,2] − n[3,5])(18)
                 + (−6n[1,3] − 8n[1,4] + 7n[3,1] + 5n[3,6])(16)
    n[2,0](26) = 329 + 7b₁ + 3n[1,0](24) − 2n[2,5](24) + (4n[1,2] + 2n[1,5] − n[2,1] − 3n[2,6])(22)
                 + (7n[1,1] + 5n[1,6] − 5n[3,0])(20) + (−2n[2,3] − 4n[2,4] − 4n[3,2] − 6n[3,5])(18)
                 + (10n[1,3] + 8n[1,4] − 9n[3,1] − 11n[3,6])(16)
    n[3,3](26) = 329 + 7b₁ − 2n[1,0](24) + 3n[2,5](24) + (−n[1,2] + n[2,1] + 2n[2,6])(22)
                 + (7n[0,3] − 8n[1,1] + 3n[1,6] + 5n[3,0])(20) + (−7n[2,3] + n[2,4] − 9n[3,2] − n[3,5])(18)
                 + (5n[1,3] − 8n[1,4] + 7n[3,1] − 6n[3,6])(16)
    n[3,4](26) = 329 + 7b₁ − 2n[1,0](24) + 3n[2,5](24) + (−3n[1,2] + 2n[1,5] − n[2,1] + 4n[2,6])(22)
                 + (7n[0,3] − 5n[1,6] + 5n[3,0])(20) + (−2n[2,3] − 4n[2,4] − 4n[3,2] − 6n[3,5])(18)
                 + (−11n[1,3] + 8n[1,4] − 9n[3,1] + 10n[3,6])(16)

Contrôle : la somme des quatre dernières, doublée, est l'identité (1) de la note 177
(a₁₃ = 2632 + 56a₇ + 7a₁₀ + 2a₁₁ + a₁₂ − 2a₈ − 16a₉), et b₂ = 1000 − 8b₁ + 25a₈ + 11a₉ + 8a₁₀ + 3a₁₁ + a₁₂.

**Conséquences.**
(a) Si une seule des normes 16, 18, 20, 22, 24 est présente, ses quatre classes se groupent en deux paires de
classes de même effectif : (u, v, v, u).
(b) Normes 18 et 26 seules (avec x₁, x₂ les deux effectifs de classe de la norme 18) : chaque classe de norme 26
contient exactement 329 + 7b₁ − 8(x₁ + x₂) vecteurs ; donc x₁ + x₂ ≤ (329 + 7b₁)/8, et sans racine la norme 26 est
toujours présente (329 est impair).
(c) Scénario S₀ (aucune racine, aucun vecteur de norme 16 à 24) : toute la série thêta est déterminée, b₂ = 1000,
b₃ = 10 648 712, a₁₃ = 2632, et les vecteurs de chaque norme sont également répartis entre les 8 classes de leur
cercle : 329 par classe en norme 26, 9338 en norme 30, 35 287 en norme 32, etc. Test d'intégralité (`s0_rank43.py`) :
a_n est un entier positif divisible par 8 pour tout n ≤ 84 non multiple de 7. S₀ n'est donc pas exclu par
l'arithmétique des classes ; il faudrait la géométrie des 538 vecteurs de norme 4 non triangulaires de M et des
329 vecteurs de norme 26 par classe.
(d) Les quatre inégalités n[·](26) ≥ 0 sont des bornes par classe que les sommes radiales ne donnent pas.

**Borne supérieure tentée, sans effet.** Dans le programme à neuf classes (§11), le maximum du nombre de cocliques
de taille 22 au rang 37 est 93 696 (`z9max.py`) : aucune majoration utile des vecteurs de Fano par cette voie
(un vecteur de Fano est un couple ordonné de cocliques de taille 22 se coupant en 15 points, note 192).

**Sommes vectorielles par classe au rang 43 (`w49odd.py`, exact).** Pour une forme linéaire ℓ sur l'espace propre
(par exemple une coordonnée y_v), F_d = Σ_{y ∈ classe d} ℓ(y) q^{|y|²/14} est impaire en d et forme une forme
vectorielle de poids 23 ; accouplée aux harmoniques zonaux impairs de N₄ (degrés 1 à 11, dix pôles) elle donne des
formes de niveau 1. L'espace a 44 dimensions ; avec les 24 zéros sous la norme 14 il reste exactement 20 paramètres,
qui sont les sommes des 20 classes de normes 16 à 24. Donc : **au rang 43, la somme vectorielle des vecteurs de
chaque classe de norme 26, et de toute couche plus haute de toute classe, est une combinaison linéaire fixe des
sommes vectorielles des classes de normes 16 à 24 ; s'il n'y a aucun vecteur de norme 16 à 24, la somme des
vecteurs de chaque norme dans chaque classe non nulle est le vecteur nul.**

**Seconds moments par classe au rang 43 (`w49evenk.py`, `s0_tensor.py`, exact ; fin 15:47 UTC).** Pour un tenseur
symétrique sans trace S sur l'espace propre, P(y) = yᵀSy, notons [d, ν] = Σ P(y) sur les vecteurs de norme ν de la
classe d (même valeur pour −d), T_ν = somme sur toute la couche de norme ν de L₁, A₄ et A₆ les sommes de P(√7x) sur
les couches de norme 4 et 6 de M, R la même somme sur les racines. Espace de poids 24 : avec les zéros il reste 24
tenseurs libres (R, les 20 classes de normes 16 à 24, trois des quatre classes de norme 26). Relations :

    [(0,2),26] + [(2,0),26] − [(3,3),26] − [(3,4),26] = −[(0,1),24] − [(1,0),24] + [(2,2),24] + [(2,5),24]
                                                        + [(0,3),20] + [(3,0),20] − [(1,1),20] − [(1,6),20]
    A₄ = −½T₂₆ − (3/2)T₂₄ − 2T₂₂ − (7/2)T₂₀ − 3T₁₈ − 6T₁₆ − 52R            (forme radiale)
    A₆ = 68([(3,3),26] + [(3,4),26]) − 2([(0,1),24] + [(1,0),24]) + 66([(2,2),24] + [(2,5),24]) − 396·(les quatre de norme 22)
         − 1870([(0,3),20] + [(3,0),20]) − 1938([(1,1),20] + [(1,6),20]) − 7062·(norme 18) − 20592·(norme 16) − 26852R

Dans la branche sans norme 16 à 24 : [(0,2)] + [(2,0)] = [(3,3)] + [(3,4)] en norme 26, A₄ = −½T₂₆ − 52R, et
A₆ = 17T₂₆ − 26852R. Sans racine (S₀) il reste **un seul tenseur libre** T (celui de la couche de norme 4 de M,
c'est-à-dire des 538 vecteurs non triangulaires, les droites formant un 2-design) : couche de norme 26 de L₁ :
−14T ; couches de M de normes 4, 6, 8, 10, 12 : T, −34T, 464T, −2412T, −15108T. En tenseurs complets, pour chaque
couple de classes orthogonales C, C′ de norme 26 :  Σ_{z ∈ C ∪ C′} zzᵀ = 560E − (7/2)F_ex, où F_ex = Σ xxᵀ sur les 538
vecteurs non triangulaires (traces : 17108 des deux côtés). Les positivités de toutes les couches jusqu'à la norme
160 laissent aux valeurs propres de T l'intervalle [−48,9 ; 111,1] : **l'isotropie n'est pas forcée**, et les
congruences modulo 49 des deux membres concordent. Le degré 2 ne ferme donc pas cette branche.

## 13. Rang 43, scénario S₀ dans le programme à neuf classes : sept paramètres entiers, effectifs forcés (9 octobre, fin 16:10 UTC)

S₀ = rang 43, aucune racine, aucun vecteur de L₁ de norme 16 à 24 (Codex a montré le même jour, à partir du
coefficient −52R du §12, que l'absence des normes 16 à 24 force l'absence de racines : la branche se réduit à S₀).

**Égalité de classe complète au rang 43.** L₉/√7·O est le plan anisotrope, donc pour chacune des cinq classes k (pas
seulement 0 et 3) un vecteur de L₉ de classe k dont l'exposant est 7e, avec e exposant permis de la classe k de O,
est dans √7·O : Ξ_k[7e] = Θ_k[e]. (`r43full.py` ; au rang 43 général : 15 paramètres libres, faisable, b₂ ≥ 913.)

**S₀ dans le programme à neuf classes (`s0_sheet.py`, `r43full.py branch 0 cert`, simplexe rationnel exact).** Il
reste 7 paramètres : les effectifs des classes de O
Θ₂[11/9], Θ₁[14/9], Θ₄[17/9], Θ₃[2], Θ₂[20/9], Θ₁[23/9], Θ₄[26/9]. Intervalles exacts, avec les entrées démontrées et
« 22 vecteurs de profil C de chaque signe par coclique de taille 22 » :

| quantité | intervalle |
|---|---|
| vecteurs de norme 4 de M | 1000 |
| dont de type entier | 346 à 538 |
| dont fractionnaires d'un signe (231 droites + profils A′, B, C) | 231 à 327 |
| vecteurs de norme 26 de L₁ | 2632 |
| dont fractionnaires d'un signe (paire Z, ensemble S de 35 sommets) | 160 à 740 |
| cocliques de taille 22 | 0 à 3 |
| ensembles réguliers de 44 sommets | 0 à 145 |
| vecteurs de L₉ de classe 1 et de norme 178/9 | 0 à 36 |
| vecteurs de O de classe 1 et de norme 28/9 (99 sommets + fantômes) | 99 à 121 |
| vecteurs de O de classe 2 et de norme 22/9 | 0 à 3 |
| **vecteurs de O de classe 2 et de norme 40/9 (693 arêtes + autres)** | **5672 à 6396** |
| vecteurs de O de classe 4 et de norme 34/9 | 0 à 290 |

Certificat de la minoration 5672 : positivité des effectifs de L₉ en classe 4 (normes 220/9 et 238/9), classe 2
(norme 190/9), classe 1 (norme 178/9), avec « 231 droites », « 99 sommets » et le lien des profils C.

**Intégralité (`s0_int.py`).** Les effectifs sont affines en les 7 paramètres avec dénominateurs 49, 98, 147 ; les
congruences sont compatibles (réseau d'indice 100 842 = 2·3·7⁵) et il existe un point entier dans le polytope, par
exemple (Θ₄[26/9], Θ₁[23/9], Θ₂[20/9], Θ₃[2], Θ₄[17/9], Θ₁[14/9], Θ₂[11/9]) = (1 618 734, 120 904, 5676, 231, 0, 99, 0),
vérifié exactement (tous les effectifs entiers positifs jusqu'à l'exposant 23). S₀ n'est donc pas exclu par
l'arithmétique des neuf classes.

**Ce que S₀ force géométriquement.** Au moins 4979 vecteurs de O de classe 2 et de norme 40/9 qui ne sont pas des
arêtes. Côté L₉ : y = 2/9 + m, m entier, Σm = −22, Σm² = 36, Am = −4 − 4m. Réduction des profils dans S₀ :
(i) m_v ∈ {−2, …, 2} (minima des classes ±1 et ±3 appliqués à y ∓ 7Ee_v) ; donc 3n₂ + n₁ + n₋₂ = 7 ;
(ii) deux coordonnées 2 : si elles sont adjacentes, y est le vecteur d'arête ; sinon y − 7E(e_a + e_b) est entier de
norme 14, exclu dans S₀ ;
(iii) un sommet de valeur −2 a une masse positive voisine ≥ 4, et deux sommets ont au plus deux voisins communs,
ce qui exclut (n₂, n₁, n₋₂) = (1, k, 4−k) pour k ≤ 2 et (0, k, 7−k) pour k ≤ 5.
Il reste quatre profils : (2 ; 1³ ; −2 ; (−1)²⁵), (2 ; 1⁴ ; (−1)²⁸), (1⁶ ; −2 ; (−1)²⁶), (1⁷ ; (−1)²⁹).
S₀ exige au moins 4979 configurations de ces quatre types ; je n'ai pas de majoration de leur nombre.

**Origine des vecteurs fantômes de classe 2 dans S₀ (à la main, 16:12 UTC).** Soit x ∈ O de classe 2, de norme 40/9,
qui n'est pas une arête, et y = √7x.
(a) Profils avec une coordonnée 2 en a : x − u_a est de classe 1 et de norme 28/9, de produit −8/9 avec u_a ; si
c'était un sommet u_w, x serait l'arête {a, w}. C'est donc un **sommet fantôme**. Il y a au plus 22 fantômes dans S₀,
chacun a au plus 17 sommets à produit −8/9 (profils de norme 196/9 en classe 1), donc au plus 374 vecteurs de ce
type, plus au plus 231 sommes de deux fantômes.
(b) Profils sans coordonnée 2, de support positif P : si P contient une arête {p, p′}, alors x − u_p − u_p′ est un
vecteur de norme 4 de M de type entier. Réciproquement, pour w de norme 4 de type entier, √7w = 1_X − 1_Y binaire, et
une arête {a, b} ⊂ Y, le vecteur w + u_a + u_b est de classe 2 et de norme 40/9, de profil (1⁶ ; −2 ; (−1)²⁶) si le
troisième point de la droite ab est hors de X ∪ Y, et (1⁷ ; (−1)²⁹) s'il est dans X ; on a e(X) = e(Y).
Donc S₀ exige : Σ sur les (au plus 538) vecteurs entiers de norme 4 du nombre d'arêtes dans leur support négatif,
plus le nombre de fantômes à support positif indépendant, au moins 4979 − 605 = 4374.

**Lemme 14 (tout rang ; noté à 16:18 UTC).** Soit y = 1_X − 1_Y un vecteur propre entier binaire de norme 28
(|X| = |Y| = 14). Alors e(X) = e(Y) ≤ 5.
*Preuve.* L'équation propre donne d_Y(a) = d_X(a) + 4 sur X, d_X(b) = d_Y(b) + 4 sur Y, d_X(u) = d_Y(u) =: t_u dehors
(71 sommets). Arêtes X–Y : 56 + 2e(X) = 56 + 2e(Y), donc e(X) = e(Y) = ε. Arêtes de X vers le dehors :
Σ t_u = 140 − 4ε. Voisins communs des paires de X : 182 − ε = Σ_v C(d_X(v), 2) = σ_X + (84 + 8ε + σ_Y) + Σ_u C(t_u, 2),
où σ compte les chemins de longueur 2 dans le support. Donc Σ_u C(t_u, 2) = 98 − 9ε − σ_X − σ_Y, et comme
C(t, 2) ≥ t − 1, on a 98 − 9ε ≥ (140 − 4ε) − 71, soit 5ε ≤ 29. ∎

**Conséquence pour S₀** (`r43full.py branch 0 ghost`). Un vecteur de classe 2, de norme 40/9, dont le support
positif contient une arête, provient d'un vecteur entier de norme 4 de M et d'une arête de son support négatif
(§13) : au plus 5 par vecteur entier binaire. Le minimum de Θ₂[20/9] − 693 − 5·Θ₀[2] sur le polytope de S₀ vaut 2289
(2285 en retranchant encore 28 par sommet fantôme). Donc, **dans S₀ sans sommet fantôme, il faut au moins 2289
vecteurs de classe 2 et de norme 40/9 à support positif indépendant**. Ceux de profil (1⁶ ; −2 ; (−1)²⁶) : si c est
le sommet de valeur −2, x + u_c est un vecteur fractionnaire de norme 4 de M qui vaut 4/3 en c et n'est pas une
droite ; il y en a au plus 96 d'un signe, avec au plus trois sommets à 4/3 chacun, donc au plus 288 tels vecteurs.
Il reste **au moins 2001 vecteurs de profil (1⁷ ; (−1)²⁹) dont les sept sommets positifs sont deux à deux non
adjacents** : P de 7 sommets indépendants, N de 29 sommets portant 28 arêtes, chaque p ∈ P ayant 8 voisins dans N,
chaque x ∈ N autant de voisins dans P que dans N, chaque autre sommet 4 voisins de plus dans N que dans P. Pour
une telle configuration : une droite contenue dans N donne un vecteur de O de classe 4 et de norme 34/9 (au plus
290 dans S₀) ; quatre sommets de N portant 4 arêtes donnent un vecteur fractionnaire de norme 4 ; sept sommets de N
portent au plus 8 arêtes. Avec des sommets fantômes (1 à 22), les vecteurs entiers non binaires ne sont pas
bornés par le lemme 14 ; ce sous-cas reste à traiter.

**Couches forcées dans S₀ (`r43full.py branch 0 layers`, simplexe exact ; noté à 16:34 UTC).** Intervalle exact du
nombre de vecteurs de L₉ par classe et par norme (classes 1, 2, 4 : une seule des deux classes opposées ; classe 3 :
un signe) :

| classe | norme | intervalle | objet |
|---|---|---|---|
| 1 | 178/9 | 0 à 36 | |
| 1 | 196/9 | 99 à 121 | sommets et fantômes |
| 1 | 214/9 | **242 à 398** | profils (1⁷ ; (−1)¹⁸) ou (1⁶ ; −2 ; (−1)¹⁵) |
| 1 | 232/9 | 834 à 1559 | |
| 2 | 154/9 | 0 à 3 | cocliques de taille 22 |
| 2 | 172/9, 190/9 | 0 à 48 chacune | |
| 2 | 208/9 | **10 à 300** | profil unique (1³ ; (−1)²⁵), les trois positifs deux à deux non adjacents |
| 2 | 226/9 | 276 à 952 | |
| 2 | 244/9 | 2605 à 3404 | |
| 2 | 280/9 | 5672 à 6396 | arêtes et vecteurs du §13 |
| 3 | 26 | 160 à 740 | paire Z, ensemble S de 35 sommets |
| 3 | 28 | 231 à 327 | droites et profils A′, B, C |
| 4 | 220/9, 238/9 | 0 à 145, 0 à 290 | |
| 4 | 256/9 | **5271 à 6624** | |

Le plus petit objet forcé est celui de la classe 2 en norme 208/9 : y = 2/9 + 1_P − 1_N avec |P| = 3, |N| = 25
(les minima des classes ±1 et ±3 donnent m ∈ {−1, 0, 1} ; une arête dans P donnerait un vecteur entier de norme 20).
Chaque p ∈ P a 8 voisins dans N ; chaque x ∈ N a autant de voisins dans P que dans N ; N porte 12 arêtes, ne contient
aucune droite, et quatre de ses sommets portent au plus 3 arêtes ; chaque autre sommet a 4 voisins de plus dans N
que dans P. S₀ en exige au moins 10. Je n'ai pas de contradiction pour cette configuration.

Réponse de Codex (relayée par LAB, non vérifiée par moi) : le sous-cas avec sommets fantômes est couvert, S₀ exige
au moins 2289 + 15g configurations (1⁷ ; (−1)²⁹) à support positif indépendant, g étant le nombre de fantômes ;
une borne uniforme 2288 sur ces configurations fermerait tout S₀.

## 14. S₀ : identité exacte du nombre de configurations P3/N25, pistes arithmétiques fermées, forme de Jacobi des droites (9 octobre, noté à 17:43 UTC)

**Rétractation de Codex (relayée par LAB à 17:0x UTC, non vérifiée par moi).** L'annonce « S₀ exclu » est retirée : sa
classification des supports P3/N25 supposait que les triangles des arêtes P–N et N–N restent dans le support. Énoncé
final de sa note 245 : N est une forêt à 12 arêtes, chemins d'au plus 7 sommets, au plus une étoile K₁,₃, et au moins
trois arêtes de N dont le triangle sort du support (δ ≥ 3) ; 5345 supports restent ouverts. **S₀ reste ouvert.**

### 14.1 La minoration « au moins 10 » est une identité exacte (`s0_cert.py`, certificat `s0_cert_N32_b9.json`)

Dans S₀, avec les sept paramètres (Θ₄[26/9], Θ₁[23/9], Θ₂[20/9], Θ₃[18/9], Θ₄[17/9], Θ₁[14/9], Θ₂[11/9]), le certificat
de Farkas exact de « Ξ₂[104/9] ≤ 9 est impossible » n'utilise que six lignes, avec les multiplicateurs 1, 1, 2, 4, 1, 7,
et leur somme est identiquement −1. Autrement dit :

    Ξ₂[104/9] = 10 + Θ₄[17/9] + Ξ₄[110/9] + 2·Ξ₂[95/9] + 4·Ξ₁[89/9] + (Θ₃[18/9] − 231) + 7·(Θ₁[14/9] − 99).

En mots : dans S₀, le nombre de vecteurs y = 2/9 + 1_P − 1_N (|P| = 3, |N| = 25) vaut **exactement** 10, plus le nombre
de vecteurs de O de classe 4 et de norme 34/9, plus le nombre d'ensembles réguliers de 44 sommets, plus deux fois le
nombre de vecteurs de L₉ de classe 2 et de norme 190/9, plus quatre fois celui de classe 1 et de norme 178/9, plus le
nombre de droites fantômes, plus sept fois le nombre de sommets fantômes. Les lignes du certificat (constante et
coefficients sur les sept paramètres) sont dans le fichier JSON ; elles sont identiques aux troncatures 32 et 38.
Entrées utilisées : équations modulaires du programme à neuf classes, zéros démontrés des cinq classes, égalités de
classe du rang 43, zéros de S₀ (normes 14 à 24 en classe 0, 22 et 24 en classe 3), « 231 droites », « 99 sommets ».

**Unicité du profil (preuve écrite).** Soit y ∈ L₉ de classe 2 et de norme 208/9, y = 2/9 + m, m entier. Alors Σm = −22
et Σm² = 28. Pour un sommet v : y − 7Ee_v est de classe 1 et de norme 404/9 − 14(2/9 + m_v), qui doit être ≥ 178/9
(minimum de la classe 1, tout rang) : m_v ≤ 1. y + 7Ee_v est de classe 3 et de norme 404/9 + 14(2/9 + m_v), qui doit
être ≥ 22 (minimum de la classe 3, tout rang) : m_v ≥ −1. Donc m ∈ {−1, 0, 1}, et Σ(m² + m) = 6 donne exactement trois
+1 et vingt-cinq −1 : **le profil (1³ ; (−1)²⁵) vaut à tout rang**. Seule l'indépendance de P utilise S₀ : pour p, p′
dans P, y − 7E(e_p + e_p′) est entier de norme 34 − 14·[p ~ p′], et la norme 20 est exclue dans S₀.

**Validation de bout en bout du programme à neuf classes (`z9_validate.py`).** Sur un réseau qui existe,
M₀ = K₈ ⊕ B¹⁸ (K₈ = diag(3,1,…,1)E₈, pair, déterminant 9, forme discriminante opposée à celle de A₈ ; B = [[2,1],[1,4]]),
de rang 44 et de « rang formel » 27, les 124 valeurs de classe calculées directement (deux côtés, cinq classes)
satisfont toutes les équations modulaires de `Model(27, 12)` : système compatible. Les équations, les exposants, le
facteur 7^((19−r)/2) et le signe sont donc corrects.

### 14.2 Rang 43 général : aucune couche n'est forcée seule (`r43gen_layers.py`)

Sans hypothèse de branche (15 paramètres), le minimum exact de chacune des couches Ξ₂[104/9], Ξ₂[113/9], Ξ₂[122/9],
Ξ₁[107/9], Ξ₁[116/9], Ξ₄[128/9], Ξ₃[117/9], Ξ₂[86/9], Ξ₂[95/9], Ξ₁[89/9], Ξ₄[110/9], Ξ₃[99/9], Ξ₃[108/9] est 0. L'objet
garanti (P3/N25) n'existe donc que dans S₀ ; au rang 43 entier, ce programme ne garantit aucun type unique.

### 14.3 Pistes arithmétiques fermées dans S₀ (calculs exacts)

- **Cubique des sommets P₃ = Σ y_v³** (`s0_cubic.py`, `s0_cubic2.py`) : 14 sommes libres dans S₀ ; sur une couche à
  coordonnées dans c/9 + {−1, 0, 1} la somme cubique est un multiple connu de l'effectif (P₃ = 11c³/81 + cν/3 + Σm³ et
  Σm³ = Σm), mais il n'y a que 7 telles couches (classe 2 de 154/9 à 244/9, classe 1 en 178/9) et elles sont
  indépendantes dans les 14 : aucune relation nouvelle sur les sept paramètres.
- **Divisibilités hypothétiques** (`s0_hyp.py`) : si toutes les couches fractionnaires étaient divisibles par 3, ou
  toutes celles des classes 1, 2, 4, S₀ serait incompatible ; la divisibilité par 8 est compatible.
- **Système joint des 441 classes** Z/9 × F₇² (`joint_even.py`, `joint_odd.py`, `joint_all.py` ; recollement de M₀ avec
  A₈ ⊕ N₄ en un réseau unimodulaire de rang 56) : 42 effectifs libres et 59 sommes vectorielles libres dans S₀.
- **Intégralité exacte des sommes vectorielles, couplée aux effectifs** (`s0_sumint.py`, `s0_sumint2.py`). La
  coordonnée en un sommet de la somme d'une couche de classe k à n vecteurs est dans kn/9 + Z, et les sommes des
  couches déterminées sont des combinaisons rationnelles fixes de 10 sommes libres (celles des couches de O :
  Θ₂[11/9], Θ₁[14/9], Θ₄[17/9], Θ₃[18/9], Θ₂[20/9], Θ₁[23/9], Θ₄[26/9], Θ₂[29/9], Θ₁[32/9], Θ₂[38/9]). Inconnues entières :
  7 paramètres d'effectif et 10 parties entières ; 176 conditions. Résultat : **compatible**, y compris dans chaque
  sous-branche où une couche libre est vide ou réduite aux sommets ou aux droites (somme nulle) : sans coclique, sans
  sommet fantôme, sans droite fantôme, sans vecteur de classe 4 de norme 34/9, et les quatre à la fois.

### 14.4 Forme de Jacobi de la configuration des droites (indice 2) (`jac_lines*.py`, `jac_rank.py`)

**Fait nouveau.** Les 231 vecteurs de droite h_ℓ = √7E1_ℓ sont des vecteurs de norme 4 du réseau pair M. Donc

    φ(τ, z) = Σ_ℓ Σ_{x ∈ M} q^{|x|²/2} ζ^{⟨x, h_ℓ⟩}

est une forme de Jacobi de poids 22 et d'indice 2 sur Γ₀(7). Son coefficient c(n, r) = #{(x, ℓ) : |x|² = 2n,
⟨x, h_ℓ⟩ = r} (r = somme des trois coordonnées de √7x sur ℓ) ne dépend que de (8n − r², r mod 4) ; de même, côté dual,
c_L(N, s) = #{(y, ℓ) : y ∈ L₁, |y|² = 2N, y(ℓ) = s} ne dépend que de (8N − 7s², s mod 4) (translation par 7E1_ℓ). Les
trois coefficients de Taylor sont 231·θ (poids 22), 0 (poids 24, car Σ_ℓ h_ℓh_ℓᵀ = 21E) et la série quartique P_T du §9
(poids 26). Chaque couche apporte trois classes nouvelles (r ou s ∈ {0, ±1, 2}) et trois équations : **tous les
c(n, r) et c_L(N, s) sont déterminés par θ et par la série quartique, et sont des nombres de couples, donc des entiers
positifs.** Par rapport au §9 : les sommes sur les droites sont entières, donc la somme quartique d'une couche est liée
à sa distribution sur {0, ±1, ±2, …} et non seulement bornée par Cauchy–Schwarz.

**Dans S₀** la série quartique a exactement deux paramètres (les zéros G_L[0..12] = 0, G_M[0] = G_M[1] = 0 laissent la
dimension 2 ; l'égalité de classe c_L(7n, s) = c(n, s) est alors satisfaite identiquement, ce qui contrôle la
récurrence et le facteur de Fricke). En prenant pour paramètres les entiers

    p = #{(x, ℓ) : x ∈ M de norme 4, ⟨x, h_ℓ⟩ = 2},      q = #{(y, ℓ) : y ∈ L₁ de norme 26, y(ℓ) = 2},

tous les coefficients sont des combinaisons **entières** de 1, p, q. Premières couches :

    norme 4 de M :   c(2,0) = 153930 + 6p,   c(2,±1) = 38304 − 4p,   c(2,±2) = p
    norme 26 de L₁ : c_L(13,0) = 402696 + 6q,  c_L(13,±1) = 102648 − 4q,  c_L(13,±2) = q
    norme 6 de M :   c(3,0) = 1305840648 − 184p + 294q,  c(3,±1) = 545782104 + 116p − 196q,  c(3,±2) = 31185504 − 20p + 49q
    norme 30 de L₁ : c_L(15,0) = 10835664 + 24p − 12q,  c_L(15,±1) = 3160080 − 16p + 8q,  c_L(15,±2) = 50400 + 4p − 2q
    norme 32 de L₁ : c_L(16,±2) = 266784 + 12p − 16q

La positivité des 213 coefficients (troncature 42) laisse le polygone 0 ≤ p ≤ 9576, 0 ≤ q ≤ 16674 + 3p/4. Les parités
(c(n, 2) et c(n, 0) sont pairs : involutions x ↦ h_ℓ − x et x ↦ −x sans point fixe) sont compatibles. Sans droite
fantôme, p = 2·(nombre de prismes) et les couples (vecteur entier de norme 4, droite de somme ±1) sont exactement
2·22596. **La forme de Jacobi ne ferme pas S₀.**

**À rang quelconque** (`jac_rank.py`, simplexe exact, troncature 40 ; variables : 7 coordonnées de θ, 9 de la série
quartique, le nombre de prismes ; contraintes : tous les c ≥ 0, c_L(N, 2) = 0 pour 7 ≤ N ≤ 10, c_L(7n, s) ≥ c(n, s),
bornes de degré 0) : rang 35 infaisable (contrôle), **rangs 37, 39, 41, 43 faisables**. Au rang 37 les nombres forcés
sont inchangés (380 / 1283 / 4932 / 34 523 pour les normes 14 / 16 / 18 / 20 seules).

**Distribution d'un vecteur P3/N25 sur les droites.** Pour y = 2/9 + 1_P − 1_N, y(ℓ) ∈ {5/3, 2/3, −1/3, −4/3}, et
y(ℓ) = −4/3 exactement quand ℓ porte une arête de N dont le troisième sommet est hors du support (le δ de Codex). Avec
7 droites par sommet de P de types (p, n, n′), (p, n, o), (p, o, o′) en nombres (a, b, c) ∈ {(4,0,3), (3,2,2), (2,4,1),
(1,6,0)}, et Σ_ℓ y(ℓ) = 0, Σ_ℓ y(ℓ)² = 208/3 : les effectifs des quatre valeurs sont **(9 − δ, 59 + 3δ, 163 − 3δ, δ)**.
Donc δ ≤ 9, Σ_ℓ y(ℓ)³ = 478/9 − 6δ et Σ_ℓ y(ℓ)⁴ = 748/9 − 4δ. La somme des δ sur la couche est le nombre de couples
(z, ℓ) avec z de classe 4, de norme 292/9 et z(ℓ) = −8/3 (translation par 7E1_ℓ).

### 14.5 Forme de Jacobi des droites classe par classe dans S₀ (`z9quartic.py`, `z9_validate34.py`, `s0_jac9.py`, `s0_jac9b.py`)

**Structure.** Pour y ∈ L₉ de classe c et une droite ℓ, s = y(ℓ) ∈ c/3 + Z. La translation y ↦ y + 7E1_ℓ (vecteur de classe 3,
de norme 28, de somme 4 sur ℓ) et la symétrie y ↦ −y donnent, pour n(c, N, s) = #{(y, ℓ) : y de classe c, |y|² = 2N, y(ℓ) = s} :

    n(c, N, s) = n(c + 3, N + 7(s + 2), s + 4) = n(−c, N, −s).

Une couche (c, N) n'a donc que quelques valeurs s ∈ (−2, 2] qui ne se lisent pas sur des couches plus basses : 0, ±1, ±2 en
classe 0 (trois inconnues), −2, −1, 0, 1 en classe 3 (s = 2 y est l'inconnue de la classe 0 : y ↦ 7E1_ℓ − y échange vecteurs
fractionnaires et entiers), quatre valeurs dans les classes 1, 2, 4. Les moments Σ1 = 231n, Σs = 0, Σs² = 6Nn, Σs³ = somme
cubique, Σs⁴ = somme quartique + (72/161)N²n donnent alors, **pour chaque couche des classes 1, 2, 3, 4, une équation linéaire
exacte : la somme quartique des droites est déterminée par l'effectif et la somme cubique des droites.** Ces équations ne
découlent pas de la modularité de chaque série prise à part (23 séries de Taylor par classe pour 19 composantes).

**Validation préalable.** Les systèmes cubique (`z9cubic.py`) et quartique (`z9quartic.py`, nouveau : poids 30 + m, facteur
7^((15−r−m)/2)) à neuf classes sont contrôlés de bout en bout sur K₈ ⊕ B¹⁸ avec des harmoniques zonaux de pôle fixe : 98 et 124
valeurs de classe calculées directement, systèmes compatibles.

**Résultat dans S₀ (troncature 32, 62 couches).** Paramètres : 7 effectifs, 14 sommes cubiques, 19 sommes quartiques.
Les 51 équations de Jacobi sont de rang 17 et **compatibles** ; il reste 23 paramètres. La positivité des 237 nombres de couples,
avec les objets connus (sommets : 7 droites de somme 4/3, 84 de somme −2/3, 140 de somme 1/3), est faisable. Le nombre de
configurations P3/N25 garde l'intervalle 10 à 300, et la somme des δ sur cette couche n'est pas contrainte : elle parcourt tout
[0, 9n]. La borne δ ≥ 3 de Codex ne contredit donc pas ce système. **Aucune fermeture de S₀ par cette voie.**

Distribution exacte des vecteurs d'arête 7E(e_u + e_v) sur les droites (pour mémoire) : somme 8/3 sur la droite de l'arête,
2/3 sur 92 droites, −1/3 sur 120, −4/3 sur 18.

(§14.5 noté à 18:07 UTC.)

## 15. Rang 43 : identité de budget, S₀ en coordonnées naturelles, formes de Jacobi de niveau 1 (9 octobre, noté à 18:35 UTC)

### 15.1 Identité de budget pour tout le rang 43 (`r43_identity.py`, exact, troncatures 32 et 38 identiques)

Sans hypothèse de branche, le programme à neuf classes avec les égalités de classe du rang 43 a 15 paramètres. Ils se
remplacent par 15 **nombres d'objets**, qui forment une base :

- couches courtes : a₇ (norme 14), a₈, a₉, a₁₀, a₁₁, a₁₂ (vecteurs entiers de normes 16 à 24), f₁₁, f₁₂ (vecteurs
  fractionnaires de normes 22 et 24, un signe) ;
- objets bas : κ (cocliques de taille 22), g_v (sommets fantômes : vecteurs de O de classe 1 et de norme 28/9 autres que
  les 99 sommets), u (vecteurs de O de classe 4 et de norme 34/9), g_ℓ (droites fantômes), c₁ (vecteurs de L₉ de classe 1 et
  de norme 178/9), w (classe 2, norme 190/9), s₄₄ (ensembles réguliers de 44 sommets).

Dans cette base le nombre n de vecteurs de L₉ de classe 2 et de norme 208/9 (profil (1³ ; (−1)²⁵) à tout rang, §14.1) vaut

    n = 10 − 17a₇ − 10a₈ − 4a₉ − 4a₁₀ − 2a₁₁ − a₁₂ − f₁₁ + 7g_v + u + g_ℓ + 4c₁ + 2w + s₄₄ .

**Conséquence (tout graphe de rang 43).**   17a₇ + 10a₈ + 4a₉ + 4a₁₀ + 2a₁₁ + a₁₂ + f₁₁ ≤ 10 + 7g_v + u + g_ℓ + 4c₁ + 2w + s₄₄.
Les a_n sont pairs : sans objet bas des six types du membre de droite, il n'y a ni vecteur de norme 14 ni de norme 16,
au plus une paire ±y de norme 18 ou 20, et le recensement pondéré « P3/N25 + vecteurs courts » vaut exactement 10.

Autres identités de la même base (contrôle : entier + 2·fractionnaire en norme 26 redonne l'identité (1) de la note 177,
et la norme 4 de M redonne b₂ = 1000 − 8b₁ + 25a₈ + 11a₉ + 8a₁₀ + 3a₁₁ + a₁₂) :

    Ξ₀[117/9] (norme 26, entiers)        = 1152 − 44a₇ − 42a₈ − 24a₉ − 13a₁₀ − 6a₁₁ − 3a₁₂ − 4f₁₁ + 32κ + 28g_v + 4u + 4g_ℓ + 14c₁ + 2s₄₄
    Ξ₃[117/9] (norme 26, fractionnaires) = 740 + 50a₇ + 20a₈ + 4a₉ + 10a₁₀ + 4a₁₁ + 2a₁₂ + 4f₁₁ + f₁₂ − 16κ − 14g_v − 2u − 2g_ℓ − 7c₁ − s₄₄
    Θ₀[18/9] (norme 4 de M, entiers)     = 538 − 8a₇ + 25a₈ + 11a₉ + 8a₁₀ + 3a₁₁ + a₁₂ + 6f₁₁ + 2f₁₂ − 2g_ℓ
    6·Ξ₂[86/9] (classe 2, norme 172/9)   = 290 + 41a₇ + 26a₈ + 10a₉ + 10a₁₀ + 4a₁₁ + 2a₁₂ + 5f₁₁ + f₁₂ − 8κ − 13g_v − u − 3g_ℓ − 8c₁ − 6w − 2s₄₄

### 15.2 S₀ en coordonnées naturelles : S₀ n'est jamais « sans fantôme » (`s0_natural.py`)

Dans S₀ les sept paramètres sont (κ, g_v, u, g_ℓ, c₁, w, s₄₄), et tous les effectifs sont à coefficients de dénominateur
1, 2, 3 ou 6 (le réseau d'intégralité est d'indice 6 dans Z⁷ ; l'indice 100 842 du §13 venait du choix de base) :

    Ξ₂[86/9]  = (290 − 8κ − 13g_v − u − 3g_ℓ − 8c₁ − 6w − 2s₄₄)/6          (classe 2, norme 172/9, profil (1 ; (−1)²³))
    Ξ₂[104/9] = 10 + 7g_v + u + g_ℓ + 4c₁ + 2w + s₄₄                         (P3/N25)
    Ξ₁[107/9] = (1016 + 4κ + 8g_v − u − 2c₁ + 3w + s₄₄)/3
    Ξ₂[113/9] = (826 − 16κ + 55g_v + 7u + 9g_ℓ + 32c₁ + 21w + 8s₄₄)/3
    Ξ₁[116/9] = 1559 − 8κ − (11g_v + 5u + 5g_ℓ)/2 − 16c₁ − w
    Ξ₀[117/9] = 1152 + 32κ + 28g_v + 4u + 4g_ℓ + 14c₁ + 2s₄₄ ;   Ξ₃[117/9] = 740 − 16κ − 14g_v − 2u − 2g_ℓ − 7c₁ − s₄₄
    Ξ₂[122/9] = 3404 − 72κ − 18g_v − 6g_ℓ − 12c₁ − 16w − 3s₄₄ ;   Ξ₁[125/9] = 6336 + 24κ + 16g_v + 11c₁ − 2w − s₄₄
    Ξ₀[126/9] = 538 − 2g_ℓ ;   Ξ₃[126/9] = 231 + g_ℓ

**Congruences exactes dans S₀ :**   g_v + u + g_ℓ ≡ 0 (mod 2)   et   2κ + g_v + u + 2c₁ + 2s₄₄ ≡ 2 (mod 3).

Donc κ = g_v = u = c₁ = s₄₄ = 0 est impossible : **dans S₀ il existe toujours une coclique de taille 22, ou un sommet
fantôme, ou un vecteur de O de classe 4 et de norme 34/9, ou un vecteur de L₉ de classe 1 et de norme 178/9, ou un ensemble
régulier de 44 sommets.** De plus n ≡ s₄₄ (mod 2) et n ≥ 11 (le point « tout nul », qui donnerait n = 10, viole la
congruence). Exemples de points admissibles : (0,0,0,0,0,0,1) (un seul ensemble régulier de 44 sommets, n = 11) ;
u = 2 seul (n = 12).

**Liens géométriques entre objets bas** (à la main ; les translations par 7Ee_v, 7E(e_a + e_b), 7E1_ℓ) :
- coclique ⟹ 22 droites fantômes de chaque signe (déjà utilisé) : g_ℓ ≥ 22κ ;
- sommet fantôme z = 1/9 + 1_P − 1_Q (|P| = 6, |Q| = 17) : l'équation propre donne e(Q) = e(P) + 1 ≥ 1, et pour une arête
  {q, q′} ⊂ Q le vecteur z + 7E(e_q + e_q′) est fractionnaire de norme 28 et n'est pas une droite : **g_v ≥ 1 ⟹ g_ℓ ≥ 1** ;
  de plus z − 7Ee_v (v ∈ P) est un vecteur entier de norme 28 de √7M avec une coordonnée −2 ;
- vecteur de classe 1 et de norme 178/9, y₁ = 1/9 + 1_P − 1_Q (|P| = 5, |Q| = 16) : e(P) = e(Q) + 1 ≥ 1, P ne contient pas
  de droite, et pour chaque arête e ⊂ P le vecteur 7E1_e − y₁ est un autre vecteur de la même couche contenant e dans son
  support positif (involution sans point fixe à e fixée) : **c₁ ≠ 1**, et le nombre de tels vecteurs dont le support
  positif contient une arête donnée est pair ; y₁ − 7Ee_v (v ∈ P) est entier de norme 26 ;
- vecteur de classe 4 et de norme 238/9 : profil (1 ; (−1)⁴⁵), et alors y − 7Ee_a est une droite fantôme (coordonnée −5/3) ;
  ou profil (−2 ; (−1)⁴²), et alors y ↦ −y − 7Ee_b est une involution sans point fixe (ils vont par paires).

### 15.3 Formes de Jacobi de niveau 1 au rang 43 (`jl1.py`, `jl1_line.py`, `jl1_vertex.py`, `jl1_p3n25.py`)

**Fait utilisé.** Au rang 43, U = M + N₄ (rang 48) et W = M₀ + A₈ + N₄ (rang 56) sont unimodulaires pairs. Pour un vecteur
v de U ou de W, Σ_u q^{|u|²/2}ζ^{⟨u,v⟩} est une forme de Jacobi de **niveau 1**, de poids 24 ou 28 et d'indice |v|²/2, dans un
espace de dimension 6 (U, norme 4), 7 (W, norme 4) ou 9 (W, norme 6). L'outil (`jl1.py`, développement de Taylor
d'Eichler–Zagier) redonne la distribution des baisers du réseau de Leech (93150, 47104, 4600).

Tout vecteur court se relève en vecteur de norme 4 : les vecteurs de L₁ de normes 16, 18, 20, 22, 24 (partenaire de N₄ de
norme 12/7, 10/7, 8/7, 6/7, 4/7), ceux de norme 26 dans quatre des huit classes (partenaire 2/7), les sommets dans W
((w_v, e_i − 1/9), 9 relèvements), et un vecteur P3/N25 se relève en vecteur de norme 6 de W (208/63 + 14/9 + 8/7).

**Dans S₀** (racines de U : les 4 de N₄ ; a₂(U) = 1000 + 12 + 4·329 = 2328) :
- **par droite ℓ** (v = (h_ℓ, 0) ∈ U) : un seul paramètre t_ℓ = #{u de norme 4 : ⟨u, v⟩ = 2}, et
  c(2,0) = 1550 + 6t_ℓ, c(2,±1) = 388 − 4t_ℓ, c(3,0) = 29416744 + 1232t_ℓ, c(3,±1) = 11335100 − 828t_ℓ, c(3,±2) = 499584 + 216t_ℓ, … ;
  positivité : 0 ≤ t_ℓ ≤ 97. Identité par droite : (vecteurs entiers de norme 4 de M de somme 1 sur ℓ) + ζ¹_ℓ + 4ζ²_ℓ = 320,
  où ζˢ_ℓ compte les vecteurs de norme 26 des quatre bonnes classes de somme s sur ℓ. La somme sur ℓ redonne 231·320,
  en accord avec le §14.4 quel que soit q.
- **par sommet** (dans W, cas sans fantôme) : deux paramètres (a₂(W), χ_v), puis tout est déterminé, par exemple
  c(3,±2) = 123232 + 14a₂(W) − 92c(2,1) + 88c(2,2).
- **par vecteur P3/N25** (dans W) : produits avec les 76 racines : (15, 46, 15) ou (16, 44, 16) selon le type de la classe ;
  avec w₂ = a₂(W) et x_r = c(2, r) : c(3,±3) = 4118 + 2w₂ − 10x₁ + 8x₂ − 66x₃ (type A), 3536 + … (type B), et de même
  c(3,0), c(3,±1), c(3,±2). Les droites y contribuent par δ (7(9 − δ) vecteurs de produit 3).
Ces identités sont exactes et nouvelles ; chacune fait intervenir des populations inconnues, et **aucune n'est violée**.

**Produits de deux vecteurs P3/N25 (rang 43).** Les classes de F₇² de type 20 forment un cercle de 8 points ; pour
y, y′ de supports (P, N), (P′, N′) et m·m′ = |P∩P′| + |N∩N′| − |P∩N′| − |N∩P′| :
m·m′ ≡ 0 (même classe), 2 (classes opposées), 1 (classes orthogonales), 3 ou 6 (autres) modulo 7 ; jamais 4 ni 5.
Dans S₀ : −6 ≤ m·m′ ≤ 15, donc m·m′ ∈ {−6, −5, −4, −1, 0, 1, 2, 3, 6, 7, 8, 9, 10, 13, 14, 15}, et comme n ≥ 11 > 8, deux
vecteurs P3/N25 au moins sont dans la même classe : m·m′ ∈ {0, 7, 14} et y − y′ ∈ √7M₀.
