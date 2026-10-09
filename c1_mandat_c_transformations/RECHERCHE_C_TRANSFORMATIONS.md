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

Cas restants pour la proposition C : droites non génériques (τ ≡ 0 ou G(T) déconnecté), et paires de rangs
(37,41), (37,43), (39,39) et au-delà. Pour (37,41), D ≡ −Y′ est le Gram de vecteurs isotropes d'un espace de
dimension 4 à produits dans {0, ±1} ; de telles configurations existent, l'argument s'arrête là.

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
