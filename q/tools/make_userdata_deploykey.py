"""Builds userdata_pilot.sh = q/userdata.sh with the GitHub token replaced by a deploy key of this repo (SSH). C2, 2026-10-01.

  py -3 q/tools/make_userdata_deploykey.py FOLDER

FOLDER must hold c2q_deploy (the private key) and known_hosts (GitHub's SSH host keys, "github.com <key>" lines from
https://api.github.com/meta). The generated FOLDER/userdata_pilot.sh contains the private key: keep it, and the key, out of git.
This is the user data the 4 machines of 2026-10-01 were launched with (see HANDOFF_2026-10-01.md, section 8)."""
import os, re, sys
D = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
key = open(os.path.join(D, "c2q_deploy"), newline="").read().replace("\r", "")
hosts = open(os.path.join(D, "known_hosts"), newline="").read().replace("\r", "")
assert key.startswith("-----BEGIN OPENSSH PRIVATE KEY-----") and key.rstrip().endswith("-----END OPENSSH PRIVATE KEY-----")
assert hosts.count("github.com ") == 3
lines = [
    "#!/bin/bash",
    "# Route (C) adaptive queue, AWS, 2026-10-01: identical to q/userdata.sh except that the machine reaches GitHub with a deploy key",
    "# of amazing-source/conway99-c2-aws (read-write, this repo only; id 165097369, revoke after the run) instead of a token.",
    "shutdown -h +60",
    "install -d -m 700 -o ubuntu -g ubuntu /home/ubuntu/.ssh",
    "cat > /home/ubuntu/.ssh/id_ed25519 <<'C2KEY'",
    key.rstrip("\n"),
    "C2KEY",
    "cat > /home/ubuntu/.ssh/known_hosts <<'C2HOSTS'",
    hosts.rstrip("\n"),
    "C2HOSTS",
    "chown ubuntu:ubuntu /home/ubuntu/.ssh/id_ed25519 /home/ubuntu/.ssh/known_hosts",
    "chmod 600 /home/ubuntu/.ssh/id_ed25519",
    "sudo -u ubuntu -H bash -lc 'cd ~ && git clone git@github.com:amazing-source/conway99-c2-aws.git && bash conway99-c2-aws/q/qmachine.sh'",
]
out = os.path.join(D, "userdata_pilot.sh")
open(out, "w", newline="\n").write("\n".join(lines) + "\n")
txt = open(out, newline="").read()
assert "\r" not in txt
print("written %s (%d bytes)" % (out, len(txt)))
print(re.sub(r"-----BEGIN OPENSSH PRIVATE KEY-----.*?-----END OPENSSH PRIVATE KEY-----", "[private key hidden]", txt, flags=re.S))
