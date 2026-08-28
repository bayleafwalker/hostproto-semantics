# Agent guidance

- Schemas in `schemas/` are the product. Docs explain them; code only validates them.
- A schema change needs: the example(s) updated, a negative test for any new invalidation rule, and an entry in `docs/DECISIONS.md` if it changes a semantic.
- Do not add a scheduler, task store, discovery mechanism, or transport here. Those belong to MCP, A2A, or the domain runtime (`docs/RESPONSIBILITY_SPLIT.md`). Adding one is a kill-gate event, not a feature.
- Claims about MCP or A2A features must cite the spec section and its revision date. Unverified claims are listed in `docs/PLAN.md` step 0 until checked.
- After any schema change run `PYTHONPATH=src python3 -m hostproto.emit_bundles`; `bundled/` is committed and adapters pin it by digest.
- Run `PYTHONPATH=src python3 -m unittest discover -s tests` before committing.
