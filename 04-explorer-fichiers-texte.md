---
title: "Lire un fichier sans l'ouvrir"
teaching: 40
exercises: 25
---

::::::::::::::::::::::::::::::::::::::::: questions

- Comment regarder le contenu d'un fichier sans lancer un éditeur ?
- Que faire quand un fichier est trop long pour tenir sur un écran ?
- Comment savoir ce que contient un fichier avant de l'ouvrir, et combien de place il occupe ?
- Comment lire un fichier compressé sans le décompresser sur le disque ?

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::: objectives

- Afficher le contenu entier d'un petit fichier avec `cat`.
- Afficher le début ou la fin d'un fichier avec `head` et `tail`.
- Parcourir un fichier long avec `less` sans le charger entièrement en mémoire.
- Compter les lignes, mots et octets d'un fichier avec `wc`.
- Identifier le type d'un fichier avec `file` et sa taille avec `du -h`.
- Lire le contenu d'un fichier compressé sans le décompresser sur le disque.

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::: prereq

Cet épisode suppose que vous savez naviguer dans l'arborescence (`cd`, chemins
relatifs, épisode 2) et que vous avez `data/` à la racine de votre répertoire de
travail.

::::::::::::::::::::::::::::::::::::::::::::::::::

Vous avez appris à vous déplacer et à organiser vos fichiers. Il est temps de
regarder ce qu'ils contiennent. Jusqu'ici, la seule façon que vous connaissiez
d'inspecter un fichier était de l'ouvrir dans un éditeur. Cette méthode devient
vite impraticable : un génome de référence, un fichier d'alignement ou un
journal d'exécution peut faire des milliers de lignes. Cet épisode présente les
outils qui permettent de lire un fichier texte directement depuis le terminal,
en entier, en partie, ou juste pour en connaître la forme.

Commencez par créer les répertoires de travail dont vous aurez besoin dans la
suite de la leçon.

```bash
mkdir -p resultats tmp scripts
```

## Afficher un fichier entier avec `cat`

La commande `cat` (de l'anglais *concatenate*) affiche le contenu d'un fichier
sur la sortie standard (*stdout*), du début à la fin, sans interruption.

```bash
cat data/tables/echantillons.tsv
```

```output
sample_id	condition	replicat	lane	fichier_R1	fichier_R2
ech01	temoin	1	L001	ech01_R1.fastq.gz	ech01_R2.fastq.gz
ech02	temoin	2	L001	ech02_R1.fastq.gz	ech02_R2.fastq.gz
ech03	temoin	3	L002	ech03_R1.fastq.gz	ech03_R2.fastq.gz
ech04	traite	1	L002	ech04_R1.fastq.gz	ech04_R2.fastq.gz
ech05	traite	2	L003	ech05_R1.fastq.gz	ech05_R2.fastq.gz
ech06	traite	3	L003	ech06_R1.fastq.gz	ech06_R2.fastq.gz
```

Pour un fichier de sept lignes, c'est parfaitement lisible. Mais essayez la même
commande sur le génome de référence.

<!-- verif: exec-seulement -->
```bash
cat data/genome/ref_toy.fa
```

```output
[...]
```

Le fichier `data/genome/ref_toy.fa` contient 1 753 lignes. Elles défilent toutes
d'un coup, et seules les dernières restent visibles à l'écran : vous n'avez rien
appris sur le contenu du fichier, si ce n'est qu'il est long. `cat` est fait
pour afficher des fichiers courts d'un seul coup, ou pour être combiné à
d'autres commandes (vous le reverrez dans ce rôle à l'épisode 6). Ce n'est pas
un outil d'exploration.

::: callout

## `cat -n` : numéroter les lignes

L'option `-n` fait précéder chaque ligne de son numéro. C'est utile pour
repérer une ligne précise, par exemple avant de la citer à un collègue.

<!-- verif: exec-seulement -->
```bash
cat -n data/regions/cibles.bed
```

```output
[...]
```

Les 25 lignes du fichier s'affichent, chacune numérotée de 1 à 25. Sur un
fichier de 1 753 lignes comme `ref_toy.fa`, le problème de `cat` reste entier :
numéroter les lignes ne les empêche pas de défiler hors de l'écran.

:::

## Regarder le début et la fin d'un fichier

La plupart du temps, vous n'avez pas besoin du fichier entier : vous voulez
juste savoir à quoi il ressemble. `head` affiche les premières lignes.

<!-- verif: exec-seulement -->
```bash
head data/genome/ref_toy.fa
```

```output
>chr1 chromosome 1, assemblage jouet v1.0 length=100000
ATTAAGGCATGCTGGTATATTTTTTAACACAGAAAAGCAAGATGACGACATTCGCGATGG
TTGACGACGTGACTTCTTTAAATTCGCGGGTTGCACCGTCCTTTGGTTCAATACAAATAT
GGACTTAACTAATTTATGCAAATTACAGTAGGTACTCTAAGCTCCGAGATGTAGGCTGGT
GGACTTAACTAATTTATGCAAATTACAGTAGGTACTCTAAGCTCCGAGATGTAGGCTGGT
TTGACGACGTGACTTCTTTAAATTCGCGGGTTGCACCGTCCTTTGGTTCAATACAAATAT
GGACTTAACTAATTTATGCAAATTACAGTAGGTACTCTAAGCTCCGAGATGTAGGCTGGT
TTGACGACGTGACTTCTTTAAATTCGCGGGTTGCACCGTCCTTTGGTTCAATACAAATAT
GGACTTAACTAATTTATGCAAATTACAGTAGGTACTCTAAGCTCCGAGATGTAGGCTGGT
TTGACGACGTGACTTCTTTAAATTCGCGGGTTGCACCGTCCTTTGGTTCAATACAAATAT
```

Par défaut, `head` affiche dix lignes. Vous pouvez en demander un autre nombre
avec l'option `-n`.

```bash
head -n 4 data/genome/ref_toy.fa
```

```output
>chr1 chromosome 1, assemblage jouet v1.0 length=100000
ATTAAGGCATGCTGGTATATTTTTTAACACAGAAAAGCAAGATGACGACATTCGCGATGG
TTGACGACGTGACTTCTTTAAATTCGCGGGTTGCACCGTCCTTTGGTTCAATACAAATAT
GGACTTAACTAATTTATGCAAATTACAGTAGGTACTCTAAGCTCCGAGATGTAGGCTGGT
```

Ces quatre premières lignes vous apprennent déjà beaucoup : la première ligne
commence par `>`, ce qui signale un en-tête au format FASTA, et les lignes
suivantes contiennent une séquence d'ADN. Vous approfondirez ce format à
l'épisode 5.

`tail` fonctionne de la même façon, mais affiche la fin du fichier.

<!-- verif: exec-seulement -->
```bash
tail -n 4 data/genome/ref_toy.fa
```

```output
TGCGTACAAGACCTGGAAGATCGCATAAATAGTTAAAAGTAACGCAACACTTGCATTTTT
TATCTATATATCGGATTTAAGGGTAAAGCTAATACCTGGTTATTCGTAATTTATTTGAAG
ATTAAAATTACGGGCGACATATGGAGTAATGATGCAAAAATTACGGTAGGACTTGGTCTG
GTATATATCGGTAAACTGGG
```

`tail` est particulièrement utile pour surveiller la fin d'un journal
d'exécution, où se trouvent en général les événements les plus récents.

<!-- verif: exec-seulement -->
```bash
tail -n 6 data/journaux/pipeline.log
```

```output
[...]
```

::::::::::::::::::::::::::::::::::::::::  challenge

## Les cinq premiers gènes annotés

Affichez les cinq premières lignes de `data/genome/annotation.gff3`. Combien de
ces lignes commencent par un `#` plutôt que par un nom de chromosome ?

:::::::::::::::  solution

## Solution

```bash
head -n 5 data/genome/annotation.gff3
```

```output
##gff-version 3
##sequence-region chr1 1 100000
##sequence-region chrM 1 5000
#!genome-build assemblage-jouet v1.0
#!genome-date 2024-09
```

Les cinq lignes commencent toutes par `#` : ce sont des lignes d'en-tête qui
décrivent le fichier lui-même (version du format, régions couvertes, date de
génération de l'assemblage), pas encore une annotation. Il faudra aller plus
loin dans le fichier pour trouver la première ligne de données.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

## Parcourir un fichier long avec `less`

`head` et `tail` ne montrent que les extrémités d'un fichier. Pour naviguer
dans tout le fichier sans l'afficher en une seule fois, utilisez `less`.

<!-- verif: ignore -->

```bash
less data/genome/annotation.gff3
```

<!-- verif: ignore -->

`less` ouvre le fichier dans un mode de lecture qui occupe tout le terminal.
Il n'affiche à l'écran que ce qui tient dans la fenêtre, et charge le reste au
fur et à mesure : contrairement à `cat`, `less` reste utilisable même sur un
fichier de plusieurs gigaoctets, puisqu'il ne lit jamais le fichier entier en
mémoire d'un coup.

Une fois dans `less`, vous ne tapez plus de commandes shell mais des touches de
navigation.

| Touche | Effet |
|---|---|
| Espace | Avancer d'une page |
| `b` | Reculer d'une page |
| `/motif` | Chercher `motif` vers l'avant |
| `n` | Aller à l'occurrence suivante du motif recherché |
| `g` | Aller au tout début du fichier |
| `G` | Aller à la toute fin du fichier |
| `q` | Quitter et revenir au shell |

Essayez : ouvrez `data/genome/annotation.gff3` dans `less`, tapez `/gene` puis
Entrée pour chercher la première occurrence du mot `gene`, appuyez sur `n`
plusieurs fois pour passer aux occurrences suivantes, puis `q` pour quitter.

::: callout

## `less` sait aussi lire les fichiers compressés

Sur la plupart des systèmes, `less` détecte automatiquement les fichiers
compressés en `.gz` et les décompresse à la volée pour l'affichage, sans que
vous ayez besoin de le lui demander. Vous pouvez donc essayer directement
`less data/reads/ech01_R1.fastq.gz`. Ce comportement dépend cependant de la
façon dont `less` a été installé sur votre système ; la méthode fiable et
portable, que vous verrez plus loin dans cet épisode, reste `gunzip -c`.

:::

## Compter lignes, mots et octets avec `wc`

`wc` (de l'anglais *word count*) compte des lignes, des mots et des octets.
Sans option, il affiche les trois à la fois.

<!-- verif: exec-seulement -->
```bash
wc data/tables/echantillons.tsv
```

```output
       7      37     313 data/tables/echantillons.tsv
```

Les trois nombres sont, dans l'ordre, le nombre de lignes, le nombre de mots et
le nombre d'octets. Chaque option permet d'isoler l'un des trois.

```bash
wc -l data/tables/echantillons.tsv
```

```output
       7 data/tables/echantillons.tsv
```

<!-- verif: exec-seulement -->
```bash
wc -w data/tables/echantillons.tsv
```

```output
[...]
```

<!-- verif: exec-seulement -->
```bash
wc -c data/tables/echantillons.tsv
```

```output
[...]
```

`wc -l` est de loin l'option la plus utile en bioinformatique, parce que de
nombreux formats de fichiers encodent une unité d'information sur un nombre
fixe de lignes. Vous le vérifierez dans un instant avec le format FASTQ, et
vous approfondirez ce lien entre format et nombre de lignes à l'épisode 5.

::::::::::::::::::::::::::::::::::::::::  challenge

## Compter les gènes annotés

Le fichier `data/genome/annotation.gff3` contient 556 lignes. Combien de mots
contient-il ?

:::::::::::::::  solution

## Solution

<!-- verif: exec-seulement -->
```bash
wc -w data/genome/annotation.gff3
```

```output
[...]
```

`wc -w` compte les mots séparés par des espaces ou des tabulations. Dans un
fichier au format GFF3, chaque ligne de données contient neuf champs séparés
par des tabulations, et le neuvième champ contient lui-même plusieurs
identifiants séparés par des points-virgules sans espace : ils comptent donc
comme un seul mot pour `wc`. Ce nombre de mots n'est donc pas directement le
nombre de champs ; c'est un indice de la forme du fichier, pas une mesure
exacte de son contenu structuré. Vous apprendrez à compter précisément les
champs avec `cut` à l'épisode 8.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

## Identifier un fichier avec `file` et sa taille avec `du -h`

Un nom de fichier ne garantit pas son contenu. `file` examine le contenu réel
et devine de quel type de fichier il s'agit.

<!-- verif: exec-seulement -->
```bash
file data/genome/ref_toy.fa
```

```output
[...]
```

<!-- verif: exec-seulement -->
```bash
file data/reads/ech01_R1.fastq.gz
```

```output
[...]
```

`file` reconnaît notamment les fichiers compressés en `gzip`, ce qui vous
évite de les décompresser juste pour vérifier leur format. Pour connaître la
taille d'un fichier ou d'un répertoire entier, utilisez `du -h` (de l'anglais
*disk usage*, avec `-h` pour un affichage lisible par un humain — *human
readable* — en kilo-octets ou méga-octets plutôt qu'en octets bruts).

<!-- verif: exec-seulement -->
```bash
du -h data/genome/ref_toy.fa
```

```output
[...]
```

<!-- verif: exec-seulement -->
```bash
du -h data/reads
```

```output
528K	data/reads
```

Appliqué à un répertoire, `du -h` donne la taille totale de tout ce qu'il
contient. C'est un bon réflexe avant de copier ou d'envoyer un jeu de données :
mieux vaut connaître sa taille avant que le transfert échoue à mi-chemin.

## Fichiers compressés : `gzip`, `gunzip` et `gunzip -c`

Les fichiers de séquençage sont presque toujours distribués compressés, pour
économiser l'espace disque. Dans `data/reads/`, les douze fichiers de lectures
portent l'extension `.fastq.gz`. `gzip` compresse un fichier, `gunzip` le
décompresse.

```bash
cp data/reads/ech01_R1.fastq.gz tmp/
gunzip tmp/ech01_R1.fastq.gz
ls tmp/
```

```output
ech01_R1.fastq
```

`gunzip` a remplacé le fichier compressé par sa version décompressée, et lui a
retiré l'extension `.gz`. Vous pouvez inverser l'opération avec `gzip`.

```bash
gzip tmp/ech01_R1.fastq
ls tmp/
```

```output
ech01_R1.fastq.gz
```

Cette façon de faire a un inconvénient : elle occupe de l'espace disque pour la
version décompressée, même temporairement, et elle oblige à recompresser après
usage. Pour un fichier que vous voulez seulement *lire*, sans le modifier, il
existe une meilleure solution : l'option `-c` de `gunzip` (de l'anglais
*stdout*) écrit le contenu décompressé sur la sortie standard, sans toucher au
fichier d'origine sur le disque.

<!-- verif: exec-seulement -->
```bash
gunzip -c data/reads/ech01_R1.fastq.gz
```

```output
[...]
```

Le fichier `data/reads/ech01_R1.fastq.gz` sur le disque n'a pas bougé :
vérifiez-le.

<!-- verif: exec-seulement -->
```bash
file data/reads/ech01_R1.fastq.gz
```

```output
[...]
```

Il est toujours reconnu comme une archive `gzip`. `gunzip -c` est donc la
manière sûre de regarder dans un fichier compressé.

::: callout

## GNU et BSD : `zcat`

Vous rencontrerez peut-être la commande `zcat`, qui fait la même chose que
`gunzip -c`. Sur les systèmes Linux (GNU), `zcat fichier.gz` fonctionne
directement. Mais sur macOS (BSD), `zcat` s'attend à un fichier nommé
`fichier.gz.Z` et échoue sur un simple `.gz`. Comme cette formation réunit des
machines Linux, macOS et WSL, cette leçon utilise systématiquement
`gunzip -c`, qui donne le même résultat partout.

:::

`gunzip -c` affiche tout le fichier décompressé d'un coup, ce qui pose le même
problème que `cat` sur un fichier long. La solution est la même : le combiner
avec `head`. La barre verticale `|` entre les deux commandes s'appelle un tube
(*pipe*) ; elle envoie la sortie de la commande de gauche directement en entrée
de celle de droite. Le tube sera expliqué en détail à l'épisode 6 — pour
l'instant, faites-lui confiance.

```bash
gunzip -c data/reads/ech01_R1.fastq.gz | head -8
```

```output
@ECH01:1:FLOWCELL1:1:1101:1000:2000 1:N:0:ATCACG
CAGTTTTTGTCTGTGATTTTGAAACTGCAATTCATTTAAACTAAGTCTACAGTAGCTACTTAAAATTGCAACTCCATTGAACGGCCTTATGCCTATCCAG
+
B?DCBCEDEGEFCGFGDEECDFFGCDDFEFDCEFCEDCEGEEEDGFDFFEFGFFEFEGGEGCCFCFFFFFDDFEFGDCGEEGFBCA@@C@@?><=>;<=;
@ECH01:1:FLOWCELL1:1:1101:1007:2003 1:N:0:ATCACG
CATAATAAAGCGTCTAAATGCTTTCTGGTATGTATTATAATGGAACTCACAACTAATACTCCGATTTATGTCTCCTGGCCATTTAGCTCCCGAGAAAGTT
+
A@CAEFGECFGCDDEDGGDDDGFEDCCGFFDFGDGGFCCGFGEEEGFGEFGFFGDFFGEFFFGDGDFEECGDCFEEEFGFGECFCA@BCAAA?<<:::9:
```

Ces huit lignes montrent deux lectures (*reads*) complètes. Chaque lecture
occupe exactement quatre lignes : un en-tête qui commence par `@`, la séquence,
une ligne contenant seulement `+`, puis une ligne de qualité de même longueur
que la séquence. Ce format s'appelle FASTQ ; vous l'étudierez en détail à
l'épisode 5. Retenez pour l'instant ce nombre de quatre lignes par lecture : il
va vous servir immédiatement.

::: caution

## Un FASTQ dont le nombre de lignes n'est pas un multiple de 4 est corrompu

Puisque chaque lecture occupe exactement quatre lignes, un fichier FASTQ valide
a toujours un nombre total de lignes qui est un multiple de 4. Si ce n'est pas
le cas, le fichier est tronqué : une lecture a été coupée en cours d'écriture,
par exemple à cause d'un transfert réseau interrompu ou d'un disque plein
pendant la génération du fichier. Un tel fichier ne doit jamais être utilisé
tel quel pour une analyse ; toute lecture partielle en fin de fichier peut
faire planter les outils qui le liront ensuite, ou pire, être interprétée
silencieusement de travers.

:::

::::::::::::::::::::::::::::::::::::::::  challenge

## Combien de lignes dans l'échantillon 2

Affichez les 8 premières lignes décompressées de `data/reads/ech02_R1.fastq.gz`,
comme vous venez de le faire pour `ech01_R1`.

:::::::::::::::  solution

## Solution

<!-- verif: exec-seulement -->
```bash
gunzip -c data/reads/ech02_R1.fastq.gz | head -8
```

```output
[...]
```

La structure est identique à celle d'`ech01_R1` : un en-tête `@…`, une
séquence, une ligne `+`, une ligne de qualité, puis la lecture suivante. Seuls
les identifiants et les séquences changent d'un échantillon à l'autre.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::  challenge

## Le nombre de lectures de l'échantillon 3

Un fichier FASTQ consacre quatre lignes à chaque lecture. Combien de lectures
contient `data/reads/ech03_R1.fastq.gz` ?

:::::::::::::::  solution

## Solution

```bash
gunzip -c data/reads/ech03_R1.fastq.gz | wc -l
```

```output
    2000
```

2 000 lignes, donc 2 000 / 4 = 500 lectures. `gunzip -c` écrit le contenu
décompressé sur la sortie standard sans toucher au fichier ; `wc -l` compte les
lignes reçues par le tube.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::  challenge

## Un fichier qui ne correspond pas aux autres

Comptez le nombre de lignes de chacun des douze fichiers de `data/reads/` avec
`gunzip -c` et `wc -l`, pour les deux membres de la paire de chaque échantillon
(`_R1` et `_R2`). Un échantillon se distingue-t-il des cinq autres ?

Indice : vous pouvez enchaîner les commandes une par une, ou consulter
directement `data/tables/echantillons.tsv` pour la liste des six échantillons.

:::::::::::::::  solution

## Solution

```bash
gunzip -c data/reads/ech04_R1.fastq.gz | wc -l
```

```output
    2000
```

```bash
gunzip -c data/reads/ech04_R2.fastq.gz | wc -l
```

```output
    1998
```

En comparant les douze fichiers, onze d'entre eux comptent 2 000 lignes.
`ech04_R2.fastq.gz` n'en compte que 1 998 : deux lignes manquent, alors que
son complément `ech04_R1.fastq.gz` en a bien 2 000. Or 1 998 n'est pas un
multiple de 4 (1 998 / 4 = 499,5) : le fichier `ech04_R2.fastq.gz` est
tronqué, exactement comme l'encadré précédent vous a mis en garde. La dernière
lecture de ce fichier est incomplète. Vous venez de repérer, avec deux
commandes seulement, une anomalie réelle du jeu de données que vous auriez pu
mettre longtemps à découvrir en travaillant à la main.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::  challenge

## Retrouver l'anomalie dans le journal (facultatif)

Le fichier `data/journaux/pipeline.log` contient 24 lignes. Affichez-en
quelques-unes avec `head` pour voir leur forme habituelle, puis ouvrez le
fichier entier avec `less` et cherchez, avec `/`, une ligne qui mentionne
`ech04`. Que raconte-t-elle ?

:::::::::::::::  solution

## Solution

<!-- verif: exec-seulement -->
```bash
head -n 4 data/journaux/pipeline.log
```

```output
[...]
```

En ouvrant le fichier avec `less data/journaux/pipeline.log`, puis en tapant
`/ech04` suivi d'Entrée, vous tombez sur une ligne signalée `[ERROR]` qui
indique que le fichier `ech04_R2.fastq.gz` est tronqué, avec un bloc FASTQ
incomplet. Le journal avait donc déjà consigné exactement l'anomalie que vous
venez de retrouver vous-même en comptant les lignes : la ligne de commande ne
vous a rien appris que le pipeline ne savait déjà, mais elle vous a permis de
le vérifier de façon indépendante, sans faire confiance à un seul journal.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::::: keypoints

- `cat` affiche un fichier entier d'un coup ; réservez-le aux fichiers courts, jamais à un fichier de plus de quelques dizaines de lignes.
- `head -n N` et `tail -n N` affichent respectivement les N premières ou dernières lignes d'un fichier.
- `less` permet de parcourir un fichier long touche par touche, sans le charger entièrement en mémoire ; on en sort avec `q`.
- `wc -l`, `wc -w` et `wc -c` comptent respectivement les lignes, les mots et les octets d'un fichier.
- `file` identifie le type réel d'un fichier, et `du -h` affiche sa taille dans une unité lisible.
- `gunzip -c fichier.gz` affiche le contenu décompressé sans modifier le fichier sur le disque ; préférez-le à `zcat`, absent sous une forme portable sur macOS.
- Un fichier FASTQ compte quatre lignes par lecture : un nombre total de lignes qui n'est pas multiple de 4 signale un fichier tronqué.

::::::::::::::::::::::::::::::::::::::::::::::::::
