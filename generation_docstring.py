# generation_docstring.py
import ast
import os
import sys

def extract_docstrings(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    
    doc = []
    if ast.get_docstring(tree):
        doc.append(f"# Documentation pour {file_path}\n")
        doc.append(ast.get_docstring(tree) + "\n")
    
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            doc.append(f"## Fonction: {node.name}\n")
            if ast.get_docstring(node):
                doc.append(ast.get_docstring(node) + "\n")
    
    return "\n".join(doc)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Usage : python generation_docstring.py <fichier.py>")
        sys.exit(1)

    file = sys.argv[1]
    output = f"DOC_{os.path.basename(file).replace('.py', '')}.md"
    markdown_doc = extract_docstrings(file)

    with open(output, "w", encoding="utf-8") as out:
        out.write(markdown_doc)

    print(f"📄 Documentation générée : {output}")
