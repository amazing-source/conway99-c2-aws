#!/bin/bash
# Route (C), adaptive queue: EC2 "User data" (Advanced details > User data). Replace JETON (2 letters J E T O N) by your GitHub token.
# Runs by itself at the first boot: nothing to type on the machine. The machine then installs, calibrates, computes, and powers
# itself off at the end (with "Shutdown behavior: Terminate" it is then deleted).
shutdown -h +60
sudo -u ubuntu -H bash -lc 'cd ~ && git clone https://x-access-token:JETON@github.com/amazing-source/conway99-c2-aws.git && bash conway99-c2-aws/q/qmachine.sh'
