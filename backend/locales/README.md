# Translation catalogues

`backend/i18n.py` remains the public compatibility facade: routes and templates keep using `t()`, `get_lang()`, and the formatting helpers unchanged.

New or modified translation keys belong to a domain catalogue in this folder. Current catalogues are:

- `budgets.py`: the Budgets module.
- `management.py`: Management and optional-module controls.

The remaining legacy catalogue stays in `backend/i18n.py` while it is migrated incrementally. Domain catalogues override legacy keys, which allows a module to move independently without changing visible text or translation call sites.
