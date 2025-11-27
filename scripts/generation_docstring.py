
import ast
import os

def extract_docstrings(file_path):
    """Extrait les docstrings d'un fichier Python."""
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    doc = []
    if ast.get_docstring(tree):
        doc.append(ast.get_docstring(tree) + "\n")

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            doc.append(f"### {node.name}\n")
            if ast.get_docstring(node):
                doc.append(ast.get_docstring(node) + "\n")

    return "\n".join(doc)

def generate_full_doc(root_dir="."):
    """Génère une documentation complète avec sommaire pour tout le projet."""
    all_docs = ["# 📚 Documentation du projet\n", "## Sommaire\n"]
    details = []

    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py") and "generation_docstring" not in file:
                path = os.path.join(root, file)
                section_title = f"## Fichier: {file}"
                anchor = section_title.lower().replace(" ", "-").replace(":", "")
                all_docs.append(f"- #{anchor}")
                content = extract_docstrings(path)
                details.append(f"{section_title}\n\n{content}\n")

    return "\n".join(all_docs + ["\n---\n"] + details)

if __name__ == "__main__":
    output = "DOC_PROJET.md"
    markdown_doc = generate_full_doc("src/")
    with open(output, "w", encoding="utf-8") as out:
        out.write(markdown_doc)
    print(f"📄 Documentation complète générée : {output}")
