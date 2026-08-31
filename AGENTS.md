# AGENTS.md

## Project Overview

Django 4.0.5 web application for managing sports races, participants, clubs, and trophies. Czech language throughout (models, views, templates).

## Quick Start

```bash
# Activate virtual environment
activate.bat

# Run development server
runserver.bat
# or manually:
_virtenv\Scripts\python.exe manage.py runserver 0.0.0.0:8085
```

## Commands

```bash
# Run migrations
_virtenv\Scripts\python.exe manage.py migrate

# Lint Python (errors only)
pylint --load-plugins=pylint_django --django-settings-module=hanes.settings

# Lint templates
djlint templates/
```

## Project Structure

- `hanes/` - Main Django project (settings, urls, middleware, mixins)
- `zavody/` - Races: Sport, Zavod, Rocnik, Kategorie models
- `zavodnici/` - Racers: Zavodnik model (links Clovek to Rocnik)
- `lide/` - People: Clovek, Clenstvi, Stat models
- `kluby/` - Clubs: Klub model
- `pohary/` - Trophies: Pohar, KategoriePoharu, BodoveHodnoceni models
- `plugins/django_wysiwyg/` - WYSIWYG editor plugin
- `templates/` - HTML templates
- `static/` - Semantic UI, jQuery UI assets

## Database

SQLite (`db.sql`). Imported from git via `_hanes_update.bat` which preserves the database file across pulls.

## Key Conventions

- **Slugs**: Auto-generated from names on save. `_get_sorting_slug()` in `lide/models.py` handles diacritics for sorting.
- **AJAX Forms**: Use `AjaxFormMixin` in `hanes/mixins.py` for modal form submissions.
- **Gender detection**: `Clovek.save()` auto-detects gender from surname if not provided.
- **View permissions**: `get_absolute_url()` switches between detail/update views based on `user.is_active`.

## Git Hooks

Post-commit and post-merge hooks write current git SHA and commit message to:
- `templates/git_sha.txt`
- `templates/git_msg.txt`

## Linting Config

- `.pylintrc`: Uses `pylint_django` plugin, errors-only mode
- `.djlintrc`: Ignores T002, H006, H020, H023, H021, H031, H037; formats CSS/JS/attributes

## Notes

- Windows-only development (`.bat` scripts, backslashes in paths)
- `TEMPLATE_DEBUG` setting toggles Django Debug Toolbar
- `SERVER_LOCAL.bat` runs on port 80; `runserver.bat` runs on port 8085
