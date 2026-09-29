# Route (C) sur AWS : tout est ici (dépôt privé)

Le calcul de 57 réseaux est coupé en **18 tranches**, une par machine : 3 comptes × 6 régions.
- **Coût prévu :** environ 135 $ (270 $ au pire).
- **Durée prévue :** environ 14 h (29 h au pire).
- **Suivi :** chaque machine envoie elle-même son état et ses résultats sur ce dépôt, sur la branche `run/<nom>`. Il n'y a rien à
  rapatrier à la main.

`c2_cloud_run.zip` est le paquet vérifié (sha256 dans `SHA256SUMS`) : même moteur que le PC du labo, octet pour octet. Chaque
machine refait d'abord une **calibration**, et ne calcule que si elle est identique à celle du labo.

## 1. Une seule fois : un jeton GitHub
Sur github.com, compte amazing-source : Settings → Developer settings → Personal access tokens → **Fine-grained tokens** →
Generate new token.
- Nom : `aws-c2`.
- Expiration : **14 jours**.
- Repository access : **Only select repositories** → `conway99-c2-aws`.
- Permissions → Repository permissions → **Contents : Read and write**.

Copie le jeton (il commence par `github_pat_…`). Il ne donne accès **qu'à ce dépôt**, et il expire tout seul.

## 2. Pour chaque machine
Crée la machine dans la région de la case : **Ubuntu**, **c7a.8xlarge**, option Spot, 20 Go de disque (tutoriel officiel AWS
« Get started with Amazon EC2 »). Connecte-toi (par exemple avec le bouton « Se connecter » de la console, qui ouvre un terminal
dans le navigateur), puis colle **une seule ligne** : celle de la case, où tu remplaces `JETON` par ton jeton.

```
git clone https://x-access-token:JETON@github.com/amazing-source/conway99-c2-aws.git && bash conway99-c2-aws/machine.sh TRANCHE NOM
```

| Compte | eu-north-1 (Stockholm) | us-east-2 (Ohio) | us-east-1 (Virginie) | us-west-2 (Oregon) | eu-west-2 (Londres) | eu-central-1 (Francfort) |
|---|---|---|---|---|---|---|
| Toi | `0/18 toi-stockholm` | `1/18 toi-ohio` | `2/18 toi-virginie` | `3/18 toi-oregon` | `4/18 toi-londres` | `5/18 toi-francfort` |
| Frère | `6/18 frere-stockholm` | `7/18 frere-ohio` | `8/18 frere-virginie` | `9/18 frere-oregon` | `10/18 frere-londres` | `11/18 frere-francfort` |
| Père | `12/18 pere-stockholm` | `13/18 pere-ohio` | `14/18 pere-virginie` | `15/18 pere-oregon` | `16/18 pere-londres` | `17/18 pere-francfort` |

Exemple pour la case Toi / Francfort :
`git clone https://x-access-token:JETON@github.com/amazing-source/conway99-c2-aws.git && bash conway99-c2-aws/machine.sh 5/18 toi-francfort`

La commande **rend la main tout de suite**. Tu peux fermer la fenêtre : la machine s'installe (5 à 15 min), calibre, puis calcule
en arrière-plan.

## 3. Suivre depuis ton PC ou ton portable
Il te faut Python 3 et git. Une fois : `git clone https://github.com/amazing-source/conway99-c2-aws.git`. Ensuite, dans ce dossier :

```
python monitor_git.py
```

Un tableau des 18 machines s'affiche toutes les 10 minutes, avec leur état, leur progression et une estimation de fin.

| État | Quoi faire |
|---|---|
| PAS LANCEE | La commande n'a pas été collée sur cette machine, ou la machine démarre |
| INSTALLATION | Attendre 5 à 15 min |
| EN_COURS | Rien. Au début, 0 job fini pendant 2 à 5 h est normal : les plus gros jobs passent en premier |
| FINI | **Supprimer la machine** dans la console AWS : c'est tout, les résultats sont déjà sur GitHub |
| ERREUR | Relancer **la même ligne** sur la même machine, ou sur une nouvelle : les jobs déjà faits sont gardés |
| SILENCIEUSE | La machine ne donne plus de nouvelles (interruption spot). Recréer une machine dans une région libre et y coller **la même ligne** : elle reprend là où l'autre s'était arrêtée |
| STOP CALIB / ERREUR INSTALLATION | Ne rien faire et prévenir Claude |

## 4. Garde-fous
- Dans chaque compte AWS : un **budget** (Billing → Budgets) avec alerte par e-mail, et une action d'arrêt des instances EC2
  avant la fin des crédits.
- Supprimer chaque machine dès qu'elle affiche **FINI**.
- Le calcul d'une machine ne dépend pas de ton PC : tu peux éteindre ton PC, les machines continuent.

## Contenu
- `machine.sh` : ce qui tourne sur chaque machine.
- `probe.sh` : lit l'état de la machine.
- `monitor_git.py` : le tableau de suivi.
- `machines.json` : les 18 cases.
- `.github/workflows/linux_test.yml` : la répétition générale, sur une machine Linux neuve de GitHub, du parcours complet
  (installation, calibration, un vrai job, envoi sur la branche `run/ci-test`).
