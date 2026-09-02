---
title: "Les formats de la bioinformatique, ligne par ligne"
teaching: 30
exercises: 20
---

:::::::::::::::::::::::::::::::::::::::  questions

- Quels formats vais-je rencontrer en bioinformatique et à quoi servent-ils ?
- Comment lire un fichier FASTA, FASTQ, GFF3, BED, VCF ou SAM sans logiciel
  spécialisé ?
- Pourquoi une même position sur le génome peut-elle être notée différemment
  selon le fichier ?

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::: objectives

- Identifier un format de fichier bioinformatique à partir de sa structure.
- Décrire le rôle de chacun des champs d'une ligne FASTQ, GFF3, BED, VCF et SAM.
- Convertir une position entre les conventions 0-based demi-ouverte et 1-based
  fermée.
- Repérer dans un fichier réel une lecture non alignée, une ligne d'en-tête ou
  une anomalie de format.

::::::::::::::::::::::::::::::::::::::::::::::::::

Depuis l'épisode 4, vous savez ouvrir n'importe quel fichier texte avec `cat`,
`head`, `tail` ou `less`, décompressé ou non. Il vous manque une chose : savoir
lire ce qui s'affiche. La bioinformatique s'appuie sur une poignée de formats
texte, chacun avec ses propres conventions. Cet épisode est une visite guidée
de `data/` : pour chaque format, vous verrez à quoi il sert, une ligne réelle
décortiquée champ par champ, et les pièges qui font perdre du temps.

Commencez par vous placer à la racine du projet et par préparer un répertoire
de travail.

```bash
mkdir -p resultats tmp
```

## FASTA : des séquences, rien d'autre

Le FASTA stocke des séquences (ADN, ARN ou protéines) sans aucune information
de position. Chaque séquence commence par une ligne d'en-tête débutant par
`>`, suivie d'une ou plusieurs lignes de séquence.

```bash
head -4 data/genome/ref_toy.fa
```

```output
>chr1 chromosome 1, assemblage jouet v1.0 length=100000
ATTAAGGCATGCTGGTATATTTTTTAACACAGAAAAGCAAGATGACGACATTCGCGATGG
TTGACGACGTGACTTCTTTAAATTCGCGGGTTGCACCGTCCTTTGGTTCAATACAAATAT
GGACTTAACTAATTTATGCAAATTACAGTAGGTACTCTAAGCTCCGAGATGTAGGCTGGT
```

Décortiquons la ligne d'en-tête :

| Élément | Valeur | Signification |
|---|---|---|
| `>` | `>` | Marque le début d'une nouvelle séquence |
| identifiant | `chr1` | Nom de la séquence, jusqu'au premier espace |
| description | `chromosome 1, assemblage jouet v1.0 length=100000` | Texte libre, ignoré par la plupart des outils |

Le piège classique du FASTA : seul ce qui précède le premier espace est
considéré comme l'identifiant par la majorité des outils. Le reste de la ligne
n'est qu'une annotation lisible par l'humain. Vérifiez combien de séquences
contient ce génome jouet :

```bash
grep -c '^>' data/genome/ref_toy.fa
```

```output
2
```

Deux séquences : `chr1` (chromosome) et `chrM` (génome mitochondrial). Autre
piège : les lignes de séquence n'ont pas toujours la même longueur. Le fichier
`ref_toy.fa` utilise 60 caractères par ligne, mais rien dans le format ne
l'impose — un même fichier FASTA peut mélanger des lignes de 60 et 80
caractères, ou même écrire une séquence entière sur une seule ligne.

Le fichier `data/proteines/proteines.fa` contient, lui, des séquences
protéiques avec des en-têtes descriptifs de type UniProt :

```bash
head -2 data/proteines/proteines.fa
```

```output
>sp|P27322|PROT01_TOY ribosomal protein OS=Escherichia coli OX=69275 GN=prot1 PE=1 SV=1
MPKECMFGVFHFITSITNEEACAMVHPFYDTCTNLRKHHDNMTDDFNTKCGMAAVGAEIN
```

| Champ (séparateur `|`) | Valeur | Signification |
|---|---|---|
| base de données | `sp` | *Swiss-Prot*, la base annotée d'UniProt |
| accession | `P27322` | Identifiant unique et stable de la protéine |
| nom d'entrée | `PROT01_TOY` | Nom court |
| description | `ribosomal protein` | Fonction |
| `OS=` | `Escherichia coli` | Organisme d'origine (*organism species*) |
| `OX=` | `69275` | Identifiant taxonomique |
| `GN=` | `prot1` | Nom du gène |

::: callout

## L'index `.fai` : retrouver une séquence sans tout lire

Un fichier FASTA peut peser plusieurs gigaoctets. Pour éviter de le relire en
entier chaque fois qu'un outil a besoin d'une séquence, on l'accompagne d'un
fichier d'index de même nom suivi de `.fai` (*FASTA index*).

```bash
cat data/genome/ref_toy.fa.fai
```

```output
chr1	100000	56	60	61
chrM	5000	101785	60	61
```

Chaque ligne décrit une séquence du FASTA : son nom, sa longueur en bases, la
position en octets du premier caractère de séquence dans le fichier, le nombre
de caractères par ligne, et le nombre d'octets par ligne (caractères plus fin
de ligne). Un outil peut ainsi sauter directement au bon endroit du fichier
sans le parcourir depuis le début. Retenez seulement la convention de nommage
`fichier.fa.fai` : vous la retrouverez pour d'autres formats indexés
(`.bai`, `.tbi`) dans la seconde formation.

:::

## FASTQ : une séquence et sa qualité

Le FASTQ complète le FASTA par une information essentielle en séquençage : la
confiance accordée à chaque base lue. Chaque lecture (*read*) occupe exactement
quatre lignes.

```bash
gunzip -c data/reads/ech01_R1.fastq.gz | head -4
```

```output
@ECH01:1:FLOWCELL1:1:1101:1000:2000 1:N:0:ATCACG
CAGTTTTTGTCTGTGATTTTGAAACTGCAATTCATTTAAACTAAGTCTACAGTAGCTACTTAAAATTGCAACTCCATTGAACGGCCTTATGCCTATCCAG
+
B?DCBCEDEGEFCGFGDEECDFFGCDDFEFDCEFCEDCEGEEEDGFDFFEFGFFEFEGGEGCCFCFFFFFDDFEFGDCGEEGFBCA@@C@@?><=>;<=;
```

| Ligne | Contenu | Signification |
|---|---|---|
| 1 | `@ECH01:1:FLOWCELL1:1:1101:1000:2000 1:N:0:ATCACG` | Identifiant de la lecture, débutant par `@` |
| 2 | `CAGTTTTTGTCTG...` | Séquence lue, une base par caractère |
| 3 | `+` | Séparateur, peut répéter l'identifiant de la ligne 1 |
| 4 | `B?DCBCEDEGEFC...` | Qualité de chaque base, un caractère par base |

La ligne 4 a exactement la même longueur que la ligne 2 : à chaque base
correspond un caractère de qualité. Ce caractère code un score Phred selon
l'encodage **Phred+33** : on prend le code ASCII du caractère et on lui
soustrait 33 pour obtenir le score de qualité. Un `!` (code ASCII 33) vaut un
score de 0, un `I` (code ASCII 73) vaut un score de 40. Plus le score est
élevé, plus la base est fiable ; un score de 30 signifie une probabilité
d'erreur d'environ 1 sur 1 000.

Comparez la ligne de qualité d'un échantillon propre et celle d'un échantillon
dégradé :

```bash
gunzip -c data/reads/ech05_R1.fastq.gz | head -4
```

```output
@ECH05:1:FLOWCELL1:3:1101:1000:2000 1:N:0:ACAGTG
TAAATGCGACTCAAGACAGTTATTTCCCATAGTTTGGGTGCATAGTTAATTGTTCGGCAAGCTGAAGTTGACGTCTACCCACGCTCGACCGTGTTCAAGA
+
42537889889675876868658567788999796985686688667787666568997888595857766586669867678446351023120/--,-
```

Dans `ech01`, la ligne de qualité est dominée par des lettres majuscules
(`D`, `E`, `F`, `G`), qui correspondent à des scores élevés. Dans `ech05`, elle
est dominée par des chiffres (`3`, `4`, `5`) et se termine par des symboles de
ponctuation (`,`, `-`, `.`), qui correspondent à des scores bas : sans calculer
de moyenne, on peut déjà voir à l'œil qu'`ech05` est de moins bonne qualité.
C'est cohérent avec le journal `pipeline.log`, qui signale cet échantillon.

::: caution

## Le piège du `+` et du `@`

La ligne 3 vaut toujours `+`, parfois suivi du même identifiant que la ligne 1.
Mais rien n'empêche un caractère de qualité de la ligne 4 d'être lui-même `@`
ou `+` : un score de qualité de 31 correspond au caractère `@`. On ne peut donc
pas repérer le début d'une lecture en cherchant simplement les lignes qui
commencent par `@` — il faut compter les lignes quatre par quatre. C'est
pourquoi compter les lectures d'un FASTQ se fait en divisant le nombre total de
lignes par quatre, jamais en comptant les `@`.

:::

## GFF3 : l'annotation du génome

Le GFF3 (*General Feature Format*, version 3) décrit des éléments annotés sur
un génome : gènes, transcrits, exons. C'est un format à 9 colonnes séparées par
des tabulations, précédé de lignes d'en-tête commençant par `##`.

```bash
head -8 data/genome/annotation.gff3
```

```output
##gff-version 3
##sequence-region chr1 1 100000
##sequence-region chrM 1 5000
#!genome-build assemblage-jouet v1.0
#!genome-date 2024-09
chr1	formation	gene	171	513	.	-	.	ID=gene:GENE00001;Name=arf4D;biotype=protein_coding
chr1	formation	mRNA	171	513	.	-	.	ID=transcript:GENE00001.1;Parent=gene:GENE00001;Name=arf4D-201
chr1	formation	exon	171	513	.	-	.	ID=exon:GENE00001.1;Parent=transcript:GENE00001.1
```

Décortiquons la première ligne de données :

| Colonne | Nom | Valeur | Signification |
|---|---|---|---|
| 1 | seqid | `chr1` | Séquence de référence |
| 2 | source | `formation` | Origine de l'annotation |
| 3 | type | `gene` | Type de l'élément (terme du vocabulaire *Sequence Ontology*) |
| 4 | start | `171` | Position de début, 1-based |
| 5 | end | `513` | Position de fin, 1-based, incluse |
| 6 | score | `.` | Score, absent ici |
| 7 | strand | `-` | Brin : `+`, `-` ou `.` si inconnu |
| 8 | phase | `.` | Phase de lecture, utilisée seulement pour les CDS |
| 9 | attributs | `ID=gene:GENE00001;Name=arf4D;biotype=protein_coding` | Paire `clé=valeur` séparées par `;` |

La colonne 9 concentre l'information la plus riche : c'est une liste
d'attributs `clé=valeur` séparés par des points-virgules. Ici, `ID` identifie
l'élément de façon unique, `Name` donne un nom lisible, et `biotype` précise la
catégorie du gène. Une ligne `mRNA` porte en plus un attribut `Parent` qui
référence l'`ID` du `gene` dont elle dépend : c'est ainsi que le fichier encode
la hiérarchie gène → transcrit → exon sans imbrication, uniquement par
référence.

::: caution

## Piège : les lignes `##` ne sont pas des commentaires ordinaires

Les lignes commençant par `##` (double croisillon) portent une information
structurée — version du format, bornes d'une séquence — que certains outils
exploitent. Les lignes commençant par `#!` sont des métadonnées libres propres
à qui a produit le fichier. Toutes deux doivent néanmoins être exclues d'un
traitement colonne par colonne, avec `grep -v '^#'` par exemple, sous peine de
faire planter un `cut` ou un `awk` qui suppose 9 colonnes partout.

:::

## BED : des intervalles simples

Le BED (*Browser Extensible Data*) décrit des intervalles sur un génome, sans
la richesse du GFF3 : pas de hiérarchie, pas d'attributs structurés, juste des
régions. C'est le format le plus simple de la visite, et c'est justement ce
qui en fait le piège le plus dangereux, comme vous allez le voir dans
l'encadré suivant.

```bash
head -3 data/regions/cibles.bed
```

```output
chr1	955	1509	eef3B	448	+
chr1	2633	3257	rho5B	244	-
chr1	6782	7339	fbx4D	605	+
```

| Colonne | Nom | Valeur | Signification |
|---|---|---|---|
| 1 | chrom | `chr1` | Séquence de référence |
| 2 | chromStart | `955` | Début de l'intervalle, 0-based |
| 3 | chromEnd | `1509` | Fin de l'intervalle, exclue |
| 4 | name | `eef3B` | Nom de la région |
| 5 | score | `448` | Score, sens libre selon le producteur du fichier |
| 6 | strand | `+` | Brin |

Seules les trois premières colonnes sont obligatoires dans la spécification
BED ; les colonnes 4 à 6 sont des extensions courantes mais optionnelles, et
d'autres fichiers BED en ajouteront davantage. Retenez que le nombre de
colonnes d'un BED n'est pas fixe d'un fichier à l'autre, contrairement au GFF3.

## VCF : les variants génétiques

Le VCF (*Variant Call Format*) décrit des positions où un échantillon diffère
d'une référence : substitutions, insertions, délétions. Comme le GFF3, il
commence par des lignes d'en-tête `##`, suivies d'une ligne `#CHROM` qui nomme
les colonnes.

```bash
head -18 data/variants/cohorte.vcf | tail -3
```

```output
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	ech01	ech02	ech03	ech04	ech05	ech06
chr1	218	.	A	AGG	482.1	PASS	DP=35;AF=0.557;TYPE=indel	GT:DP:GQ	0/0:19:17	0/1:7:53	0/1:6:29	1/1:16:85	0/0:51:37	1/1:51:34
chr1	1435	var0002	T	C	427.9	PASS	DP=20;AF=0.82;TYPE=snp	GT:DP:GQ	1/1:57:36	0/1:14:33	1/1:46:75	./.:45:20	1/1:6:83	0/0:53:29
```

Décortiquons cette ligne de variant :

| Colonne | Valeur | Signification |
|---|---|---|
| CHROM | `chr1` | Séquence de référence |
| POS | `218` | Position, 1-based |
| ID | `.` | Identifiant connu du variant, absent ici (`.`) |
| REF | `A` | Allèle de référence |
| ALT | `AGG` | Allèle alternatif observé (ici, une insertion) |
| QUAL | `482.1` | Score de confiance du variant |
| FILTER | `PASS` | Résultat des filtres qualité (`PASS`, ou une raison de rejet) |
| INFO | `DP=35;AF=0.557;TYPE=indel` | Attributs `clé=valeur` décrivant le variant lui-même |
| FORMAT | `GT:DP:GQ` | Liste ordonnée des champs fournis pour chaque échantillon |
| ech01 | `0/0:19:17` | Valeurs de ech01 pour GT, DP et GQ, dans cet ordre |

La colonne FORMAT est une clé de lecture : elle définit l'ordre des valeurs
qui suivent, une colonne par échantillon. Ici, `GT:DP:GQ` signifie que
`0/0:19:17` se lit génotype `0/0` (homozygote pour la référence), profondeur
`19`, qualité de génotype `17`. Un autre fichier VCF pourrait annoncer
`GT:AD:DP:GQ:PL` en FORMAT, avec un champ de plus par échantillon : il faut
toujours relire la colonne FORMAT de la ligne considérée, elle peut varier
d'une ligne à l'autre du même fichier.

::: caution

## Piège : `FILTER` n'est pas toujours `PASS`

La colonne FILTER ne garantit rien par défaut : `PASS` signifie que le
variant a passé les filtres qualité, mais une valeur comme `LowQual` ou
`LowDepth` signifie qu'il ne les a pas passés et qu'il figure quand même dans
le fichier, à titre informatif. Prendre tous les variants d'un VCF sans
regarder FILTER revient à ignorer un contrôle qualité déjà calculé pour vous.

:::

## SAM : les lectures alignées sur le génome

Le SAM (*Sequence Alignment/Map*) décrit où chaque lecture d'un FASTQ se
positionne sur un génome de référence. Il commence par des lignes d'en-tête
débutant par `@`, puis une ligne par lecture alignée, avec 11 champs
obligatoires.

```bash
head -6 data/alignements/ech01.sam
```

```output
@HD	VN:1.6	SO:coordinate
@SQ	SN:chr1	LN:100000
@SQ	SN:chrM	LN:5000
@RG	ID:ech01	SM:ech01	LB:lib1	PL:ILLUMINA
@PG	ID:aligneur-jouet	PN:aligneur-jouet	VN:0.1
ECH01:1:FLOWCELL1:1:1101:2659:2711	0	chr1	69	60	60M3D40M	*	0	0	GTGACTTCTTTAAATTCGCGGGTTGCACCGTCCTTTGGTTCAATACAAATATGGACTTAACTAATTTATGCAAATTACAGTAGGTACTCTAAGCTCCGAG	?C==DG?E=?AFBCG>CAHIECGEC@FG?=ABEFGEHI=F=CHCA?D?E?EEI=?FFC>DDC=@CABCIFCBDGDHFGCGE?HB=GHEBBGH??FBHG=I	NM:i:1	RG:Z:ech01	AS:i:95
```

Les lignes d'en-tête se lisent ainsi :

| Ligne | Signification |
|---|---|
| `@HD` | En-tête général : version du format (`VN`), ordre de tri (`SO:coordinate`) |
| `@SQ` | Une ligne par séquence du génome de référence, avec son nom (`SN`) et sa longueur (`LN`) |
| `@RG` | Groupe de lecture : échantillon (`SM`), bibliothèque (`LB`), technologie (`PL`) |
| `@PG` | Programme ayant produit le fichier |

Puis les 11 champs obligatoires de la ligne d'alignement :

| N° | Nom | Valeur | Signification |
|---|---|---|---|
| 1 | QNAME | `ECH01:...:2711` | Identifiant de la lecture, identique à la ligne 1 du FASTQ d'origine |
| 2 | FLAG | `0` | Codes binaires empilés (voir plus bas) |
| 3 | RNAME | `chr1` | Séquence de référence sur laquelle la lecture s'aligne |
| 4 | POS | `69` | Position de début de l'alignement, 1-based |
| 5 | MAPQ | `60` | Qualité de l'alignement (0 = mauvaise, jusqu'à 60 environ) |
| 6 | CIGAR | `60M3D40M` | Description de l'alignement base par base (M = match, D = délétion, ...) |
| 7 | RNEXT | `*` | Référence de la lecture appariée, `*` si sans objet ici |
| 8 | PNEXT | `0` | Position de la lecture appariée |
| 9 | TLEN | `0` | Longueur totale du fragment |
| 10 | SEQ | `GTGACTTC...` | Séquence alignée |
| 11 | QUAL | `?C==DG?E...` | Qualité, même encodage Phred+33 que le FASTQ |

Au-delà du champ 11, des champs optionnels `TAG:TYPE:VALEUR` comme `NM:i:1`
(nombre de différences avec la référence) complètent la ligne, en nombre
variable selon l'aligneur.

Le champ FLAG mérite une explication à part : c'est un nombre unique qui
empile plusieurs informations binaires. Retenez seulement les valeurs les plus
courantes de ce jeu de données :

| FLAG | Signification |
|---|---|
| `0` | Lecture alignée sur le brin direct, rien de particulier à signaler |
| `16` | Lecture alignée sur le brin inverse (complémentaire) |
| `4` | Lecture non alignée |

Une lecture non alignée se reconnaît par son FLAG à `4`, et corrélativement par
un RNAME à `*` (aucune référence) et un MAPQ à `0` :

<!-- verif: exec-seulement -->
```bash
awk -F'\t' '$2 == 4' data/alignements/ech01.sam | head -1
```

```output
ECH01:1:FLOWCELL1:1:1101:1133:2057	4	*	0	0	*	*	0	0	GTAACTCATTAGATGCTTTAAACGGACTCTGTTTATTGAAGTTAATATACGTCGCGTATTTAATTATTAATCTATAAGGTTTAAATCTGCGTCAGTGCTA	=CBA@AFB@ADIGA=@HFIF?BG>@AHDCFDIEIID>FCCHGE>E>=EGFEEG@EGBBIEHFFDFIE>EBF??BI?ECBCFCHEIFE@=>AID>=>E=BI	NM:i:3	RG:Z:ech01	AS:i:85
```

Notez que RNAME et CIGAR valent tous les deux `*` : sans référence
d'alignement, il n'y a rien à décrire en CIGAR non plus.

::: caution

## Coordonnées : 0-based demi-ouvert contre 1-based fermé

**C'est le piège le plus coûteux de toute la bioinformatique en ligne de
commande.** Deux conventions coexistent pour numéroter les positions sur une
séquence, et confondre les deux décale silencieusement tous vos résultats
d'une base.

- **BED** compte à partir de **0** et exclut la borne de fin : c'est un
  intervalle *demi-ouvert*, noté `[début, fin)`.
- **GFF3, VCF et SAM** comptent à partir de **1** et incluent la borne de
  fin : c'est un intervalle *fermé*, noté `[début, fin]`.

Schéma pour les 5 premières bases d'une séquence `A T T A A` :

```
position 1-based :   1   2   3   4   5
séquence :           A   T   T   A   A
position 0-based : 0   1   2   3   4   5
```

Le premier `A` est en position `1` en 1-based, mais occupe l'intervalle `[0, 1)`
en 0-based. Prenons un exemple chiffré avec le gène `eef3B` du fichier BED :

```
BED  (0-based, demi-ouvert) : chromStart=955   chromEnd=1509
GFF3 (1-based, fermé)       : start=956        end=1509
```

Pour passer d'une base en 0-based à la même base en 1-based, on ajoute 1 au
début et on ne change pas la fin. C'est exactement ce que l'on observe entre
`cibles.bed` (`955`) et `annotation.gff3` (`956`) pour la même région
génique : la borne de fin, `1509`, est identique dans les deux fichiers,
seule la borne de début diffère d'une unité.

**Retenez la règle pratique : BED début → GFF3/VCF/SAM début, on ajoute 1. Les
fins ne changent pas.** Ne jamais soustraire ou additionner à l'aveugle sans
avoir vérifié dans quel format on se trouve.

:::

## TSV : des tables simples

Le TSV (*Tab-Separated Values*) n'est pas un format bioinformatique à
proprement parler, mais c'est le format le plus fréquent pour tout ce qui n'est
ni séquence ni alignement : matrices de comptage, feuilles d'échantillons,
résultats tabulaires. Une ligne d'en-tête nomme les colonnes, puis une ligne
par enregistrement, colonnes séparées par une tabulation.

```bash
head -3 data/tables/comptages.tsv
```

```output
gene_id	gene_name	ech01	ech02	ech03	ech04	ech05	ech06
GENE00001	arf4D	518	478	269	513	369	411
GENE00002	eef3B	0	0	0	0	0	0
```

| Colonne | Valeur (GENE00001) | Signification |
|---|---|---|
| gene_id | `GENE00001` | Identifiant stable du gène |
| gene_name | `arf4D` | Nom lisible du gène |
| ech01 … ech06 | `518` … `411` | Nombre de lectures comptées pour ce gène dans chaque échantillon |

Le TSV ne porte aucune règle propre au-delà de « une tabulation entre chaque
champ » : c'est sa force (n'importe quel outil sait le lire) et sa faiblesse
(rien n'empêche une valeur de contenir elle-même un espace, ce qui n'est pas un
problème puisque le séparateur est la tabulation, mais devient un problème si
le fichier mélange tabulations et espaces).

:::::::::::::::::::::::::::::::::::::::  challenge

## Compter les champs d'une ligne SAM

Combien de champs séparés par une tabulation compte la première ligne
d'alignement (non `@`) de `data/alignements/ech01.sam` ? Le nombre correspond-il
aux 11 champs obligatoires ?

:::::::::::::::  solution

## Solution

```bash
grep -v '^@' data/alignements/ech01.sam | head -1 | tr '\t' '\n' | wc -l
```

```output
      14
```

14 champs, alors que le SAM n'impose que 11 champs obligatoires. Les trois
champs supplémentaires (`NM:i:1`, `RG:Z:ech01`, `AS:i:95`) sont des champs
optionnels ajoutés par l'aligneur : leur nombre varie d'une ligne à l'autre et
d'un aligneur à l'autre, contrairement aux 11 premiers champs qui sont fixes.
`tr '\t' '\n'` remplace chaque tabulation par une fin de ligne, ce qui permet à
`wc -l` de compter les champs comme s'ils étaient des lignes.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  challenge

## Convertir une position BED en position GFF3

La deuxième région de `data/regions/cibles.bed` est `rho5B`, avec
`chromStart=2633` et `chromEnd=3257`. Quelles seraient les valeurs `start` et
`end` équivalentes dans un fichier GFF3 ?

:::::::::::::::  solution

## Solution

Le BED est 0-based demi-ouvert, le GFF3 est 1-based fermé. On ajoute 1 à la
borne de début, la borne de fin ne change pas :

- `start` GFF3 = 2633 + 1 = **2634**
- `end` GFF3 = **3257**

Vous pouvez vérifier que ce calcul correspond bien à une région du GFF3 réel :

```bash
awk -F'\t' '$4 == 2634' data/genome/annotation.gff3
```

```output
chr1	formation	gene	2634	3257	.	-	.	ID=gene:GENE00004;Name=rho5B;biotype=lncRNA
chr1	formation	mRNA	2634	3257	.	-	.	ID=transcript:GENE00004.1;Parent=gene:GENE00004;Name=rho5B-201
chr1	formation	exon	2634	2753	.	-	.	ID=exon:GENE00004.1;Parent=transcript:GENE00004.1
```

Le gène `GENE00004` porte le nom `rho5B`, exactement la région annoncée dans
le BED, avec les coordonnées converties comme prévu.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  challenge

## Le VCF est-il trié par position

En parcourant seulement les 20 premières lignes de variants (hors en-tête) de
`data/variants/cohorte.vcf`, les positions de la colonne POS sont-elles dans
l'ordre croissant au sein de chaque chromosome ?

:::::::::::::::  solution

## Solution

<!-- verif: exec-seulement -->
```bash
grep -v '^#' data/variants/cohorte.vcf | cut -f1,2 | head -5
```

```output
chr1	218
chr1	1435
chr1	1696
chr1	3078
chr1	3528
```

Les positions augmentent ligne après ligne pour `chr1`, ce qui est le
comportement attendu d'un VCF trié par coordonnée : c'est la convention
habituelle, qui permet à un outil de balayer le fichier séquentiellement sans
jamais revenir en arrière. Un VCF non trié n'est pas invalide, mais il oblige
les outils à charger tout le fichier en mémoire pour le retrier, ou à réclamer
un tri préalable.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  challenge

## Repérer une lecture non alignée

Sans compter à l'œil, déterminez si la ligne suivante décrit une lecture
alignée ou non alignée, et justifiez avec les champs qui vous permettent de le
dire :

```
ECH01:1:FLOWCELL1:1:1103:5522:8841	4	*	0	0	*	*	0	0	TTGACG...	FFDCB...	NM:i:0	RG:Z:0	AS:i:0
```

:::::::::::::::  solution

## Solution

Non alignée. Trois indices concordants, chacun suffisant en soi :

- le champ FLAG (2e champ) vaut `4`, qui signale précisément l'absence
  d'alignement ;
- le champ RNAME (3e champ) vaut `*`, c'est-à-dire aucune séquence de
  référence ;
- le champ MAPQ (5e champ) vaut `0`, qualité minimale, cohérente avec
  l'absence d'alignement.

Le champ CIGAR (6e champ) vaut également `*` : sans alignement, il n'y a rien
à décrire base par base.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  challenge

## Combien de lectures non alignées dans ech01 (facultatif)

En utilisant `grep` et `wc -l` uniquement, comptez le nombre de lignes
d'alignement de `data/alignements/ech01.sam` dont le champ RNAME vaut `*`.

:::::::::::::::  solution

## Solution

<!-- verif: exec-seulement -->
```bash
grep -v '^@' data/alignements/ech01.sam | cut -f3 | grep -c '^\*$'
```

```output
18
```

`cut -f3` extrait la colonne RNAME de chaque ligne d'alignement, puis
`grep -c '^\*$'` compte les lignes qui contiennent exactement un astérisque.
L'astérisque doit être protégé par un antislash car, dans une expression
régulière, `*` est un quantificateur et non un caractère littéral : sans
antislash, le motif ne voudrait rien dire à cette position. Ce nombre de
lectures non alignées est cohérent avec l'anomalie volontaire du jeu de
données, qui prévoit une proportion minoritaire de lectures non alignées dans
`ech01.sam`.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

Vous savez maintenant lire, champ par champ, les formats FASTA, FASTQ, GFF3,
BED, VCF, SAM et TSV, et vous ne confondrez plus une position BED avec une
position GFF3. Le prochain épisode s'appuie directement sur cette lecture pour
combiner plusieurs fichiers entre eux avec les redirections et les tubes.

:::::::::::::::::::::::::::::::::::::::: keypoints

- Un fichier FASTA associe un en-tête `>` à une séquence ; seul le texte avant
  le premier espace de l'en-tête sert d'identifiant.
- Un enregistrement FASTQ occupe toujours quatre lignes : identifiant, séquence,
  séparateur `+`, qualité encodée en Phred+33.
- Le GFF3 a 9 colonnes fixes dont une colonne d'attributs `clé=valeur`, précédée
  de lignes d'en-tête `##`.
- Le BED décrit des intervalles avec un nombre de colonnes variable, dont
  seules les trois premières sont obligatoires.
- Le VCF nomme ses colonnes d'échantillons après une ligne `#CHROM`, et la
  colonne FORMAT donne l'ordre de lecture des valeurs par échantillon.
- Le SAM a 11 champs obligatoires par ligne d'alignement ; le FLAG `4`, le
  RNAME `*` et le MAPQ `0` signalent ensemble une lecture non alignée.
- BED compte les positions à partir de 0 et exclut la fin de l'intervalle ;
  GFF3, VCF et SAM comptent à partir de 1 et incluent la fin.
- Un fichier `.fai` indexe un FASTA pour permettre l'accès direct à une
  séquence sans relire le fichier entier.

::::::::::::::::::::::::::::::::::::::::::::::::::
