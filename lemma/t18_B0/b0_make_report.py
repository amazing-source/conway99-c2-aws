# Writes REPORT.md = b0_body_src.txt + a FINAL STATE section generated from the logs (+ b0_final_note.txt if present).
import subprocess, sys, datetime, os
body = open("b0_body_src.txt", encoding="utf-8").read()
c = subprocess.run([sys.executable, "b0_summaryC.py"], capture_output=True, text=True).stdout
x = subprocess.run([sys.executable, "b0_summaryX0.py"], capture_output=True, text=True).stdout
extra = open("b0_final_note.txt", encoding="utf-8").read() if os.path.exists("b0_final_note.txt") else ""
fence = chr(96) * 3
out = (body + chr(10) + "## FINAL STATE (generated " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + ")" + chr(10) + chr(10) + extra + chr(10)
       + "Output of b0_summaryC.py:" + chr(10) + chr(10) + fence + chr(10) + c + fence + chr(10) + chr(10)
       + "Output of b0_summaryX0.py:" + chr(10) + chr(10) + fence + chr(10) + x + fence + chr(10))
open("REPORT.md", "w", encoding="utf-8").write(out)
print("REPORT.md written,", len(out), "characters")
