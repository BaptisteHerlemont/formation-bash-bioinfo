---
title: "awk : compter et calculer par groupe"
teaching: 30
exercises: 25
---

:::::::::::::::::::::::::::::::::::::::  questions

- Comment compter le nombre d'entités de chaque type dans une annotation ?
- Comment calculer une moyenne, un minimum, un maximum en une seule lecture du fichier ?
- Comment regrouper des lignes par une clé et faire un total par groupe ?
- Comment extraire un attribut particulier d'une colonne structurée comme la colonne 9 d'un GFF3 ?

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::: objectives

- Utiliser `BEGIN` et `END` pour initialiser et conclure un calcul.
- Accumuler une somme, une moyenne, un minimum et un maximum au fil de la lecture d'un fichier.
- Compter des occurrences par catégorie avec un tableau associatif et une boucle `for (clé in tableau)`.
- Extraire un champ d'un attribut structuré avec `split` et `sub`.

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  prereq

Cet épisode s'appuie directement sur l'épisode 9 (« awk : champs, motifs,
conditions »). Vous devez être à l'aise avec `$0`, `$1`, `NF`, `NR`, `-F` et les
motifs de condition avant de continuer.

::::::::::::::::::::::::::::::::::::::::::::::::::

À l'épisode précédent, vous avez appris à lire `awk` colonne par colonne et à
filtrer des lignes. Mais `awk` sait aussi retenir de l'information d'une ligne
à l'autre : c'est ce qui permet de compter, de sommer, de calculer une moyenne,
ou de regrouper des lignes par catégorie. C'est exactement ce dont vous avez
besoin pour résumer `annotation.gff3`, `ech01.sam` ou `comptages.tsv` en
quelques chiffres.

```bash
mkdir -p resultats tmp
```

## Une variable qui survit d'une ligne à l'autre

Un programme `awk` est fait de blocs `motif { action }`. Jusqu'ici, chaque
bloc s'exécutait indépendamment pour chaque ligne. Mais une variable qu'on
crée dans une action n'est pas oubliée à la ligne suivante : `awk` la garde
en mémoire jusqu'à la fin du programme. C'est ce qui permet d'accumuler.

Comptons les lignes de `annotation.gff3` qui ne sont pas des lignes d'en-tête
(celles qui commencent par `#`) :

```bash
awk '!/^#/ { n = n + 1 } END { print n }' data/genome/annotation.gff3
```

```output
551
```

À chaque ligne qui ne commence pas par `#`, `n` augmente de un. Une variable
jamais initialisée vaut `0` par défaut en contexte numérique : il n'y a donc
pas besoin d'écrire `n = 0` avant la boucle. `END` désigne un bloc qui
s'exécute une seule fois, après la dernière ligne : c'est le moment idéal pour
afficher un résultat accumulé.

## `BEGIN` et `END` : avant et après le fichier

`BEGIN` est le symétrique de `END` : son action s'exécute une seule fois,
avant la lecture de la première ligne. C'est l'endroit pour préparer un
séparateur de champs, afficher un en-tête de tableau, ou initialiser une
variable de façon explicite.

```bash
awk 'BEGIN { FS = "\t"; print "type\tdebut\tfin" } !/^#/ { print $3"\t"$4"\t"$5 }' data/genome/annotation.gff3 | head -5
```

```output
type	debut	fin
gene	171	513
mRNA	171	513
exon	171	513
gene	956	1509
```

Un programme `awk` complet a donc trois zones possibles, dans n'importe quel
ordre à l'écrit, mais toujours exécutées dans cet ordre à l'exécution :
`BEGIN` une fois au départ, le bloc principal une fois par ligne, `END` une
fois à la fin.

::: callout

## `-F` ou `FS` dans `BEGIN`

L'épisode précédent a introduit l'option `-F` pour fixer le séparateur de
champs depuis la ligne de commande : `awk -F'\t' '{...}'`. Écrire
`BEGIN { FS = "\t" }` produit exactement le même effet. Les deux formes
existent : `-F` est plus rapide à taper pour un one-liner, `FS` dans `BEGIN`
se lit mieux dans un script plus long.

:::

## Somme, moyenne, minimum, maximum

Le calcul le plus fréquent sur une table est le résumé statistique d'une
colonne. Prenons la longueur des gènes de `annotation.gff3` : colonne 4
(début), colonne 5 (fin), colonne 3 (type) pour ne garder que les gènes.

```bash
awk '$3 == "gene" { longueur = $5 - $4 + 1; total = total + longueur; n = n + 1 } END { print "genes:", n; print "longueur moyenne:", total / n }' data/genome/annotation.gff3
```

```output
genes: 128
longueur moyenne: 494.25
```

Le `+ 1` compte les deux bornes incluses : un gène qui commence en 171 et
finit en 513 couvre 513 - 171 + 1 = 343 positions, pas 342. Ce sont les
coordonnées 1-based du GFF3 vues à l'épisode 5.

Ajoutons maintenant le minimum et le maximum. Le principe est de comparer
chaque nouvelle valeur à la meilleure connue jusqu'ici, et de la remplacer si
elle fait mieux :

```bash
awk '$3 == "gene" {
    longueur = $5 - $4 + 1
    total = total + longueur
    n = n + 1
    if (n == 1 || longueur < min) { min = longueur }
    if (n == 1 || longueur > max) { max = longueur }
}
END {
    print "genes:", n
    printf "moyenne: %.1f\n", total / n
    print "minimum:", min
    print "maximum:", max
}' data/genome/annotation.gff3
```

```output
genes: 128
moyenne: 494.2
minimum: 304
maximum: 711
```

Le test `n == 1` sert à initialiser `min` et `max` avec la première valeur
rencontrée, sans avoir à écrire une valeur de départ arbitraire qui pourrait
être fausse (un `min` qui démarrerait à `0` ne serait jamais dépassé par le
bas). Remarquez que la structure du programme tient sur plusieurs lignes :
`awk` accepte très bien un script étalé ainsi entre guillemets simples, avec
une instruction par ligne et pas de point-virgule nécessaire en fin de ligne.

::::::::::::::::::::::::::::::::::::::::::::::::::  challenge

## Longueur moyenne des exons

En reprenant le même principe, calculez le nombre d'exons, leur longueur
moyenne, minimale et maximale dans `data/genome/annotation.gff3`.

:::::::::::::::  solution

## Solution

```bash
awk '$3 == "exon" {
    longueur = $5 - $4 + 1
    total = total + longueur
    n = n + 1
    if (n == 1 || longueur < min) { min = longueur }
    if (n == 1 || longueur > max) { max = longueur }
}
END {
    print "exons:", n
    printf "moyenne: %.1f\n", total / n
    print "minimum:", min
    print "maximum:", max
}' data/genome/annotation.gff3
```

```output
exons: 295
moyenne: 149.6
minimum: 4
maximum: 502
```

Seule la condition `$3 == "gene"` devient `$3 == "exon"` : le reste du
programme, l'accumulation et les comparaisons de minimum et maximum, ne
change pas. C'est la force d'un programme bien structuré : changer le filtre
ne demande pas de réécrire la logique de calcul.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

## Compter par catégorie avec un tableau associatif

Compter le nombre total de gènes, c'est utile. Mais compter le nombre
d'entités *par type* (`gene`, `mRNA`, `exon`) demande de tenir un compteur
différent pour chaque valeur rencontrée, sans savoir à l'avance combien de
valeurs différentes existent. C'est le rôle d'un tableau associatif
(*associative array*) : un tableau indexé non par des numéros mais par des
chaînes de caractères, ici directement le contenu de la colonne.

```bash
awk '!/^#/ { compte[$3]++ } END { for (type in compte) { print type, compte[type] } }' data/genome/annotation.gff3
```

```output
mRNA 128
exon 295
gene 128
```

`compte[$3]++` incrémente de un l'entrée du tableau `compte` dont la clé est
la valeur de la colonne 3. `compte` n'a pas besoin d'être déclaré ni
dimensionné : la première fois qu'`awk` rencontre `compte["exon"]`, il crée
cette entrée avec la valeur `0`, puis l'incrémente. `for (type in compte)`
parcourt ensuite toutes les clés du tableau, une fois chacune, dans un ordre
qui n'est pas garanti.

::: callout

## L'ordre de `for (clé in tableau)` n'est pas garanti

La norme POSIX ne fixe pas l'ordre de parcours d'un `for (clé in tableau)`. Il
peut varier d'une implémentation d'`awk` à l'autre, et parfois d'une exécution
à l'autre. Si vous avez besoin d'un résultat trié, faites-le trier en aval par
la commande `sort` déjà connue : `awk '...' fichier | sort`.

:::

Trions ce résultat par nombre décroissant pour retrouver l'ordre lu plus
haut :

```bash
awk '!/^#/ { compte[$3]++ } END { for (type in compte) { print type, compte[type] } }' data/genome/annotation.gff3 | sort -k2 -n -r
```

```output
exon 295
mRNA 128
gene 128
```

::: caution

## Ce que l'awk de cette formation ne sait PAS faire

Certaines implémentations d'`awk` — en particulier `gawk`, celle des
distributions Linux — ajoutent des fonctions absentes de l'awk POSIX installé
par défaut sur macOS (le *One True Awk*, aussi appelé `bwk`). Trois pièges
fréquents :

- `length(tableau)` pour compter les entrées d'un tableau associatif :
  n'existe pas partout. Utilisez un compteur explicite, incrémenté à côté du
  tableau.
- `asort(tableau)` pour trier les valeurs d'un tableau : n'existe pas partout.
  Faites sortir les valeurs avec `print` et triez-les avec `sort` en aval.
- `gensub()` pour une substitution avec expression régulière renvoyant un
  résultat sans modifier la variable d'origine : n'existe pas partout.
  Utilisez `sub` ou `gsub`, qui existent en awk POSIX mais modifient leur
  argument sur place.

Un script écrit avec ces fonctions fonctionnera sur le portable Linux d'un
collègue et échouera sur un Mac. Cette leçon s'en tient volontairement à
l'awk POSIX.

:::

Pour compter les entrées d'un tableau associatif de façon portable, ajoutez
un compteur à côté de la boucle :

```bash
awk '!/^#/ { compte[$3]++ } END { nb_types = 0; for (type in compte) { nb_types++ }; print "nombre de types distincts:", nb_types }' data/genome/annotation.gff3
```

```output
nombre de types distincts: 3
```

::::::::::::::::::::::::::::::::::::::::::::::::::  challenge

## Compter les variants par filtre

`data/variants/cohorte.vcf` a une colonne `FILTER` (la 7e colonne des lignes
de données, après les lignes d'en-tête qui commencent par `#`). Comptez le
nombre de variants pour chaque valeur de `FILTER`.

:::::::::::::::  solution

## Solution

```bash
awk '!/^#/ { compte[$7]++ } END { for (f in compte) { print f, compte[f] } }' data/variants/cohorte.vcf
```

La colonne `FILTER` distingue les variants retenus (`PASS`) des variants
écartés pour cause de qualité insuffisante (`LowQual`) ou de profondeur trop
faible (`LowDepth`), comme annoncé dans l'en-tête `##FILTER` du VCF. Le
principe est identique au comptage par type du GFF3 : seule la colonne
utilisée comme clé change.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

## Retrouver l'ordre d'une clé avec `delete`

Un tableau associatif peut aussi servir à repérer des doublons ou à vider une
information devenue inutile en cours de programme. `delete tableau[clé]`
retire une entrée précise ; `delete tableau` (sans indice, extension non
universelle, à éviter) n'est pas portable — pour vider tout un tableau de
façon portable, on le reconstruit dans un nouveau `BEGIN` ou on recrée les
clés une par une. Dans cette leçon, `delete` sert surtout à retirer une entrée
ponctuelle, par exemple pour ignorer un identifiant déjà vu :

```bash
awk '!/^#/ { if ($3 in vu) { next }; vu[$3] = 1; print $3 }' data/genome/annotation.gff3
```

```output
gene
mRNA
exon
```

`($3 in vu)` teste l'appartenance d'une clé à un tableau sans créer l'entrée
si elle n'existe pas — contrairement à `if (vu[$3] == 1)`, qui créerait
silencieusement une entrée vide pour toute clé absente. C'est la façon
correcte de tester la présence d'une clé. Ici, le résultat n'a que trois
lignes : chaque type de la colonne 3 n'est affiché qu'à sa première
rencontre, exactement les trois types déjà connus (`gene`, `mRNA`, `exon`) et
dans l'ordre où ils apparaissent dans le fichier.

## Compter les lectures alignées et non alignées d'un SAM

Un fichier SAM décrit chaque lecture alignée sur une ligne, avec un champ
FLAG en deuxième colonne. Le bit `4` du FLAG signale une lecture non alignée.
Sans entrer dans le détail binaire du FLAG (ce n'est pas l'objet de cette
leçon), retenons un repère pratique déjà visible dans le fichier : les
lectures non alignées ont `RNAME` égal à `*` (colonne 3) et `MAPQ` égal à `0`
(colonne 5). Comptons sur ce critère, en ignorant les lignes d'en-tête qui
commencent par `@` :

```bash
awk '!/^@/ {
    total++
    if ($3 == "*") { non_alignees++ } else { alignees++ }
}
END {
    print "total:", total
    print "alignees:", alignees
    print "non alignees:", non_alignees
}' data/alignements/ech01.sam
```

```output
total: 300
alignees: 277
non alignees: 23
```

C'est ici qu'intervient le `if/else` dans une action : pour chaque ligne, une
seule des deux branches s'exécute, et la somme des deux compteurs vaut
forcément le total. Ce chiffre confirme l'anomalie volontaire déjà signalée à
l'épisode 5 : une fraction des lectures de `ech01.sam` ne s'aligne sur aucune
région du génome de référence.

::::::::::::::::::::::::::::::::::::::::::::::::::  challenge

## Répartir les lectures alignées par chromosome

En reprenant `data/alignements/ech01.sam`, comptez le nombre de lectures
alignées (celles dont la colonne 3 n'est pas `*`) pour chaque valeur de la
colonne 3 (`RNAME`).

:::::::::::::::  solution

## Solution

```bash
awk '!/^@/ && $3 != "*" { compte[$3]++ } END { for (chrom in compte) { print chrom, compte[chrom] } }' data/alignements/ech01.sam
```

```output
chrM 10
chr1 267
```

Toutes les lectures alignées de cet échantillon le sont sur `chr1` : c'est
cohérent avec le fait que `chrM`, le contig mitochondrial, est beaucoup plus
court que `chr1` et donc moins susceptible d'y voir tomber une lecture dans
ce petit jeu de données. La condition combine deux tests avec `&&`, déjà
rencontré à l'épisode 9.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

## Totaliser une table par groupe

`data/tables/comptages.tsv` a un gène par ligne et un échantillon par
colonne, de la colonne 3 (`ech01`) à la colonne 8 (`ech06`). Sommons chaque
colonne, c'est-à-dire le total de comptages par échantillon, en ignorant la
ligne d'en-tête :

```bash
awk 'BEGIN { FS = "\t" }
NR == 1 { next }
{
    for (i = 3; i <= 8; i++) { total[i] += $i }
}
END {
    for (i = 3; i <= 8; i++) { print "colonne", i, ":", total[i] }
}' data/tables/comptages.tsv
```

```output
colonne 3 : 29180
colonne 4 : 27249
colonne 5 : 31196
colonne 6 : 43079
colonne 7 : 38289
colonne 8 : 39603
```

`NR == 1 { next }` saute la ligne d'en-tête : `next` interrompt le
traitement de la ligne courante et passe directement à la ligne suivante,
sans exécuter le reste du programme pour cette ligne. La boucle
`for (i = 3; i <= 8; i++)` est une boucle numérique classique, la même
syntaxe qu'en C : elle permet ici de désigner une colonne par un numéro
variable, `$i`, ce qu'un nom de champ fixe comme `$3` ne permettrait pas.

Le résultat par numéro de colonne n'est pas très lisible. Utilisons plutôt
l'en-tête pour nommer chaque total, avec un tableau associatif indexé par le
nom d'échantillon lu dans `NR == 1` :

```bash
awk 'BEGIN { FS = "\t" }
NR == 1 { for (i = 3; i <= 8; i++) { nom[i] = $i }; next }
{ for (i = 3; i <= 8; i++) { total[i] += $i } }
END { for (i = 3; i <= 8; i++) { print nom[i], total[i] } }' data/tables/comptages.tsv > resultats/totaux_par_echantillon.tsv
cat resultats/totaux_par_echantillon.tsv
```

```output
ech01 29180
ech02 27249
ech03 31196
ech04 43079
ech05 38289
ech06 39603
```

L'échantillon `ech03` sort nettement du lot : son total est environ 60 % de
celui des autres échantillons, alors que les cinq autres échantillons se
tiennent tous entre 40 000 et 41 500. Une table de comptages où un
échantillon totalise beaucoup moins de lectures que les autres est un signal
à vérifier : profondeur de séquençage plus faible, problème de préparation
de librairie, ou étape d'alignement moins efficace pour cet échantillon.

::::::::::::::::::::::::::::::::::::::::::::::::::  challenge

## Le gène le plus variable

Facultatif : en reprenant le tableau `total` par colonne construit plus haut,
pouvez-vous, sans changer la logique déjà écrite, ajouter le calcul de la
moyenne par échantillon (total divisé par le nombre de gènes) ? Le nombre de
gènes est le nombre de lignes de données, soit `NR - 1` à la fin de la
lecture puisque `NR` continue de compter la ligne d'en-tête.

:::::::::::::::  solution

## Solution

```bash
awk 'BEGIN { FS = "\t" }
NR == 1 { for (i = 3; i <= 8; i++) { nom[i] = $i }; next }
{ for (i = 3; i <= 8; i++) { total[i] += $i } }
END {
    n = NR - 1
    for (i = 3; i <= 8; i++) { printf "%s total=%d moyenne=%.1f\n", nom[i], total[i], total[i] / n }
}' data/tables/comptages.tsv
```

```output
ech01 total=29180 moyenne=228.0
ech02 total=27249 moyenne=212.9
ech03 total=31196 moyenne=243.7
ech04 total=43079 moyenne=336.6
ech05 total=38289 moyenne=299.1
ech06 total=39603 moyenne=309.4
```

`NR` continue d'être incrémenté à chaque ligne lue, y compris pendant le
bloc `END` il conserve la valeur atteinte à la fin de la lecture : c'est donc
le nombre total de lignes du fichier, en-tête compris, d'où le `- 1`.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

## Taux de GC d'une séquence FASTA

Le taux de GC (proportion des bases G et C) est un indicateur classique de
composition d'une séquence. Calculons-le sur le contig `chrM` de
`data/genome/ref_toy.fa`. Il faut d'abord isoler les lignes de séquence de ce
contig, sans son en-tête, ce que sait déjà faire `sed` — mais nous n'avons
pas encore vu `sed` : utilisons `awk` seul, avec une variable qui retient si
l'on est actuellement dans le bon contig.

```bash
awk '/^>/ { dans_chrM = ($0 ~ /^>chrM/); next }
dans_chrM {
    sequence = sequence $0
}
END {
    n = length(sequence)
    gc = gsub(/[GCgc]/, "", sequence)
    printf "longueur: %d\ntaux de GC: %.1f%%\n", n, 100 * gc / n
}' data/genome/ref_toy.fa
```

```output
longueur: 5000
taux de GC: 40.0%
```

Deux fonctions de chaînes de caractères apparaissent ici. `length(chaine)`
renvoie le nombre de caractères d'une chaîne — c'est la fonction `length`
appliquée à une variable simple, à ne pas confondre avec `length(tableau)`
signalée plus haut comme non portable. `gsub(motif, remplacement, variable)`
remplace *toutes* les occurrences du motif par le remplacement dans la
variable donnée, la modifie sur place, et renvoie le nombre de remplacements
effectués : c'est ce nombre, capturé dans `gc`, qui donne le compte des bases
G et C sans avoir à les compter une par une. `sequence = sequence $0`
concatène : accoler deux valeurs côte à côte, sans opérateur entre elles, est
la façon dont `awk` construit une chaîne plus longue à partir de plusieurs
morceaux.

::: callout

## `sub` et `gsub`

`sub(motif, remplacement, variable)` ne remplace que la *première* occurrence
du motif ; `gsub` les remplace *toutes*. Les deux modifient la variable
passée en troisième argument (ou `$0` si on omet cet argument) et renvoient
le nombre de remplacements effectués. C'est ce nombre qui est utile pour
compter des occurrences, comme dans le calcul du taux de GC ci-dessus.

:::

::::::::::::::::::::::::::::::::::::::::::::::::::  challenge

## Taux de GC de chr1

En vous inspirant du programme précédent, calculez la longueur et le taux de
GC du contig `chr1` de `data/genome/ref_toy.fa`.

:::::::::::::::  solution

## Solution

```bash
awk '/^>/ { dans_chr1 = ($0 ~ /^>chr1/); next }
dans_chr1 {
    sequence = sequence $0
}
END {
    n = length(sequence)
    gc = gsub(/[GCgc]/, "", sequence)
    printf "longueur: %d\ntaux de GC: %.1f%%\n", n, 100 * gc / n
}' data/genome/ref_toy.fa
```

```output
longueur: 100000
taux de GC: 39.7%
```

Seul le motif d'en-tête `^>chr1` change, en veillant à ce qu'il ne
corresponde pas aussi à `>chrM` — c'est le cas ici, puisque `chr1` et `chrM`
diffèrent dès le quatrième caractère.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

## Découper un attribut avec `split`

La colonne 9 d'un GFF3 contient plusieurs attributs séparés par des
points-virgules, chacun sous la forme `clé=valeur`. C'est une colonne dans
une colonne : `split` sert exactement à ce cas. `split(chaine, tableau, sep)`
découpe `chaine` selon le séparateur `sep` et range les morceaux dans
`tableau`, indexé à partir de `1`.

```bash
awk '$3 == "gene" {
    split($9, attributs, ";")
    print attributs[1]
}' data/genome/annotation.gff3 | head -3
```

```output
ID=gene:GENE00001
ID=gene:GENE00002
ID=gene:GENE00003
```

::: caution

## Éviter `length(tableau)` sur le résultat de `split`

Il est tentant d'écrire `n = length(attributs)` après un `split` pour savoir
combien de morceaux ont été produits. C'est justement l'extension GNU signalée
plus haut, absente de l'awk POSIX de macOS. Si vous avez besoin du nombre de
morceaux, `split` lui-même renvoie ce nombre : `n = split($9, attributs, ";")`
range le résultat dans `n` directement, sans passer par `length`.

:::

Chaque morceau garde son préfixe `clé=` : `attributs[1]` vaut
`ID=gene:GENE00001`, pas seulement `GENE00001`. Pour isoler la valeur du nom
du gène, combinons `split` sur le point-virgule pour séparer les attributs,
puis `sub` pour retirer le préfixe `Name=` de celui qui nous intéresse :

```bash
awk '$3 == "gene" {
    n = split($9, attributs, ";")
    for (i = 1; i <= n; i++) {
        if (attributs[i] ~ /^Name=/) {
            valeur = attributs[i]
            sub(/^Name=/, "", valeur)
            print valeur
        }
    }
}' data/genome/annotation.gff3 | head -3
```

```output
arf4D
eef3B
rho6B
```

`sub(/^Name=/, "", valeur)` remplace la première occurrence du motif
`^Name=` (l'ancre `^` impose que ce soit en tout début de chaîne) par une
chaîne vide, ce qui revient à la retirer. C'est le même mécanisme que la
suppression de préfixe pratiquée avec `sed` que vous verrez au prochain
épisode, mais réalisée ici entièrement en `awk`.

::::::::::::::::::::::::::::::::::::::::::::::::::  challenge

## Extraire le biotype des gènes

Les lignes de type `gene` de `data/genome/annotation.gff3` portent aussi un
attribut `biotype=`, par exemple `biotype=protein_coding` ou
`biotype=pseudogene`. Écrivez un programme `awk` qui compte le nombre de
gènes pour chaque valeur de `biotype`.

:::::::::::::::  solution

## Solution

```bash
awk '$3 == "gene" {
    n = split($9, attributs, ";")
    for (i = 1; i <= n; i++) {
        if (attributs[i] ~ /^biotype=/) {
            valeur = attributs[i]
            sub(/^biotype=/, "", valeur)
            compte[valeur]++
        }
    }
}
END {
    for (b in compte) { print b, compte[b] }
}' data/genome/annotation.gff3
```

On retrouve la combinaison de toutes les notions de l'épisode : `split` pour
isoler l'attribut voulu parmi les autres, `sub` pour n'en garder que la
valeur, et un tableau associatif pour compter les occurrences de chaque
valeur distincte, exactement comme pour les types de la colonne 3 en début
d'épisode.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

## `substr`, `index`, `toupper`, `tolower`

Trois autres fonctions de chaînes complètent la boîte à outils, utiles dès
qu'il faut inspecter ou transformer un morceau précis d'un champ.
`substr(chaine, debut, longueur)` extrait une sous-chaîne à partir de la
position `debut` (les positions commencent à `1`, pas à `0`), sur `longueur`
caractères — cet argument est facultatif, et son absence va jusqu'à la fin de
la chaîne. `index(chaine, motif)` renvoie la position de la première
occurrence de `motif` dans `chaine`, ou `0` si absent. `toupper` et `tolower`
changent la casse d'une chaîne entière.

Illustrons sur les en-têtes de `data/proteines/proteines.fa`, dont chacun
contient un code d'organisme après `OS=` : par exemple
`OS=Escherichia coli`. Regardons d'abord les quatre premiers caractères après
le symbole `>`, qui correspondent toujours au préfixe `sp|` de la base
UniProt suivi du début de l'identifiant :

```bash
awk '/^>/ { print substr($0, 2, 4) }' data/proteines/proteines.fa | head -3
```

```output
sp|P
sp|P
sp|P
```

`substr($0, 2, 4)` part du deuxième caractère de la ligne (juste après `>`)
et en garde quatre. Utilisons maintenant `index` pour vérifier, ligne par
ligne, que chaque en-tête contient bien la mention `OS=` avant d'aller plus
loin dans un traitement :

```bash
awk '/^>/ { print index($0, "OS=") }' data/proteines/proteines.fa | sort -u
```

```output
41
42
44
46
48
49
52
```

La position de `OS=` varie légèrement d'un en-tête à l'autre parce que le nom
qui précède (`ribosomal protein`, `hypothetical protein`, etc.) n'a pas
toujours la même longueur. `toupper` et `tolower` s'utilisent directement,
sans découpage préalable :

```bash
awk '/^>/ { print toupper(substr($0, 2, 4)) }' data/proteines/proteines.fa | sort -u
```

```output
SP|P
```

::::::::::::::::::::::::::::::::::::::::::::::::::  challenge

## Nom de gène en minuscules

Reprenez l'extraction du nom de gène (`Name=`) faite plus haut sur
`data/genome/annotation.gff3`, et affichez chaque nom entièrement en
minuscules.

:::::::::::::::  solution

## Solution

```bash
awk '$3 == "gene" {
    n = split($9, attributs, ";")
    for (i = 1; i <= n; i++) {
        if (attributs[i] ~ /^Name=/) {
            valeur = attributs[i]
            sub(/^Name=/, "", valeur)
            print tolower(valeur)
        }
    }
}' data/genome/annotation.gff3 | head -3
```

```output
arf4d
eef3b
rho6b
```

Il suffit d'envelopper la valeur déjà extraite dans `tolower(...)` au moment
de l'afficher : les fonctions de chaînes se combinent librement, sans qu'il
soit nécessaire de repasser par une variable intermédiaire.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

## Interprétation : pourquoi ce compteur reste-t-il à zéro

::::::::::::::::::::::::::::::::::::::::::::::::::  challenge

## Ce script a un défaut, lequel

Un collègue a écrit ce programme pour compter les gènes de chaque biotype de
`data/genome/annotation.gff3`, mais chaque compteur affiché vaut `0`.
Retrouvez l'erreur sans l'exécuter, puis vérifiez.

```bash
awk '$3 == "gene" {
    split($9, attributs, ";")
    for (i = 1; i <= n; i++) {
        if (attributs[i] ~ /^biotype=/) {
            compte[attributs[i]]++
        }
    }
}
END { for (b in compte) { print b, compte[b] } }' data/genome/annotation.gff3
```

:::::::::::::::  solution

## Solution

L'erreur est dans la boucle `for (i = 1; i <= n; i++)` : `n` n'est jamais
défini, alors que `split($9, attributs, ";")` renvoie précisément ce compte
mais sans que le résultat soit récupéré. `n` vaut donc `0` (valeur par défaut
d'une variable non initialisée), la condition `i <= n` est fausse dès le
départ, et la boucle ne s'exécute jamais : le tableau `compte` reste vide.

Correction :

```bash
awk '$3 == "gene" {
    n = split($9, attributs, ";")
    for (i = 1; i <= n; i++) {
        if (attributs[i] ~ /^biotype=/) {
            compte[attributs[i]]++
        }
    }
}
END { for (b in compte) { print b, compte[b] } }' data/genome/annotation.gff3
```

```output
biotype=pseudogene 7
biotype=lncRNA 17
biotype=protein_coding 90
biotype=rRNA 4
biotype=tRNA 10
```

Un second défaut plus discret subsiste : la clé du tableau `compte` est
`attributs[i]`, c'est-à-dire `biotype=protein_coding` avec son préfixe, non
la valeur seule. Le résultat reste correct pour compter, mais moins lisible
qu'après un `sub(/^biotype=/, "", ...)`.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

## Récapitulatif : recettes awk

Le tableau suivant réunit les usages les plus fréquents rencontrés dans cet
épisode et le précédent. Gardez-le à portée de main : la plupart des besoins
courants sur un fichier tabulaire se couvrent avec l'une de ces lignes.

| Recette | Usage |
|---|---|
| `awk '{ n++ } END { print n }' fichier` | Compter le nombre de lignes |
| `awk -F'\t' '{ print $3 }' fichier` | Extraire une colonne avec un séparateur explicite |
| `awk '$3 == "gene"' fichier` | Filtrer les lignes selon la valeur d'une colonne |
| `awk '{ compte[$3]++ } END { for (k in compte) print k, compte[k] }' fichier` | Compter les occurrences par catégorie |
| `awk '{ total += $5 } END { print total, total/NR }' fichier` | Somme et moyenne d'une colonne |
| `awk '{ if (n==0 || $5<min) min=$5; if (n==0 || $5>max) max=$5; n++ } END { print min, max }' fichier` | Minimum et maximum d'une colonne |
| `awk '($3 in vu) { next } { vu[$3]=1 }' fichier` | Ne garder que la première occurrence de chaque clé |
| `awk '{ n = split($9, a, ";"); print a[1] }' fichier` | Découper un champ composite en sous-parties |
| `awk '{ v=$1; sub(/^prefixe=/, "", v); print v }' fichier` | Retirer un préfixe connu d'une valeur |
| `awk '{ gc = gsub(/[GC]/, "", $0); print gc }' fichier` | Compter les occurrences d'un motif dans une chaîne |
| `awk '{ print substr($0, 1, 10) }' fichier` | Extraire les *n* premiers caractères d'une ligne |
| `awk '{ print toupper($2) }' fichier` | Changer la casse d'une colonne |

::: callout

## Trois extensions à ne jamais utiliser dans un script portable

Pour mémoire, avant de passer à `sed` au prochain épisode : `length(tableau)`
pour la taille d'un tableau associatif, `asort()` pour trier les valeurs d'un
tableau, et `gensub()` pour une substitution non destructive, sont trois
extensions de `gawk` absentes de l'awk POSIX installé par défaut sur macOS. Un
script qui les utilise fonctionnera chez vous si vous êtes sous Linux et
échouera chez un collègue sous macOS. Préférez systématiquement un compteur
explicite, un tri en aval avec `sort`, et `sub`/`gsub` sur une copie de la
variable.

:::

:::::::::::::::::::::::::::::::::::::::: keypoints

- `BEGIN { ... }` s'exécute une fois avant la lecture du fichier, `END { ... }` une fois après.
- Une variable non initialisée vaut `0` ou chaîne vide, ce qui permet d'accumuler directement avec `total += $5` ou `n++`.
- `tableau[cle]++` crée et incrémente une entrée de tableau associatif sans déclaration préalable.
- `for (cle in tableau) { ... }` parcourt toutes les clés d'un tableau, dans un ordre non garanti ; triez en aval avec `sort` si besoin.
- `(cle in tableau)` teste l'appartenance sans créer l'entrée ; `delete tableau[cle]` retire une entrée précise.
- `n = split(chaine, tableau, separateur)` découpe une chaîne et renvoie le nombre de morceaux obtenus.
- `sub(motif, remplacement, variable)` et `gsub(...)` modifient la variable sur place et renvoient le nombre de remplacements.
- `length`, `substr`, `index`, `toupper`, `tolower` opèrent sur des chaînes de caractères simples.
- `length(tableau)`, `asort()` et `gensub()` sont des extensions GNU absentes de l'awk POSIX de macOS : à ne jamais utiliser dans un script portable.

::::::::::::::::::::::::::::::::::::::::::::::::::
