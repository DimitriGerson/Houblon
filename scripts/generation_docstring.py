
import ast
import os

def extract_docstrings(file_path):
    """Extrait les docstrings d'un fichier Python (module, classes, fonctions)."""
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    doc = []

    # Docstring du module
    module_doc = ast.get_docstring(tree)
    if module_doc:
        doc.append(f"### Description du module\n{module_doc}\n")

    for node in tree.body:
        # Classes
        if isinstance(node, ast.ClassDef):
            doc.append(f"## Classe `{node.name}`\n")
            class_doc = ast.get_docstring(node)
            if class_doc:
                doc.append(class_doc + "\n")

            # Méthodes
            for subnode in node.body:
                if isinstance(subnode, ast.FunctionDef):
                    doc.append(f"### Méthode `{subnode.name}`\n")
                    method_doc = ast.get_docstring(subnode)
                    if method_doc:
                        doc.append(method_doc + "\n")

        # Fonctions globales
        elif isinstance(node, ast.FunctionDef):
            doc.append(f"## Fonction `{node.name}`\n")
            func_doc = ast.get_docstring(node)
            if func_doc:
                doc.append(func_doc + "\n")

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
    markdown_doc = generate_full_doc("src/")  # ⚠️ Vérifiez que vos .py sont bien dans src/
    with open(output, "w", encoding="utf-8") as out:
        out.write(markdown_doc)
