import shutil, sys
shutil.copytree(sys.argv[1], sys.argv[2], ignore=shutil.ignore_patterns(".venv", ".git", "__pycache__", ".claude"), dirs_exist_ok=True)
