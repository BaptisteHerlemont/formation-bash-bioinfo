---
title: "Se déplacer dans l'arborescence"
teaching: 35
exercises: 25
---

:::::::::::::::::::::::::::::::::::::::  questions

- Comment savoir précisément où je me trouve dans l'arborescence de fichiers ?
- Comment afficher le contenu d'un répertoire, avec plus ou moins de détails ?
- Comment me déplacer d'un répertoire à un autre sans passer par la souris ?
- Que signifient `.`, `..` et `~` dans un chemin ?

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::: objectives

- Afficher le chemin du répertoire de travail courant avec `pwd`.
- Lister le contenu d'un répertoire avec `ls` et ses options `-l`, `-a`, `-h`, `-F`, `-R`.
- Distinguer un chemin absolu d'un chemin relatif et choisir lequel utiliser.
- Se déplacer entre répertoires avec `cd`, y compris avec `.`, `..`, `~`, `cd -` et `cd` seul.
- Utiliser la complétion par tabulation et l'historique des commandes pour aller plus vite.

::::::::::::::::::::::::::::::::::::::::::::::::::

## Où suis-je

À la fin de l'épisode précédent, vous saviez lancer une commande. Mais une
commande comme `wc` ou `cat` agit toujours sur un fichier, et un fichier se
trouve *quelque part*. Avant d'aller plus loin, il faut donc répondre à une
question qui paraît triviale et qui, pourtant, est à l'origine de la plupart
des blocages des débutants : dans quel répertoire (*directory*) le shell
travaille-t-il en ce moment.

Le shell garde toujours en mémoire un répertoire courant, celui depuis lequel
il interprète tous les chemins relatifs. Pour l'afficher, une seule commande :

<!-- verif: exec-seulement -->
```bash
pwd
```

`pwd` (*print working directory*) affiche le chemin complet du répertoire dans
lequel vous vous trouvez. C'est la commande la plus utile de toute la leçon,
et de loin la plus sous-utilisée par les débutants.

```output
/home/apprenant/formation-bash
```

Le chemin exact dépend de votre machine et de l'endroit où vous avez placé le
dossier de la formation : ce qui compte est de reconnaître la structure, pas
la valeur précise. Dans la suite de cet épisode, on suppose que vous êtes
placé dans le répertoire `formation-bash`, celui qui contient `data/`.
Vérifiez-le maintenant :

<!-- verif: ordre-libre -->
```bash
ls
```

```output
_verif.sh
data
```

Si `data` n'apparaît pas, vous n'êtes pas au bon endroit : déplacez-vous
d'abord avec `cd` vers le répertoire qui le contient, ce que vous saurez faire
dans quelques minutes.

::::::::::::::::::::::::::::::::::::::::::: callout

## Le réflexe à installer dès aujourd'hui

Le message d'erreur le plus fréquent chez les débutants est :

```error
No such file or directory
```

Il ne signifie presque jamais que le fichier n'existe pas. Il signifie, neuf
fois sur dix, que vous n'êtes pas dans le répertoire que vous croyez. Avant de
chercher une explication compliquée, faites systématiquement deux gestes, dans
cet ordre :

1. `pwd` — où suis-je réellement ?
2. `ls` — qu'y a-t-il vraiment ici ?

Ces deux commandes ne coûtent rien, ne modifient rien, et résolvent la
majorité des blocages. Prenez l'habitude de les taper par réflexe avant de
vous demander si la commande elle-même est fausse.

::::::::::::::::::::::::::::::::::::::::::::::::::

## L'arborescence comme un arbre

Le système de fichiers est organisé en arbre : un répertoire de départ, appelé
racine, contient des répertoires, qui contiennent eux-mêmes des fichiers ou
d'autres répertoires. `formation-bash` est une branche de cet arbre, et voici
à quoi ressemble la partie qui vous intéresse aujourd'hui :

```output
~/formation-bash/
└── data/
    ├── README.md
    ├── alignements/
    │   └── ech01.sam
    ├── brut_desordre/
    │   ├── Ech04_final_VRAIMENT_final.fastq
    │   ├── Echantillon 01 - Run mars.fastq
    │   ├── RESUME Manip.txt
    │   ├── ech 03 (copie).fastq
    │   ├── ech05.resultats.fastq
    │   ├── ech06 -- a refaire.fastq
    │   ├── echantillon_02.FASTQ
    │   └── notes du 12 mars.txt
    ├── genome/
    │   ├── annotation.gff3
    │   ├── ref_toy.fa
    │   └── ref_toy.fa.fai
    ├── journaux/
    │   └── pipeline.log
    ├── proteines/
    │   └── proteines.fa
    ├── reads/
    │   ├── ech01_R1.fastq.gz
    │   ├── ech01_R2.fastq.gz
    │   ├── ech02_R1.fastq.gz
    │   ├── ...
    │   └── ech06_R2.fastq.gz
    ├── regions/
    │   └── cibles.bed
    ├── tables/
    │   ├── comptages.tsv
    │   └── echantillons.tsv
    └── variants/
        └── cohorte.vcf
```

Chaque barre verticale représente une branche de l'arbre. `formation-bash`
est le répertoire dans lequel vous vous trouvez ; `data` en est un
sous-répertoire ; `reads` est un sous-répertoire de `data`, et
`ech01_R1.fastq.gz` est un fichier qui vit à l'intérieur de `reads`. C'est
cette structure que les commandes `ls` et `cd` vous permettent d'explorer.

::::::::::::::::::::::::::::::::::::::::::: instructor

## Faire dessiner l'arborescence

Avant de continuer, demandez au groupe de dessiner au tableau (ou sur une
feuille) l'arborescence ci-dessus, sans regarder l'écran, à partir de ce que
`ls` leur montrera dans les minutes qui suivent. L'exercice est volontairement
simple : il s'agit de faire correspondre le schéma en art ASCII à quelque
chose de concret et de vérifier, avant d'aborder `cd`, que la notion de
répertoire parent et de répertoire enfant est bien installée. Reprenez le
dessin au tableau chaque fois qu'une confusion apparaît sur `.` ou `..` plus
loin dans l'épisode.

::::::::::::::::::::::::::::::::::::::::::::::::::

## Lister le contenu d'un répertoire

Vous connaissez déjà `ls` sans option. Elle affiche les noms, mais rien sur
leur nature. Un premier raffinement utile est `-F`, qui ajoute un symbole
après chaque nom pour préciser ce qu'il est : `/` pour un répertoire, `*` pour
un fichier exécutable, rien pour un fichier ordinaire.

<!-- verif: ordre-libre -->
```bash
ls -F data
```

```output
README.md    brut_desordre/  journaux/    reads/     tables/
alignements/ genome/         proteines/   regions/   variants/
```

Les noms suivis de `/` sont des répertoires : `brut_desordre`, `genome`,
`reads`, et les autres. `README.md` n'en a pas : c'est un fichier ordinaire.

### Afficher les détails avec `ls -l`

L'option `-l` (*long format*) affiche une ligne d'informations par fichier au
lieu du seul nom.

<!-- verif: exec-seulement -->
```bash
ls -l data
```

```output
total 8
-rw-r--r--@  1 baptisteherlemont  staff  3143 Aug 31 22:36 README.md
drwxr-xr-x@  3 baptisteherlemont  staff    96 Aug 31 22:36 alignements
drwxr-xr-x@ 10 baptisteherlemont  staff   320 Aug 31 22:36 brut_desordre
drwxr-xr-x@  5 baptisteherlemont  staff   160 Aug 31 22:36 genome
drwxr-xr-x@  3 baptisteherlemont  staff    96 Aug 31 22:36 journaux
drwxr-xr-x@  3 baptisteherlemont  staff    96 Aug 31 22:36 proteines
drwxr-xr-x@ 14 baptisteherlemont  staff   448 Aug 31 22:36 reads
drwxr-xr-x@  3 baptisteherlemont  staff    96 Aug 31 22:36 regions
drwxr-xr-x@  4 baptisteherlemont  staff   128 Aug 31 22:36 tables
drwxr-xr-x@  3 baptisteherlemont  staff    96 Aug 31 22:36 variants
```

Chaque colonne porte une information précise :

| Colonne | Exemple | Signification |
|---|---|---|
| Type et permissions | `drwxr-xr-x` | `d` si répertoire, `-` si fichier ordinaire, suivi des droits de lecture, écriture, exécution |
| Nombre de liens | `2` | Nombre de références internes vers l'élément (peu utile pour l'instant) |
| Propriétaire | `participant` | Personne qui possède le fichier |
| Groupe | `participant` | Groupe auquel appartient le fichier |
| Taille | `1234` | Taille en octets |
| Date de modification | `17 sep 08:00` | Dernière modification du contenu |
| Nom | `README.md` | Nom du fichier ou du répertoire |

Le premier caractère de la première colonne suffit, à lui seul, à distinguer
un répertoire (`d`) d'un fichier (`-`) : c'est souvent l'information la plus
utile de toute la ligne.

### Des tailles lisibles avec `-h`

La colonne de taille de `ls -l` est en octets, ce qui devient illisible dès
que les fichiers grossissent. L'option `-h` (*human-readable*) l'affiche en
kio, Mio ou Gio.

<!-- verif: exec-seulement -->
```bash
ls -lh data/reads
```

```output
total 528
-rw-r--r-- 1 participant participant  44K 17 sep 08:00 ech01_R1.fastq.gz
-rw-r--r-- 1 participant participant  44K 17 sep 08:00 ech01_R2.fastq.gz
-rw-r--r-- 1 participant participant  44K 17 sep 08:00 ech02_R1.fastq.gz
-rw-r--r-- 1 participant participant  44K 17 sep 08:00 ech02_R2.fastq.gz
-rw-r--r-- 1 participant participant  44K 17 sep 08:00 ech03_R1.fastq.gz
-rw-r--r-- 1 participant participant  44K 17 sep 08:00 ech03_R2.fastq.gz
-rw-r--r-- 1 participant participant  44K 17 sep 08:00 ech04_R1.fastq.gz
-rw-r--r-- 1 participant participant  44K 17 sep 08:00 ech04_R2.fastq.gz
-rw-r--r-- 1 participant participant  44K 17 sep 08:00 ech05_R1.fastq.gz
-rw-r--r-- 1 participant participant  44K 17 sep 08:00 ech05_R2.fastq.gz
-rw-r--r-- 1 participant participant  44K 17 sep 08:00 ech06_R1.fastq.gz
-rw-r--r-- 1 participant participant  44K 17 sep 08:00 ech06_R2.fastq.gz
```

`-l` et `-h` se combinent en `-lh`, ou dans n'importe quel ordre : `-hl`
fonctionne identiquement. C'est une propriété générale des options courtes en
une seule lettre.

### Voir aussi les fichiers cachés avec `-a`

Certains fichiers ont un nom qui commence par un point : le shell les
considère comme cachés et ne les affiche pas par défaut. L'option `-a`
(*all*) les révèle.

<!-- verif: ordre-libre -->
```bash
ls -a
```

```output
.
..
_verif.sh
data
```

Deux entrées surprenantes apparaissent : `.` et `..`. Ce ne sont pas des
fichiers cachés ordinaires mais deux raccourcis présents dans absolument tous
les répertoires, sur lesquels nous revenons dans un instant.

### Explorer en profondeur avec `-R`

Pour l'instant, `ls` ne montre que le contenu direct d'un répertoire. Pour
descendre récursivement (*recursive*) dans tous les sous-répertoires en une
seule commande, utilisez `-R`.

<!-- verif: ordre-libre -->
```bash
ls -R data/regions data/journaux
```

```output
data/regions:
cibles.bed

data/journaux:
pipeline.log
```

Sur un répertoire aux nombreux sous-répertoires, `-R` produit une sortie très
longue : gardez-le pour les répertoires ciblés, ou pour une vue d'ensemble
rapide comme celle que vous venez de demander sur `data` tout entier au début
de l'épisode.

::::::::::::::::::::::::::::::::::::::::::::: challenge

## Combiner les options de `ls`

Affichez, en une seule commande, le contenu détaillé (`-l`) et lisible (`-h`)
du répertoire `data/genome`, incluant les éventuels fichiers cachés.

:::::::::::::::  solution

## Solution

<!-- verif: exec-seulement -->
```bash
ls -lha data/genome
```

```output
total 328
drwxr-xr-x@  5 baptisteherlemont  staff   160B Aug 31 22:36 .
drwxr-xr-x@ 12 baptisteherlemont  staff   384B Aug 31 22:36 ..
-rw-r--r--@  1 baptisteherlemont  staff    49K Aug 31 22:37 annotation.gff3
-rw-r--r--@  1 baptisteherlemont  staff   104K Aug 31 22:37 ref_toy.fa
-rw-r--r--@  1 baptisteherlemont  staff    44B Aug 31 22:37 ref_toy.fa.fai
```

Les trois options se combinent librement derrière un seul tiret :
`-lha`, `-alh` ou `-ahl` produisent exactement le même résultat. `data/genome`
ne contient pas de fichier caché supplémentaire : seules `.` et `..`
apparaissent en plus, comme dans tout répertoire.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::::::::

## Se déplacer avec `cd`

Lister le contenu d'un répertoire depuis l'extérieur, avec `ls chemin`, est
utile mais limité. Pour travailler *dans* un répertoire, on s'y déplace avec
`cd` (*change directory*), qui modifie le répertoire de travail courant.

<!-- verif: exec-seulement -->
```bash
cd data/reads
pwd
```

```output
/home/participant/formation-bash/data/reads
```

Une fois déplacé, `ls` sans argument liste le contenu du nouveau répertoire
courant :

<!-- verif: ordre-libre -->
```bash
ls
```

```output
ech01_R1.fastq.gz
ech01_R2.fastq.gz
ech02_R1.fastq.gz
ech02_R2.fastq.gz
ech03_R1.fastq.gz
ech03_R2.fastq.gz
ech04_R1.fastq.gz
ech04_R2.fastq.gz
ech05_R1.fastq.gz
ech05_R2.fastq.gz
ech06_R1.fastq.gz
ech06_R2.fastq.gz
```

### Chemins absolus et chemins relatifs

Il existe deux façons d'indiquer un chemin (*path*) à une commande. Un chemin
absolu part de la racine du système de fichiers et commence toujours par
`/` : il désigne le même emplacement quel que soit le répertoire courant. Un
chemin relatif part du répertoire courant et n'a de sens que depuis là où
vous êtes.

Vous êtes actuellement dans `data/reads`. Les deux commandes suivantes
atteignent le même répertoire, l'une en absolu, l'autre en relatif :

<!-- verif: exec-seulement -->
```bash
cd ..
pwd
```

```output
/home/apprenant/formation-bash/data
```

`..` est le raccourci vers le répertoire parent : celui qui contient le
répertoire courant. C'est lui qui apparaissait dans la sortie de `ls -a` un
peu plus haut. Revenons à `reads`, cette fois avec un chemin relatif explicite
depuis `data` :

<!-- verif: exec-seulement -->
```bash
cd reads
pwd
```

```output
/home/participant/formation-bash/data/reads
```

Un chemin relatif est plus court à taper mais dépend entièrement du
répertoire courant : la même commande `cd reads` échouera si vous n'êtes pas
dans `data`. Un chemin absolu fonctionne depuis n'importe où, mais suppose de
le connaître ou de le retrouver avec `pwd`.

### `.`, `..` et l'empilement de répertoires

`.` est le raccourci vers le répertoire courant lui-même. Il est rarement
nécessaire avec `cd` — `cd .` ne change rien — mais il devient utile dès
qu'une commande demande un chemin de destination, comme vous le verrez à
l'épisode suivant avec `cp`. `..` s'enchaîne pour remonter de plusieurs
niveaux à la fois :

<!-- verif: exec-seulement -->
```bash
cd ../..
pwd
```

```output
/home/participant/formation-bash
```

Chaque `..` remonte d'un niveau : `../..` remonte de deux niveaux depuis
`data/reads`, ce qui vous ramène directement à la racine de `formation-bash`.

### `~`, le raccourci vers le répertoire personnel

Le symbole `~` (tilde) désigne toujours votre répertoire personnel
(*home directory*), quel que soit l'endroit où vous vous trouvez. Si
`formation-bash` a été installé directement dans votre répertoire personnel,
les deux commandes suivantes vous y ramènent de façon équivalente :

<!-- verif: exec-seulement -->
```bash
cd ~/formation-bash
pwd
```

```output
/home/participant/formation-bash
```

`cd` employé seul, sans argument, fait exactement la même chose que
`cd ~` : il vous ramène toujours à votre répertoire personnel, d'où que vous
partiez.

<!-- verif: exec-seulement -->
```bash
cd data/genome
cd
pwd
```

```output
/home/participant
```

Ce comportement est pratique pour se réorienter en cas de doute, mais il vous
a éloigné de `formation-bash`. Revenez-y avant de continuer :

<!-- verif: exec-seulement -->
```bash
cd formation-bash
pwd
```

```output
/home/participant/formation-bash
```

### `cd -`, revenir sur ses pas

Une dernière variante retient le dernier répertoire visité avant le
déplacement courant, et y retourne :

<!-- verif: exec-seulement -->
```bash
cd data/proteines
cd data/../data/variants
cd -
pwd
```

```output
/home/participant/formation-bash/data/proteines
```

`cd -` a basculé vers le répertoire précédent, exactement comme le ferait un
bouton « précédent » de navigateur. Revenez maintenant à la racine du projet
pour la suite de l'épisode :

```bash
cd ~/formation-bash
```

::::::::::::::::::::::::::::::::::::::::::::: challenge

## Retrouver son chemin

Déplacez-vous dans `data/variants`, puis, sans taper `cd ..` plusieurs fois,
revenez directement à `formation-bash` en une seule commande `cd`. Vérifiez
avec `pwd`.

:::::::::::::::  solution

## Solution

<!-- verif: exec-seulement -->
```bash
cd data/variants
cd ../..
pwd
```

```output
/home/apprenant/formation-bash
```

`data/variants` est à deux niveaux sous `formation-bash` : un `..` remonte à
`data`, le second remonte à `formation-bash`. `cd ~/formation-bash` ou
`cd -` (si `formation-bash` était bien le répertoire précédent) auraient
aussi fonctionné.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::: challenge

## Explorer une branche inconnue

Sans utiliser `ls -R`, retrouvez, en vous déplaçant avec `cd` et en listant
avec `ls` à chaque étape, le nom du seul fichier présent dans
`data/alignements`. Notez le chemin absolu de ce fichier obtenu avec `pwd`.

:::::::::::::::  solution

## Solution

<!-- verif: ordre-libre -->
```bash
cd data/alignements
ls
pwd
```

```output
ech01.sam
/home/apprenant/formation-bash/data/alignements
```

<!-- verif: exec-seulement -->
```output
/home/participant/formation-bash/data/alignements
```

Le fichier est `ech01.sam`, et son chemin absolu est
`/home/participant/formation-bash/data/alignements/ech01.sam` (le début de ce
chemin dépend de votre machine). Revenez à la racine pour la suite :

```bash
cd ~/formation-bash
```

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::: callout

## La casse et les espaces comptent

Le shell distingue les majuscules des minuscules : `Genome`, `genome` et
`GENOME` seraient trois noms différents. Le répertoire `data/genome` ne
répond pas à `cd data/Genome` :

<!-- verif: ignore -->
```bash
cd data/Genome
```

```error
```

Cette erreur illustre exactement le réflexe présenté plus haut : le
répertoire existe, mais pas sous ce nom-là.

Les espaces posent un problème différent et plus sérieux : le shell les
utilise pour séparer les arguments d'une commande. Un nom comme
`Echantillon 01 - Run mars.fastq`, que vous avez peut-être remarqué dans
`data/brut_desordre` en listant `data` en tout début d'épisode, sera lu par
`cd` ou `ls` comme plusieurs arguments distincts plutôt que comme un seul
nom de fichier. La solution — mettre le nom entre guillemets — fait l'objet
de l'épisode 16 sur les variables et le quoting. En attendant, retenez
seulement qu'un nom de fichier contenant des espaces demande une précaution
particulière, et évitez d'en créer vous-même : l'épisode suivant reviendra
sur les bonnes pratiques de nommage.

::::::::::::::::::::::::::::::::::::::::::::::::::::::

## Aller plus vite : tabulation et historique

Vous venez de taper plusieurs fois des chemins comme `data/alignements` ou
`~/formation-bash`. Deux outils du shell évitent de les retaper en entier et,
surtout, évitent les fautes de frappe qui produisent justement l'erreur
« No such file or directory » présentée plus haut.

### La complétion par tabulation

Depuis `formation-bash`, tapez le début d'un nom puis appuyez sur la touche
de tabulation avant de valider :

<!-- verif: exec-seulement -->
```bash
cd data/prot
```

En appuyant sur Tab après `prot`, le shell complète lui-même jusqu'à
`data/proteines/`, car c'est le seul nom du répertoire `data` qui commence
par ces lettres. Si plusieurs noms correspondaient, une première pression sur
Tab ne complèterait que la partie commune, et une seconde pression afficherait
la liste des possibilités. Validez avec Entrée pour vous y déplacer :

```output
/home/participant/formation-bash/data/proteines
```

Revenez à la racine avant de continuer :

```bash
cd ~/formation-bash
```

La complétion par tabulation n'est pas un confort accessoire : elle évite de
retaper des noms longs comme `brut_desordre` ou `ech01_R1.fastq.gz`, et elle
signale immédiatement une faute de frappe, puisqu'un nom mal orthographié ne
se complète pas.

### L'historique des commandes

Le shell garde en mémoire les commandes que vous avez tapées durant la
session. La flèche du haut du clavier les rappelle une par une, de la plus
récente à la plus ancienne, sans qu'il soit nécessaire de les retaper. Pour
les consulter toutes d'un coup, la commande `history` en affiche la liste
numérotée :

<!-- verif: exec-seulement -->
```bash
history
```

```output
  1  pwd
  2  ls
  3  ls -F data
  4  ls -l data
  5  ls -lh data/reads
[...]
```

La sortie complète dépend de tout ce que vous avez tapé depuis le début de la
session : seul le principe compte ici. Combinée à la flèche du haut, elle
vous permet de rappeler une commande ancienne sans la retaper, de la modifier
légèrement, puis de la valider.

::::::::::::::::::::::::::::::::::::::::::::: challenge

## S'entraîner à la vitesse

1. Depuis `formation-bash`, tapez `cd data/al` puis complétez avec la
   tabulation pour atteindre `data/alignements` sans taper le nom en entier.
2. Utilisez la flèche du haut pour rappeler la commande `pwd` que vous venez
   de taper juste après, sans la retaper.
3. Utilisez `history` pour retrouver le numéro de la commande `ls -F data`
   tapée plus haut dans cet épisode.

:::::::::::::::  solution

## Solution

Le premier point se réalise en tapant `cd data/al`, puis en appuyant sur Tab :
le shell complète en `data/alignements/` puisqu'aucun autre nom de `data` ne
commence par `al`. Le deuxième point consiste simplement à appuyer sur la
flèche du haut une fois : la dernière commande tapée, `pwd`, réapparaît
prête à être validée avec Entrée. Le troisième point s'obtient en lisant la
liste numérotée produite par `history` et en repérant la ligne contenant
`ls -F data` ; le numéro exact dépend de tout ce que vous avez tapé depuis
le début de la session.

Ces deux outils — tabulation et historique — sont des outils de survie au
même titre que `pwd` : plus vous les utiliserez tôt, moins vous ferez de
fautes de frappe et moins vous perdrez de temps à retaper des chemins
longs comme `data/brut_desordre` ou `data/alignements`.

Revenez à la racine avant de continuer :

```bash
cd ~/formation-bash
```

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::::::::

## Nettoyer l'écran

Après quelques dizaines de commandes, le terminal devient difficile à lire.
`clear` efface l'écran sans effacer l'historique : les commandes précédentes
restent accessibles avec la flèche du haut ou `history`, seul l'affichage est
vidé.

<!-- verif: ignore -->
```bash
clear
```

::::::::::::::::::::::::::::::::::::::::::::: challenge

## Pourquoi cette erreur (facultatif)

Une collègue vous montre la séquence de commandes suivante, tapée depuis
`~/formation-bash`, et ne comprend pas le message obtenu :

```bash
cd data
cd reads
cd genome
```

```error
```

Sans taper la séquence vous-même, expliquez pourquoi cette erreur apparaît,
et proposez la commande `cd` qui aurait permis d'atteindre `data/genome`
depuis `data/reads`.

:::::::::::::::  solution

## Solution

Après les deux premières commandes, le répertoire courant est `data/reads`.
`genome` n'est pas un sous-répertoire de `reads` : c'est un sous-répertoire
de `data`, donc un répertoire *frère* de `reads`, pas un enfant. La commande
`cd genome` cherche `data/reads/genome`, qui n'existe pas — d'où le message.
Pour atteindre `data/genome` depuis `data/reads`, il fallait remonter d'un
niveau avant de redescendre : `cd ../genome`, ou repartir d'un chemin
absolu ou relatif depuis la racine, comme `cd ~/formation-bash/data/genome`.
C'est exactement le réflexe `pwd` puis `ls` qui permet de repérer ce genre
d'erreur avant qu'elle ne se reproduise.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::: keypoints

- `pwd` affiche le chemin complet du répertoire de travail courant : c'est le premier réflexe en cas de doute.
- `ls -F` distingue les répertoires des fichiers, `ls -l` affiche les détails, `-h` les rend lisibles, `-a` révèle les fichiers cachés, `-R` descend récursivement.
- Un chemin absolu commence par `/` et fonctionne depuis n'importe où ; un chemin relatif part du répertoire courant.
- `.` désigne le répertoire courant, `..` le répertoire parent, `~` le répertoire personnel ; `cd -` revient au répertoire précédent et `cd` seul ramène au répertoire personnel.
- Le message `No such file or directory` signale presque toujours qu'on n'est pas là où l'on croit : la réponse est `pwd` puis `ls`.
- La complétion par tabulation et l'historique (`history`, flèche du haut) évitent de retaper les chemins et réduisent les fautes de frappe.
- `clear` vide l'affichage du terminal sans toucher à l'historique des commandes.

::::::::::::::::::::::::::::::::::::::::::::::::::
