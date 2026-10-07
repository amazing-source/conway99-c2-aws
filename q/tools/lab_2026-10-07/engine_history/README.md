# Engine files of 27-29/09 kept on the lab PC

Found on 2026-10-07 by hashing every `*hstage_stream*.py` on the lab PC: the stream wrapper whose hash `4e310e729b7df3d0` is carried
by 251 records of 29/09 (39 lattices, 4,409,816 pairs) is `scripts/hstage_stream_v_pre_telemetry.py`, saved at 17:50 on 29/09 just
before the telemetry change. Earlier in the day it had been reported as "no longer on the PC": only the current
`scripts/hstage_stream.py` had been hashed. The core of those records, `frame_dfs.py` b48cf844, is the file of package v1.

`MANIFEST.json`: every backup of the engine files (`*_v_pre_<change>.py` = the file as it was just before <change>), with its size,
its modification time (local time of the lab PC) and its sha256 as on the lab disk, with LF and with CRLF. The record hashes of the
campaign are of the file as on the lab disk (CRLF). Git may store these files with other line endings: compare with the CRLF hash.

Dating of the 132 records WITHOUT code version (27/09 23:03 to 29/09 17:02), by their start time (t - wall_secs) against the
modification times above: 75 started under wrapper `hstage_stream_v_pre_twin.py` (= the file of commit 609cc3b of
conway99-c2-experimental, 29/09 08:44) and core `frame_dfs_v_pre_shared.py`; 23 under the same wrapper and `frame_dfs_v_pre_ec.py`;
15 under the same wrapper and `frame_dfs_v_pre_wprune.py`; 8 under `hstage_stream_v_pre_fastconv.py` and `frame_dfs_v_pre_wprune.py`;
9 under `hstage_stream_v_pre_telemetry.py` and the final core; 2 (lattice 149, 27/09) before the first wrapper backup. This dating
is an INFERENCE (it assumes that the record time and the file times are the same clock and that every change was preceded by a
backup); it is not a recorded version.
