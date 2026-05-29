# Changelog

## [0.5.2](https://github.com/niklastypes/kindling/compare/v0.5.1...v0.5.2) (2026-05-29)


### Documentation

* add guidance for evolving into full-stack application & productionalization ([b95cfda](https://github.com/niklastypes/kindling/commit/b95cfdaff32ed12234445d84509dad78bafbdb5e))
* add testing strategy section and fix single-app paths ([0097e56](https://github.com/niklastypes/kindling/commit/0097e56bd70d41c435ae288524e6d9e313255ea4))

## [0.5.1](https://github.com/niklastypes/kindling/compare/v0.5.0...v0.5.1) (2026-05-22)


### Bug Fixes

* tag scaffold commit as v0.1.0 and document GitHub publish flow ([e7e7c78](https://github.com/niklastypes/kindling/commit/e7e7c7816a24015b640c6f876a90f4e7d759ff46)), closes [#5](https://github.com/niklastypes/kindling/issues/5)

## [0.5.0](https://github.com/niklastypes/kindling/compare/v0.4.0...v0.5.0) (2026-05-22)


### Features

* add check-ast and pre-commit-update hooks to template ([75618b5](https://github.com/niklastypes/kindling/commit/75618b51fcebb2026020059a369530510870d34e))
* add kebab-case validation to project_name ([6e91ec6](https://github.com/niklastypes/kindling/commit/6e91ec6a201f0401c706c0a5476083b4722cc81a))


### Documentation

* add check-ast and pre-commit-update to docs ([f2eb6da](https://github.com/niklastypes/kindling/commit/f2eb6da06b4f90ea006f05a71896248014790bc4))
* rewrite CLAUDE.md as operational reference ([2b4d261](https://github.com/niklastypes/kindling/commit/2b4d2619730b7ccfde7eb92e40bc997046c23e4a))
* update CLAUDE.md and README.md for template improvements ([aad29f6](https://github.com/niklastypes/kindling/commit/aad29f64fbf0daa1092d289495ca69f047281798))

## [0.4.0](https://github.com/niklastypes/kindling/compare/v0.3.0...v0.4.0) (2026-05-21)


### Features

* protect LICENSE and .gitignore from being overwritten on copier update ([2d6e0f0](https://github.com/niklastypes/kindling/commit/2d6e0f01f81a22ff17ca6a84c9ce1ff6741d83ff))


### Documentation

* refresh README and CLAUDE.md to reflect final state ([b1993fc](https://github.com/niklastypes/kindling/commit/b1993fce0478983bc748f8b8f541cb3dd8be9500))

## [0.3.0](https://github.com/niklastypes/kindling/compare/v0.2.0...v0.3.0) (2026-05-21)


### Features

* add AGENTS.md template ([56fc691](https://github.com/niklastypes/kindling/commit/56fc69110cd5ecfd9ff3aa5e688e2ecaeabf31e8))
* add github_username question and project URLs to pyproject.toml ([2140798](https://github.com/niklastypes/kindling/commit/2140798156dca77f9574c617aff0870ac33f3b1d))
* add README template ([571b205](https://github.com/niklastypes/kindling/commit/571b2054c16da9302a619196e97a4ecd2ea8db47))
* add template verification tests ([ad88deb](https://github.com/niklastypes/kindling/commit/ad88debe08804c3202a67c94f610b03d108d7360))
* auto git init and first commit on project generation ([64e2e6d](https://github.com/niklastypes/kindling/commit/64e2e6d0869a77bd8183f2e2cfe281329bfe31eb))
* restore readme field in pyproject.toml now that README template exists ([97d3216](https://github.com/niklastypes/kindling/commit/97d32164bb06df4613b7d05f4fb8adffe3c8269a))


### Documentation

* update README and CLAUDE.md to reflect current state ([d46aa52](https://github.com/niklastypes/kindling/commit/d46aa524c44bfd476af5d418852beff5a5fbcc61))

## [0.2.0](https://github.com/niklastypes/kindling/compare/v0.1.0...v0.2.0) (2026-05-21)


### Features

* add CI workflow template ([88e30ec](https://github.com/niklastypes/kindling/commit/88e30ecb94cb9daea01faa87ead1751f51147369))
* add pre-commit config template ([54b4217](https://github.com/niklastypes/kindling/commit/54b421788ffba854a5a5dbad5635a00887f1050f))
* add release workflow and release-please manifest templates ([289ee02](https://github.com/niklastypes/kindling/commit/289ee022845ccb7608292c24a4294e9d24b30346))
* add smoke test template so CI always has at least one test ([9881944](https://github.com/niklastypes/kindling/commit/9881944cdb68ae5622ff52b00742ee6a891aabe7))

## [0.1.0](https://github.com/niklastypes/kindling/commits/v0.1.0) (2026-05-21)


### Features

* add LICENSE template ([90fb8c7](https://github.com/niklastypes/kindling/commit/90fb8c78795592cae3c0e06c1a3e539f61b630f5))
* add pyproject.toml, python-version, and src layout templates ([6951591](https://github.com/niklastypes/kindling/commit/6951591f3bb695a5fe9ace7cc3806866bff5982b))
* add release-please and copier-answers templates ([545d08b](https://github.com/niklastypes/kindling/commit/545d08b39baabdbcc39f8b0c62736361bda7b2f9))
* add renovate.json template ([a99c1d4](https://github.com/niklastypes/kindling/commit/a99c1d4537097e2506a913b2b03da2257a8bc056))


### Bug Fixes

* remove readme field until README template exists, drop workflows .gitkeep ([7707fe9](https://github.com/niklastypes/kindling/commit/7707fe9b4433907d1ac924b2ca15a4f9e107d63b))


### Miscellaneous Chores

* add lean .gitignore and .env.example templates ([4f1013b](https://github.com/niklastypes/kindling/commit/4f1013b7d0235438b1d648c256834f4e2f23ec22))
* add release-please manifest at v0.1.0 ([8e05195](https://github.com/niklastypes/kindling/commit/8e05195c629f5235a080357a75355890f64453fd))
* initialize copier.yml and project directory skeleton ([2e4ed01](https://github.com/niklastypes/kindling/commit/2e4ed0173c9eae28b6786460d32380303b9f0cca))
