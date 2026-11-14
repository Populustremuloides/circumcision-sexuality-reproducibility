"""Check active imports, documentation links, and documentation file targets."""
import ast,re
from pathlib import Path
from src.specification import ROOT

def main():
    checked=0
    for directory in ['src','analyses','validation','scripts']:
        for path in (ROOT/directory).rglob('*.py'):
            for node in ast.walk(ast.parse(path.read_text())):
                imports=[a.name for a in node.names] if isinstance(node,ast.Import) else [node.module or ''] if isinstance(node,ast.ImportFrom) else []
                assert not any('bayesian' in name for name in imports),path
            checked+=1
    documents=[ROOT/'README.md']
    for directory in ['docs','analyses','figures']:documents.extend((ROOT/directory).rglob('*.md'))
    for path in documents:
        base=path.parent
        if path.name=='readme_template.md':base=ROOT
        if path.name=='figures_template.md':base=ROOT/'figures'
        for link in re.findall(r'\]\(([^)]+)\)',path.read_text()):
            if ':' in link or link.startswith('#'):continue
            target=link.split('#')[0]
            assert not target or (base/target).exists(),(path,link)
    print(f'{checked} active Python modules have no Bayesian imports; local documentation links resolve.')
if __name__=='__main__':main()
