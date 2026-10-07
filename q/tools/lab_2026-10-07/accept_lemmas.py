"""Write data/finishC/lemmas_accepted.json: the record that T18 and T20 are accepted (C2 lab, 2026-10-07).

  .venv/Scripts/python.exe scripts/cloud/accept_lemmas.py --yes

It is the file scripts/cloud/convert_deferred.py requires before it may turn a DEFERRED pair into an exclusion. Run by hand, once,
after the user's agreement; it refuses to overwrite an existing file. The top-level keys are the lemma names only (the conversion
lists them as the accepted lemmas). Each entry pins the proof text by its git blob id in the compute repository (aws_repo, HEAD at
the time of writing) and states who accepted it and what the acceptance covers."""
import sys, os, json, subprocess, time
LAB = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); REPO = os.path.join(LAB, "aws_repo")


def git(*a): return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True).stdout.strip()


def main():
    assert "--yes" in sys.argv, "run with --yes after the user's agreement"
    out = os.path.join(LAB, "data", "finishC", "lemmas_accepted.json"); assert not os.path.exists(out), "already written"
    head = git("rev-parse", "HEAD"); now = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    who = ("the user, 2026-10-07: asked by the lab session at 15:26 UTC for his explicit word before T18 and T20 are written as accepted, he "
           "replied \"Pouruqoi on les considererait pas comme acceptés?\"; the lab session told him it took this as a yes, with the scope below, "
           "and that it would write this file once the last checks were in")
    scope = ("checked by AI sessions only (authors, referees, second programs); no human reader; not formalised")
    d = {"T18": {"reference": "compute repository conway99-c2-aws, lemma/T18_PROOF.md (no sigma-odd integer (-4)-eigenfunction of squared norm 18)",
                 "git_blob": git("rev-parse", "HEAD:lemma/T18_PROOF.md"), "repo_commit": head, "date": now,
                 "referees": "lemma/t18_REFEREE/REPORT.md (on the working reports); lemma/t18_REFEREE2/REPORT.md (read the text only and re-did every "
                             "computation with programs of his own: no error, eleven presentation points, merged)",
                 "accepted_by": who, "scope": scope + "; not reread by the lab session"},
         "T20": {"reference": "compute repository conway99-c2-aws, lemma/T20_PROOF.md, Theorem 10.2 (no such eigenfunction of squared norm 20)",
                 "git_blob": git("rev-parse", "HEAD:lemma/T20_PROOF.md"), "repo_commit": head, "date": now,
                 "referees": "Codex, lemma/t20_CODEX/REFEREE_T20_PROOF.md (two passes, no blocking error; corrections merged per the laptop session); "
                             "two programs for every computation; provenance table lemma/ARTIFACTS_T18_T20.md (not reviewed)",
                 "open_reserves": "G2 (wording of the verifier contract); case III.1: the second verification shares the model file and part of the "
                                  "enumeration skeleton",
                 "accepted_by": who, "scope": scope}}
    assert all(len(d[k]["git_blob"]) == 40 for k in d), "proof text not found at HEAD"
    json.dump(d, open(out, "w", encoding="ascii", newline=chr(10)), indent=1, ensure_ascii=True)   # portable: no platform encoding
    print("written: %s\n%s" % (out, json.dumps({k: (v["git_blob"][:16], v["date"]) for k, v in d.items()})))


if __name__ == "__main__":
    main()
