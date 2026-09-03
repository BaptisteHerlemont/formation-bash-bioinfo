---
title: "find, xargs et parallélisation simple"
teaching: 25
exercises: 20
---

::::::::::::::::::::::::::::::::::::::::::::: questions

- Comment retrouver un fichier dans une arborescence sans savoir exactement où il est ?
- Comment appliquer une commande à une longue liste de fichiers sans écrire de boucle ?
- Comment lancer plusieurs traitements indépendants en même temps, et quand cela vaut-il vraiment la peine ?

::::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::: objectives

- Rechercher des fichiers avec `find` selon leur nom, leur type, leur taille ou leur date de modification.
- Combiner plusieurs critères de recherche et agir sur les résultats avec `-exec` ou `-delete`.
- Construire une liste de fichiers sûre avec `find -print0` et la parcourir avec `while read -r -d ''`.
- Paralléliser un traitement sur plusieurs échantillons avec `xargs -P` ou avec `&` et `wait`.
- Reconnaître les situations où la parallélisation aide et celles où elle ne sert à rien.

::::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::::::::: prereq

Cet épisode suppose l'épisode 16 (guillemets, `IFS`, substitution de commandes)
et l'épisode 17 (boucle `while read -r` sur un flux de données).

::::::::::::::::::::::::::::::::::::::::::::::::::::

Vous connaissez déjà `ls`, les jokers et les boucles `for`. Cela suffit tant
que vous savez où sont vos fichiers et qu'ils se comptent sur les doigts de la
main. Mais `data/brut_desordre/` porte bien son nom : les fichiers y ont des
noms avec espaces, majuscules variables, parenthèses. Impossible de deviner un
motif de joker fiable. Il faut un outil qui interroge le système de fichiers
lui-même : `find`.

Une fois la liste de fichiers obtenue, une deuxième question se pose : vous
avez six échantillons à traiter, un traitement indépendant par échantillon. La
boucle `for` de l'épisode 14 les traite un par un, dans l'ordre. Si votre
ordinateur a plusieurs cœurs de processeur, pourquoi ne pas en traiter
plusieurs à la fois ? C'est le rôle de `xargs -P`.

Mettez-vous dans votre répertoire de travail et préparez un espace de sortie :

```bash
mkdir -p resultats tmp scripts
```

## Retrouver des fichiers avec `find`

### Chercher par nom

La syntaxe générale de `find` est : un point de départ, puis des critères.

<!-- verif: ordre-libre -->
```bash
find data -name "*.fastq.gz"
```

```output
data/reads/ech01_R2.fastq.gz
data/reads/ech04_R2.fastq.gz
data/reads/ech05_R1.fastq.gz
data/reads/ech06_R1.fastq.gz
data/reads/ech03_R1.fastq.gz
data/reads/ech02_R2.fastq.gz
data/reads/ech04_R1.fastq.gz
data/reads/ech05_R2.fastq.gz
data/reads/ech01_R1.fastq.gz
data/reads/ech03_R2.fastq.gz
data/reads/ech02_R1.fastq.gz
data/reads/ech06_R2.fastq.gz
```

`find` descend récursivement dans `data` et compare le nom de chaque fichier
au motif. Les guillemets autour du motif empêchent le shell de développer le
joker lui-même : c'est `find` qui doit le voir, pas le shell (rappel de
l'épisode 3).

`brut_desordre/` mélange les casses : `.fastq`, `.FASTQ`. Avec `-name`, la
casse compte, et une partie des fichiers échappe à la recherche :

<!-- verif: ordre-libre -->
```bash
find data/brut_desordre -name "*.fastq"
```

```output
data/brut_desordre/Ech04_final_VRAIMENT_final.fastq
data/brut_desordre/Echantillon 01 - Run mars.fastq
data/brut_desordre/ech 03 (copie).fastq
data/brut_desordre/ech05.resultats.fastq
data/brut_desordre/ech06 -- a refaire.fastq
```

`echantillon_02.FASTQ` manque : son extension est en majuscules. `-iname` fait
la même recherche sans tenir compte de la casse :

<!-- verif: ordre-libre -->
```bash
find data/brut_desordre -iname "*.fastq"
```

```output
data/brut_desordre/Ech04_final_VRAIMENT_final.fastq
data/brut_desordre/Echantillon 01 - Run mars.fastq
data/brut_desordre/ech 03 (copie).fastq
data/brut_desordre/ech05.resultats.fastq
data/brut_desordre/ech06 -- a refaire.fastq
data/brut_desordre/echantillon_02.FASTQ
```

Les six fichiers de séquences sont là, quelle que soit leur casse.

### Filtrer par type et par profondeur

`-type f` ne garde que les fichiers ordinaires, `-type d` ne garde que les
répertoires :

<!-- verif: ordre-libre -->
```bash
find data -maxdepth 1 -type d
```

```output
data
data/alignements
data/brut_desordre
data/genome
data/journaux
data/proteines
data/reads
data/regions
data/tables
data/variants
```

`-maxdepth 1` arrête la descente après un niveau : c'est ce qui limite le
résultat aux sous-répertoires directs de `data`, sans aller regarder à
l'intérieur. Sans cette limite, `find` explorerait toute l'arborescence.

### Filtrer par taille et par date

`-size` accepte un signe et une unité : `k` pour kilo-octets, `M` pour
méga-octets. `+` signifie « plus grand que », `-` signifie « plus petit que ».

<!-- verif: ordre-libre -->
```bash
find data -type f -size +50k
```

```output
data/alignements/ech01.sam
data/genome/ref_toy.fa
```

`-newer` compare la date de modification à celle d'un fichier de référence :
il renvoie les fichiers modifiés après lui. C'est utile pour retrouver ce
qu'un script vient de produire. Créons un repère temporel, puis un fichier de
résultat, et comparons :

```bash
touch tmp/repere
gunzip -c data/reads/ech01_R1.fastq.gz | wc -l > resultats/compte_ech01.txt
find resultats -type f -newer tmp/repere
```

```output
resultats/compte_ech01.txt
```

`resultats/compte_ech01.txt` a été écrit après `tmp/repere` : `find` le
signale. Le `-type f` n'est pas décoratif ici : sans lui, `find` examinerait
aussi le répertoire `resultats` lui-même, dont la date de modification change
quand son contenu change — et la liste obtenue dépendrait alors de l'état
antérieur du répertoire. Restreindre aux fichiers rend la réponse
prévisible. C'est ainsi qu'on repère, dans un répertoire de résultats qui
grossit, ce qui vient d'être produit par le dernier lancement d'un script.

### Combiner les critères

Les critères de `find` s'enchaînent simplement les uns après les autres : par
défaut, `find` les combine avec un « et » implicite. Cherchons, dans
`data/reads`, les fichiers de plus de 40 kilo-octets dont le nom contient
`R1` :

<!-- verif: ordre-libre -->
```bash
find data/reads -type f -size +40k -name "*_R1*"
```

```output
data/reads/ech05_R1.fastq.gz
data/reads/ech06_R1.fastq.gz
data/reads/ech03_R1.fastq.gz
data/reads/ech04_R1.fastq.gz
data/reads/ech01_R1.fastq.gz
data/reads/ech02_R1.fastq.gz
```

Chaque critère supplémentaire réduit la liste : c'est un filtre qui se
resserre, pas une addition de résultats.

## Agir sur les fichiers trouvés

### `-exec … {} \;` : une commande par fichier

`-exec` lance une commande pour chaque fichier trouvé. `{}` est remplacé par
le chemin du fichier, et `\;` marque la fin de la commande (l'antislash
empêche le shell d'interpréter ce point-virgule lui-même) :

<!-- verif: ordre-libre -->
```bash
find data/brut_desordre -iname "*.fastq" -exec wc -l {} \;
```

```output
100 data/brut_desordre/Ech04_final_VRAIMENT_final.fastq
100 data/brut_desordre/Echantillon 01 - Run mars.fastq
100 data/brut_desordre/ech 03 (copie).fastq
100 data/brut_desordre/ech05.resultats.fastq
100 data/brut_desordre/ech06 -- a refaire.fastq
100 data/brut_desordre/echantillon_02.FASTQ
```

Avec `\;`, `wc` est relancé séparément pour chaque fichier : six fichiers,
six processus `wc`. Avec `+` à la place, `find` regroupe autant de fichiers
que possible dans un minimum d'appels :

<!-- verif: exec-seulement -->
```bash
find data/brut_desordre -iname "*.fastq" -exec wc -l {} +
```

```output
 100 data/brut_desordre/Ech04_final_VRAIMENT_final.fastq
 100 data/brut_desordre/Echantillon 01 - Run mars.fastq
 100 data/brut_desordre/ech 03 (copie).fastq
 100 data/brut_desordre/ech05.resultats.fastq
 100 data/brut_desordre/ech06 -- a refaire.fastq
 100 data/brut_desordre/echantillon_02.FASTQ
 600 total
```

La différence se voit ici : `wc` reçoit les six fichiers en un seul appel et
peut donc afficher un total. Avec `\;`, chaque appel ne voit qu'un fichier et
il n'y a pas de total. Sur six petits fichiers la différence de vitesse est
négligeable, mais sur des milliers de fichiers, lancer un processus par
fichier (`\;`) devient nettement plus lent que les regrouper (`+`) : chaque
processus a un coût de démarrage.

::: callout

## `{}` doit rester seul avec `+`

Avec `-exec … {} +`, `{}` ne peut apparaître qu'une seule fois, en dernière
position. C'est parce que tous les fichiers trouvés sont ajoutés à sa place en
une seule fois, comme des arguments supplémentaires à la commande. Avec
`\;`, `{}` peut apparaître plusieurs fois puisque la commande est reconstruite
à chaque fichier.

:::

### `-delete` : à n'utiliser qu'après avoir regardé

`-delete` supprime directement les fichiers trouvés, sans confirmation. La
règle de sécurité est simple : on lance toujours d'abord la recherche seule,
on lit la liste, et on n'ajoute `-delete` qu'une fois certain qu'elle ne
contient que ce qu'on veut supprimer.

::: caution

## Toujours regarder avant de supprimer

`find … -delete` ne demande jamais confirmation, à la différence de `rm -i`
vu à l'épisode 3. Une erreur de critère (`-size +1k` au lieu de `-size -1k`,
un `-maxdepth` oublié) supprime immédiatement les mauvais fichiers, sans
corbeille pour les récupérer.

La méthode qui évite l'accident :

```bash
find tmp -name "*.txt" -type f
```

Si, et seulement si, la liste affichée correspond exactement à ce que vous
voulez supprimer, vous rajoutez `-delete` à la fin de la même commande, sans
rien changer d'autre.

:::

Illustrons sur un fichier jetable, dans `tmp/` :

<!-- verif: ignore -->
```bash
touch tmp/a_supprimer.txt
find tmp -name "*.txt" -type f
```

```output
tmp/a_supprimer.txt
```

La liste ne contient que le fichier attendu. On ajoute `-delete` :

```bash
find tmp -name "*.txt" -type f -delete
```

```bash
find tmp -name "*.txt" -type f
```

```output
```

Le fichier a disparu, et rien d'autre dans `tmp/` n'a été touché.

:::::::::::::::::::::::::::::::::::::::::  challenge

## Les gros fichiers du jeu de données

Trouvez tous les fichiers de `data` (pas seulement `data/reads`) qui dépassent
100 kilo-octets.

:::::::::::::::  solution

## Solution

<!-- verif: ordre-libre -->
```bash
find data -type f -size +100k
```

```output
data/genome/ref_toy.fa
```

Seul le génome de référence dépasse ce seuil : les fichiers de lectures, pris
individuellement, restent en dessous de 100 kilo-octets chacun.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

## Construire une liste de fichiers sûre : `-print0`

Les noms de `data/brut_desordre/` contiennent des espaces. Une boucle `for
f in $(find …)` casserait ces noms au premier espace, exactement comme
l'épisode 16 l'a montré pour les variables non protégées. La solution vue à
l'épisode 16 se combine ici avec `find` : `-print0` sépare les résultats par
un octet nul plutôt que par un saut de ligne, et `while read -r -d ''` les
relit sans jamais couper sur un espace.

<!-- verif: ordre-libre -->
```bash
find data/brut_desordre -iname "*.fastq" -print0 | while read -r -d '' fichier; do
  echo "trouve : $fichier"
done
```

```output
trouve : data/brut_desordre/Ech04_final_VRAIMENT_final.fastq
trouve : data/brut_desordre/Echantillon 01 - Run mars.fastq
trouve : data/brut_desordre/ech 03 (copie).fastq
trouve : data/brut_desordre/ech05.resultats.fastq
trouve : data/brut_desordre/ech06 -- a refaire.fastq
trouve : data/brut_desordre/echantillon_02.FASTQ
```

`-d ''` dit à `read` d'utiliser l'octet nul comme séparateur au lieu du saut
de ligne, ce qui correspond exactement à ce que produit `-print0`. `-r`
empêche `read` d'interpréter les antislashs. Le nom complet, espaces et
parenthèses compris, arrive intact dans `$fichier`.

Servons-nous de cet inventaire pour compter les lectures de chaque fichier
mal nommé, avant de songer à les renommer proprement :

<!-- verif: ordre-libre -->
```bash
find data/brut_desordre -iname "*.fastq" -print0 | while read -r -d '' fichier; do
  n_lignes=$(wc -l < "$fichier")
  echo "$fichier : $((n_lignes / 4)) lectures"
done
```

```output
data/brut_desordre/Ech04_final_VRAIMENT_final.fastq : 25 lectures
data/brut_desordre/Echantillon 01 - Run mars.fastq : 25 lectures
data/brut_desordre/ech 03 (copie).fastq : 25 lectures
data/brut_desordre/ech05.resultats.fastq : 25 lectures
data/brut_desordre/ech06 -- a refaire.fastq : 25 lectures
data/brut_desordre/echantillon_02.FASTQ : 25 lectures
```

Chaque fichier contient 100 lignes, donc 25 lectures FASTQ (quatre lignes par
lecture, rappel de l'épisode 1 et de l'épisode 5).

:::::::::::::::::::::::::::::::::::::::::  challenge

## Inventaire complet de `data/brut_desordre`

En vous inspirant de l'exemple précédent, écrivez une commande qui affiche,
pour chaque fichier de `data/brut_desordre` quel que soit son type
(`.fastq`, `.FASTQ`, `.txt`), sa taille en octets suivie de son nom. Indice :
`wc -c` compte les octets.

:::::::::::::::  solution

## Solution

<!-- verif: ordre-libre -->
```bash
find data/brut_desordre -type f -print0 | while read -r -d '' fichier; do
  taille=$(wc -c < "$fichier")
  echo "$taille $fichier"
done
```

```output
    6300 data/brut_desordre/Ech04_final_VRAIMENT_final.fastq
    6300 data/brut_desordre/ech 03 (copie).fastq
    6300 data/brut_desordre/Echantillon 01 - Run mars.fastq
    6300 data/brut_desordre/echantillon_02.FASTQ
     127 data/brut_desordre/notes du 12 mars.txt
    6300 data/brut_desordre/ech06 -- a refaire.fastq
    6300 data/brut_desordre/ech05.resultats.fastq
     127 data/brut_desordre/RESUME Manip.txt
```

Sans `-iname` ni `-name`, `-type f` seul suffit à prendre tous les fichiers du
répertoire, y compris les deux fichiers `.txt` qui n'étaient pas concernés par
les exemples précédents. `-print0` associé à `while read -r -d ''` protège de
la même façon tous ces noms, qu'ils contiennent des espaces, des majuscules ou
des parenthèses.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

## `xargs` : transformer une liste en arguments

`xargs` lit une liste sur l'entrée standard et construit avec elle une ligne
de commande. C'est une autre façon d'agir sur les résultats de `find`,
complémentaire de `-exec`.

<!-- verif: ordre-libre -->
```bash
find data/reads -name "*_R1*" -print0 | xargs -0 wc -l
```

```output
     170 data/reads/ech05_R1.fastq.gz
     163 data/reads/ech06_R1.fastq.gz
     156 data/reads/ech03_R1.fastq.gz
     138 data/reads/ech04_R1.fastq.gz
     140 data/reads/ech01_R1.fastq.gz
     155 data/reads/ech02_R1.fastq.gz
     922 total
```

`-0` dit à `xargs` que l'entrée est séparée par des octets nuls, en écho au
`-print0` de `find` : la même précaution contre les espaces dans les noms
s'applique ici aussi.

`-n` limite le nombre d'arguments passés à chaque appel de la commande :

<!-- verif: ordre-libre -->
```bash
find data/reads -name "*_R1*" -print0 | xargs -0 -n 2 echo "paire :"
```

```output
paire : data/reads/ech01_R1.fastq.gz data/reads/ech02_R1.fastq.gz
paire : data/reads/ech03_R1.fastq.gz data/reads/ech04_R1.fastq.gz
paire : data/reads/ech05_R1.fastq.gz data/reads/ech06_R1.fastq.gz
```

`-I{}` remplace un jeton par chaque élément de la liste, un par un, ce qui
permet de le placer où l'on veut dans la commande plutôt qu'à la fin :

<!-- verif: exec-seulement -->
```bash
find data/reads -name "*_R1*" -print0 | xargs -0 -I{} gunzip -c {} \
  | wc -l
```

```output
   12000
```

Ici, `{}` est remplacé successivement par chacun des six fichiers, et
`gunzip -c` envoie leur contenu décompressé, l'un après l'autre, dans le même
tube vers `wc -l`.

## Paralléliser avec `xargs -P`

Jusqu'ici, `xargs` traite les éléments un par un, dans l'ordre. `-P` change
cela : il indique le nombre de commandes à exécuter en même temps. Écrivons un
petit script de traitement, volontairement lent, pour rendre la différence
visible :

<!-- verif-setup:
mkdir -p scripts
cat > scripts/traiter_echantillon.sh <<'FIN'
#!/usr/bin/env bash
set -euo pipefail
fichier="$1"
nom=$(basename "$fichier" .fastq.gz)
n_lignes=$(gunzip -c "$fichier" | wc -l)
sleep 1
echo "$nom : $((n_lignes / 4)) lectures" > "resultats/${nom}.txt"
FIN
chmod +x scripts/traiter_echantillon.sh
-->

Créez le script avec votre éditeur :

<!-- verif: ignore -->

```bash
nano scripts/traiter_echantillon.sh
```

<!-- verif: ignore -->
Et donnez-lui ce contenu :

<!-- verif: fichier scripts/traiter_echantillon.sh -->

```bash
#!/usr/bin/env bash
set -euo pipefail
fichier="$1"
nom=$(basename "$fichier" .fastq.gz)
n_lignes=$(gunzip -c "$fichier" | wc -l)
sleep 1
echo "$nom : $((n_lignes / 4)) lectures" > "resultats/${nom}.txt"
```

Ce script compte les lectures d'un fichier FASTQ compressé et écrit le
résultat dans `resultats/`. Le `sleep 1` simule un traitement qui prend du
temps — une étape de nettoyage ou d'alignement réelle, plutôt qu'un simple
comptage. Rendez-le exécutable :

```bash
chmod +x scripts/traiter_echantillon.sh
```

Traitons d'abord les six fichiers `_R1` en série, avec `-n 1` (un fichier par
appel) et `time` pour mesurer la durée totale :

<!-- verif: exec-seulement -->
```bash
time (find data/reads -name "*_R1*" -print0 \
  | xargs -0 -n 1 scripts/traiter_echantillon.sh)
```

```output
```

Six fichiers, un `sleep 1` chacun, exécutés l'un après l'autre : la durée
réelle (*real*) tourne autour de six secondes. Maintenant, avec `-P 4`, quatre
appels s'exécutent en même temps :

<!-- verif: exec-seulement -->
```bash
rm -f resultats/ech0*.txt
time (find data/reads -name "*_R1*" -print0 \
  | xargs -0 -P 4 -n 1 scripts/traiter_echantillon.sh)
```

```output

real	0m2.XXXs
user	0m0.XXXs
sys	0m0.XXXs
```

Avec quatre traitements en parallèle sur six fichiers, la durée réelle chute
nettement, alors que le temps de travail effectif cumulé (*user* + *sys*)
reste comparable. C'est la signature d'un travail qui attend plus qu'il ne
calcule : ici l'attente est artificielle (`sleep 1`), mais elle a le même
effet qu'une vraie opération d'entrée/sortie qui laisse le processeur inactif.

Vérifions que les six résultats sont bien là, quel que soit l'ordre dans
lequel ils ont fini :

<!-- verif: ordre-libre -->
```bash
cat resultats/ech0*.txt
```

```output
ech01_R1 : 500 lectures
ech02_R1 : 500 lectures
ech03_R1 : 500 lectures
ech04_R1 : 500 lectures
ech05_R1 : 500 lectures
ech06_R1 : 500 lectures
```

## `&` et `wait` : paralléliser sans `xargs`

`xargs -P` convient bien quand la même commande s'applique à une liste de
fichiers. Pour lancer à la main quelques commandes différentes en parallèle,
le shell offre `&`, qui lance une commande en arrière-plan et rend
immédiatement l'invite, et `wait`, qui attend que tous les arrière-plans
lancés soient terminés.

<!-- verif: exec-seulement -->
```bash
scripts/traiter_echantillon.sh data/reads/ech01_R1.fastq.gz &
scripts/traiter_echantillon.sh data/reads/ech02_R1.fastq.gz &
scripts/traiter_echantillon.sh data/reads/ech03_R1.fastq.gz &
wait
echo "les trois traitements sont termines"
```

```output
les trois traitements sont termines
```

Chaque `&` détache la commande qui le précède : le shell continue
immédiatement sans attendre qu'elle finisse, et affiche le numéro du
processus lancé. `wait`, sans argument, bloque jusqu'à ce que tous les
processus d'arrière-plan de ce shell se terminent. Sans ce `wait`, le message
final pourrait s'afficher avant la fin des trois traitements.

`xargs -P` reste préférable dès que la liste dépasse quelques éléments : il
gère lui-même la limite du nombre de processus simultanés, alors qu'enchaîner
des `&` à la main pour vingt fichiers demanderait une boucle et un compteur.
`&`/`wait` a sa place pour deux ou trois commandes ponctuelles, différentes
les unes des autres.

:::::::::::::::::::::::::::::::::::::::::  challenge

## Paralléliser les fichiers `_R2`

Répétez le traitement en parallèle, cette fois sur les fichiers `_R2` de
`data/reads`, avec `xargs -P 4`.

:::::::::::::::  solution

## Solution

<!-- verif: ordre-libre -->
```bash
find data/reads -name "*_R2*" -print0 \
  | xargs -0 -P 4 -n 1 scripts/traiter_echantillon.sh
cat resultats/ech0*_R2.txt
```

```output
ech01_R2 : 500 lectures
ech02_R2 : 500 lectures
ech03_R2 : 500 lectures
ech04_R2 : 500 lectures
ech05_R2 : 500 lectures
ech06_R2 : 499 lectures
```

`ech04_R2` est tronqué (1 998 lignes, rappel de l'épisode 4 et de l'épisode
15) : la division par quatre le laisse à 499 lectures complètes, la dernière
étant coupée. `xargs -P` ne s'en aperçoit pas — il lance simplement le script
sur chaque fichier — mais le résultat porte la trace de l'anomalie.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::::  challenge

## Pourquoi ce nombre de processus et pas un autre

Sur un ordinateur portable à deux cœurs, un collègue lance
`xargs -P 16 -n 1 scripts/traiter_echantillon.sh` sur une liste de vingt
fichiers dont le traitement est limité par le calcul (beaucoup d'arithmétique,
peu de lecture disque). Il se plaint que ce n'est pas plus rapide qu'avec
`-P 2`. Pourquoi ?

:::::::::::::::  solution

## Solution

Un processeur à deux cœurs ne peut exécuter que deux calculs à la fois. Lancer
seize traitements simultanés quand seuls deux peuvent réellement progresser en
même temps ne fait qu'ajouter du changement de contexte entre processus, sans
accélérer le calcul lui-même. Au-delà du nombre de cœurs disponibles, augmenter
`-P` n'apporte rien pour un travail limité par le calcul, et peut même
ralentir légèrement l'ensemble.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

## Quand la parallélisation aide, et quand elle ne sert à rien

L'exemple avec `sleep 1` était volontairement favorable à `-P` : le script
n'utilisait presque pas le processeur, il attendait. Il faut être honnête sur
les limites de cette technique.

- **Travail limité par le processeur** (calculs, compression, alignement) :
  la parallélisation aide, jusqu'à concurrence du nombre de cœurs disponibles
  sur la machine. Au-delà, elle n'apporte plus rien, comme le montre le défi
  précédent.
- **Travail limité par les entrées/sorties** (lecture ou écriture de gros
  fichiers sur un disque, en particulier un disque mécanique ou un support
  réseau) : plusieurs processus qui lisent en même temps se disputent le même
  disque. La parallélisation peut alors ralentir l'ensemble plutôt que
  l'accélérer, parce que le disque passe son temps à sauter d'un fichier à
  l'autre au lieu de lire en continu.
- **Travail limité par la mémoire** : si chaque traitement charge un gros
  fichier en mémoire, en lancer quatre à la fois peut épuiser la mémoire
  disponible et forcer le système à utiliser le disque comme mémoire
  d'appoint (*swap*), ce qui est très lent. Mieux vaut alors un `-P` bas,
  voire `-P 1`.

Il n'existe pas de valeur de `-P` universellement bonne : elle dépend de la
nature du traitement et de la machine. Dans le doute, comparez avec `time`,
comme plus haut, plutôt que de supposer.

::: callout

## Pourquoi il existe des gestionnaires de flux de travaux

`xargs -P` et `&`/`wait` parallélisent, mais ne font rien de plus : si le
troisième fichier sur six échoue, les cinq autres continuent sans prévenir
personne, rien n'est journalisé proprement, et relancer uniquement ce qui a
échoué se fait à la main. Des outils dédiés — les gestionnaires de flux de
travaux (*workflow managers*) — ajoutent la reprise sur erreur, la gestion des
dépendances entre étapes et un journal détaillé de chaque exécution. Ils
sortent du cadre de cette formation et font l'objet d'une formation
ultérieure.

:::

:::::::::::::::::::::::::::::::::::::::::  challenge

## Lecture d'un script existant (facultatif)

Un collègue vous montre cette commande et vous demande pourquoi elle a mis
plus de temps à s'exécuter que prévu sur son ordinateur portable, qui n'a que
deux cœurs :

```bash
find data/reads -name "*.fastq.gz" -print0 | xargs -0 -P 12 -n 1 gunzip -c
```

Que répondez-vous, et que changeriez-vous ?

:::::::::::::::  solution

## Solution

Deux problèmes distincts. D'abord, `-P 12` sur une machine à deux cœurs ne
peut aider que si le travail est limité par les entrées/sorties, jamais par
le calcul : ici, `gunzip` décompresse, ce qui sollicite surtout le
processeur, et douze décompressions simultanées sur deux cœurs ne vont pas
plus vite qu'avec `-P 2`. Ensuite, la sortie décompressée de `gunzip -c` part
directement sur la sortie standard du terminal, mélangée entre les douze
processus, sans être ni triée ni enregistrée : même en admettant que la
parallélisation aide, le résultat serait illisible. Il faudrait rediriger
chaque sortie vers un fichier distinct (par exemple avec `-I{}` et une
redirection construite à partir du nom de `{}`) et limiter `-P` à deux ou
trois.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::: keypoints

- `find point_de_depart -name motif` cherche des fichiers par nom ; `-iname` ignore la casse.
- `-type f`, `-type d`, `-maxdepth`, `-size +N` / `-size -N` et `-newer autre_fichier` se combinent librement : chaque critère resserre le résultat.
- `-exec commande {} \;` lance un processus par fichier trouvé ; `-exec commande {} +` regroupe les fichiers en un minimum d'appels.
- `find … -delete` supprime sans confirmation : on regarde toujours la liste produite sans `-delete` avant de l'ajouter.
- `find … -print0` combiné à `while read -r -d ''` construit une liste de fichiers robuste aux espaces, majuscules et parenthèses des noms.
- `xargs -0` lit une liste séparée par des octets nuls ; `-n` limite les arguments par appel, `-I{}` place chaque élément où on le souhaite.
- `xargs -P n` exécute jusqu'à `n` commandes en parallèle ; `&` lance une commande en arrière-plan et `wait` attend la fin de tous les arrière-plans en cours.
- La parallélisation aide un travail limité par le processeur, jusqu'au nombre de cœurs disponibles ; elle n'aide pas, et peut nuire, à un travail limité par le disque ou par la mémoire.
- Les gestionnaires de flux de travaux ajoutent la reprise sur erreur, les dépendances entre étapes et la journalisation : hors du cadre de cette formation.

::::::::::::::::::::::::::::::::::::::::::::::::::::
