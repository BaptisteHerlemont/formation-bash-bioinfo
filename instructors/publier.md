---
title: Publier et diffuser la formation
---

Trois canaux, dans cet ordre : le site GitHub Pages (indispensable), l'archive
Zenodo (pour citer et figer une version), la proposition à l'Incubator des
Carpentries (pour la visibilité et la relecture par des pairs).

## 1. Le site GitHub Pages

Le Workbench ne publie **pas** le site depuis vos fichiers sources : un workflow
construit le HTML dans un conteneur, puis le pousse dans deux branches
orphelines — `md-outputs` (markdown intermédiaire) et `gh-pages` (le site).
C'est `gh-pages` que GitHub Pages doit servir.

### Préparer le dépôt (une commande)

```bash
sh scripts/preparer_publication.sh MON-COMPTE-GITHUB moi@exemple.fr "Prénom Nom"
```

Le script renseigne le compte, l'adresse de contact et l'auteur dans
`config.yaml`, `CITATION.cff` et `.zenodo.json`, vérifie qu'aucune valeur à
personnaliser ne subsiste, et relance le contrôle des blocs de code. Il est
idempotent.

### Pousser et publier

```bash
git init -b main
git add .
git commit -m "Formation Bash pour la bioinformatique, version initiale"
git remote add origin https://github.com/MON-COMPTE-GITHUB/formation-bash-bioinfo.git
git push -u origin main
```

1. Dépôt **public** (Pages sur dépôt privé demande un compte payant).
2. Onglet **Actions** : le workflow *01 Maintain: Build and Deploy Site* démarre
   au premier push. Il tourne dans un conteneur préconstruit, donc en 2 à
   4 minutes, et se termine en créant `md-outputs` et `gh-pages`.
3. **Settings → Pages → Build and deployment → Source : Deploy from a branch**,
   branche `gh-pages`, dossier `/ (root)`, *Save*.
4. Deux minutes plus tard, le site est sur
   `https://MON-COMPTE-GITHUB.github.io/formation-bash-bioinfo/`.

Si `gh-pages` n'apparaît pas dans le menu déroulant, le workflow n'a pas
terminé — ou il a échoué : lire son journal dans *Actions* avant toute autre
hypothèse. Si l'étape de déploiement se plaint de droits d'écriture, vérifier
**Settings → Actions → General → Workflow permissions : Read and write**.

Cette leçon ne contient aucun code R exécuté à la construction : rien d'autre à
configurer, ni cache de paquets, ni variable de dépôt.

### Si la première construction échoue

Deux échecs sont attendus au premier push, et tous deux sont déjà corrigés dans
ce dépôt. Ils sont documentés ici parce qu'ils reviendront le jour où vous
créerez une autre leçon.

**« Record container version used » en échec, « Build Full Site » sauté.** Avant
de construire, le workflow veut inscrire dans `.github/workbench-docker-version.txt`
la version du conteneur utilisée — en ouvrant une *pull request*, ce que les
réglages par défaut d'un dépôt neuf interdisent. Deux remèdes, à appliquer
plutôt tous les deux :

- créer le fichier soi-même, ce qui rend l'étape inutile (c'est fait ici :
  il contient `v0.2.8`) ;
- **Settings → Actions → General → Workflow permissions** : cocher *Read and
  write permissions* **et** *Allow GitHub Actions to create and approve pull
  requests*. Sans cela, l'étape échouera de nouveau à chaque montée de version
  du conteneur.

**Vérification des blocs de code en échec sur `ubuntu-latest`, réussie sur
`macos-latest`.** C'est le cas intéressant : le contrôle tourne sur les deux
systèmes précisément pour attraper les divergences entre outils BSD et GNU, et
il en a trouvé quatre au premier essai. Elles sont corrigées, et chacune est
devenue une remarque de portabilité dans l'épisode concerné :

| Épisode | Divergence | Correction |
|---|---|---|
| 07 | `\t` dans un motif `grep -E` : tabulation sur macOS, lettre `t` sur GNU | une vraie tabulation via `$(printf '\t')` |
| 10 (deux fois) | l'ordre de `for (clé in tableau)` en awk n'est pas spécifié | `| sort` explicite en sortie |
| 15 | `wc -l` aligne son résultat en colonnes sur macOS, pas sur GNU | `| tr -d ' '` avant usage |
| 19 | le chemin rendu par `command -v` dépend de la machine | bloc exécuté sans comparaison de sortie |

La morale, à retenir pour la suite : ne jamais valider une leçon sur son seul
portable. La matrice à deux systèmes du workflow `verifier-code.yaml` coûte
30 secondes par push et remplace une classe entière signalant que « ça ne donne
pas ça chez moi ».

### Ce que contient `.github/workflows/`

Le jeu officiel du Workbench, version `v1.0.2`, tel que produit par
`sandpaper::update_github_workflows()` :

| Fichier | Rôle |
|---|---|
| `docker_build_deploy.yaml` | construit le site et le pousse dans `gh-pages` |
| `docker_pr_receive.yaml`, `pr-*.yaml` | prévisualisation et commentaire automatique sur les *pull requests* |
| `docker_apply_cache.yaml`, `update-cache.yaml` | cache des paquets R — inertes ici, la leçon n'en a pas |
| `update-workflows.yaml` | met à jour ces fichiers eux-mêmes |
| `verifier-code.yaml` | **propre à cette formation** : rejoue tous les blocs de code des épisodes |
| `README.md` | documentation officielle du jeu de workflows |

Pour les remettre à niveau plus tard, lancer *04 Maintain: Update Workflow
Files* depuis l'onglet Actions, ou en local `sandpaper::update_github_workflows()`.

### Vérifier le rendu français

`config.yaml` porte `lang: fr` : les éléments d'interface produits par le moteur
— Objectifs, Défi, Solution, Points clés, navigation — s'affichent en français,
la traduction existant en amont dans sandpaper. Au premier coup d'œil sur le
site, contrôler dans l'ordre :

- l'entête (titre, sous-titre `carpentry_description`, habillage Incubator) ;
- l'ordre des 21 épisodes dans la barre latérale, et les durées affichées ;
- la page **Installation**, celle que les apprenants liront avant de venir ;
- le rendu des blocs `error`, qui doivent se distinguer visuellement des blocs
  `output` : c'est ce qui permet de reconnaître un message d'erreur enseigné ;
- la figure de progression dans le README de la leçon.

### Prévisualiser sans passer par GitHub

Avec R installé, le site se construit en local et se recharge à chaque
enregistrement :

```r
install.packages("sandpaper", repos = c("https://carpentries.r-universe.dev/",
                                        getOption("repos")))
sandpaper::serve()
```

C'est la boucle de travail pour la relecture ; le validateur signale au passage
les défauts de structure (titre manquant, bloc mal fermé, lien cassé).

## 2. Un DOI Zenodo

Le fichier `.zenodo.json` décrit déjà la formation (titre, licence, mots-clés,
langue `fra`).

1. Se connecter à [Zenodo](https://zenodo.org) avec le compte GitHub, section
   **GitHub**, et activer le dépôt.
2. Créer une *release* GitHub (par exemple `v1.0.0`). Zenodo l'archive et
   attribue un DOI.
3. Reporter le DOI obtenu dans `CITATION.cff` (champ `doi`) et dans le `README`,
   puis créer une release `v1.0.1` : le DOI « toutes versions » reste stable.

L'archive Zenodo doit contenir `data/` : c'est ce qui rend la formation
reproductible dix ans plus tard, indépendamment du dépôt Git.

## 3. La proposition à l'Incubator

L'[Incubator](https://carpentries-incubator.org/) héberge les leçons en
développement. La démarche : ouvrir une *issue* dans
`carpentries-incubator/proposals` décrivant la leçon, le public visé et l'état
d'avancement ; l'équipe transfère ensuite le dépôt dans l'organisation, ce qui
lui donne visibilité et relecteurs.

À préparer avant de proposer :

- un enseignement réel de la formation, au moins une fois, et les corrections
  qui en découlent — c'est le retour qui compte le plus ;
- le site en ligne et fonctionnel ;
- le code de conduite en place (`CODE_OF_CONDUCT.md`) ;
- une phrase honnête sur l'état : « enseignée une fois, en français, retours
  intégrés » vaut mieux qu'une promesse.

La leçon étant en français, préciser dans la proposition que la langue est un
choix assumé (public francophone insuffisamment servi) et non un obstacle à la
traduction ultérieure. Le guide de style de `instructors/guide-de-style.md`
facilite une traduction anglaise : la structure et les blocs de code n'ont pas à
changer.

## 4. Après la première session

Ouvrir une *issue* par difficulté observée, le jour même, pendant que le
souvenir est frais : le nom de l'épisode, la commande, ce que l'apprenant a
compris. C'est le seul matériau qui améliore une formation.
