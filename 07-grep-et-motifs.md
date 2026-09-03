---
title: "Chercher un motif avec grep"
teaching: 30
exercises: 25
---

:::::::::::::::::::::::::::::::::::::::  questions

- Comment retrouver toutes les lignes qui contiennent un mot ou un motif précis ?
- Comment compter des occurrences sans les afficher une par une ?
- Comment repérer, dans un texte long, un motif décrit par une forme plutôt que par un mot exact ?

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::: objectives

- Extraire les lignes correspondant à un motif avec `grep`.
- Combiner les options `-c`, `-i`, `-v`, `-n`, `-w`, `-o`, `-l`, `-r`, `-A`/`-B`/`-C` selon le besoin.
- Écrire une expression régulière étendue avec les ancres, les classes de caractères et les quantificateurs.
- Distinguer un motif littéral d'un motif construit avec des métacaractères.

::::::::::::::::::::::::::::::::::::::::::::::::::

## Depuis le début de la journée

Vous savez lire un fichier (`cat`, `head`, `less`), le rediriger, et enchaîner
des commandes avec le tube (*pipe*). Vous avez rencontré les principaux formats
de la bioinformatique et vous savez déjà trier et dédupliquer avec `sort` et
`uniq`. Il vous manque un outil essentiel : chercher, dans un fichier de
plusieurs centaines ou milliers de lignes, seulement celles qui vous
intéressent. C'est le rôle de `grep` — le nom vient de *global regular
expression print*, une commande de recherche née avec Unix il y a cinquante
ans et toujours la première qu'on utilise.

Placez-vous à la racine du projet, là où se trouve `data/`, et créez un
répertoire pour vos résultats :

```bash
mkdir -p resultats tmp
```

## `grep` tout court : chercher une chaîne

La forme la plus simple de `grep` prend un motif (*pattern*) et un fichier, et
affiche toutes les lignes qui le contiennent :

```bash
grep 'gene' data/genome/annotation.gff3 | head -3
```

```output
chr1	formation	gene	171	513	.	-	.	ID=gene:GENE00001;Name=arf4D;biotype=protein_coding
chr1	formation	mRNA	171	513	.	-	.	ID=transcript:GENE00001.1;Parent=gene:GENE00001;Name=arf4D-201
chr1	formation	gene	956	1509	.	+	.	ID=gene:GENE00002;Name=eef3B;biotype=protein_coding
```

Remarquez la première ligne : `##gff-version 3` ne contient pas le mot
« gene » au sens biologique, mais la chaîne de caractères `gene` apparaît bien
dans « gff-version 3 »… non, en réalité elle n'y est pas — regardez de plus
près ce que `grep` a réellement trouvé à chaque fois. C'est la première leçon
de cet épisode : `grep` ne comprend rien à la biologie, il compare des
caractères. Une bonne partie de l'art consiste à écrire un motif qui ne
capture que ce que vous voulez.

::: callout

## Toujours entre apostrophes

Dans toute cette leçon, le motif de `grep` est systématiquement écrit entre
apostrophes : `grep 'motif' fichier`. Sans elles, le shell essaierait
d'interpréter certains caractères du motif — une étoile, un crochet, une
espace — avant même que `grep` ne les reçoive, avec des résultats
imprévisibles selon le contenu du répertoire courant. Les apostrophes disent
au shell : ce texte est à transmettre tel quel. Retenez le geste dès
maintenant ; l'épisode 16 en donnera la raison complète, liée à
l'interprétation des variables et des jokers par le shell.

:::

## Compter plutôt qu'afficher : `-c`

La première question qu'on se pose devant un FASTA est presque toujours : « combien
de séquences contient ce fichier ? ». Chaque séquence commence par une ligne
d'en-tête débutant par `>`. Il suffit de compter ces lignes :

```bash
grep -c '>' data/proteines/proteines.fa
```

```output
40
```

L'option `-c` (*count*) remplace l'affichage des lignes par leur nombre. Ici,
40 correspond exactement au nombre d'en-têtes du fichier de protéines.

::: caution

## `grep '>' fichier` écrase le fichier

Il existe une confusion dangereuse, spécifique à `grep` : le caractère `>`
dans un motif ressemble à une redirection. Si vous oubliez les apostrophes et
tapez :

<!-- verif: ignore -->
```bash
grep -c >gene data/genome/annotation.gff3
```

le shell lit ceci *avant* de lancer `grep` : il voit `>gene`, comprend « crée
(ou vide) un fichier nommé `gene` et redirige la sortie dedans », puis lance
`grep -c` sans motif ni fichier à comparer. Le résultat est silencieux et
dévastateur : un fichier `gene` vide apparaît dans votre répertoire, et si ce
nom existait déjà, son contenu est perdu. Le motif `'>'`, entre apostrophes,
n'est jamais interprété par le shell : c'est la forme à utiliser
systématiquement, en particulier avec les FASTA où l'en-tête commence
justement par `>`.

La bonne commande pour compter les séquences d'un FASTA est donc :

```bash
grep -c '^>' data/proteines/proteines.fa
```

(le `^` sera expliqué dans la section sur les ancres ; retenez pour l'instant
la forme complète telle qu'elle est écrite ici).

:::

## Ignorer la casse : `-i`

Les noms de gènes ou d'organismes n'ont pas toujours une casse homogène dans
les fichiers réels. L'option `-i` (*ignore case*) rend la recherche
insensible aux majuscules et minuscules :

```bash
grep -i 'coli' data/proteines/proteines.fa | head -2
```

```output
>sp|P27322|PROT01_TOY ribosomal protein OS=Escherichia coli OX=69275 GN=prot1 PE=1 SV=1
>sp|P33266|PROT08_TOY heat shock protein OS=Escherichia coli OX=75484 GN=prot8 PE=1 SV=1
```

Sans `-i`, une variante orthographiée `Coli` ou `COLI` serait passée
inaperçue.

## Inverser la sélection : `-v`

`-v` (*invert*) affiche les lignes qui ne contiennent **pas** le motif. C'est
la commande à retenir pour retirer les lignes d'en-tête d'un fichier
tabulaire avant un traitement, ou pour écarter une catégorie qui ne vous
intéresse pas :

```bash
grep -v '^#' data/variants/cohorte.vcf | head -2
```

```output
chr1	218	.	A	AGG	482.1	PASS	DP=35;AF=0.557;TYPE=indel	GT:DP:GQ	0/0:19:17	0/1:7:53	0/1:6:29	1/1:16:85	0/0:51:37	1/1:51:34
chr1	1435	var0002	T	C	427.9	PASS	DP=20;AF=0.82;TYPE=snp	GT:DP:GQ	1/1:57:36	0/1:14:33	1/1:46:75	./.:45:20	1/1:6:83	0/0:53:29
```

Toutes les lignes d'en-tête du VCF commencent par `#` ; `-v '^#'` les retire
et ne laisse que les variants eux-mêmes.

## Numéroter les lignes trouvées : `-n`

`-n` (*number*) fait précéder chaque ligne trouvée de son numéro dans le
fichier — utile pour revenir ensuite au bon endroit avec un éditeur, ou pour
signaler une anomalie :

<!-- verif: exec-seulement -->
```bash
grep -n 'LowQual' data/variants/cohorte.vcf | head -3
```

```output
8:##FILTER=<ID=LowQual,Description="Qualite insuffisante">
42:chr1	14350	.	C	T	4.5	LowQual	DP=43;AF=0.253;TYPE=snp	GT:DP:GQ	./.:52:97	0/0:9:80	0/1:10:79	0/0:5:84	0/0:22:13	./.:39:22
82:chr1	39768	var0066	T	A	11.2	LowQual	DP=84;AF=0.521;TYPE=snp	GT:DP:GQ	0/0:48:52	0/1:57:83	1/1:51:66	0/0:21:25	1/1:6:48	0/0:31:20
```

## Chercher un mot entier : `-w`

Un problème classique : chercher le nom de gène `arf4D` avec un simple
`grep 'arf4D'` fonctionne, mais chercher un identifiant court comme `1` ou une
abréviation risque de tomber sur des occurrences partielles à l'intérieur d'un
autre mot. L'option `-w` (*word*) exige que le motif forme un mot entier,
délimité par des espaces, la ponctuation ou le début/la fin de ligne :

```bash
grep -w 'gene' data/genome/annotation.gff3 | wc -l
```

```output
     256
```

```bash
grep 'gene' data/genome/annotation.gff3 | wc -l
```

```output
     256
```

Ici les deux commandes donnent le même compte, car dans ce fichier « gene »
n'apparaît jamais comme fragment d'un autre mot sur la colonne qui nous
intéresse. Mais réservez le réflexe `-w` pour tout identifiant court ou tout
nom de gène qui pourrait être le préfixe d'un autre : c'est une sécurité peu
coûteuse.

## N'extraire que la partie qui correspond : `-o`

Par défaut, `grep` affiche la ligne entière dès qu'elle contient le motif.
L'option `-o` (*only matching*) n'affiche que la portion de texte qui a
réellement été reconnue. C'est la différence entre « quelle ligne contient
ça ? » et « qu'est-ce qui a été trouvé, exactement ? » :

```bash
grep -o 'GENE[0-9]*' data/genome/annotation.gff3 | head -5
```

```output
GENE00001
GENE00001
GENE00001
GENE00001
GENE00001
```

Nous reviendrons dans un instant sur ce que signifie `[0-9]*` : c'est déjà une
expression régulière.

## Lister les fichiers concernés : `-l`

Quand la question porte sur des fichiers plutôt que sur des lignes — « dans
quel fichier ce motif apparaît-il ? » — `-l` (*files with matches*) remplace
l'affichage des lignes par la simple liste des noms de fichiers où le motif a
été trouvé au moins une fois :

```bash
grep -l 'chrM' data/genome/*.gff3 data/variants/*.vcf
```

```output
data/genome/annotation.gff3
data/variants/cohorte.vcf
```

## Chercher dans toute une arborescence : `-r`

`-r` (*recursive*) descend dans les sous-répertoires au lieu de se limiter aux
fichiers indiqués explicitement. Combinée à `-l`, elle répond à « où, dans
tout mon jeu de données, ce motif apparaît-il ? » :

<!-- verif: ordre-libre -->
```bash
grep -rl 'chrM' data/
```

```output
data/regions/cibles.bed
data/variants/cohorte.vcf
data/alignements/ech01.sam
data/README.md
data/genome/ref_toy.fa
data/genome/annotation.gff3
data/genome/ref_toy.fa.fai
```

## Voir le contexte : `-A`, `-B`, `-C`

Une ligne isolée manque parfois de contexte. Les trois options `-A`
(*after*), `-B` (*before*) et `-C` (*context*) affichent respectivement les
lignes qui suivent, qui précèdent, ou qui entourent chaque ligne trouvée.
C'est indispensable pour lire un journal d'exécution : une ligne `ERROR`
prend tout son sens entourée des étapes qui l'encadrent.

```bash
grep -B 2 -A 1 'ERROR' data/journaux/pipeline.log
```

```output
2024-09-17 08:48:55 [INFO] ech03 alignement - etape alignement terminee en 887s
2024-09-17 08:50:05 [INFO] ech03 comptage - etape comptage terminee en 70s
2024-09-17 08:50:52 [ERROR] ech04 controle_qualite - fichier ech04_R2.fastq.gz tronque : bloc FASTQ incomplet
2024-09-17 08:53:28 [INFO] ech04 nettoyage - etape nettoyage terminee en 156s
```

`-C 2` aurait affiché deux lignes avant et deux lignes après, de façon
symétrique. Ici nous avons choisi une asymétrie volontaire : deux lignes de
contexte avant l'erreur (pour voir les étapes précédentes de l'échantillon
concerné), une seule après.

:::::::::::::::::::::::::::::::::::::::  challenge

## Toutes les alertes du journal

`data/journaux/pipeline.log` contient 24 lignes au total. Affichez, en une
seule commande, toutes les lignes signalant un problème — qu'il s'agisse
d'une erreur ou d'un simple avertissement — avec leur numéro de ligne dans le
fichier.

:::::::::::::::  solution

## Solution

```bash
grep -n -E 'ERROR|WARNING' data/journaux/pipeline.log
```

```output
13:2024-09-17 08:50:52 [ERROR] ech04 controle_qualite - fichier ech04_R2.fastq.gz tronque : bloc FASTQ incomplet
18:2024-09-17 09:03:42 [WARNING] ech05 nettoyage - qualite moyenne inferieure au seuil (Q22), poursuite forcee
```

`-E` active les expressions régulières étendues (détaillées dans la section
suivante) et `|` signifie ici « ou » à l'intérieur du motif : la ligne est
retenue si elle contient `ERROR` **ou** `WARNING`. Sur les 24 lignes du
journal, deux seulement signalent un problème — une erreur sur `ech04`, un
avertissement sur `ech05 — noyées parmi les lignes `INFO` qui décrivent le
déroulement normal du pipeline.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

## Au-delà du mot exact : les expressions régulières

Jusqu'ici, chaque motif était une chaîne de caractères littérale, à
l'exception de `[0-9]*` utilisé plus haut sans explication. Une expression
régulière (*regular expression*) décrit une **forme** que peut prendre un
texte, plutôt qu'un texte précis. Elle répond à des questions comme
« un chiffre suivi de trois lettres », « une ligne qui commence par un
symbole précis », « ce mot ou cet autre ». `grep` sait interpréter les
expressions régulières étendues (*extended regular expressions*, POSIX ERE)
dès qu'on ajoute l'option `-E`.

### Le point : n'importe quel caractère

`.` représente un caractère quelconque, un et un seul :

```bash
grep -E 'ech0.' data/tables/echantillons.tsv
```

```output
ech01	temoin	1	L001	ech01_R1.fastq.gz	ech01_R2.fastq.gz
ech02	temoin	2	L001	ech02_R1.fastq.gz	ech02_R2.fastq.gz
ech03	temoin	3	L002	ech03_R1.fastq.gz	ech03_R2.fastq.gz
ech04	traite	1	L002	ech04_R1.fastq.gz	ech04_R2.fastq.gz
ech05	traite	2	L003	ech05_R1.fastq.gz	ech05_R2.fastq.gz
ech06	traite	3	L003	ech06_R1.fastq.gz	ech06_R2.fastq.gz
```

Chaque `ech0` suivi d'un chiffre correspond, mais un `.` correspondrait tout
aussi bien à une lettre : le point ne signifie pas « un chiffre », il
signifie « n'importe quoi ». Nous verrons dans un instant comment restreindre
précisément ce qui est accepté.

### Les ancres : `^` et `$`

`^` ancre le motif au début de la ligne, `$` à sa fin. Vous les avez déjà
croisés : `grep -c '^>'` compte les en-têtes de FASTA parce que `^>` n'accepte
le `>` qu'en toute première position de la ligne, jamais ailleurs.

```bash
grep -c '^>' data/proteines/proteines.fa
```

```output
40
```

Comparez avec la recherche du gène `eef3B`, qui doit apparaître précisément
comme nom de gène et non comme fragment d'un autre champ de la ligne
d'annotation :

```bash
grep 'Name=eef3B;' data/genome/annotation.gff3
```

```output
chr1	formation	gene	956	1509	.	+	.	ID=gene:GENE00002;Name=eef3B;biotype=protein_coding
```

### Les classes de caractères : `[...]` et `[^...]`

`[...]` accepte n'importe lequel des caractères listés entre crochets, un
seul à la fois. `[^...]`, à l'inverse, accepte n'importe quel caractère
**sauf** ceux listés. Les alignements SAM utilisent la colonne 2 comme
drapeau (*flag*) numérique : une lecture non alignée porte le drapeau `4`.
Repérer les lignes où le champ FLAG contient un `4` isolé, entouré de
tabulations, permet une première approche :

<!-- verif: exec-seulement -->
```bash
grep -E $'\t4\t' data/alignements/ech01.sam | wc -l
```

```output
      23
```

Ici `$'\t4\t'` insère de vraies tabulations dans le motif — une convention
du shell qui dépasse le cadre de cet épisode, mais que vous retrouverez utile
face à des fichiers tabulaires. Sur les 305 lignes du fichier SAM (dont 5
d'en-tête), ce motif retrouve les lectures dont le drapeau vaut exactement 4,
c'est-à-dire non alignées.

Un exemple plus direct des crochets : trouver, dans le génome, un motif
nucléotidique qui peut commencer par `A` ou par `T` :

<!-- verif: exec-seulement -->
```bash
grep -o '[AT]TGACG' data/genome/ref_toy.fa | sort | uniq -c
```

```output
      2 ATGACG
      1 TTGACG
```

### Les quantificateurs : `*`, `+`, `?`, `{n,m}`

Un quantificateur précise combien de fois l'élément qui le précède peut se
répéter :

| Quantificateur | Signification |
|---|---|
| `*` | zéro fois ou plus |
| `+` | une fois ou plus |
| `?` | zéro ou une fois |
| `{n,m}` | entre `n` et `m` fois |
| `{n}` | exactement `n` fois |

Reprenons l'extraction des identifiants de gène, en exigeant cette fois
explicitement des chiffres, ni plus ni moins :

```bash
grep -oE 'GENE[0-9]+' data/genome/annotation.gff3 | sort -u | head -3
```

```output
GENE00001
GENE00002
GENE00003
```

`[0-9]+` signifie « un chiffre, puis encore autant de chiffres qu'il en
faut, mais au moins un ». Sans le `+`, `[0-9]` seul n'aurait capturé qu'un
unique chiffre.

### L'alternative et les groupes : `|` et `(...)`

`|` signifie « ceci ou cela », comme dans le motif `ERROR|WARNING` déjà
rencontré. Les parenthèses `(...)` regroupent une partie du motif, en
particulier pour appliquer un quantificateur à plusieurs caractères à la
fois plutôt qu'à un seul :

<!-- verif: exec-seulement -->
```bash
grep -E '(TATA){2,}' data/genome/ref_toy.fa | head -1
```

```output
TGTTTCGCGACGTTATTGGAACGAGCTTGTTGTTGAAGTTGTAACGTGCATTATATATAA
```

Le groupe `(TATA)` répété deux fois ou plus chercherait la répétition exacte
`TATATATA` ; il se peut qu'aucune ligne de ce petit génome jouet ne la
contienne sous cette forme stricte, ce qui est en soi une information utile
lors d'une recherche de motif répété.

### Les classes POSIX

Écrire `[0-9]` fonctionne, mais les expressions régulières étendues
proposent des classes nommées, plus lisibles et surtout indépendantes de la
disposition des caractères dans la table utilisée par le système :

| Classe POSIX | Signification |
|---|---|
| `[[:digit:]]` | un chiffre |
| `[[:alpha:]]` | une lettre |
| `[[:alnum:]]` | une lettre ou un chiffre |
| `[[:space:]]` | une espace, une tabulation, un retour à la ligne |

Ces classes s'utilisent à l'intérieur des crochets, avec une paire de
crochets supplémentaire :

```bash
grep -oE 'GENE[[:digit:]]+' data/genome/annotation.gff3 | sort -u | wc -l
```

```output
     128
```

::: callout

## Pourquoi jamais `\d` ni `grep -P`

Sur un serveur Linux récent, `grep -P '\d+'` fonctionne : `-P` active les
expressions régulières compatibles Perl (*Perl-compatible regular
expressions*), qui ajoutent des raccourcis comme `\d` (chiffre), `\w`
(caractère de mot) ou `\s` (espace). Mais `-P` est une extension GNU,
absente du `grep` fourni par défaut sur macOS et sur les systèmes BSD : la
même commande y échoue avec une erreur. Les classes POSIX `[[:digit:]]`,
`[[:alpha:]]`, `[[:alnum:]]` et `[[:space:]]` utilisées avec `-E` produisent
le même résultat et fonctionnent identiquement sur tous les systèmes que
vous rencontrerez, y compris les serveurs de calcul sur lesquels vous
travaillerez après cette formation. Cette leçon n'utilise donc jamais `\d`,
`\w`, `\s` ni `grep -P`.

:::

:::::::::::::::::::::::::::::::::::::::  challenge

## Combien de séquences protéiques d'*Escherichia coli* ?

Combien de protéines de `data/proteines/proteines.fa` proviennent de
l'organisme *Escherichia coli* ? Le nom de l'organisme apparaît dans chaque
en-tête après `OS=`.

:::::::::::::::  solution

## Solution

```bash
grep -c 'OS=Escherichia coli' data/proteines/proteines.fa
```

```output
11
```

`-c` compte les lignes correspondantes plutôt que de les afficher. Le motif
`OS=Escherichia coli` est ici une chaîne littérale, sans métacaractère : elle
n'a besoin de rien d'autre pour être exacte, à condition de reproduire
fidèlement l'espace entre les deux mots de l'organisme.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  challenge

## Variants sans identifiant connu

Dans `data/variants/cohorte.vcf`, certains variants portent un identifiant
réel (par exemple `var0002`), d'autres n'ont qu'un point `.` en colonne ID
faute d'identifiant connu. Comptez les lignes de variants (pas les lignes
d'en-tête) où la colonne ID vaut exactement un point.

:::::::::::::::  solution

## Solution

```bash
grep -v '^#' data/variants/cohorte.vcf | grep -c -E $'\t\\.\t'
```

`-v '^#'` retire d'abord les lignes d'en-tête. Le second `grep` cherche une
tabulation, un point, une tabulation : le point doit être protégé par un
antislash (`\.`) parce que dans une expression régulière, un point non
protégé représente n'importe quel caractère et correspondrait aussi à autre
chose qu'un point littéral. Sans cette précaution, on compterait aussi des
lignes où un autre caractère se trouve exactement à cette position.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  challenge

## Repérer les lectures non alignées d'un SAM

Dans un fichier SAM, une lecture non alignée porte la valeur `*` dans la
colonne RNAME (le nom du chromosome de référence), en troisième position.
Utilisez `grep -c` pour compter, dans `data/alignements/ech01.sam`, les
lignes de données (pas les lignes d'en-tête `@`) où le troisième champ vaut
`*`.

:::::::::::::::  solution

## Solution

```bash
tabulation=$(printf '\t')
grep -v '^@' data/alignements/ech01.sam |
    grep -c -E "^[^$tabulation]+$tabulation[^$tabulation]+$tabulation\*$tabulation"
```

```output
23
```

Attention à un piège de portabilité : `\t` dans un motif n'est **pas** reconnu
par toutes les implémentations de `grep`. Celle de macOS l'interprète comme une
tabulation, celle de GNU/Linux le lit comme la lettre `t`, et le motif ne
correspond alors à rien. D'où le détour par `tabulation=$(printf '\t')`, qui
place une vraie tabulation dans la variable : le motif contient dès lors le
caractère lui-même, et se comporte de la même façon partout.

`grep -v '^@'` élimine les lignes d'en-tête, qui commencent toutes par `@`.
Le second motif décompose la ligne en champs séparés par des tabulations :
`[^\t]+` signifie « un ou plusieurs caractères qui ne sont pas une
tabulation », donc un champ entier. En répétant ce groupe deux fois avant de
chercher `\*` suivi d'une tabulation, on s'assure de tester précisément le
troisième champ (RNAME), et non n'importe quelle occurrence du caractère `*`
ailleurs dans la ligne — par exemple dans la colonne CIGAR ou la séquence.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  challenge

## Un motif nucléotidique dans le génome (facultatif)

Cherchez, dans `data/genome/ref_toy.fa`, toutes les occurrences du motif
`GAATTC` (site de coupure de l'enzyme EcoRI), en excluant bien la ligne
d'en-tête. Affichez uniquement la portion trouvée avec `-o`, et comptez le
nombre total d'occurrences dans le fichier.

:::::::::::::::  solution

## Solution

```bash
grep -v '^>' data/genome/ref_toy.fa | grep -o 'GAATTC' | wc -l
```

`grep -v '^>'` retire les lignes d'en-tête (celles qui commencent par `>`),
qui ne contiennent pas de séquence et n'ont pas à être scrutées pour ce
motif. `grep -o 'GAATTC'` n'affiche que la sous-chaîne trouvée, une fois par
occurrence, y compris si plusieurs occurrences apparaissent sur la même
ligne — un simple `grep -c` aurait compté des *lignes*, pas des
*occurrences*, ce qui aurait sous-estimé le résultat en cas de motif répété
sur une même ligne. `wc -l` compte enfin le nombre total de lignes produites,
donc le nombre total d'occurrences.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

## Récapitulatif des métacaractères

| Métacaractère | Signification | Nécessite `-E` |
|---|---|---|
| `.` | un caractère quelconque | non |
| `^` | début de ligne | non |
| `$` | fin de ligne | non |
| `[...]` | un caractère parmi ceux listés | non |
| `[^...]` | un caractère absent de la liste | non |
| `*` | zéro occurrence ou plus de l'élément précédent | non |
| `+` | une occurrence ou plus | oui |
| `?` | zéro ou une occurrence | oui |
| `{n,m}` | entre `n` et `m` occurrences | oui |
| `\|` | alternative (ceci ou cela) | oui |
| `(...)` | regroupement | oui |
| `[[:digit:]]` | un chiffre | non (mais dans des crochets) |
| `[[:alpha:]]` | une lettre | non (mais dans des crochets) |
| `[[:alnum:]]` | une lettre ou un chiffre | non (mais dans des crochets) |
| `[[:space:]]` | un caractère d'espacement | non (mais dans des crochets) |

En pratique, cette leçon utilise systématiquement `-E` dès qu'un
métacaractère apparaît dans un motif : c'est une habitude simple qui évite
de devoir se souvenir, au cas par cas, de ce qui nécessite ou non un
antislash devant lui en syntaxe POSIX de base.

:::::::::::::::::::::::::::::::::::::::::::::::::: keypoints

- `grep 'motif' fichier` affiche les lignes contenant le motif ; le motif se met toujours entre apostrophes.
- `-c` compte, `-i` ignore la casse, `-v` inverse, `-n` numérote, `-w` exige un mot entier, `-o` n'affiche que la partie trouvée.
- `-l` liste les fichiers concernés, `-r` cherche récursivement dans une arborescence.
- `-A`, `-B` et `-C` affichent des lignes de contexte après, avant et autour de chaque résultat.
- `grep -c '^>' fichier.fa` compte les séquences d'un FASTA sans risquer d'écraser le fichier, contrairement à `grep '>' fichier.fa` mal protégé.
- `-E` active les expressions régulières étendues : `.`, `^`, `$`, `[...]`, `*`, `+`, `?`, `{n,m}`, `|`, `(...)`.
- Les classes `[[:digit:]]`, `[[:alpha:]]`, `[[:alnum:]]` et `[[:space:]]` remplacent partout `\d`, `\w`, `\s` et `grep -P`, absents des systèmes BSD.

::::::::::::::::::::::::::::::::::::::::::::::::::
