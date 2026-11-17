import re
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOCK = re.compile(r'^FILE:[ \t]*(\S.*?)[ \t]*\n(`{3,})[^\n]*\n(.*?)\n\2[ \t]*$', re.M | re.S)
HEADER = re.compile(r'^FILE:[ \t]*(\S.*?)[ \t]*$', re.M)


def read_input(args):
    if args:
        return Path(args[0]).read_text(encoding='utf-8')
    import tkinter
    root = tkinter.Tk()
    root.withdraw()
    try:
        return root.clipboard_get()
    finally:
        root.destroy()


def main():
    dry = '--dry-run' in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    text = read_input(args).replace('\r\n', '\n')
    stamp = time.strftime('%Y%m%d-%H%M%S')
    done = []
    for name, _fence, body in BLOCK.findall(text):
        target = (ROOT / name).resolve()
        if ROOT not in target.parents or '.git' in target.parts or '.venv' in target.parts:
            print(f'SKIPPED (unsafe path): {name}')
            continue
        if target.exists() and not dry:
            backup = ROOT / '.unpack_backup' / stamp / name
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, backup)
        print(('WOULD WRITE ' if dry else 'WROTE ') + name)
        if not dry:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(body + '\n', encoding='utf-8', newline='\n')
        done.append(name)
    missing = [h for h in HEADER.findall(text) if h not in done]
    for name in missing:
        print(f'INCOMPLETE or unsafe, not written: {name}')
    if not done:
        print('No files found. Did you click Copy on the whole reply?')
    elif missing:
        print('Ask Claude: Continue from ' + missing[0])


main()
