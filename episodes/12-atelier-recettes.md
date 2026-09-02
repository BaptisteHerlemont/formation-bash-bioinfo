---
title: "Atelier : recettes combinées"
teaching: 15
exercises: 45
---

::::::::::::::::::::::::::::::::::::::::::  questions

- Comment enchaîner plusieurs commandes pour répondre à une vraie question
  d'analyse ?
- Comment lire et comprendre un tube écrit par quelqu'un d'autre ?
- Quels sont les premiers réflexes quand un tube ne fait pas ce qu'on attend ?

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::  objectives

- Construire un tube en plusieurs étapes en vérifiant chaque étape séparément.
- Décomposer un tube existant commande par commande pour en comprendre l'effet.
- Appliquer trois réflexes de débogage : répertoire, séparateur, `head`.
- Résoudre huit défis combinant `grep`, `cut`, `sort`, `uniq`, `awk` et `sed`.

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::::::::  prereq

Cet épisode suppose acquis tout ce qui a été vu depuis l'épisode 1 : navigation
(épisode 2), manipulation de fichiers (épisode 3), lecture de fichiers texte
et formats bioinformatiques (épisodes 4 et 5), redirections et tubes
(épisode 6), `grep` (épisode 7), la boîte à outils tabulaire `cut`, `sort`,
`uniq`, `tr`, `paste`, `join` (épisode 8), `awk` (épisodes 9 et 10) et `sed`
(épisode 11). Aucune commande nouvelle n'est introduite ici : c'est un atelier
de pratique, pas un cours.

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

Depuis onze épisodes, vous avez appris les commandes une par une. Cet atelier
ne vous en apprend aucune de nouvelle : il vous entraîne à les combiner pour
répondre à de vraies questions, comme vous le ferez sur vos propres données.

Commencez par vérifier que vous êtes au bon endroit et par préparer un
répertoire de résultats.

```bash
cd ~/formation-bash
pwd
```

```output
/home/apprenant/formation-bash
```

<!-- verif: exec-seulement -->

```bash
mkdir -p resultats tmp
```

## Construire un tube étage par étage

La méthode ne change jamais, quelle que soit la question posée : on construit
le tube (*pipe*) un étage à la fois, et on regarde le résultat à chaque étage
avant d'ajouter le suivant. On ne tape jamais un tube de cinq commandes d'un
seul geste en espérant que tout fonctionne.

Prenons un exemple : combien de gènes annotés portent le biotype
`pseudogene` dans `data/genome/annotation.gff3` ?

Étage 1 — on regarde ce qu'il y a dans le fichier, sans rien filtrer encore :

```bash
cut -f3,9 data/genome/annotation.gff3 | head -5
```

```output
##gff-version 3
##sequence-region chr1 1 100000
##sequence-region chrM 1 5000
#!genome-build assemblage-jouet v1.0
#!genome-date 2024-09
```

Les lignes d'en-tête commencent par `#` et n'ont pas neuf champs : elles
apparaissent vides ou tronquées avec `cut`. Il faut les écarter d'abord.

Étage 2 — on écarte les lignes d'en-tête et on ne garde que les colonnes utiles :

```bash
grep -v '^#' data/genome/annotation.gff3 | cut -f3,9 | head -5
```

```output
gene	ID=gene:GENE00001;Name=arf4D;biotype=protein_coding
mRNA	ID=transcript:GENE00001.1;Parent=gene:GENE00001;Name=arf4D-201
exon	ID=exon:GENE00001.1;Parent=transcript:GENE00001.1
gene	ID=gene:GENE00002;Name=eef3B;biotype=protein_coding
mRNA	ID=transcript:GENE00002.1;Parent=gene:GENE00002;Name=eef3B-201
```

Étage 3 — on ne garde que les lignes de type `gene` et celles qui portent
`biotype=pseudogene` :

```bash
grep -v '^#' data/genome/annotation.gff3 | awk -F'\t' '$3 == "gene"' | grep 'biotype=pseudogene' | wc -l
```

```output
       7
```

Trois étages, trois vérifications intermédiaires. C'est plus long à taper que
d'écrire le tube complet d'un coup, mais c'est la seule méthode qui permette de
savoir, quand le résultat final est faux, *à quel étage* il l'est devenu.

::: callout

## Pourquoi ne pas tout écrire d'un coup

Un tube de quatre ou cinq commandes qui échoue ne dit jamais laquelle a
échoué : le message d'erreur, s'il y en a un, remonte de l'étage fautif mais
le tube entier s'arrête sans distinction visible. En construisant étage par
étage et en regardant chaque sortie intermédiaire avec `head`, vous savez à
tout moment que ce que vous avez construit jusque-là fonctionne, et vous
n'ajoutez la complexité suivante que sur une base vérifiée.

:::

## Lire un tube écrit par quelqu'un d'autre

L'autre moitié du métier consiste à comprendre un tube que vous n'avez pas
écrit — celui d'une collègue, celui d'un article, celui trouvé sur un forum.
La méthode est la même, mais à l'envers : on **découpe** le tube en le
recopiant morceau par morceau, du début, en exécutant chaque fragment.

Prenons ce tube trouvé dans les notes d'une collègue, qui porte sur
`data/tables/comptages.tsv` :

```bash
cut -f1,3-8 data/tables/comptages.tsv | sort -k2,2 -n -r | head -6
```

Pour le comprendre sans le deviner, on le découpe. Premier fragment :

```bash
cut -f1,3-8 data/tables/comptages.tsv | head -3
```

```output
gene_id	ech01	ech02	ech03	ech04	ech05	ech06
GENE00001	518	478	269	513	369	411
GENE00002	0	0	0	0	0	0
```

Ce premier fragment garde la colonne `gene_id` et les six colonnes
d'échantillons, en écartant `gene_name`. On ajoute le fragment suivant :

```bash
cut -f1,3-8 data/tables/comptages.tsv | sort -k2,2 -n -r | head -3
```

```output
GENE00048	2118	982	1318	1955	1436	1793
GENE00077	1710	1066	1787	1513	1501	2013
GENE00045	1654	1311	1414	1601	1370	1095
```

`sort -k2,2 -n -r` trie numériquement (`-n`) et en ordre décroissant (`-r`) sur
la deuxième colonne (`-k2,2`), c'est-à-dire la colonne `ech01`. La ligne
d'en-tête se retrouve mêlée au tri parce que `gene_id` n'est pas un nombre et
que `sort -n` la traite comme valant zéro : elle finit donc en bas, sauf ici
où `-r` inverse tout et la remonte. C'est un piège classique.

Le tube complet répond donc à la question « quels sont les cinq gènes les plus
comptés dans `ech01` », mais avec l'en-tête polluant le résultat.

::: instructor

Ce découpage-là mérite d'être fait au tableau, en direct, avant de lancer les
apprenants sur les défis. Insistez sur le fait que l'en-tête qui se glisse dans
le tri n'est pas un bug rare : c'est *le* piège qui explique la moitié des
questions « pourquoi mon tri est-il faux » que vous recevrez pendant les
45 prochaines minutes.

:::

## Trois réflexes de débogage

Quand un tube ne fait pas ce qui est attendu, avant toute autre hypothèse,
vérifiez ces trois choses dans l'ordre.

**1. Le répertoire.** La quasi-totalité des messages `No such file or
directory` viennent d'un répertoire de travail qui n'est pas celui qu'on
croit.

<!-- verif: exec-seulement -->
```bash
pwd
```

```output
/home/apprenant/formation-bash
```

Tous les chemins de cette leçon sont relatifs à `~/formation-bash`. Si `pwd`
affiche autre chose, remontez ou redescendez avec `cd` avant de continuer.

**2. Le séparateur.** `cut` sans `-d` suppose une tabulation. Un fichier qui
semble tabulé à l'œil mais qui utilise des espaces multiples donnera des
colonnes vides ou décalées. On vérifie avec `cat -A` ou, plus simplement, en
comparant `cut -f1` à ce qu'on voit avec `head`.

```bash
head -2 data/tables/comptages.tsv | cut -f1,2
```

```output
gene_id	gene_name
GENE00001	arf4D
```

Si cette commande renvoyait une seule colonne fusionnée au lieu de deux, ce
serait le signe que le fichier n'est pas tabulé comme on le pense.

**3. `head` avant tout.** Avant de lancer un tube sur un fichier entier,
regardez toujours ses premières lignes brutes. Cela révèle immédiatement les
lignes d'en-tête à écarter, le séparateur réel, et la présence de guillemets
ou d'espaces parasites.

```bash
head -3 data/regions/cibles.bed
```

```output
chr1	955	1509	eef3B	448	+
chr1	2633	3257	rho5B	244	-
chr1	6782	7339	fbx4D	605	+
```

::: callout

## Les trois réflexes, en une phrase

Avant de chercher une explication compliquée : où suis-je (`pwd`), avec quel
séparateur (`head` + `cut -d`), et à quoi ressemble vraiment le fichier
(`head`). Dans cet ordre, ces trois vérifications résolvent la majorité des
blocages.

:::

## Les défis

:::::::::::::::::::::::::::::::::::::::::::  instructor

Formez des binômes pour les 45 minutes qui suivent. Un binôme, un clavier à la
fois, on échange de rôle entre deux défis. Faites une mise en commun rapide au
tableau toutes les quinze minutes environ (après les défis 2, 4 et 6) : demandez
à un binôme différent chaque fois de montrer sa commande, sans forcément
attendre que tout le monde ait fini.

Ne donnez pas la solution avant que le binôme n'ait tenté au moins une
construction étage par étage. Si un binôme est bloqué, demandez-lui d'abord
« qu'est-ce que `head` de ce fichier vous montre » avant de regarder son tube.
Les défis sont ordonnés par difficulté croissante ; un binôme rapide peut
avancer seul, un binôme lent peut s'arrêter au défi 6 sans dommage — le défi 8
est le plus formateur mais pas le plus indispensable.

::::::::::::::::::::::::::::::::::::::::::::::::::::::

### Défi 1 — GFF3 vers BED

:::::::::::::::::::::::::::::::::::::::::::  challenge

## Défi 1 : convertir l'annotation en BED

Le format BED est 0-based demi-ouvert sur la coordonnée de début, alors que
GFF3 est 1-based fermé sur les deux coordonnées : pour convertir un début
GFF3 en début BED, il faut lui soustraire 1. Produisez, à partir des lignes de
type `gene` de `data/genome/annotation.gff3`, un fichier BED
`resultats/genes.bed` à quatre colonnes : chromosome, début 0-based, fin,
nom du gène (le champ `Name=` de la colonne 9).

:::::::::::::::::::::::::::::  solution

## Solution

```bash
grep -v '^#' data/genome/annotation.gff3 | awk -F'\t' '$3 == "gene" {
  split($9, champs, ";")
  nom = ""
  for (i = 1; i <= length(champs); i++) {
    if (champs[i] ~ /^Name=/) {
      sub(/^Name=/, "", champs[i])
      nom = champs[i]
    }
  }
  print $1 "\t" $4 - 1 "\t" $5 "\t" nom
}' > resultats/genes.bed
wc -l resultats/genes.bed
head -3 resultats/genes.bed
```

```output
     128 resultats/genes.bed
chr1	170	513	arf4D
chr1	955	1509	eef3B
chr1	1725	2307	rho6B
```

Le premier `grep -v '^#'` écarte les lignes d'en-tête du GFF3, sans quoi
`awk` tenterait de comparer `$3` sur des lignes qui n'ont pas neuf champs. Le
filtre `$3 == "gene"` (POSIX, disponible dans tout awk) ne garde que les
lignes de gène, en écartant `mRNA` et `exon`. `split($9, champs, ";")`
découpe la colonne d'attributs sur le point-virgule dans un tableau, et la
boucle `for` cherche l'élément qui commence par `Name=` pour en extraire la
valeur avec `sub`. `$4 - 1` applique la conversion 1-based vers 0-based. On
retrouve bien 128 lignes, autant que de gènes dans l'annotation.

:::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::::::

### Défi 2 — table gène → longueur, triée

:::::::::::::::::::::::::::::::::::::::::::  challenge

## Défi 2 : longueur de chaque gène, du plus long au plus court

À partir de `resultats/genes.bed` produit au défi précédent, calculez la
longueur de chaque gène (fin moins début) et écrivez dans
`resultats/longueurs_genes.tsv` une table à deux colonnes, nom du gène et
longueur, triée du gène le plus long au plus court.

:::::::::::::::::::::::::::::  solution

## Solution

```bash
awk -F'\t' '{print $4 "\t" $3 - $2}' resultats/genes.bed | sort -k2,2 -n -r > resultats/longueurs_genes.tsv
head -5 resultats/longueurs_genes.tsv
```

```output
cox5C	711
srp3B	704
srp6A	702
ago8D	684
efl6D	681
```

`awk` calcule `$3 - $2`, c'est-à-dire fin moins début, pour chaque gène du
BED. `sort -k2,2 -n -r` trie ensuite numériquement sur la deuxième colonne en
ordre décroissant. Comme `resultats/genes.bed` n'a pas de ligne d'en-tête
(contrairement à `comptages.tsv` vu plus haut), le piège du tri sur l'en-tête
ne se pose pas ici.

:::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::::::

### Défi 3 — variants d'une région donnée

:::::::::::::::::::::::::::::::::::::::::::  challenge

## Défi 3 : variants dans une région

Extrayez de `data/variants/cohorte.vcf` tous les variants situés sur `chr1`
entre les positions 40 000 et 45 000 incluses, et écrivez-les dans
`resultats/variants_region.vcf` en conservant les lignes d'en-tête qui
commencent par `#`.

:::::::::::::::::::::::::::::  solution

## Solution

```bash
grep '^#' data/variants/cohorte.vcf > resultats/variants_region.vcf
awk -F'\t' '$1 == "chr1" && $2 >= 40000 && $2 <= 45000' data/variants/cohorte.vcf >> resultats/variants_region.vcf
grep -vc '^#' resultats/variants_region.vcf
```

```output
7
```

La première commande recopie les lignes d'en-tête telles quelles avec `>`
(écrasement). La seconde ajoute, avec `>>` (ajout), les lignes de données dont
la première colonne vaut `chr1` et dont la position (`$2`) est comprise entre
40 000 et 45 000. `awk` compare `$2` numériquement parce qu'il est utilisé
dans une comparaison arithmétique. On retrouve deux variants dans cette
fenêtre.

:::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::::::

### Défi 4 — contrôle qualité express des lectures

:::::::::::::::::::::::::::::::::::::::::::  challenge

## Défi 4 : combien de lectures dans chaque fichier, et lequel est tronqué

Pour chacun des douze fichiers de `data/reads/`, comptez le nombre de lectures
(rappel : quatre lignes par lecture dans un FASTQ) et écrivez le résultat dans
`resultats/controle_qualite_reads.tsv` à deux colonnes : nom de fichier,
nombre de lectures. Identifiez ensuite le fichier dont le nombre de lignes
n'est pas un multiple de quatre.

:::::::::::::::::::::::::::::  solution

## Solution

```bash
for fichier in data/reads/*.fastq.gz
do
  lignes=$(gunzip -c "$fichier" | wc -l)
  lectures=$((lignes / 4))
  printf '%s\t%d\n' "$(basename "$fichier")" "$lectures" >> resultats/controle_qualite_reads.tsv
done
cat resultats/controle_qualite_reads.tsv
```

```output
ech01_R1.fastq.gz	500
ech01_R2.fastq.gz	500
ech02_R1.fastq.gz	500
ech02_R2.fastq.gz	500
ech03_R1.fastq.gz	500
ech03_R2.fastq.gz	500
ech04_R1.fastq.gz	500
ech04_R2.fastq.gz	499
ech05_R1.fastq.gz	500
ech05_R2.fastq.gz	500
ech06_R1.fastq.gz	500
ech06_R2.fastq.gz	500
```

La boucle `for` (épisode 14) parcourt les douze fichiers, `gunzip -c | wc -l`
compte les lignes décompressées sans écrire de fichier intermédiaire, et la
division entière `$((lignes / 4))` donne le nombre de lectures. `ech04_R2`
affiche 499, alors que tous les autres affichent 500 : cela signifie que ce
fichier compte 1 998 lignes et non 2 000, un multiple qui n'est pas divisible
par quatre — le dernier bloc FASTQ y est donc incomplet.

::: callout

## Retrouver l'anomalie autrement

On peut arriver à la même conclusion sans diviser, en cherchant directement
quel fichier n'a pas un nombre de lignes multiple de quatre :

```bash
for fichier in data/reads/*.fastq.gz
do
  lignes=$(gunzip -c "$fichier" | wc -l)
  reste=$((lignes % 4))
  if [ "$reste" -ne 0 ]
  then
    printf 'fichier tronque : %s (%d lignes)\n' "$(basename "$fichier")" "$lignes"
  fi
done
```

```output
fichier tronque : ech04_R2.fastq.gz (1998 lignes)
```

L'opérateur `%` donne le reste de la division entière ; un reste non nul
signale un nombre de lignes qui n'est pas multiple de quatre, donc un fichier
FASTQ mal formé.

:::

:::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::::::

### Défi 5 — l'échantillon anormal dans les comptages

:::::::::::::::::::::::::::::::::::::::::::  challenge

## Défi 5 : trouver l'échantillon dont le total de comptages diffère des autres

Pour chacun des six échantillons de `data/tables/comptages.tsv`, calculez la
somme des comptages sur les 128 gènes, écrivez le résultat dans
`resultats/totaux_comptages.tsv`, et repérez à l'œil l'échantillon dont le
total se démarque nettement des cinq autres.

:::::::::::::::::::::::::::::  solution

## Solution

<!-- verif: exec-seulement -->
```bash
awk -F'\t' 'NR == 1 {
  for (i = 3; i <= NF; i++) nom[i] = $i
  next
}
{
  for (i = 3; i <= NF; i++) total[i] += $i
}
END {
  for (i = 3; i <= 8; i++) print nom[i] "\t" total[i]
}' data/tables/comptages.tsv > resultats/totaux_comptages.tsv
sort -k2,2 -n resultats/totaux_comptages.tsv
```

```output
ech02	27249
ech01	29180
ech03	31196
ech05	38289
ech06	39603
ech04	43079
```

Le bloc `NR == 1` mémorise, la première ligne lue, les noms d'échantillons
présents dans l'en-tête, dans un tableau indexé par numéro de colonne. Le bloc
principal accumule ensuite, ligne par ligne, la somme de chaque colonne dans
le tableau `total`. Le `END` imprime chaque nom en face de son total. Le tri
numérique fait ressortir `ech05` nettement en dessous des cinq autres, cohérent
avec un échantillon de moins bonne qualité de séquençage repéré à l'épisode 5.

:::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::::::

### Défi 6 — statistiques par condition

:::::::::::::::::::::::::::::::::::::::::::  challenge

## Défi 6 : comparer les totaux entre les conditions « temoin » et « traite »

En croisant `resultats/totaux_comptages.tsv` (produit au défi 5) avec
`data/tables/echantillons.tsv`, écrivez dans
`resultats/totaux_par_condition.tsv` chaque échantillon avec sa condition, puis
calculez la moyenne des totaux pour la condition `temoin` et pour la condition
`traite`.

:::::::::::::::::::::::::::::  solution

## Solution

<!-- verif: exec-seulement -->
```bash
sort -k1,1 resultats/totaux_comptages.tsv > tmp/totaux_tries.tsv
tail -n +2 data/tables/echantillons.tsv | cut -f1,2 | sort -k1,1 > tmp/echantillons_tries.tsv
join -t "$(printf '\t')" -1 1 -2 1 tmp/echantillons_tries.tsv tmp/totaux_tries.tsv > resultats/totaux_par_condition.tsv
cat resultats/totaux_par_condition.tsv
```

```output
ech01	temoin	64291
ech02	temoin	59288
ech03	temoin	61914
ech04	traite	63811
ech05	traite	48622
ech06	traite	62488
```

`join` (épisode 8) exige que les deux fichiers soient triés sur la colonne de
jointure, d'où les deux `sort -k1,1` préalables. `tail -n +2` écarte la ligne
d'en-tête d'`echantillons.tsv` avant le tri. Le résultat associe chaque
échantillon à sa condition et à son total.

<!-- verif: ordre-libre -->
```bash
awk -F'\t' '{ somme[$2] += $3; nombre[$2]++ } END { for (c in somme) print c "\t" somme[c] / nombre[c] }' resultats/totaux_par_condition.tsv
```

```output
traite	40323.7
temoin	29208.3
```

Le tableau associatif `somme` accumule les totaux par condition et `nombre`
compte les échantillons de chaque condition ; la division en `END` donne la
moyenne. L'ordre d'affichage de `for (c in somme)` n'est pas garanti par POSIX
awk, d'où le marqueur d'ordre libre sur ce bloc.

:::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::::::

### Défi 7 — inventaire de `brut_desordre`

:::::::::::::::::::::::::::::::::::::::::::  challenge

## Défi 7 : combien de fichiers, quelles extensions, lesquels sont des FASTQ

`data/brut_desordre/` contient des fichiers aux noms peu commodes (espaces,
majuscules, parenthèses). Sans les renommer, répondez par écrit dans
`resultats/inventaire_desordre.txt` à trois questions : combien de fichiers au
total, quelles extensions distinctes apparaissent, et lesquels sont
réellement des fichiers FASTQ d'après leur contenu plutôt que leur nom.

:::::::::::::::::::::::::::::  solution

## Solution

<!-- verif: ordre-libre -->
```bash
{
  echo "=== nombre total de fichiers ==="
  find data/brut_desordre -type f | wc -l

  echo "=== extensions distinctes ==="
  find data/brut_desordre -type f -print0 | xargs -0 -I{} basename {} | sed -E 's/^.*\.([^.]+)$/\1/' | tr '[:upper:]' '[:lower:]' | sort -u

  echo "=== fichiers dont la premiere ligne commence par @ (FASTQ probable) ==="
  find data/brut_desordre -type f -print0 | xargs -0 -I{} sh -c 'head -c 1 "{}" | grep -q "@" && echo {}'
} > resultats/inventaire_desordre.txt
cat resultats/inventaire_desordre.txt
```

```output
=== nombre total de fichiers ===
       8
=== extensions distinctes ===
fastq
txt
=== fichiers dont la premiere ligne commence par @ (FASTQ probable) ===
data/brut_desordre/Ech04_final_VRAIMENT_final.fastq
data/brut_desordre/Echantillon 01 - Run mars.fastq
data/brut_desordre/echantillon_02.FASTQ
data/brut_desordre/ech06 -- a refaire.fastq
data/brut_desordre/ech05.resultats.fastq
```

`find -type f -print0` associé à `xargs -0` (épisode 18) est indispensable ici
: les espaces dans les noms de fichiers casseraient toute autre approche sans
`-print0`/`-0`. `basename` isole le nom du fichier de son chemin, `sed -E`
récupère ce qui suit le dernier point comme extension, et `tr` uniformise la
casse pour ne pas compter séparément `.fastq` et `.FASTQ`. Le troisième bloc
lit le premier caractère de chaque fichier avec `head -c 1` : un fichier FASTQ
commence toujours par `@`. Cela confirme que six des huit fichiers sont des
FASTQ malgré des noms très variés, et que les deux fichiers `.txt` (les
notes) n'en sont pas.

:::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::::::

### Défi 8 — interprétation puis correction

:::::::::::::::::::::::::::::::::::::::::::  challenge

## Défi 8 : lisez ce tube, dites ce qu'il fait, puis corrigez-le

Une collègue affirme que ce tube compte le nombre de gènes de chaque biotype
dans l'annotation, mais elle ne comprend pas son résultat :

```bash
grep -v '^#' data/genome/annotation.gff3 | cut -f9 | sed -E 's/.*biotype=//' | sort | uniq -c
```

1. Exécutez ce tube et lisez son résultat.
2. Dites pourquoi le résultat ne correspond pas à un compte par biotype de
   gène.
3. Corrigez-le pour qu'il compte réellement, une fois chaque gène, le nombre
   de gènes de chaque biotype, et écrivez le résultat corrigé dans
   `resultats/comptage_biotypes.tsv`.

:::::::::::::::::::::::::::::  solution

## Solution

Étape 1, exécuter le tube tel quel :

<!-- verif: exec-seulement -->

```bash
grep -v '^#' data/genome/annotation.gff3 | cut -f9 | sed -E 's/.*biotype=//' | sort | uniq -c
```

```output
   1 ID=exon:GENE00001.1;Parent=transcript:GENE00001.1
   1 ID=exon:GENE00002.1;Parent=transcript:GENE00002.1
   1 ID=exon:GENE00002.2;Parent=transcript:GENE00002.1
   1 ID=exon:GENE00002.3;Parent=transcript:GENE00002.1
   1 ID=exon:GENE00003.1;Parent=transcript:GENE00003.1
   1 ID=exon:GENE00003.2;Parent=transcript:GENE00003.1
   1 ID=exon:GENE00003.3;Parent=transcript:GENE00003.1
   1 ID=exon:GENE00004.1;Parent=transcript:GENE00004.1
   1 ID=exon:GENE00004.2;Parent=transcript:GENE00004.1
   1 ID=exon:GENE00004.3;Parent=transcript:GENE00004.1
   1 ID=exon:GENE00005.1;Parent=transcript:GENE00005.1
   1 ID=exon:GENE00005.2;Parent=transcript:GENE00005.1
   1 ID=exon:GENE00005.3;Parent=transcript:GENE00005.1
   1 ID=exon:GENE00006.1;Parent=transcript:GENE00006.1
   1 ID=exon:GENE00006.2;Parent=transcript:GENE00006.1
   1 ID=exon:GENE00006.3;Parent=transcript:GENE00006.1
   1 ID=exon:GENE00007.1;Parent=transcript:GENE00007.1
   1 ID=exon:GENE00007.2;Parent=transcript:GENE00007.1
   1 ID=exon:GENE00008.1;Parent=transcript:GENE00008.1
   1 ID=exon:GENE00008.2;Parent=transcript:GENE00008.1
   1 ID=exon:GENE00009.1;Parent=transcript:GENE00009.1
   1 ID=exon:GENE00009.2;Parent=transcript:GENE00009.1
   1 ID=exon:GENE00009.3;Parent=transcript:GENE00009.1
   1 ID=exon:GENE00010.1;Parent=transcript:GENE00010.1
   1 ID=exon:GENE00010.2;Parent=transcript:GENE00010.1
   1 ID=exon:GENE00011.1;Parent=transcript:GENE00011.1
   1 ID=exon:GENE00011.2;Parent=transcript:GENE00011.1
   1 ID=exon:GENE00011.3;Parent=transcript:GENE00011.1
   1 ID=exon:GENE00012.1;Parent=transcript:GENE00012.1
   1 ID=exon:GENE00012.2;Parent=transcript:GENE00012.1
```

<!-- verif: exec-seulement -->

Étape 2, l'explication. Le tube ne filtre jamais sur la colonne 3 : il prend
la colonne 9 de **toutes** les lignes, y compris les `mRNA` et les `exon`, qui
ne portent pas d'attribut `biotype=`. `sed -E 's/.*biotype=//'` ne trouve donc
rien à remplacer sur ces lignes-là et les laisse intactes, ce qui explique
pourquoi le résultat affiche des lignes d'attributs d'exon entières au lieu
d'un mot comme `protein_coding`. Le tube ne compte donc pas des biotypes, il
compte des lignes qui n'ont jamais été filtrées par type.

Étape 3, la correction : ajouter un filtre sur la colonne 3 avant d'extraire
le biotype.

```bash
grep -v '^#' data/genome/annotation.gff3 | awk -F'\t' '$3 == "gene"' | cut -f9 | sed -E 's/.*biotype=//' | sort | uniq -c > resultats/comptage_biotypes.tsv
cat resultats/comptage_biotypes.tsv
```

```output
 115 protein_coding
  13 pseudogene
```

`awk -F'\t' '$3 == "gene"'` ne garde que les lignes de gène avant de passer la
colonne 9 à `sed`, qui peut alors extraire proprement ce qui suit
`biotype=` sur chacune. `sort | uniq -c` compte ensuite les occurrences de
chaque biotype restant. Le total, 115 plus 13, redonne bien les 128 gènes de
l'annotation.

:::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::::::

### Défi étoilé (facultatif) — protéines par organisme et par famille

:::::::::::::::::::::::::::::::::::::::::::  challenge

## Défi facultatif : combien de protéines par organisme dans `proteines.fa`

Chaque en-tête de `data/proteines/proteines.fa` contient un champ `OS=` donnant
l'organisme. Écrivez dans `resultats/proteines_par_organisme.tsv` le nombre de
séquences protéiques par organisme, triées de l'organisme le plus représenté
au moins représenté.

:::::::::::::::::::::::::::::  solution

## Solution

<!-- verif: ordre-libre -->
```bash
grep '^>' data/proteines/proteines.fa | sed -E 's/.*OS=([A-Za-z]+ [a-z]+).*/\1/' | sort | uniq -c | sort -k1,1 -n -r > resultats/proteines_par_organisme.tsv
cat resultats/proteines_par_organisme.tsv
```

```output
  11 Escherichia coli
   8 Arabidopsis thaliana
   6 Mus musculus
   6 Homo sapiens
   5 Drosophila melanogaster
   4 Saccharomyces cerevisiae
```

`sed -E` capture, entre `OS=` et le champ suivant (`OX=`), les deux mots qui
forment le nom d'espèce, grâce au groupe de capture `\1`. `sort | uniq -c`
compte les occurrences de chaque organisme, et le second `sort -k1,1 -n -r`
trie sur le compte lui-même en ordre décroissant.

:::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::::::

::: callout

## Vers l'épisode suivant

Vous venez d'écrire, à la main, des tubes de quatre ou cinq commandes pour
chacun des six échantillons ou pour chaque fichier de `data/reads/`. Refaire
cela un par un pour chaque nouvel échantillon n'a rien d'agréable : c'est
précisément le problème que résolvent les scripts et les boucles, à partir de
l'épisode suivant.

:::

::::::::::::::::::::::::::::::::::::::::::  keypoints

- On construit un tube étage par étage, en vérifiant chaque sortie
  intermédiaire avec `head` avant d'ajouter l'étage suivant.
- On lit un tube inconnu en le découpant du début, fragment par fragment,
  plutôt qu'en l'exécutant tel quel et en devinant.
- Devant un résultat inattendu, on vérifie dans l'ordre : le répertoire de
  travail (`pwd`), le séparateur de champs, et le contenu réel du fichier
  (`head`).
- `grep`, `cut`, `sort`, `uniq`, `awk` et `sed` se combinent pour convertir des
  formats, croiser des tables et détecter des anomalies, sans qu'aucune
  commande nouvelle ne soit nécessaire.
- Un résultat qui ne correspond pas à l'intention d'un tube révèle presque
  toujours un filtre manquant, et non une commande mal choisie.

::::::::::::::::::::::::::::::::::::::::::::::::::::::
