
import ast
import os

def extract_docstrings(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    
    doc = []
    # Docstring du module
    if ast.get_docstring(tree):
        doc.append(f"# Documentation pour {file_path}\n")
        doc.append(ast.get_docstring(tree) + "\n")
    
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            doc.append(f"## Fonction: {node.name}\n")
            if ast.get_docstring(node):
                doc.append(ast.get_docstring(node) + "\n")
    
    return "\n".join(doc)

# Exemple d'utilisation
file = "boot.py"
markdown_doc = extract_docstrings(file)

with open("DOC_BOOT.md", "w", encoding="utf-8") as out:
    out.write(markdown_doc)

