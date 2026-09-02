---
title: "Pourquoi la ligne de commande en biologie"
teaching: 20
exercises: 5
---

:::::::::::::::::::::::::::::::::::::::  questions

- Pourquoi le tableur ne suffit-il pas pour traiter les données de séquençage de mon laboratoire ?
- Qu'est-ce qu'un terminal, un shell, une invite de commande ?
- Comment une commande est-elle construite, et comment obtenir de l'aide sur son fonctionnement ?
- Comment vérifier que le terminal répond bien à ce que je tape ?

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::: objectives

- Expliquer pourquoi une tâche répétée sur plusieurs échantillons appelle une solution automatisable.
- Distinguer le terminal, le shell et l'invite de commande.
- Identifier la commande, les options et les arguments dans une ligne de commande.
- Consulter la page de manuel ou l'aide intégrée d'une commande, et en sortir.
- Exécuter une première commande et lire sa réponse.

::::::::::::::::::::::::::::::::::::::::::::::::::

::: instructor

## Gérer la première demi-heure

Cet épisode se joue en grande partie sur l'installation matérielle, pas sur le
contenu. Avant de passer à la section « Anatomie d'une commande », vérifiez
un par un, à l'écran, que chaque participant voit bien une invite (un `$` ou
un `%` suivi d'un curseur) dans une fenêtre de terminal, et non un message
d'erreur, un shell exotique, ou une invite Windows classique (`C:\>`). C'est
le moment de résoudre les problèmes d'installation, pas pendant l'épisode 2.
Ne cédez pas à la tentation d'avancer parce qu'une majorité a une invite :
une personne bloquée maintenant restera bloquée toute la semaine.

:::

## Six échantillons, un répertoire, et un problème qui se répète

Le laboratoire a fait séquencer six échantillons. Le prestataire a livré un
répertoire nommé `data/`, avec entre autres un sous-répertoire `reads/`
contenant les fichiers de lectures (*reads*) de chaque échantillon, et un
sous-répertoire `tables/` contenant déjà une feuille d'échantillons
(*sample sheet*), `echantillons.tsv`.

Ouvrez un tableur et essayez d'y glisser `data/reads/ech01_R1.fastq.gz`. Rien
ne s'ouvre proprement : le fichier est compressé (*gzip*), et un tableur ne
sait pas le décompresser à la volée. Il faudrait déjà, avant toute chose,
le décompresser à la main.

Supposons que ce soit fait. Une fois décompressé, ce même fichier compte
2 000 lignes. Un fichier FASTQ consacre quatre lignes à chaque lecture, donc
ce fichier contient 500 lectures. Vous le vérifierez vous-même vendredi.
Cinq cents lignes à inspecter à l'œil, ce n'est déjà plus raisonnable dans un
tableur — et il faudrait refaire cette inspection pour chacun des deux
fichiers (`R1` et `R2`) de chacun des six échantillons.

La commande `wc` (*word count*) compte les lignes, les mots ou les caractères
d'un fichier. Elle est introduite dans cet épisode : retenez-la, vous ne vous
en séparerez plus. Avec l'option `-l`, elle compte les lignes :

```bash
wc -l data/tables/echantillons.tsv
```

```output
7 data/tables/echantillons.tsv
```

Sept lignes : l'en-tête, plus une ligne par échantillon. Six échantillons,
donc six fois la même opération à faire aujourd'hui. Le mois prochain, le
laboratoire en traitera peut-être vingt. Refaire vingt fois à la main une
opération qu'on a déjà faite six fois, sans se tromper une seule fois, n'est
pas un objectif raisonnable pour un être humain. C'est un objectif tout à
fait raisonnable pour un ordinateur, à condition de lui donner des
instructions écrites plutôt que des clics de souris. C'est tout l'objet de
cette formation.

## Anatomie d'une commande

Trois éléments sont en jeu quand vous travaillez en ligne de commande.

Le **terminal** est le programme — une fenêtre — qui vous permet de dialoguer
avec l'ordinateur en texte. Le **shell** est le programme qui, à l'intérieur
de ce terminal, lit ce que vous tapez, l'exécute, et vous répond. Le shell
utilisé dans cette formation s'appelle Bash. Quand le shell est prêt à
recevoir une commande, il affiche une **invite** (*prompt*) : une courte
ligne de texte, terminée en général par `$` ou par `%`, suivie d'un curseur
qui attend que vous tapiez quelque chose.

Une commande se construit toujours sur le même schéma, dont les deux
dernières parties sont facultatives :

```
commande -options arguments
```

Reprenons l'exemple précédent :

```bash
wc -l data/tables/echantillons.tsv
```

- `wc` est la **commande** : le programme que vous invoquez.
- `-l` est une **option** : elle modifie le comportement de la commande — ici,
  ne compter que les lignes plutôt que les mots ou les caractères.
- `data/tables/echantillons.tsv` est l'**argument** : la donnée sur laquelle
  la commande travaille — ici, le fichier à examiner.

Une commande peut n'avoir aucune option ni aucun argument. C'est le cas des
commandes que vous allez taper dans un instant.

## Obtenir de l'aide sans se perdre

Aucune commande ne se retient entièrement par cœur, et ce n'est pas le but.
Deux réflexes suffisent.

Le premier est la page de manuel (*manual page*), consultable avec `man`
suivi du nom de la commande :

<!-- verif: ignore -->
```bash
man wc
```

Cette page s'affiche dans un lecteur plein écran (le même principe que
`less`, que vous rencontrerez plus tard) : NOM, SYNOPSIS, DESCRIPTION, puis
la liste des options. Vous vous déplacez avec les flèches, et surtout, vous
en sortez avec la touche `q` (*quit*). Tant que vous n'avez pas appuyé sur
`q`, le shell attend patiemment que vous quittiez la page : ce n'est pas un
blocage, c'est le fonctionnement normal de `man`.

Le second réflexe, plus rapide, est l'option `--help`, qui affiche un résumé
directement dans le terminal, sans passer par un lecteur plein écran :

<!-- verif: ignore -->
```bash
wc --help
```

```error
Usage: wc [OPTION]... [FICHIER]...
[...]
```

Sur certains systèmes, en particulier sur macOS, `--help` n'est pas reconnu
par tous les outils : dans ce cas, `man` reste le recours qui fonctionne
toujours.

## Vérifier que le terminal répond

Avant d'aller plus loin, tapez quelques commandes sans conséquence, juste
pour voir le terminal vous répondre. `date` affiche la date et l'heure du
système :

<!-- verif: exec-seulement -->
```bash
date
```

```output
mar. 17 sept. 2024 08:00:00 CEST
```

La date et l'heure affichées chez vous seront évidemment les vôtres.
`whoami` (*who am I*) affiche le nom sous lequel vous êtes connecté :

<!-- verif: exec-seulement -->
```bash
whoami
```

```output
alice
```

`echo` répète ce que vous lui donnez en argument :

```bash
echo Bonjour, biologistes
```

```output
Bonjour, biologistes
```

Enfin, `pwd` (*print working directory*) affiche le chemin (*path*) du
répertoire (*directory*) où vous vous trouvez actuellement. Nous
l'étudierons en détail au prochain épisode ; pour l'instant, tapez-la
simplement pour constater qu'elle répond, elle aussi :

<!-- verif: exec-seulement -->
```bash
pwd
```

```output
/home/alice/formation-bash
```

Le chemin exact affiché chez vous dépendra de l'endroit où vous avez placé
le dossier de la formation sur votre machine.

::: callout

## Le terminal ne casse rien

Tant que vous ne tapez pas `rm` (qui supprime), vous ne risquez rien. Une
commande mal orthographiée, une option qui n'existe pas, un fichier
introuvable : le shell répond par un message d'erreur, et rien d'autre ne se
passe. Il n'y a pas de corbeille à vider ni de mauvaise manipulation
irréversible tant que vous vous contentez de lire et de compter. Explorez
sans crainte.

:::

## Avant-goût : ce que vous saurez faire vendredi

Voici, sans aucune explication pour l'instant, une seule ligne de commande.
Elle compte, pour chacun des douze fichiers de lectures des six échantillons,
le nombre de lectures qu'il contient :

```bash
for f in data/reads/*.fastq.gz; do echo "$f : $(( $(gunzip -c "$f" | wc -l) / 4 )) lectures"; done
```

```output
data/reads/ech01_R1.fastq.gz : 500 lectures
data/reads/ech01_R2.fastq.gz : 500 lectures
data/reads/ech02_R1.fastq.gz : 500 lectures
data/reads/ech02_R2.fastq.gz : 500 lectures
data/reads/ech03_R1.fastq.gz : 500 lectures
data/reads/ech03_R2.fastq.gz : 500 lectures
data/reads/ech04_R1.fastq.gz : 500 lectures
data/reads/ech04_R2.fastq.gz : 499 lectures
data/reads/ech05_R1.fastq.gz : 500 lectures
data/reads/ech05_R2.fastq.gz : 500 lectures
data/reads/ech06_R1.fastq.gz : 500 lectures
data/reads/ech06_R2.fastq.gz : 500 lectures
```

Regardez la septième ligne : 499, alors que toutes les autres affichent 500.
Ce n'est pas une coquille. Il y a une explication, et vous la trouverez vous
même. D'ici vendredi, vous saurez lire cette ligne de commande, la modifier,
et surtout comprendre pourquoi ce nombre-là diffère des onze autres.

:::::::::::::::::::::::::::::::::::::::  challenge

## Combien de régions dans le fichier de cibles ?

Le répertoire `data/regions/` contient un fichier `cibles.bed` qui recense des
régions d'intérêt du génome. Utilisez la commande vue dans cet épisode pour
trouver combien de lignes — donc combien de régions — il contient.

:::::::::::::::  solution

## Solution

```bash
wc -l data/regions/cibles.bed
```

```output
25 data/regions/cibles.bed
```

25 lignes, donc 25 régions. C'est exactement la même commande que pour
`echantillons.tsv`, appliquée à un autre fichier : `wc -l` compte les lignes
de n'importe quel fichier texte qu'on lui donne en argument, quel que soit
son contenu.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::: keypoints

- Une opération à répéter sur plusieurs échantillons, aujourd'hui et le mois
  prochain, justifie la ligne de commande plutôt que le tableur.
- Le terminal héberge un shell, qui affiche une invite et attend une
  commande.
- Une commande s'écrit `commande -options arguments`, options et arguments
  étant facultatifs.
- `man commande` affiche la documentation complète (on la quitte avec `q`) ;
  `commande --help` en affiche un résumé rapide.
- `date`, `whoami`, `echo` et `pwd` sont des commandes sans risque qui
  montrent que le terminal répond bien à ce que vous tapez.

::::::::::::::::::::::::::::::::::::::::::::::::::
