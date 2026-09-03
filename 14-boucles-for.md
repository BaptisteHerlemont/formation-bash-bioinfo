---
title: "Traiter tous les échantillons avec une boucle"
teaching: 30
exercises: 25
---

:::::::::::::::::::::::::::::::::::::::  questions

- Comment répéter la même commande sur les six échantillons sans la retaper six fois ?
- Comment construire le nom d'un fichier de sortie à partir du nom d'un fichier d'entrée ?
- Comment vérifier ce qu'une boucle va faire avant de la laisser agir ?

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::: objectives

- Écrire une boucle `for` sur une liste littérale, sur un joker et sur une substitution de commande.
- Extraire le nom d'un fichier ou son répertoire parent avec `basename` et `dirname`.
- Construire un nom de fichier de sortie cohérent à partir d'un nom d'entrée.
- Utiliser `break` et `continue` pour interrompre ou sauter une itération.
- Produire un tableau récapitulatif en bouclant sur les six échantillons.

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::  prereq

Cet épisode suppose que vous savez déjà écrire un script exécutable avec un
shebang, le rendre exécutable avec `chmod +x`, et lui passer des arguments
(`$1`, `$@`, `$#`). Voir l'épisode précédent, *Du one-liner au script*.

::::::::::::::::::::::::::::::::::::::::::::::::::

Depuis le premier jour, vous retapez la même commande pour chaque échantillon,
ech01 puis ech02 puis ech03, jusqu'à ech06. C'est fastidieux, et c'est surtout
risqué : à la sixième répétition, on recopie mal une ligne, on oublie de
changer un numéro, on ne s'en rend pas compte. La boucle `for` permet de dire
une seule fois « fais ceci », et de laisser le shell répéter l'opération pour
chaque échantillon.

Commencez par vous placer dans votre répertoire de travail et créez les
répertoires dont vous aurez besoin aujourd'hui.

```bash
mkdir -p resultats tmp scripts
```

## La forme générale d'une boucle `for`

Une boucle `for` a toujours la même structure : une liste de valeurs, une
variable qui prend tour à tour chacune de ces valeurs, et un bloc de commandes
exécuté à chaque tour.

```bash
for echantillon in ech01 ech02 ech03
do
  echo "traitement de l'échantillon : $echantillon"
done
```

```output
traitement de l'échantillon : ech01
traitement de l'échantillon : ech02
traitement de l'échantillon : ech03
```

Trois éléments à retenir dans cette syntaxe :

- `for VARIABLE in LISTE` : `VARIABLE` est un nom que vous choisissez librement
  (ici `echantillon`), `LISTE` est une suite de mots séparés par des espaces.
- `do` ouvre le bloc de commandes, `done` le ferme. Entre les deux, on utilise
  `$echantillon` (avec le signe dollar) pour lire la valeur courante de la
  variable.
- La boucle s'exécute une fois par élément de la liste, dans l'ordre où ils
  sont écrits.

On peut aussi écrire la boucle sur une seule ligne, en séparant les mots-clés
par des points-virgules. C'est la forme que vous verrez le plus souvent dans
des scripts existants :

```bash
for echantillon in ech01 ech02 ech03; do echo "traitement de : $echantillon"; done
```

```output
traitement de : ech01
traitement de : ech02
traitement de : ech03
```

Les deux formes sont rigoureusement équivalentes. La forme multi-lignes est
plus lisible pour un bloc de commandes ; la forme sur une ligne est pratique
pour une vérification rapide à l'invite.

::::::::::::::::::::::::::::::::::::::::  callout

## La règle d'or : `echo` avant d'agir

Avant de laisser une boucle créer, déplacer ou supprimer des fichiers,
remplacez temporairement la commande finale par un `echo` qui affiche ce
qu'elle *aurait* fait. Vous voyez ainsi les six lignes qui vont s'exécuter,
vous repérez une erreur de construction de nom avant qu'elle ne produise six
fichiers mal nommés, puis vous retirez le `echo` pour de bon. Cette leçon
applique systématiquement cette règle, et vous devriez en faire une habitude
au moins aussi automatique que de sauvegarder un fichier avant de le modifier.

::::::::::::::::::::::::::::::::::::::::::::::::::

## Boucler sur un joker

Écrire `ech01 ech02 ech03 ech04 ech05 ech06` à la main reste fastidieux, et le
principe même d'une boucle est d'éviter ce genre d'énumération. La liste après
`in` peut être un joker (*wildcard*), que le shell développe en la liste des
fichiers correspondants avant même que la boucle ne démarre.

```bash
for fichier in data/reads/*_R1.fastq.gz
do
  echo "fichier trouvé : $fichier"
done
```

```output
fichier trouvé : data/reads/ech01_R1.fastq.gz
fichier trouvé : data/reads/ech02_R1.fastq.gz
fichier trouvé : data/reads/ech03_R1.fastq.gz
fichier trouvé : data/reads/ech04_R1.fastq.gz
fichier trouvé : data/reads/ech05_R1.fastq.gz
fichier trouvé : data/reads/ech06_R1.fastq.gz
```

Le shell a remplacé `data/reads/*_R1.fastq.gz` par la liste triée des six
chemins correspondants avant de lancer la boucle. `$fichier` contient donc à
chaque tour un chemin complet, pas seulement un nom de fichier.

::::::::::::::::::::::::::::::::::::::::  callout

## Quand aucun fichier ne correspond au joker

Que se passe-t-il si le joker ne correspond à aucun fichier ? Testez :

```bash
for fichier in data/reads/*.bam
do
  echo "fichier trouvé : $fichier"
done
```

```output
fichier trouvé : data/reads/*.bam
```

Il n'y a aucun fichier `.bam` dans `data/reads/`, et pourtant la boucle
s'exécute une fois, avec le motif littéral `data/reads/*.bam` comme valeur de
`$fichier`. C'est le comportement par défaut de Bash : quand un joker ne
développe rien, il est laissé tel quel, comme une simple chaîne de
caractères. Une boucle qui suppose que `$fichier` désigne toujours un fichier
existant peut donc essayer de lire un fichier appelé littéralement
`*.bam`, qui n'existe pas, et échouer de façon déroutante. L'épisode suivant,
*Tests et code défensif*, montre comment se protéger de ce cas avec `test -f`.

::::::::::::::::::::::::::::::::::::::::::::::::::

## Boucler sur le résultat d'une commande

La troisième forme de liste est une substitution de commande (*command
substitution*) : `$(commande)`. Le shell exécute d'abord la commande entre
parenthèses, capture sa sortie, puis boucle sur les mots qu'elle contient.

```bash
for gene in $(cut -f2 data/tables/comptages.tsv | head -4 | tail -3)
do
  echo "gène : $gene"
done
```

```output
gène : arf4D
gène : eef3B
gène : rho6B
```

`cut -f2 data/tables/comptages.tsv` extrait la deuxième colonne (le nom du
gène) de tout le fichier, `head -4` en garde les quatre premières lignes (la
ligne d'en-tête et les trois premiers gènes), `tail -3` retire l'en-tête. Le
résultat, trois noms de gènes séparés par des retours à la ligne, est passé à
la boucle : chaque mot devient une valeur de `$gene`.

::::::::::::::::::::::::::::::::::::::::  callout

## Pourquoi ne pas boucler directement sur les lignes d'un fichier

Vous serez tenté d'écrire `for ligne in $(cat fichier.tsv)`. Résistez : le
shell découpe la sortie de `$(...)` sur les espaces *et* sur les retours à la
ligne, ce qui mélange les colonnes d'une même ligne avec les colonnes des
lignes suivantes dès qu'un champ contient un espace. Ici, comme on ne boucle
que sur une seule colonne déjà extraite par `cut`, il n'y a pas d'ambiguïté.
Pour boucler correctement ligne par ligne sur un tableau entier, on utilise
`while read -r`, vu à l'épisode *Fonctions et pilotage par feuille
d'échantillons*.

::::::::::::::::::::::::::::::::::::::::::::::::::

## `basename` et `dirname`

Une fois qu'on boucle sur des chemins complets comme
`data/reads/ech01_R1.fastq.gz`, on a souvent besoin d'en extraire seulement le
nom de fichier, ou seulement le répertoire. `basename` retire le chemin du
répertoire ; `dirname` fait l'inverse.

```bash
basename data/reads/ech01_R1.fastq.gz
```

```output
ech01_R1.fastq.gz
```

```bash
dirname data/reads/ech01_R1.fastq.gz
```

```output
data/reads
```

`basename` accepte un second argument : un suffixe à retirer en plus du
chemin. C'est la façon la plus directe d'obtenir le nom de l'échantillon seul,
sans l'extension.

```bash
basename data/reads/ech01_R1.fastq.gz _R1.fastq.gz
```

```output
ech01
```

En combinant `basename` avec suffixe et une boucle sur le joker, on obtient le
nom de chaque échantillon sans rien retaper à la main :

```bash
for r1 in data/reads/*_R1.fastq.gz
do
  echantillon=$(basename "$r1" _R1.fastq.gz)
  echo "échantillon : $echantillon"
done
```

```output
échantillon : ech01
échantillon : ech02
échantillon : ech03
échantillon : ech04
échantillon : ech05
échantillon : ech06
```

Remarquez les guillemets doubles autour de `"$r1"` : ils protègent le chemin
au cas où il contiendrait un espace. L'épisode *Variables, guillemets et
substitution de commandes* reviendra en détail sur cette protection ; pour
l'instant, prenez l'habitude de toujours mettre une variable de chemin entre
guillemets doubles.

## Construire un nom de sortie à partir d'un nom d'entrée

Le schéma qui revient sans cesse en bioinformatique est : lire un fichier
d'entrée, produire un fichier de sortie dont le nom rappelle celui de
l'entrée. On applique la règle d'or avant d'écrire quoi que ce soit sur le
disque : on `echo` d'abord la commande qui *serait* exécutée.

```bash
for r1 in data/reads/*_R1.fastq.gz
do
  echantillon=$(basename "$r1" _R1.fastq.gz)
  echo "gunzip -c $r1 > tmp/${echantillon}_R1.fastq"
done
```

```output
gunzip -c data/reads/ech01_R1.fastq.gz > tmp/ech01_R1.fastq
gunzip -c data/reads/ech02_R1.fastq.gz > tmp/ech02_R1.fastq
gunzip -c data/reads/ech03_R1.fastq.gz > tmp/ech03_R1.fastq
gunzip -c data/reads/ech04_R1.fastq.gz > tmp/ech04_R1.fastq
gunzip -c data/reads/ech05_R1.fastq.gz > tmp/ech05_R1.fastq
gunzip -c data/reads/ech06_R1.fastq.gz > tmp/ech06_R1.fastq
```

Les six lignes sont exactement celles que l'on voulait : chaque fichier
compressé donne un fichier décompressé de même nom, dans `tmp/`. On peut
maintenant retirer le `echo` en confiance.

```bash
for r1 in data/reads/*_R1.fastq.gz
do
  echantillon=$(basename "$r1" _R1.fastq.gz)
  gunzip -c "$r1" > "tmp/${echantillon}_R1.fastq"
done
```

Notez l'utilisation de `${echantillon}` avec des accolades : elles délimitent
clairement le nom de la variable, ce qui est nécessaire dès qu'un caractère
non ambigu suit immédiatement, comme le `_` ci-dessus (`$echantillon_R1`
serait interprété comme la variable `echantillon_R1`, qui n'existe pas).

Vérifiez le résultat :

<!-- verif: ordre-libre -->
```bash
ls tmp/
```

```output
ech01_R1.fastq
ech02_R1.fastq
ech03_R1.fastq
ech04_R1.fastq
ech05_R1.fastq
ech06_R1.fastq
```

## Boucles imbriquées

On peut placer une boucle `for` à l'intérieur d'une autre. C'est utile quand
deux dimensions doivent être croisées, par exemple les six échantillons et
leurs deux lectures appariées (R1 et R2). À utiliser avec modération : deux
niveaux d'imbrication restent lisibles, au-delà le script devient difficile à
suivre.

```bash
for echantillon in ech01 ech02 ech03 ech04 ech05 ech06
do
  for brin in R1 R2
  do
    echo "$echantillon $brin : data/reads/${echantillon}_${brin}.fastq.gz"
  done
done
```

```output
ech01 R1 : data/reads/ech01_R1.fastq.gz
ech01 R2 : data/reads/ech01_R2.fastq.gz
ech02 R1 : data/reads/ech02_R1.fastq.gz
ech02 R2 : data/reads/ech02_R2.fastq.gz
ech03 R1 : data/reads/ech03_R1.fastq.gz
ech03 R2 : data/reads/ech03_R2.fastq.gz
ech04 R1 : data/reads/ech04_R1.fastq.gz
ech04 R2 : data/reads/ech04_R2.fastq.gz
ech05 R1 : data/reads/ech05_R1.fastq.gz
ech05 R2 : data/reads/ech05_R2.fastq.gz
ech06 R1 : data/reads/ech06_R1.fastq.gz
ech06 R2 : data/reads/ech06_R2.fastq.gz
```

Pour chaque valeur de `$echantillon` (boucle externe), la boucle interne
s'exécute entièrement pour `R1` puis `R2` avant de passer à l'échantillon
suivant.

## `seq`

Quand on a besoin d'une suite de nombres plutôt que d'une liste de noms,
`seq debut fin` produit les entiers de `debut` à `fin`, un par ligne.

```bash
seq 1 6
```

```output
1
2
3
4
5
6
```

Combiné à `printf`, `seq` permet de reconstruire les noms des échantillons
sans les écrire à la main, à condition de gérer le zéro initial :

```bash
for i in $(seq 1 6)
do
  numero=$(printf '%02d' "$i")
  echo "échantillon numéro : ech${numero}"
done
```

```output
échantillon numéro : ech01
échantillon numéro : ech02
échantillon numéro : ech03
échantillon numéro : ech04
échantillon numéro : ech05
échantillon numéro : ech06
```

Dans le jeu de données de cette formation, boucler sur le joker
`data/reads/*_R1.fastq.gz` est presque toujours préférable à reconstruire les
noms avec `seq` : le joker s'adapte automatiquement si un échantillon est
ajouté ou retiré, alors que `seq 1 6` reste figé à six. Gardez `seq` pour les
cas où vous avez réellement besoin de nombres, par exemple pour numéroter des
lignes ou répéter une opération un nombre fixe de fois.

## `break` et `continue`

Deux instructions permettent de dévier du déroulement normal d'une boucle.
`break` arrête complètement la boucle et passe à ce qui suit `done`.
`continue` arrête seulement le tour en cours et passe directement à
l'itération suivante.

```bash
for echantillon in ech01 ech02 ech03 ech04 ech05 ech06
do
  if [ "$echantillon" = "ech04" ]
  then
    echo "arrêt à $echantillon"
    break
  fi
  echo "traitement de $echantillon"
done
```

```output
traitement de ech01
traitement de ech02
traitement de ech03
arrêt à ech04
```

La boucle ne va jamais jusqu'à ech06 : dès que la condition `break` est
atteinte, la boucle s'arrête entièrement. `continue`, en revanche, laisse la
boucle se poursuivre en sautant seulement le reste du tour courant :

```bash
for echantillon in ech01 ech02 ech03 ech04 ech05 ech06
do
  if [ "$echantillon" = "ech04" ]
  then
    echo "on saute $echantillon"
    continue
  fi
  echo "traitement de $echantillon"
done
```

```output
traitement de ech01
traitement de ech02
traitement de ech03
on saute ech04
traitement de ech05
traitement de ech06
```

Ici, ech01, ech02, ech03, ech05 et ech06 sont traités ; seul ech04 est
annoncé comme sauté puis la boucle continue normalement. La syntaxe complète
de `if` sera détaillée dans le prochain épisode ; retenez pour l'instant
seulement `break` et `continue`, qui se comprennent sans elle.

## La variable de boucle et sa portée

La variable de boucle n'est pas une variable spéciale : c'est une variable
de shell ordinaire, qui existe encore après la fin de la boucle, avec la
dernière valeur qu'elle a prise.

```bash
for echantillon in ech01 ech02 ech03
do
  :
done
echo "après la boucle, echantillon vaut : $echantillon"
```

```output
après la boucle, echantillon vaut : ech03
```

(`:` est une commande qui ne fait rien ; elle sert ici uniquement à donner un
corps valide à la boucle.) Cette persistance a une conséquence pratique
importante : si vous réutilisez le même nom de variable dans deux boucles
successives, la seconde boucle écrase silencieusement la valeur laissée par
la première, ce qui ne pose en général pas de problème puisque chaque boucle
réattribue la variable dès son premier tour. Le risque apparaît plutôt quand
on utilise la variable de boucle *après* la boucle en pensant qu'elle
contient encore une valeur particulière : elle contient la dernière valeur de
la liste, pas une valeur remise à vide.

::::::::::::::::::::::::::::::::::::::::::::::::::  caution

## Les noms de fichiers avec espaces cassent une boucle simple

Le répertoire `data/brut_desordre/` contient des fichiers aux noms peu
soignés, avec des espaces. Observez ce qui se passe avec la construction de
boucle que vous venez d'apprendre :

```bash
for f in data/brut_desordre/*
do
  echo "fichier : $f"
done
```

```output
fichier : data/brut_desordre/Ech04_final_VRAIMENT_final.fastq
fichier : data/brut_desordre/Echantillon 01 - Run mars.fastq
fichier : data/brut_desordre/RESUME Manip.txt
fichier : data/brut_desordre/ech 03 (copie).fastq
fichier : data/brut_desordre/ech05.resultats.fastq
fichier : data/brut_desordre/ech06 -- a refaire.fastq
fichier : data/brut_desordre/echantillon_02.FASTQ
fichier : data/brut_desordre/notes du 12 mars.txt
```

Le fichier `Echantillon 01 - Run mars.fastq` n'existe pas en un seul morceau
pour cette boucle : le shell l'a découpé sur chaque espace en autant de mots
séparés, aucun d'entre eux ne correspondant à un fichier réel. La variable
`$f` n'a pas été protégée par des guillemets au moment où le joker a été
développé, et le découpage en mots (*word splitting*) s'applique. Ce
comportement, et la manière de s'en protéger, fait l'objet d'un épisode
entier un peu plus loin dans la formation ; pour l'instant, retenez seulement
qu'un nom de fichier contenant un espace n'est jamais anodin en Bash.

::::::::::::::::::::::::::::::::::::::::::::::::::

## Traiter les six échantillons : contrôle qualité minimal

Vous disposez maintenant de tout ce qu'il faut pour répondre à une vraie
question : pour chacun des six échantillons, R1 et R2 ont-ils le même nombre
de lectures ? C'est la première vérification qu'on fait avant de considérer
un séquençage comme exploitable, puisque des lectures appariées doivent
toujours venir en même nombre des deux côtés.

On applique la règle d'or une dernière fois avant d'écrire le fichier final.

```bash
for r1 in data/reads/*_R1.fastq.gz
do
  echantillon=$(basename "$r1" _R1.fastq.gz)
  r2="data/reads/${echantillon}_R2.fastq.gz"
  echo "echantillon=$echantillon r1=$r1 r2=$r2"
done
```

```output
echantillon=ech01 r1=data/reads/ech01_R1.fastq.gz r2=data/reads/ech01_R2.fastq.gz
echantillon=ech02 r1=data/reads/ech02_R1.fastq.gz r2=data/reads/ech02_R2.fastq.gz
echantillon=ech03 r1=data/reads/ech03_R1.fastq.gz r2=data/reads/ech03_R2.fastq.gz
echantillon=ech04 r1=data/reads/ech04_R1.fastq.gz r2=data/reads/ech04_R2.fastq.gz
echantillon=ech05 r1=data/reads/ech05_R1.fastq.gz r2=data/reads/ech05_R2.fastq.gz
echantillon=ech06 r1=data/reads/ech06_R1.fastq.gz r2=data/reads/ech06_R2.fastq.gz
```

Le chemin de R2 est reconstruit à partir du nom de l'échantillon, sans jamais
être lu dans un joker séparé : c'est ce qui garantit qu'on compare bien le R2
qui correspond au R1 du même tour de boucle. On retire le `echo` et on écrit
le tableau dans `resultats/qc_lectures.tsv`, avec un en-tête écrit une seule
fois avant la boucle.

```bash
printf 'echantillon\tlectures_R1\tlectures_R2\tcoherent\n' > resultats/qc_lectures.tsv
for r1 in data/reads/*_R1.fastq.gz
do
  echantillon=$(basename "$r1" _R1.fastq.gz)
  r2="data/reads/${echantillon}_R2.fastq.gz"
  lignes_r1=$(gunzip -c "$r1" | wc -l)
  lignes_r2=$(gunzip -c "$r2" | wc -l)
  lectures_r1=$((lignes_r1 / 4))
  lectures_r2=$((lignes_r2 / 4))
  if [ "$lectures_r1" -eq "$lectures_r2" ]
  then
    coherent="oui"
  else
    coherent="NON"
  fi
  printf '%s\t%d\t%d\t%s\n' "$echantillon" "$lectures_r1" "$lectures_r2" "$coherent" >> resultats/qc_lectures.tsv
done
cat resultats/qc_lectures.tsv
```

```output
echantillon	lectures_R1	lectures_R2	coherent
ech01	500	500	oui
ech02	500	500	oui
ech03	500	500	oui
ech04	500	499	NON
ech05	500	500	oui
ech06	500	500	oui
```

L'échantillon ech04 ressort avec une incohérence : 500 lectures en R1 contre
499 en R2. C'est exactement l'anomalie que le journal `pipeline.log` signalait
déjà par une ligne `ERROR` — le fichier `ech04_R2.fastq.gz` est tronqué, son
dernier bloc de quatre lignes est incomplet. Sans la boucle, il aurait fallu
lancer la même vérification six fois pour la remarquer ; avec elle, il suffit
de lire une seule colonne du tableau produit. La construction `if` utilisée
ici pour comparer les deux nombres sera détaillée dans le prochain épisode ;
retenez pour l'instant seulement qu'elle décide, à chaque tour, ce qui est
écrit dans la colonne `coherent`.

:::::::::::::::::::::::::::::::::::::::  challenge

## Défi 1 : boucler sur les fichiers protéiques

Le répertoire `data/proteines/` ne contient qu'un seul fichier,
`proteines.fa`. Écrivez une boucle `for` qui affiche, pour chaque fichier
`.fa` de ce répertoire, une ligne `fichier trouvé : CHEMIN`. Vous ne devez pas
écrire le nom du fichier en dur dans la boucle.

:::::::::::::::  solution

## Solution

```bash
for f in data/proteines/*.fa
do
  echo "fichier trouvé : $f"
done
```

```output
fichier trouvé : data/proteines/proteines.fa
```

Le joker `*.fa` se développe sur un seul fichier ici, mais la boucle
fonctionnerait sans modification si on ajoutait demain un deuxième fichier
`.fa` dans ce répertoire : c'est tout l'intérêt de boucler sur un joker plutôt
que sur un nom écrit en dur.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  challenge

## Défi 2 : compter les gènes annotés

En combinant une boucle `for` sur la liste littérale `chr1 chrM` et une
commande vue à l'épisode 7, affichez, pour chaque contig du génome, le nombre
de lignes de type `gene` qui lui appartiennent dans
`data/genome/annotation.gff3`.

:::::::::::::::  solution

## Solution

```bash
for contig in chr1 chrM
do
  nombre=$(awk -v c="$contig" '$1 == c && $3 == "gene"' data/genome/annotation.gff3 | wc -l)
  echo "$contig : $nombre gènes"
done
```

```output
chr1 :      120 gènes
chrM :        8 gènes
```

`awk -v c="$contig"` transmet la valeur de la variable de boucle à `awk`, qui
sélectionne les lignes dont la première colonne est ce contig et la troisième
colonne vaut `gene`. `wc -l` compte les lignes retenues. Les 128 gènes du
fichier sont tous portés par `chr1` ; `chrM` n'en porte aucun.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  challenge

## Défi 3 : extraire chaque échantillon annoncé dans la feuille d'échantillons

Écrivez une boucle qui affiche, pour chaque `sample_id` de
`data/tables/echantillons.tsv` (sans la ligne d'en-tête), une ligne de la
forme `echantillon annoncé : ech01`. Utilisez une substitution de commande
pour construire la liste.

:::::::::::::::  solution

## Solution

```bash
for echantillon in $(cut -f1 data/tables/echantillons.tsv | tail -n +2)
do
  echo "echantillon annoncé : $echantillon"
done
```

```output
echantillon annoncé : ech01
echantillon annoncé : ech02
echantillon annoncé : ech03
echantillon annoncé : ech04
echantillon annoncé : ech05
echantillon annoncé : ech06
```

`cut -f1` extrait la première colonne, `tail -n +2` retire la ligne d'en-tête
(vue à l'épisode 4). La substitution de commande capture les six identifiants
et la boucle les affiche un par un. Cette liste correspond exactement à celle
obtenue en bouclant sur le joker `data/reads/*_R1.fastq.gz` : c'est cohérent,
puisque la feuille d'échantillons décrit précisément les fichiers présents
dans `data/reads/`.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  challenge

## Défi 4 : que fait cette boucle, et pourquoi s'arrête-t-elle tôt

Sans l'exécuter d'abord, prédisez la sortie de la boucle suivante, puis
vérifiez.

```bash
compteur=0
for echantillon in ech01 ech02 ech03 ech04 ech05 ech06
do
  compteur=$((compteur + 1))
  if [ "$compteur" -gt 3 ]
  then
    break
  fi
  echo "$compteur : $echantillon"
done
echo "boucle terminée, compteur=$compteur"
```

:::::::::::::::  solution

## Solution

```output
1 : ech01
2 : ech02
3 : ech03
boucle terminée, compteur=4
```

À chaque tour, `compteur` est incrémenté avant le test. Les trois premiers
tours (ech01, ech02, ech03) affichent leur ligne car `compteur` vaut alors 1,
2 puis 3, qui ne sont pas strictement supérieurs à 3. Au quatrième tour,
`compteur` passe à 4 avant l'affichage : le test devient vrai, `break` arrête
la boucle immédiatement, et la ligne pour ech04 n'est jamais affichée. La
variable `compteur` garde sa dernière valeur, 4, après la boucle : c'est la
même persistance de variable que celle observée plus haut pour la variable de
boucle elle-même.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  challenge

## Défi 5 : un tableau croisé condition et échantillon (facultatif)

En vous appuyant sur `data/tables/echantillons.tsv`, écrivez une boucle
imbriquée qui affiche, pour chaque condition (`temoin`, `traite`) et pour
chaque numéro de réplicat (1, 2, 3), une ligne
`condition=... replicat=...`. N'utilisez que des listes littérales.

:::::::::::::::  solution

## Solution

```bash
for condition in temoin traite
do
  for replicat in 1 2 3
  do
    echo "condition=$condition replicat=$replicat"
  done
done
```

```output
condition=temoin replicat=1
condition=temoin replicat=2
condition=temoin replicat=3
condition=traite replicat=1
condition=traite replicat=2
condition=traite replicat=3
```

Cette combinaison reproduit exactement la structure de
`data/tables/echantillons.tsv`, qui associe à chaque paire condition/réplicat
un identifiant d'échantillon unique. La boucle imbriquée énumère les six
combinaisons dans le même ordre que le fichier, sans avoir lu le fichier :
c'est un bon exercice de prédiction, mais dans un vrai script on préférera
lire les valeurs directement dans le fichier plutôt que les recopier en dur,
pour rester correct si la feuille d'échantillons change.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::::: keypoints

- `for VARIABLE in LISTE; do COMMANDES; done` répète `COMMANDES` une fois par élément de `LISTE`, littérale, issue d'un joker, ou issue d'une substitution `$(...)`.
- Remplacez toujours d'abord la commande finale par un `echo` pour vérifier ce que la boucle va faire, avant de retirer le `echo`.
- `basename CHEMIN` retire le répertoire, `basename CHEMIN SUFFIXE` retire aussi un suffixe, `dirname CHEMIN` ne garde que le répertoire.
- Un joker qui ne correspond à aucun fichier est laissé tel quel comme chaîne littérale : la boucle s'exécute une fois avec ce motif non développé.
- `break` arrête la boucle entièrement, `continue` saute seulement le tour courant.
- La variable de boucle est une variable de shell ordinaire : elle garde sa dernière valeur après `done`.
- `seq DEBUT FIN` produit une suite d'entiers, utile quand on a réellement besoin de nombres plutôt que de noms de fichiers.
- Un nom de fichier contenant un espace, comme dans `data/brut_desordre/`, est décomposé en plusieurs mots par une boucle sur joker non protégée.

::::::::::::::::::::::::::::::::::::::::::::::::::
