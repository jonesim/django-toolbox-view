# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**django-toolbox-view** (PyPI: `django-toolbox-view`, package dir `toolbox_view/`) provides a staff-only Django view that discovers functions defined in a `toolbox` module of each installed app and presents them as runnable buttons, with optional confirmation modals; functions can optionally run as Celery tasks. `django_examples/` is the demo project.

The package has almost no UI of its own: one page template (`toolbox/base.html`) rendering `{{ tool_box_buttons }}`; buttons are built with `django_menus.HtmlMenu(template='buttons')` and the confirm modal comes from `django_modals.messages`. Depends on `django-nested-modals` and `django-tab-menus`.

## jQuery removal & Bootstrap 5 support (July 2026)

Part of a cross-package migration (summary in `X:\CLAUDE.md`). This package has **zero jQuery** of its own and exactly **one** Bootstrap-4-only site:

- `toolbox_view/views.py:46` — `css_classes=f'mr-1 mb-1 btn btn-...'`: `mr-1` → `me-1` for BS5 (`mb-1` is fine in both).

Everything else (modal chrome, button/menu templates, `lib_include` bundles in `base.html`) is upstream in django-nested-modals / django-tab-menus / django-ajax-helpers — when those ship their migrated releases, update the dependency pins in `requirements.txt` (currently pins `django-nested-modals==0.0.25` — `pyproject.toml` needs `>=0.0.24` for `ConfirmAjaxMethod.get_html` — `django-ajax-helpers==0.0.22`, `django-tab-menus==0.0.16`, and a stale `django-crispy-forms==1.12.0` that can be dropped once the new django-nested-modals is pinned).

## Releasing

Full process in `X:\CLAUDE.md` → "Releasing a package". Summary: once-over the diff since the last release tag (`git fetch --tags origin` first), bump `version` in `pyproject.toml`, commit, run `X:\release.bat` — it tags `v<version>` and pushes, and `.github/workflows/publish.yml` publishes to PyPI via trusted publishing. First Actions release: confirm the GitHub `pypi` environment and the PyPI trusted publisher for `django-toolbox-view` are configured.
