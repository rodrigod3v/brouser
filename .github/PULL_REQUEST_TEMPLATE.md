## O que muda

<!-- resumo curto -->

## Tipo

<!-- feat | fix | refactor | docs | test | chore | ci -->

## Checklist (CI bloqueia se faltar)

- [ ] `ruff check .` limpo
- [ ] `ruff format --check .` limpo
- [ ] `mypy` limpo
- [ ] `pytest -m "not integration"` verde
- [ ] Titulo do PR em conventional commit (ex.: `feat: gate Jev em acoes sensiveis`)
- [ ] Sem segredos/keys no diff
- [ ] Mudanca em camada respeitou regras de `docs/ARCHITECTURE.md`
