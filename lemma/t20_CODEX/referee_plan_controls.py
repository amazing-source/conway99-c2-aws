"""Bounded negative controls for T20's plan-following contract, no search replay."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import traceback
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
R2 = ROOT/'lemma/t20_R2'
IV = ROOT/'lemma/t20_R3_I/in_verify.py'


def main():
    records = []
    with tempfile.TemporaryDirectory(prefix='plan_controls_',dir=HERE) as temp:
        task_dir = Path(temp).resolve()
        assert task_dir.parent == HERE
        for name,content,expected in [('invalid_unit','0 99 99 0 0\n','AssertionError: plan out of step (unit)'),
                                      ('truncated','','StopIteration')]:
            plan = task_dir/(name+'.plan')
            plan.write_text(content)
            tag = task_dir/name
            cmd = [sys.executable,str(R2/'run_engv2.py'),'III.1','0','1','10','3',str(tag),'setwise','plan='+str(plan)]
            run = subprocess.run(cmd,text=True,capture_output=True,timeout=30)
            assert run.returncode != 0 and expected in run.stderr,run.stderr
            assert not Path(str(tag)+'_0of1.json').exists()
            records.append({'engine':'engv2','case':'III.1','control':name,'returncode':run.returncode,
                            'error':run.stderr.strip().splitlines()[-1],'no_result_json':True})
    # This script has an unconditional CLI dispatcher. Load its unchanged
    # definitions only, preserving original filenames and line numbers.
    source = IV.read_text()
    prefix, dispatcher = source.split('\nif sys.argv[1] == "bases":',1)
    assert dispatcher and 'def follow(' in prefix
    iv = types.ModuleType('referee_iv')
    iv.__file__ = str(IV)
    exec(compile(prefix,str(IV),'exec'),iv.__dict__)
    pin = 'b960cd136b:s1z/s1z_I0_421_t0.json'
    raw = subprocess.check_output(['git','-c','safe.directory='+str(ROOT).replace('\\','/'),'show',pin],cwd=ROOT)
    s = json.loads(raw)
    B = iv.load_B(s['graph'])
    A21 = iv.support21(B)
    defi = iv.deficient(B)
    ztype = tuple(tuple(t) for t in s['ztype'])
    for name,plan,expected in [('invalid_unit',[[0,99,99,0,0]],AssertionError),('truncated',[],StopIteration)]:
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                iv.follow(B,A21,defi,s['bases'][0],plan,ztype)
        except expected as exc:
            frame = traceback.extract_tb(exc.__traceback__)[-1]
            assert Path(frame.filename) == IV and frame.name == 'dfs'
            assert frame.line == ('assert U0 in remaining' if name=='invalid_unit' else 'pl = next(plan)')
            records.append({'engine':'in_verify','case':'I.0/n3=2/421','control':name,
                            'error':type(exc).__name__,'source_line':frame.lineno,'source_statement':frame.line})
        else:
            raise AssertionError('malformed plan returned normally')
    sources = [Path(__file__),R2/'engv2.py',R2/'run_engv2.py',R2/'cases.py',IV]
    report = {'controls':records,'all_four_rejected_before_candidate_generation':True,
              'route_B_base_source':pin,'route_B_source_sha256':hashlib.sha256(raw).hexdigest(),
              'source_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
    HERE.joinpath('referee_plan_controls.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
