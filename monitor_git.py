"""Suivi des machines AWS par GitHub (C2, 29/09/2026). A lancer DANS le clone du depot conway99-c2-aws, sur n'importe quel PC :

    python monitor_git.py            # un tableau toutes les 10 minutes (Ctrl+C pour quitter)
    python monitor_git.py --once     # un seul tableau
    python monitor_git.py --fetch    # + copie les resultats de chaque machine dans resultats/<nom>/ (pour l'import par Claude)

Chaque machine pousse son etat sur la branche run/<nom> toutes les 10 minutes. Le moniteur lit ces branches : pas d'adresse IP,
pas de cle, pas de ssh. Python 3 seul suffit (aucune bibliotheque a installer), avec git."""
import argparse, datetime, io, json, os, re, subprocess, sys, time, unicodedata, zipfile
HERE = os.path.dirname(os.path.abspath(__file__))
asc = lambda t: unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()


def git(*a, binary=False):
    r = subprocess.run(["git", "-C", HERE] + list(a), capture_output=True)
    return r.stdout if binary else r.stdout.decode("utf-8", "replace")


def row(name, slc, ref):
    st = git("show", "%s:status.txt" % ref)
    if not st: return (name, slc, "PAS LANCEE", "-", "pas encore de nouvelles (commande pas lancee, ou machine en demarrage)")
    d = dict(l.split("=", 1) for l in st.splitlines() if "=" in l)
    age = (time.time() - int(git("log", "-1", "--format=%ct", ref).strip() or 0)) / 60
    nres = len([l for l in git("ls-tree", "--name-only", "%s:results" % ref).splitlines() if l.endswith(".jsonl")])
    state = d.get("STATE", "?")
    m = re.search(r"-- (\d+)/(\d+) jobs", d.get("LAST", "")); done, total = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    if not total and d.get("STARTJOBS"): total = int(d["STARTJOBS"])
    prog = "%d/%d" % (max(done, nres), total) if total else ("%d" % nres if nres else "-")
    late = "  !! SILENCIEUSE depuis %.0f min : machine arretee ou interrompue ? (voir console AWS)" % age if age > 35 and state not in ("FINI", "STOP CALIB", "ERREUR", "ERREUR INSTALLATION") else ""
    if state == "INSTALLATION": det = "installation + calibration en cours (5 a 15 min)"
    elif state == "STOP CALIB": det = "CALIBRATION PAS EQUIVALENTE : ne rien faire, prevenir Claude"
    elif state == "ERREUR INSTALLATION": det = "l'installation a echoue : prevenir Claude (voir tail_setup.log.txt sur la branche)"
    elif state == "ERREUR": det = "le calcul s'est arrete sans finir : relancer la meme commande (les jobs faits sont gardes)"
    elif state == "FINI": det = "TERMINE : supprimer la machine dans la console AWS"
    else:
        eta = ""
        try:
            t0 = datetime.datetime.strptime(d["START"], "%Y-%m-%d %H:%M:%S"); now = datetime.datetime.strptime(d["NOW"], "%Y-%m-%d %H:%M:%S")
            el = (now - t0).total_seconds() / 3600
            eta = (", fin estimee ~%.0f h" % (el / done * (total - done))) if done else (", lancee depuis %.1f h (0 au debut : normal, gros jobs d'abord)" % el)
        except Exception:
            pass
        bad = int(d.get("BADJOBS") or 0)
        det = "%s calculs actifs sur %s coeurs, RAM libre %s Go%s%s" % (d.get("PROCS", "?"), d.get("NPROC", "?"), d.get("MEMFREE", "?"), eta,
                                                                       (" | %d job(s) en erreur : relancer la commande a la fin" % bad) if bad else "")
        if d.get("ERRLOG"): state, det = "ERREUR", d["ERRLOG"]
    return (name, slc, state, prog, det + late)


def table(args):
    git("fetch", "-q", "--prune", "origin", "+refs/heads/run/*:refs/remotes/origin/run/*")
    ms = json.load(open(os.path.join(HERE, "machines.json"), encoding="utf-8"))
    names = [m["name"] for m in ms]
    extra = [l.strip().split("origin/run/")[1] for l in git("branch", "-r").splitlines() if "origin/run/" in l and l.strip().split("origin/run/")[1] not in names]
    rows = [row(m["name"], m["slice"], "origin/run/" + m["name"]) for m in ms] + [row(n, "test", "origin/run/" + n) for n in extra]
    print(asc("\n=== Route (C) sur AWS : %s ===" % time.strftime("%d/%m %H:%M")))
    for r in rows: print(asc("%-16s %-6s %-12s %-9s %s" % r))
    n = lambda k: sum(1 for r in rows if r[2] == k)
    print(asc("--- en cours %d | finies %d | en installation %d | pas lancees %d | a regarder %d ---" % (
        n("EN_COURS"), n("FINI"), n("INSTALLATION"), n("PAS LANCEE"), sum(1 for r in rows if r[2] in ("ERREUR", "STOP CALIB", "ERREUR INSTALLATION") or "SILENCIEUSE" in r[4]))))
    if args.fetch:
        for m in [r[0] for r in rows if r[2] != "PAS LANCEE"]:
            data = git("archive", "--format=zip", "origin/run/" + m, "results", binary=True)
            if data:
                dst = os.path.join(HERE, "resultats", m); os.makedirs(dst, exist_ok=True); zipfile.ZipFile(io.BytesIO(data)).extractall(dst)
        print(asc("resultats copies dans %s" % os.path.join(HERE, "resultats")))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--once", action="store_true"); ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--every", type=float, default=10); args = ap.parse_args()
    while True:
        if not args.once: os.system("cls" if os.name == "nt" else "clear")
        table(args)
        if args.once: break
        time.sleep(args.every * 60)


if __name__ == "__main__":
    main()
