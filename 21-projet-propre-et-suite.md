---
title: "Garder un projet propre, et la suite"
teaching: 10
exercises: 0
---

::::::::::::::::::::::::::::::::::::::::::  questions

- Comment organiser un projet pour que quelqu'un d'autre — ou moi-même dans six
  mois — puisse le comprendre ?
- Qu'est-ce qu'il ne faut jamais laisser traîner dans un projet ?
- Qu'apportera la seconde formation ?

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::: objectives

- Organiser un projet en répertoires `data/`, `scripts/`, `resultats/`,
  `docs/` et `journal/`.
- Protéger les données brutes en écriture avec `chmod a-w`.
- Rédiger un `README.md` minimal décrivant un projet.
- Identifier ce qui ne doit jamais rester dans un projet.
- Situer les sujets couverts par la seconde formation.

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::  prereq

Cet épisode suppose que vous avez suivi les 20 épisodes précédents, en
particulier l'épisode 3 (« les données brutes ne se modifient jamais ») et
l'épisode 20 (le projet final).

::::::::::::::::::::::::::::::::::::::::::::::::::

Vous venez de construire, à l'épisode précédent, un pipeline complet allant des
lectures brutes à une table de résultats. Cet épisode ne vous apprend plus de
commande : il vous propose une manière de ranger ce que vous avez construit
pour qu'il reste utilisable, et il vous indique où continuer.

## Une arborescence de projet

Un projet bioinformatique qui se relit bien suit toujours à peu près la même
forme. Reprenons le répertoire de travail et donnons-lui cette structure :

<!-- verif: ordre-libre -->
```bash
mkdir -p scripts resultats docs journal
ls -F
```

```output
_verif.sh
data/
docs/
journal/
resultats/
scripts/
```

Chaque répertoire a un rôle et un seul :

| Répertoire | Contenu | Règle |
|---|---|---|
| `data/` | Les données de départ | Jamais modifié, jamais écrit |
| `scripts/` | Les scripts qui produisent les résultats | Versionné mentalement, relu |
| `resultats/` | Tout ce qui est calculé | Peut être supprimé et régénéré |
| `docs/` | Notes de méthode, description des colonnes, figures | Texte, pas de code |
| `journal/` | Un compte rendu par jour ou par étape | S'accumule, ne se réécrit pas |
| `README.md` | Point d'entrée pour qui ouvre le projet | Un seul, à la racine |

La règle qui commande tout le reste, vue à l'épisode 3, tient en une phrase :
**les données brutes ne se modifient jamais.** Un script qui a besoin de
transformer une donnée écrit sa sortie dans `resultats/`, jamais dans `data/`.
Pour vous obliger vous-même à la respecter, retirez le droit d'écriture sur
`data/` dès le début d'un projet :

<!-- verif: exec-seulement -->
```bash
chmod a-w data/tables/echantillons.tsv
ls -l data/tables/echantillons.tsv
```

```output
-r--r--r--@ 1 baptisteherlemont  staff  392 Aug 31 22:37 data/tables/echantillons.tsv
```

Toute tentative d'écraser ce fichier par erreur — une redirection `>` tapée
sur le mauvais chemin, par exemple — échoue immédiatement au lieu de
silencieusement remplacer une donnée que vous ne pourrez pas régénérer :

<!-- verif: ignore -->
```bash
echo "test" > data/tables/echantillons.tsv
```

```error
bash: data/tables/echantillons.tsv: Permission denied
```

::: callout

## Rendre tout `data/` non modifiable d'un coup

Pour appliquer `chmod a-w` à l'ensemble d'un jeu de données plutôt qu'à un
seul fichier, l'épisode 18 vous a montré `find` et `-exec` :

```bash
find data -type f -exec chmod a-w {} +
```

Le jeu de données de cette formation reste, lui, protégé uniquement à titre de
démonstration ci-dessus : ne l'appliquez pas maintenant si vous comptez
continuer à vous en servir dans un autre exercice.

:::

## Conventions de nommage

Les noms de fichiers rencontrés dans `data/brut_desordre/` à l'épisode 16 —
espaces, majuscules incohérentes, parenthèses, doubles tirets — ne sont pas
seulement pénibles à taper : ils sont une source d'erreurs silencieuses dans
les scripts. Trois conventions suffisent pour ne plus jamais y revenir :

- pas d'espace dans un nom de fichier ni de répertoire, un tiret bas ou un
  tiret à la place ;
- un identifiant d'échantillon ou de gène toujours écrit de la même façon,
  d'un bout à l'autre du projet (`ech01`, pas tantôt `ech01` tantôt `Ech_01`) ;
- un nom de fichier de résultat qui indique ce qu'il contient et comment il a
  été obtenu, par exemple `resultats/comptages_filtres_dp10.tsv` plutôt que
  `resultats/final.tsv`.

## Tout dans un script, rien dans l'historique

L'historique du shell (`history`, vu à l'épisode 2) est une mémoire de travail,
pas une documentation. Il contient des essais, des commandes corrigées, des
fautes de frappe, et il disparaît avec le terminal. Une commande qui a produit
un résultat que vous gardez doit être copiée dans un script de `scripts/`, avec
un shebang et un commentaire qui explique pourquoi elle existe — c'est ce que
vous avez pratiqué depuis l'épisode 13. Le test est simple : si vous deviez
reproduire un résultat de `resultats/` dans six mois, l'historique du shell ne
vous y aiderait pas, un script le ferait.

## Un `README.md` minimal

Le `README.md` est le premier fichier que quelqu'un ouvre. Il répond à trois
questions : à quoi sert ce projet, comment reproduire les résultats, où
trouver quoi. En voici un exemple complet, à la mesure d'un petit projet :

<!-- verif-setup:
mkdir -p scripts resultats docs journal
cat > README.md <<'FIN'
# Comptage de gènes exprimés par condition

## Objectif

Filtrer la table de comptages `data/tables/comptages.tsv` pour ne garder que
les genes exprimes (comptage non nul dans au moins un echantillon), et
produire un resume par condition (temoin vs traite) a partir de
`data/tables/echantillons.tsv`.

## Reproduire les resultats

```
scripts/filtrer_comptages.sh
```

Le script lit `data/`, n'ecrit jamais dedans, et depose ses sorties dans
`resultats/`.

## Contenu

- `scripts/` : un script par etape, executable, commente.
- `resultats/` : tables produites par les scripts. Peut etre supprime et
  regenere.
- `docs/` : description des colonnes de sortie.
- `journal/` : un compte rendu par jour de travail.

## Donnees

Les donnees de depart sont dans `data/`, en lecture seule (`chmod a-w`). Voir
`data/README.md` pour leur origine.

## Auteur et date

Prenom Nom, projet demarre le 2024-09-17.
FIN
-->

<!-- verif: exec-seulement -->
```bash
cat README.md
```

```output
# Comptage de gènes exprimés par condition

## Objectif

Filtrer la table de comptages `data/tables/comptages.tsv` pour ne garder que
les genes exprimes (comptage non nul dans au moins un echantillon), et
produire un resume par condition (temoin vs traite) a partir de
`data/tables/echantillons.tsv`.

## Reproduire les resultats

```
scripts/filtrer_comptages.sh
```

Le script lit `data/`, n'ecrit jamais dedans, et depose ses sorties dans
`resultats/`.

## Contenu

- `scripts/` : un script par etape, executable, commente.
- `resultats/` : tables produites par les scripts. Peut etre supprime et
  regenere.
- `docs/` : description des colonnes de sortie.
- `journal/` : un compte rendu par jour de travail.

## Donnees

Les donnees de depart sont dans `data/`, en lecture seule (`chmod a-w`). Voir
`data/README.md` pour leur origine.
```
scripts/filtrer_comptages.sh
```

Le script lit `data/`, n'ecrit jamais dedans, et depose ses sorties dans
`resultats/`.

## Contenu

- `scripts/` : un script par etape, executable, commente.
- `resultats/` : tables produites par les scripts. Peut etre supprime et
  regenere.
- `docs/` : description des colonnes de sortie.
- `journal/` : un compte rendu par jour de travail.

## Donnees

Les donnees de depart sont dans `data/`, en lecture seule (`chmod a-w`). Voir
`data/README.md` pour leur origine.
```
scripts/filtrer_comptages.sh
```

Le script lit `data/`, n'ecrit jamais dedans, et depose ses sorties dans
`resultats/`.

## Contenu

- `scripts/` : un script par etape, executable, commente.
- `resultats/` : tables produites par les scripts. Peut etre supprime et
  regenere.
- `docs/` : description des colonnes de sortie.
- `journal/` : un compte rendu par jour de travail.

## Donnees

Les donnees de depart sont dans `data/`, en lecture seule (`chmod a-w`). Voir
`data/README.md` pour leur origine.
```
scripts/filtrer_comptages.sh
```

Le script lit `data/`, n'ecrit jamais dedans, et depose ses sorties dans
`resultats/`.

## Contenu

- `scripts/` : un script par etape, executable, commente.
- `resultats/` : tables produites par les scripts. Peut etre supprime et
  regenere.
- `docs/` : description des colonnes de sortie.
- `journal/` : un compte rendu par jour de travail.

## Donnees

Les donnees de depart sont dans `data/`, en lecture seule (`chmod a-w`). Voir
`data/README.md` pour leur origine.
```
scripts/filtrer_comptages.sh
```

Le script lit `data/`, n'ecrit jamais dedans, et depose ses sorties dans
`resultats/`.

## Contenu

- `scripts/` : un script par etape, executable, commente.
- `resultats/` : tables produites par les scripts. Peut etre supprime et
  regenere.
- `docs/` : description des colonnes de sortie.
- `journal/` : un compte rendu par jour de travail.

## Donnees

Les donnees de depart sont dans `data/`, en lecture seule (`chmod a-w`). Voir
`data/README.md` pour leur origine.
```
scripts/filtrer_comptages.sh
```

Le script lit `data/`, n'ecrit jamais dedans, et depose ses sorties dans
`resultats/`.

## Contenu

- `scripts/` : un script par etape, executable, commente.
- `resultats/` : tables produites par les scripts. Peut etre supprime et
  regenere.
- `docs/` : description des colonnes de sortie.
- `journal/` : un compte rendu par jour de travail.

## Donnees

Les donnees de depart sont dans `data/`, en lecture seule (`chmod a-w`). Voir
`data/README.md` pour leur origine.

## Auteur et date

Prenom Nom, projet demarre le 2024-09-17.
```

Remarquez la section « Reproduire les résultats » : une seule ligne de
commande. C'est le signe qu'un projet est bien construit — tout le travail
tient dans des scripts appelables, pas dans une suite d'étapes à refaire de
mémoire.

## Ce qu'il ne faut jamais laisser traîner

Un projet se dégrade rarement d'un coup : il accumule, exercice après
exercice, ce qu'on remettra « à plus tard » à ranger.

- **Des fichiers temporaires oubliés.** Ce que vous écrivez dans `tmp/` pendant
  un traitement — vu depuis l'épisode 11 pour `sed` — doit être supprimé une
  fois le résultat définitif copié dans `resultats/`. Un projet livré avec un
  `tmp/` plein est un projet qui n'a pas été relu.
- **Des copies `final_v2_VRAIMENT_final`.** Ce nom, croisé dans
  `data/brut_desordre/`, décrit exactement ce qu'il ne faut pas faire : une
  suite de copies manuelles qui ne dit plus laquelle est la bonne. Un script
  rejoué produit toujours le même résultat ; il n'a jamais besoin d'être
  dupliqué « au cas où ».
- **Des mots de passe et des clés d'accès.** Aucun script du projet ne doit
  contenir un mot de passe, une clé d'API ou un jeton d'accès en dur. S'il en
  faut un, il est fourni au script au moment de l'exécution, jamais écrit dans
  un fichier qui traîne dans le projet.
- **Des données identifiantes.** Un identifiant de patient, un nom, une date
  de naissance n'ont pas leur place dans un `resultats/` ni dans un `journal/`
  qui pourrait être partagé ou archivé sans précaution. Le jeu de données de
  cette formation est entièrement synthétique précisément pour vous éviter
  d'avoir à vous poser la question pendant les exercices ; sur de vraies
  données, la question se pose à chaque fichier que vous écrivez.

::: caution

## Un projet propre n'est jamais fini par accident

Ranger un projet à la fin est presque toujours trop tard : les fichiers
temporaires et les copies douteuses se créent au fil du travail, pas à la
fin. La discipline qui fonctionne consiste à ne jamais écrire dans `data/`,
à nommer les sorties correctement dès leur création, et à vider `tmp/`
régulièrement plutôt qu'une fois par projet.

:::

## Et la suite

Ces 21 épisodes vous ont donné le socle : vous déplacer, lire et transformer
des fichiers texte, écrire des scripts, les rendre robustes, les faire
tourner sur plusieurs échantillons. Ce socle est celui sur lequel repose tout
le reste du travail bioinformatique, et une seconde formation le complète sur
cinq points que cette formation a volontairement laissés de côté :

- **Git et le suivi de versions** — remplacer les copies
  `final_v2_VRAIMENT_final` par un historique de modifications réel, revenir
  en arrière, comparer deux versions d'un script.
- **conda et les conteneurs** — installer un outil bioinformatique réel avec
  ses dépendances exactes, et le faire tourner de façon identique sur une
  autre machine.
- **Les gestionnaires de flux de travaux (Snakemake, Nextflow)** — remplacer
  la boucle `for` et le script séquentiel de l'épisode 20 par une description
  déclarative des étapes, rejouable automatiquement à partir de ce qui a
  changé.
- **Le travail sur serveur et l'ordonnanceur** — soumettre un calcul à un
  cluster partagé plutôt que de le lancer sur son portable, et attendre son
  tour.
- **Le reporting reproductible** — produire un document qui mêle texte,
  code et résultats, régénérable en une commande.

## Pour continuer

Quelques ressources, en français et en anglais, pour approfondir la ligne de
commande et préparer la seconde formation :

- *Software Carpentry* — [The Unix Shell](https://swcarpentry.github.io/shell-novice/)
  (en anglais), la leçon de référence dont celle-ci s'inspire.
- *Data Carpentry* — [Data Analysis and Visualization in Genomics](https://datacarpentry.github.io/genomics-workshop/)
  pour aller vers l'analyse de données de séquençage réelles.
- *ROCKER-project.org* et la documentation de `man bash` (`man bash` en local,
  déjà sur votre machine) pour approfondir la syntaxe du shell.
- Le site *bioinformatics.ca* et ses ateliers ouverts, pour du contenu
  francophone et anglophone sur les usages bioinformatiques du shell.
- La documentation `--help` de chaque commande que vous avez apprise
  (`grep --help`, `awk --help`) reste la référence la plus fiable une fois
  loin de la salle de formation.

## Liste de contrôle finale

Avant de clore, une liste que vous pouvez garder : si vous cochez toutes les
cases, vous disposez de tout ce dont vous avez besoin pour aborder des
données réelles en ligne de commande.

- [ ] Je sais afficher où je me trouve et m'y déplacer avec des chemins
      absolus ou relatifs (`pwd`, `cd`, `ls`).
- [ ] Je sais créer, copier, déplacer et supprimer des fichiers et des
      répertoires sans passer par une interface graphique.
- [ ] Je sais lire un fichier texte volumineux sans l'ouvrir entièrement
      (`head`, `tail`, `less`, `wc`) et je reconnais les formats FASTA,
      FASTQ, BED, GFF3, VCF et SAM.
- [ ] Je sais rediriger une sortie vers un fichier, enchaîner des commandes
      avec un tube, et séparer la sortie standard de la sortie d'erreur.
- [ ] Je sais chercher un motif avec `grep`, y compris avec une expression
      régulière simple.
- [ ] Je sais découper, trier et recoller des tables avec `cut`, `sort`,
      `uniq`, `join` et `paste`.
- [ ] Je sais écrire une commande `awk` qui filtre des lignes, calcule un
      total ou groupe par catégorie.
- [ ] Je sais réécrire du texte avec `sed` sans modifier le fichier
      d'origine.
- [ ] Je sais transformer une commande qui fonctionne en un script
      exécutable, avec arguments et code de retour.
- [ ] Je sais répéter un traitement sur plusieurs échantillons avec une
      boucle `for`.
- [ ] Je sais écrire un script défensif qui vérifie ses entrées et s'arrête
      proprement en cas de problème.
- [ ] Je sais utiliser des variables, distinguer guillemets simples et
      doubles, et capturer la sortie d'une commande.
- [ ] Je sais piloter un traitement à partir d'une feuille d'échantillons
      lue ligne par ligne.
- [ ] Je sais retrouver des fichiers avec `find` et leur appliquer une
      commande en série avec `xargs`.
- [ ] Je sais lire mon `PATH`, installer un outil dans `~/bin` et comprendre
      pourquoi un alias ne survit pas à une nouvelle session.
- [ ] Je sais organiser un projet en gardant `data/` intact et en écrivant
      un `README.md` qui explique comment le reproduire.

::: instructor

## Clôturer la formation

Prévoyez dix minutes en plus des dix minutes d'exposé de cet épisode pour
clore la session dans de bonnes conditions.

- Un tour de table rapide : chaque participant nomme une commande ou une
  notion qu'il pense réutiliser dès la semaine prochaine dans son propre
  travail. Cela donne une mesure informelle de ce qui a été retenu, et
  valorise les acquis de chacun devant le groupe.
- Un questionnaire de satisfaction, envoyé en fin de séance plutôt qu'en fin
  de journée pour un meilleur taux de réponse. Les questions les plus utiles
  portent sur le rythme (trop rapide/trop lent selon les épisodes), la
  pertinence du jeu de données, et la volonté de suivre la seconde
  formation.
- Rappelez explicitement que la liste de contrôle finale peut être reprise
  telle quelle par les participants comme aide-mémoire personnel, et que rien
  n'empêche de revenir sur un épisode précédent une fois la formation
  terminée : les épisodes restent disponibles en ligne.

:::

:::::::::::::::::::::::::::::::::::::::: keypoints

- Un projet type sépare `data/` (lecture seule), `scripts/`, `resultats/`,
  `docs/` et `journal/`, avec un `README.md` à la racine.
- Les données brutes ne se modifient jamais : `chmod a-w` sur `data/` rend
  cette règle impossible à enfreindre par accident.
- Un résultat qui compte est produit par un script dans `scripts/`, jamais
  seulement par une commande tapée et laissée dans l'historique.
- Un `README.md` minimal décrit l'objectif du projet, comment reproduire ses
  résultats, et où trouver chaque type de fichier.
- Fichiers temporaires oubliés, copies `final_v2_VRAIMENT_final`, mots de
  passe en dur et données identifiantes n'ont leur place dans aucun projet.
- La seconde formation couvre Git, conda et les conteneurs, les gestionnaires
  de flux de travaux, le travail sur cluster et le reporting reproductible.

::::::::::::::::::::::::::::::::::::::::::::::::::
