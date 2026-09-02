# Workflows GitHub Actions

## `sandpaper-main.yaml`

Construit le site avec sandpaper et le publie sur la branche `gh-pages`. Il
appelle les actions maintenues par The Carpentries
(`carpentries/actions/setup-sandpaper`, `carpentries/actions/setup-lesson-deps`),
si bien qu'il suit automatiquement les évolutions du Workbench.

## `verifier-code.yaml`

Contrôle propre à cette leçon : régénère `data/` puis exécute tous les blocs de
code des épisodes, sous Ubuntu (outils GNU) **et** sous macOS (outils BSD). Ce
n'est pas un workflow Carpentries ; il garantit que le contenu enseigné reste
exécutable et portable.

## Compléter avec le jeu officiel du Workbench

Ce dépôt ne contient **pas** l'intégralité du jeu de workflows officiel des
Carpentries : manquent notamment les workflows d'aperçu des *pull requests*
(`pr-receive`, `pr-comment`, `pr-close-signal`, `pr-post-remove-branch`,
`pr-preflight`), de mise à jour du cache de paquets (`update-cache`) et
d'auto-mise à jour des workflows (`update-workflows`).

Pour les installer dans leur version courante — c'est la seule manière correcte
de les obtenir, puisqu'ils sont maintenus en amont —, depuis R à la racine du
dépôt :

```r
sandpaper::update_github_workflows()
```

À faire **avant** de proposer la leçon à The Carpentries Incubator : l'aperçu
automatique des *pull requests* est ce qui rend les contributions externes
confortables.
