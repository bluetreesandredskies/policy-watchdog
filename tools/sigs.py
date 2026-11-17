import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def sig(fn):
    ret = f' -> {ast.unparse(fn.returns)}' if fn.returns else ''
    prefix = 'async def' if isinstance(fn, ast.AsyncFunctionDef) else 'def'
    return f'{prefix} {fn.name}({ast.unparse(fn.args)}){ret}'


def main():
    skip = {Path(a).as_posix() for a in sys.argv[1:]}
    for path in sorted((ROOT / 'src').rglob('*.py')):
        rel = path.relative_to(ROOT).as_posix()
        if rel in skip:
            continue
        tree = ast.parse(path.read_text(encoding='utf-8'))
        lines = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                lines.append(sig(node))
            elif isinstance(node, ast.ClassDef):
                fields = [n.target.id for n in node.body
                          if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)]
                lines.append(f'class {node.name}' + (f' fields={fields}' if fields else ''))
                for sub in node.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)) and not sub.name.startswith('_'):
                        lines.append('    ' + sig(sub))
        if lines:
            print(f'# {rel}')
            print('\n'.join(lines))
            print()


main()
