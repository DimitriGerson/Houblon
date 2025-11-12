# tests/conftest.py

import os
import pytest

@pytest.fixture(autouse=True, scope="session")
def clean_after_tests():
    """
    Nettoie les fichiers temporaires (config.json, boot.log, etc.)
    après la fin de tous les tests.
    """
    yield # <-- Laisse d'abord les tests s'exécuter

    # --- Nettoyage après tous les tests ---
    for f in ["config.json", "boot.log"]:
        path = os.path.join(os.path.dirname(__file__), "..", f)
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            try:
                os.remove(abs_path)
                print(f"[CLEANUP] Supprimé : {abs_path}")
            except Exception as e:
                print(f"[CLEANUP] Impossible de supprimer {abs_path}: {e}")
