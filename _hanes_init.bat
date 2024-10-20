git init
git remote add -f hanes https://github.com/gumish/hanes.git
git config core.sparsecheckout true

echo hanes >> .git/info/sparse-checkout
echo kluby >> .git/info/sparse-checkout
echo lide >> .git/info/sparse-checkout
echo plugins >> .git/info/sparse-checkout
echo pohary >> .git/info/sparse-checkout
echo static >> .git/info/sparse-checkout
echo templates >> .git/info/sparse-checkout
echo zavodnici >> .git/info/sparse-checkout
echo zavody >> .git/info/sparse-checkout
echo activate.bat >> .git/info/sparse-checkout
echo runserver.bat >> .git/info/sparse-checkout
echo SERVER_LOCAL.bat >> .git/info/sparse-checkout
echo manage.py >> .git/info/sparse-checkout
echo requirements.txt >> .git/info/sparse-checkout

echo #!/bin/sh >> .git\hooks\post-merge
echo git show --no-patch --format=%%h ^> templates/git_sha.txt >> .git\hooks\post-merge
echo git show --no-patch --format=%%B ^> templates/git_msg.txt >> .git\hooks\post-merge
echo #!/bin/sh >> .git\hooks\post-commit
echo git show --no-patch --format=%%h ^> templates/git_sha.txt >> .git\hooks\post-commit
echo git show --no-patch --format=%%B ^> templates/git_msg.txt >> .git\hooks\post-commit


git pull hanes Import
python -m venv _virtenv
_virtenv\Scripts\pip install -r requirements.txt