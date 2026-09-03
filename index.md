---
site: sandpaper::sandpaper_site
---

Cette formation apprend à **travailler en ligne de commande** — dans un shell
Bash — pour manipuler des données de biologie : séquences, annotations,
alignements, variants, tables de comptages.

Elle ne suppose **aucune connaissance préalable** du terminal. On part de
« comment savoir où je suis dans l'ordinateur » et l'on arrive, au bout des
20 heures, à écrire un script qui traite six échantillons de séquençage sans
intervention manuelle, en journalisant ce qu'il fait.

::::::::::::::::::::::::::::::::::::::::::  prereq

## À qui s'adresse cette formation ?

À toute personne qui produit ou reçoit des données de séquençage et qui n'a
jamais — ou presque jamais — utilisé de terminal : étudiantes et étudiants de
master, doctorants, techniciennes et techniciens de plateforme, chercheuses et
chercheurs en reconversion vers l'analyse de données.

**Prérequis techniques** : savoir utiliser un ordinateur (créer un dossier,
retrouver un fichier) et disposer d'une machine sur laquelle installer un
terminal. Voir la page [Installation et configuration](learners/setup.md).

**Prérequis en biologie** : aucun formalisme particulier. Il est utile de savoir
ce qu'est une séquence d'ADN et ce qu'est un gène ; le vocabulaire des formats
de fichiers est introduit dans la formation.

::::::::::::::::::::::::::::::::::::::::::::::::::

## Pourquoi la ligne de commande ?

Un fichier de séquençage brut contient couramment plusieurs dizaines de
millions de lignes. Aucun tableur ne l'ouvre. Les outils de bioinformatique
— aligneurs, appelants de variants, quantificateurs — n'ont pour la plupart pas
d'interface graphique : ils s'appellent depuis un terminal. Et les calculs
sérieux se font sur des serveurs distants, auxquels on accède justement par un
terminal.

Apprendre Bash, ce n'est donc pas apprendre un outil de plus : c'est apprendre
la langue dans laquelle la bioinformatique se pratique.

## Organisation

La formation est découpée en **21 épisodes** répartis sur **cinq journées de
4 heures**. Chaque épisode alterne démonstration guidée et exercices sur un jeu
de données commun, fourni au début de la formation.

| Journée | Thème | Épisodes |
|---|---|---|
| 1 | Prendre pied dans le shell : se déplacer, manipuler des fichiers, les lire | 1 à 4 |
| 2 | Les formats de la bioinformatique, les tubes, `grep`, la boîte à outils tabulaire | 5 à 8 |
| 3 | `awk` et `sed` : extraire, calculer, réécrire | 9 à 12 |
| 4 | Passer du one-liner au script : arguments, boucles, tests, quoting | 13 à 16 |
| 5 | Automatiser sur une feuille d'échantillons, projet final, hygiène de projet | 17 à 21 |

Un [aide-mémoire](learners/aide-memoire.md) imprimable et une page de
[dépannage](learners/depannage.md) accompagnent les épisodes.

## Ce que cette formation ne couvre pas

Volontairement : les conteneurs (Docker, Apptainer), les gestionnaires de
pipelines (Nextflow, Snakemake), Git et le travail collaboratif, la
soumission de tâches sur un cluster, et la production de rapports
reproductibles. Ces sujets font l'objet d'une **seconde formation**, dont
Bash est le prérequis. Le dernier épisode en donne l'aperçu.

::::::::::::::::::::::::::::::::::::::::::  callout

## Conventions typographiques

Les blocs de commandes se lisent ainsi :

```bash
ls data/
```

```output
alignements  brut_desordre  genome  journaux  proteines  reads  regions  tables  variants
```

Le premier bloc est **ce que vous tapez** ; le second est **ce que la machine
répond**. L'invite (`$` ou `%`) n'est jamais recopiée : elle est déjà à l'écran.

::::::::::::::::::::::::::::::::::::::::::::::::::
