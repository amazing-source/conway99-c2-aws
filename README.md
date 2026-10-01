# Route (C) sur AWS — file d'attente adaptative (à jour au 01/10/2026)

Ce dépôt privé fait tourner sur AWS **exactement le calcul du PC du labo**, au moindre coût, sans jamais payer deux fois le même
travail et sans dépasser le budget. L'ancien plan à 54 tranches du 29/09 est archivé dans `OLD_README_54_TRANCHES.md` ; ne plus
l'utiliser.

## Où on en est
- **Route (C) : 94/156 enveloppes exclues.** Ce chiffre inclut les 399 jobs AWS du 29-30/09, importés au labo le 01/10.
- **Ce lot.** Tous les jobs encore ouverts du paquet vérifié `c2_cloud_run.zip` (sha256 `263ab75b…`), sur 56 réseaux. La liste est
  dans la branche `queue`.
- **Hors de ce lot** (ils demandent d'abord du code) : la famille Golay 001/002/004/010, et 000 (O24).
- **Coût mesuré.** Les 399 jobs déjà faits sur AWS ont pris en moyenne **1,30 ×** leur estimation. Le lot complet représente donc
  environ **295 heures-machine c7a.8xlarge, soit environ 91 $ en eu-north-1** (environ 3 jours avec 4 machines). Selon les jobs,
  le vrai temps varie de 0,24 × à 3 × l'estimation : le plafond (ci-dessous) est là pour ça.

## Ce qui protège ton argent (tout est automatique)
1. **Calcul identique au PC.**
   - Chaque job est lancé par les fonctions mêmes du paquet (`run_jobs.start`), avec les mêmes commandes et les mêmes réglages du
     moteur.
   - Les 559 fichiers sont vérifiés par sha256 avant tout calcul.
   - Chaque machine refait le job de calibration 118:2 et ne calcule que s'il est **EQUIVALENT** à celui du labo.
   - À l'import, le labo refuse tout résultat qui ne vient pas du même moteur.
2. **Jamais deux fois le même job.** Une seule file d'attente (branche `queue`). Une réservation n'est acceptée que si personne n'a
   écrit avant (push git non forcé). Une machine morte libère ses jobs au bout de 30 min.
3. **Un résultat n'est déclaré « fait » qu'une fois déposé sur GitHub.** Aucun travail payé ne peut être perdu.
4. **Plafond dur de 115 $.**
   - Chaque machine additionne le coût de **toutes** les machines au **prix maximum Spot** (+ 0,01 $/h de disque et d'IP). C'est une
     borne haute : la vraie facture est toujours inférieure.
   - Une machine ne prend un job que s'il peut se terminer sous le plafond.
   - Au plafond, toutes les machines s'arrêtent.
5. **Aucune machine oubliée.** Chaque machine porte un interrupteur « homme mort » :
   - si elle ne peut plus rendre compte pendant **20 min** (60 min pendant l'installation), elle s'éteint seule ;
   - avec « Comportement d'arrêt : Résilier », elle est alors **supprimée**.
6. **Machine non conforme = refusée et éteinte dans la minute** : pas Spot, pas c7a.8xlarge, ou région sans prix dans
   `q/prices.json`.
7. **Filet AWS.** Le budget AWS « c2-route-c-backstop » (120 $/mois, usage brut hors crédits) envoie un e-mail à
   **206353265+amazing-source@users.noreply.github.com** à 50, 80, 95 et 100 %.
   - AWS ne sait pas imposer un vrai plafond : ses chiffres arrivent avec des heures de retard. C'est pourquoi le vrai plafond est
     tenu par les machines elles-mêmes (point 4).

## 1. Une seule fois : le jeton GitHub
Sur github.com, compte **amazing-source** : Settings → Developer settings → Personal access tokens → **Fine-grained tokens** →
Generate new token.
- Nom : `aws-c2`.
- Expiration : 14 jours.
- Repository access : **Only select repositories**, puis `conway99-c2-aws`.
- Permissions → Repository permissions → **Contents : Read and write**.

Copie le jeton (il commence par `github_pat_…`). Il ne donne accès qu'à ce dépôt et expire tout seul. Celui du 29/09 reste valable
jusqu'au 13/10 si tu l'as gardé.

## 2. Lancer des machines (autant que tu veux, quand tu veux)
Région par région, **dans cet ordre** (la moins chère d'abord). Quota : 128 vCPU Spot par région, soit **4 machines maximum par région**.

| Ordre | Région (console) | Prix maximum à taper | Prix Spot relevé le 01/10 |
|---|---|---|---|
| 1 | Europe (Stockholm) `eu-north-1` | **0.34** | 0.30 |
| 2 | US East (Ohio) `us-east-2` | **0.42** | 0.38 |
| 3 | US West (Oregon) `us-west-2` | **0.68** | 0.55 |
| 4 | US East (N. Virginia) `us-east-1` | **0.85** | 0.53 (volatile) |

**Conseil budget : 4 machines à Stockholm seulement** (environ 91 $, environ 3 jours). N'ajoute l'Ohio que pour aller plus vite :
le plafond protège de toute façon.

Dans la console EC2 de la région : **Lancer une instance**, puis exactement :
1. **Nom** : `c2q` (au choix ; la machine utilise son identifiant AWS).
2. **Image** : Ubuntu Server **24.04 LTS**, architecture **64 bits (x86)**.
3. **Type d'instance** : **c7a.8xlarge**.
4. **Paire de clés** : « Continuer sans paire de clés ». Il n'y aura jamais besoin de se connecter.
5. **Réseau** : par défaut (aucune règle à ajouter).
6. **Stockage** : **20 Gio**, gp3.
7. **Détails avancés** :
   - **Option d'achat : Instances Spot.**
   - **Prix maximum : Définir le prix maximum**, puis le nombre exact du tableau (par exemple **0.34** à Stockholm).
   - **Type de demande : Unique.** **Comportement d'interruption : Résilier.**
   - **Comportement d'arrêt : Résilier** (si le champ est proposé).
   - **Données utilisateur** : colle tout le contenu de `q/userdata.sh`, en remplaçant `JETON` par ton jeton.
8. **Nombre d'instances** (à droite) : 1 à 4.
9. **Lancer l'instance.** C'est tout : chaque machine s'installe (environ 10 min), se calibre, prend des jobs, envoie ses
   résultats, puis se supprime seule à la fin.

Si la région refuse (« insufficient capacity » ou quota), passe à la région suivante du tableau, avec **son** prix maximum.

## 3. Suivre depuis le PC
Dans ce dossier (`Desktop\c2_experimental\aws_repo`) :

```
python q/monitor_q.py           tableau toutes les 5 min (Ctrl+C pour quitter)
python q/monitor_q.py --once    un seul tableau
python q/monitor_q.py --aws     contrôle AWS en lecture seule
```

Le contrôle `--aws` vérifie que chaque instance allumée apparaît bien dans le tableau, avec le bon type, en Spot et au bon prix
maximum.

Normal :
- `INSTALLATION` pendant environ 10 min ;
- puis `EN_COURS`. Les premiers résultats arrivent au bout de 2 à 3 h environ, car un job dure environ 2 h.

La ligne « spend ledger » donne le coût total compté (borne haute) face au plafond.

## 4. Arrêter, ralentir, reprendre (à distance, depuis le PC)
```
python q/monitor_q.py --drain     les machines finissent leurs jobs en cours, n'en prennent plus, puis s'éteignent
python q/monitor_q.py --stop      arrêt immédiat de tout (les jobs en cours retournent dans la file), puis extinction
python q/monitor_q.py --run       retour à la normale (pour les machines encore allumées et celles lancées ensuite)
python q/monitor_q.py --cap 100   changer le plafond (en $)
```

## 5. Quand c'est fini : importer les résultats (PC du labo)
```
cd C:\Users\RESEARCHER\Desktop\c2_experimental\aws_repo
python q/monitor_q.py --fetch
cd ..
.venv\Scripts\python.exe scripts\cloud\import_results.py c2_cloud_run aws_repo\resultats_q\q-i-XXXX\results ...   (un dossier par machine)
.venv\Scripts\python.exe scripts\stream_finish.py
```

L'import peut aussi se faire en cours de route, autant de fois qu'on veut (les doublons sont ignorés).

## 6. États affichés, et quoi faire
| État | Sens | Quoi faire |
|---|---|---|
| INSTALLATION | installation + calibration | attendre (environ 10 min) |
| EN_COURS | calcule | rien |
| DRAINING | finit ses jobs, n'en prend plus | rien |
| FINI | file vide, machine éteinte et supprimée | rien |
| DRAINED | arrêt propre (plafond prévu atteint, ou `--drain`) | rien |
| STOP | arrêt immédiat (plafond atteint, ou `--stop`) | rien |
| INTERRUPTED | AWS a repris la machine Spot ; ses jobs retournent dans la file | relancer une machine si tu veux |
| REFUS | machine non conforme (pas Spot / mauvais type / région) ; déjà éteinte | relancer avec les bons réglages |
| STOP CALIB | la calibration diffère du labo : rien n'a été calculé ; déjà éteinte | **ne pas relancer**, prévenir Claude |
| ERREUR INSTALLATION / ERREUR AGENT | déjà éteinte ; le détail est sur la branche `run/<nom>` | prévenir Claude |
| SILENT (dans la note) | ne donne plus de nouvelles ; l'homme mort l'éteint | vérifier avec `--aws`, sinon rien |

## 7. Le dossier `q/`
- `qmachine.sh` : démarrage d'une machine. C'est la même ligne partout, lancée par `userdata.sh`.
- `qagent.py` : la boucle de calcul, avec la file, le plafond et l'homme mort.
- `prices.json` : prix maximum par région, et type autorisé.
- `make_queue.py` : construit la branche `queue` depuis l'état réel du labo (seulement les jobs pas encore faits, le réseau le plus
  riche d'abord, comme `sched.py`).
- `monitor_q.py` : suivi, pilotage et import.
- `rehearsal_check.py` et `.github/workflows/q_rehearsal.yml` : répétition générale **gratuite** sur une machine Linux de GitHub,
  avec trois scénarios :
  - deux agents sur de vrais jobs : aucune double réservation, chaque job fait une fois, résultats déposés ;
  - plafond atteint : arrêt sans rien prendre ;
  - arrêt et vidange à distance.
