"""Apply BRC navigation, material surfaces and BFS dual learning controls."""
from pathlib import Path
import sys

from apply import ROOT, apply as learning, extend_manifest
from resume.apply import apply as resume
from material.access import apply as materials
from chrome.chrome import apply as chrome
from documents.documents import apply as documents
from terms.terms import apply as terms
from feedback.feedback import apply as feedback

def package_paths():
    base=ROOT/'Fachbereiche/BFSdual'
    return [*sorted(base.glob('LF0[123]/LS*')),base/'LF06/Buero/LS09']

def install(folder):
    resume(folder)
    chrome(folder,ROOT/'Fachbereiche/BRC/LG01/LS04')
    terms(folder)
    feedback(folder)
    num=documents(folder,ROOT/'Materialvorlagen')
    materials(folder)
    extend_manifest(folder,['assets/bfs-material-access.js','assets/bfs-materials-data.js','assets/bfs-material-access.css'])
    learning(folder)
    print(folder.parent.name,folder.name,num,'Materialansichten',flush=True)

if __name__=='__main__':
    for folder in ([Path(p) for p in sys.argv[1:]] or package_paths()):
        install(folder)
