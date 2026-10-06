"""Keep the queue's spend cap on the FIRST account only: the machines of the second account are paid by its free credits, so their
share of the ledger is written to control.json as credit_usd (the ledger formula subtracts it). The second account's machines of
this run are exactly the c7a.2xlarge machines booted on or after 2026-10-06 12:00 UTC.   python credit.py <repo> [--dry]"""
import sys, os, json, subprocess, time
REPO = os.path.abspath(sys.argv[1]); sys.path.insert(0, os.path.join(REPO, "q")); os.chdir(REPO)
import monitor_q as M
M.fetch(); order, ctl, ev, ms = M.state(); now = time.time(); le = M.last_events(ev)
TERMINAL = M.TERMINAL; share = 0.0; n = 0
for name, st in ms.items():
    try:
        if st.get("ITYPE") != "c7a.2xlarge" or float(st["BOOT"]) < 1791288000: continue
        last = M.last_seen(st, name, le); rate = float(st["PRICE"]) + float(st["OVH"])
        if st.get("STATE") in TERMINAL: end = last + 180
        elif now - last <= int(ctl.get("lease_s", 1800)): end = now
        else: end = last + 22 * 60
        share += max(0.0, end - float(st["BOOT"])) / 3600.0 * rate; n += 1
    except (KeyError, ValueError):
        pass
share = round(share, 2); cur = float(ctl.get("credit_usd", 0))
led, proj = M.ledger(ms, now, ctl, 300, 20, last_event=le)
print("second-account machines: %d, share of the ledger %.2f $ (credit_usd was %.2f) | ledger shown %.2f of cap %.0f" % (n, share, cur, led, float(ctl["cap_usd"])))
if "--dry" not in sys.argv and abs(share - cur) >= 0.05:
    M.set_control(credit_usd=share)
