---
title: "awk : champs, motifs, conditions"
teaching: 30
exercises: 25
---

:::::::::::::::::::::::::::::::::::::::  questions

- Comment extraire une colonne quand `cut` ne suffit plus ?
- Comment ne garder que les lignes qui vérifient une condition numérique ?
- Comment recalculer une valeur à partir de plusieurs champs, à la volée ?

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::: objectives

- Décrire le fonctionnement de `awk` : lecture ligne par ligne, découpage en
  champs, exécution de `motif { action }`.
- Extraire et réorganiser des champs avec `$1`, `$NF`, `-F` et `print`.
- Filtrer des lignes avec une expression régulière ou une condition sur un
  champ, en combinant plusieurs conditions.
- Mettre en forme une sortie avec `printf` et ses spécificateurs `%s`, `%d`,
  `%.2f`.

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::: prereq

Cet épisode suppose l'épisode 8 acquis (`cut`, `sort`, `tr`) ainsi que la
lecture des formats GFF3 et VCF vue à l'épisode 5.

::::::::::::::::::::::::::::::::::::::::::::::::::

Depuis le début de la journée, vous découpez des tables avec `cut`, vous les
triez avec `sort`, vous en comptiez les doublons avec `uniq -c`. Ces outils
partagent tous la même limite : ils ne savent rien faire d'un champ à part le
copier ou le comparer tel quel. Impossible de calculer la longueur d'un gène,
impossible de ne garder que les variants dont la qualité dépasse un seuil,
impossible de reformater une ligne GFF3 en ligne BED. C'est exactement ce que
fait `awk`.

Placez-vous à la racine du projet et préparez un répertoire pour vos
résultats.

```bash
mkdir -p resultats tmp
```

## Le modèle d'exécution de awk

`awk` lit son entrée **ligne par ligne**. Pour chaque ligne, il découpe
automatiquement le contenu en **champs** séparés par des espaces ou des
tabulations, puis il évalue un programme de la forme :

```
motif { action }
```

Si le motif est vrai pour la ligne courante, l'action s'exécute. Si vous
omettez le motif, l'action s'exécute pour toutes les lignes. Si vous omettez
l'action, `awk` imprime la ligne (comme `grep`) quand le motif est vrai.

Commencez par le programme le plus simple possible : imprimer une colonne du
fichier d'annotation.

```bash
head -6 data/genome/annotation.gff3
```

```output
##gff-version 3
##sequence-region chr1 1 100000
##sequence-region chrM 1 5000
#!genome-build assemblage-jouet v1.0
#!genome-date 2024-09
chr1	formation	gene	171	513	.	-	.	ID=gene:GENE00001;Name=arf4D;biotype=protein_coding
```

Le fichier est au format GFF3 : les colonnes sont séparées par des
tabulations. Affichez la troisième colonne, celle du type de caractéristique,
pour les dix premières lignes de données :

```bash
grep -v '^#' data/genome/annotation.gff3 | head -10 | awk '{ print $3 }'
```

```output
gene
mRNA
exon
gene
mRNA
exon
exon
exon
gene
mRNA
```

`$3` désigne le troisième champ de la ligne courante. `$0` désigne la ligne
entière, non découpée : `awk '{ print $0 }'` se comporte comme `cat`. `NF`
(*number of fields*) contient le nombre de champs de la ligne courante, et
`NR` (*number of records*) le numéro de la ligne courante depuis le début de
l'entrée — le même compteur que celui qu'affiche `grep -n`.

```bash
grep -v '^#' data/genome/annotation.gff3 | head -3 | awk '{ print NR, NF, $3 }'
```

```output
1 9 gene
2 9 mRNA
3 9 exon
```

Chaque ligne du GFF3 a bien neuf champs, comme vu à l'épisode 5.

::::::::::::::::::::::::::::::::::::::  callout

## Pourquoi les apostrophes autour du programme awk

Le programme awk contient des espaces, des accolades et souvent des signes
`$`. Sans apostrophes, le shell essaierait d'interpréter `$3` comme une
variable shell (et la remplacerait par une chaîne vide) avant même que `awk`
ne voie le programme. Les apostrophes (guillemets simples) empêchent toute
substitution : le shell transmet le texte tel quel à `awk`, qui l'interprète
lui-même.

```bash
echo 'sans apostrophes, $3 disparaîtrait'
```

```output
sans apostrophes, $3 disparaîtrait
```

Prenez l'habitude d'écrire systématiquement `awk '{ ... }'` avec des
apostrophes, même pour un programme qui ne contient pas de `$` : c'est le
réflexe qui évite l'erreur le jour où vous en ajoutez un.

:::::::::::::::::::::::::::::::::::::::::::::::::

## Séparateur de champs : `-F`

Le GFF3 est séparé par des tabulations, ce que `awk` détecte correctement
avec son comportement par défaut (espaces et tabulations confondus). Mais le
fichier `regions/cibles.bed` aussi est séparé par des tabulations, et le VCF
également : pour l'instant tout va bien. Le jour où un fichier est séparé par
des virgules, vous devez le dire à `awk` avec l'option `-F` :

```bash
awk -F',' '{ print $1 }' data/tables/echantillons.tsv
```

Ce fichier est en réalité séparé par des tabulations, pas des virgules :
`-F','` cherche des virgules qu'il ne trouve pas, et chaque ligne entière
devient donc le premier champ.

```output
sample_id	condition	replicat	lane	fichier_R1	fichier_R2
ech01	temoin	1	L001	ech01_R1.fastq.gz	ech01_R2.fastq.gz
ech02	temoin	2	L001	ech02_R1.fastq.gz	ech02_R2.fastq.gz
ech03	temoin	3	L002	ech03_R1.fastq.gz	ech03_R2.fastq.gz
ech04	traite	1	L002	ech04_R1.fastq.gz	ech04_R2.fastq.gz
ech05	traite	2	L003	ech05_R1.fastq.gz	ech05_R2.fastq.gz
ech06	traite	3	L003	ech06_R1.fastq.gz	ech06_R2.fastq.gz
```

Avec le bon séparateur explicite, `-F'\t'`, `awk` retrouve les colonnes :

```bash
awk -F'\t' '{ print $1, $2 }' data/tables/echantillons.tsv
```

```output
sample_id condition
ech01 temoin
ech02 temoin
ech03 temoin
ech04 traite
ech05 traite
ech06 traite
```

## `print` avec virgules, `print` par concaténation

Observez la différence entre les deux programmes suivants, qui affichent
tous deux le nom et la condition d'un échantillon.

```bash
awk -F'\t' 'NR > 1 { print $1, $2 }' data/tables/echantillons.tsv
```

```output
ech01 temoin
ech02 temoin
ech03 temoin
ech04 traite
ech05 traite
ech06 traite
```

```bash
awk -F'\t' 'NR > 1 { print $1 $2 }' data/tables/echantillons.tsv
```

```output
ech01temoin
ech02temoin
ech03temoin
ech04traite
ech05traite
ech06traite
```

La virgule entre `$1` et `$2` insère le séparateur de sortie (`OFS`, *output
field separator*), une espace par défaut. Sans virgule, `awk` **concatène**
les deux champs bout à bout, sans rien entre eux : c'est presque toujours une
erreur involontaire plutôt qu'un choix. Vous pouvez changer ce séparateur de
sortie pour une tabulation, ce qui est utile si vous produisez un nouveau
fichier TSV :

```bash
awk -F'\t' -v OFS='\t' 'NR > 1 { print $1, $2, $4 }' data/tables/echantillons.tsv
```

```output
ech01	temoin	L001
ech02	temoin	L001
ech03	temoin	L002
ech04	traite	L002
ech05	traite	L003
ech06	traite	L003
```

`-v OFS='\t'` définit une variable awk avant l'exécution du programme, ici le
séparateur de sortie. Vous retrouverez `-v` chaque fois que vous voudrez faire
entrer une valeur du shell dans un programme awk.

## Filtrer avec un motif : expression régulière ou condition

Un motif peut être une expression régulière entre barres obliques, comme avec
`grep -E`. Cherchez les gènes dont le nom contient `rho`, en filtrant sur le
neuvième champ du GFF3 :

```bash
grep -v '^#' data/genome/annotation.gff3 | awk -F'\t' '$3 == "gene" && $9 ~ /rho/'
```

```output
chr1	formation	gene	1726	2307	.	-	.	ID=gene:GENE00003;Name=rho6B;biotype=pseudogene
chr1	formation	gene	2634	3257	.	-	.	ID=gene:GENE00004;Name=rho5B;biotype=lncRNA
```

Ce programme n'a pas d'action explicite : quand le motif est vrai, `awk`
imprime la ligne entière, exactement comme `grep`. L'opérateur `~` teste si un
champ correspond à une expression régulière ; `!~` teste le contraire. Le
motif combine ici deux conditions avec `&&` (« et ») : le champ 3 doit valoir
exactement `gene`, et le champ 9 doit contenir `rho`.

Un motif peut aussi être une simple condition, numérique ou textuelle, sans
expression régulière. Isolez les seuls gènes du fichier :

```bash
grep -v '^#' data/genome/annotation.gff3 | awk -F'\t' '$3 == "gene"' | head -3
```

```output
chr1	formation	gene	171	513	.	-	.	ID=gene:GENE00001;Name=arf4D;biotype=protein_coding
chr1	formation	gene	956	1509	.	+	.	ID=gene:GENE00002;Name=eef3B;biotype=protein_coding
chr1	formation	gene	1726	2307	.	-	.	ID=gene:GENE00003;Name=rho6B;biotype=pseudogene
```

Vous pouvez combiner les conditions avec `&&` (et), `||` (ou), `!` (non), et
tester une plage de lignes avec `NR==2,NR==5` :

```bash
grep -v '^#' data/genome/annotation.gff3 | awk -F'\t' 'NR==2,NR==5'
```

```output
chr1	formation	mRNA	171	513	.	-	.	ID=transcript:GENE00001.1;Parent=gene:GENE00001;Name=arf4D-201
chr1	formation	exon	171	513	.	-	.	ID=exon:GENE00001.1;Parent=transcript:GENE00001.1
chr1	formation	gene	956	1509	.	+	.	ID=gene:GENE00002;Name=eef3B;biotype=protein_coding
chr1	formation	mRNA	956	1509	.	+	.	ID=transcript:GENE00002.1;Parent=gene:GENE00002;Name=eef3B-201
```

Ce motif de plage se lit « à partir de la ligne où `NR==2` est vrai jusqu'à
la ligne où `NR==5` est vrai, ces deux lignes comprises ». Une fois la
seconde condition atteinte, `awk` recommence à chercher `NR==2` — utile
surtout avec des motifs textuels plutôt que des numéros de ligne fixes.

::::::::::::::::::::::::::::::::::::::  caution

## Comparaison de chaînes contre comparaison numérique

`awk` décide seul si une comparaison est numérique ou textuelle, et ce choix
dépend de l'apparence de la valeur. Le neuvième champ du GFF3 est une
chaîne (`ID=gene:GENE00001;...`), la comparaison `$3 == "gene"` est donc
naturellement textuelle. Mais attention aux champs qui *ressemblent* à des
nombres tout en étant du texte, comme un identifiant `007` : `$1 == 7`
compare alors numériquement et peut donner un résultat inattendu.

Le cas le plus fréquent est inverse : comparer une valeur qui doit être
numérique, comme la colonne QUAL d'un VCF, avec des guillemets qui la
transformeraient en chaîne. Comparez :

```bash
awk -F'\t' 'BEGIN { if ("9" > "80") print "chaine : vrai" ; else print "chaine : faux" }'
```

```output
chaine : vrai
```

En comparaison textuelle, `"9"` est bien inférieur à `"80"` alphabétiquement
(comme dans un dictionnaire, le premier caractère `9` se compare directement
à `8`… ici `"9" > "80"` teste en fait des chaînes numériques que awk
convertit automatiquement dès qu'elles ressemblent à des nombres). Le point à
retenir est plus simple à l'usage : quand vous comparez un champ à un nombre
sans guillemets, comme `$6 > 100`, `awk` fait la comparaison numérique
attendue. Le risque apparaît surtout si vous construisez le nombre de
comparaison vous-même comme une chaîne — gardez `$5 > 1000` sans guillemets
autour de `1000`, jamais `$5 > "1000"`.

:::::::::::::::::::::::::::::::::::::::::::::::::

## Filtrer le VCF sur la qualité

Le fichier `variants/cohorte.vcf` contient une colonne QUAL, la sixième, qui
mesure la confiance dans chaque variant. Combinez `grep -v` pour retirer
l'en-tête et `awk` pour filtrer numériquement :

```bash
grep -v '^#' data/variants/cohorte.vcf | awk -F'\t' '$6 > 400' | head -3
```

```output
chr1	218	.	A	AGG	482.1	PASS	DP=35;AF=0.557;TYPE=indel	GT:DP:GQ	0/0:19:17	0/1:7:53	0/1:6:29	1/1:16:85	0/0:51:37	1/1:51:34
chr1	1435	var0002	T	C	427.9	PASS	DP=20;AF=0.82;TYPE=snp	GT:DP:GQ	1/1:57:36	0/1:14:33	1/1:46:75	./.:45:20	1/1:6:83	0/0:53:29
chr1	3528	.	A	C	793.6	PASS	DP=57;AF=0.054;TYPE=snp	GT:DP:GQ	0/0:4:79	1/1:14:73	0/0:54:87	0/0:34:42	0/1:51:97	0/0:16:41
```

Combinez maintenant une condition numérique et une condition textuelle pour
ne garder que les variants de haute qualité qui ont effectivement passé le
filtre :

```bash
grep -v '^#' data/variants/cohorte.vcf | awk -F'\t' '$6 > 400 && $7 == "PASS"' | wc -l
```

```output
     109
```

Et pour repérer au contraire les variants écartés — utile pour vérifier que
le filtrage amont fonctionne comme attendu :

```bash
grep -v '^#' data/variants/cohorte.vcf | awk -F'\t' '$7 != "PASS"' | wc -l
```

## Calculer une longueur : GFF3 vers coordonnées de gène

Les coordonnées GFF3 sont en base 1, les deux bornes incluses (rappel de
l'épisode 5) : la longueur d'une caractéristique se calcule donc par
`fin - debut + 1`. Affichez le nom et la longueur de chaque gène :

```bash
grep -v '^#' data/genome/annotation.gff3 | awk -F'\t' '$3 == "gene" { print $9, $5 - $4 + 1 }' | head -3
```

```output
ID=gene:GENE00001;Name=arf4D;biotype=protein_coding 343
ID=gene:GENE00002;Name=eef3B;biotype=protein_coding 554
ID=gene:GENE00003;Name=rho6B;biotype=pseudogene 582
```

Le champ 9 entier est peu lisible. `printf` permet de choisir précisément ce
qui s'affiche et comment, plutôt que de laisser `print` tout concaténer avec
des espaces.

## Mettre en forme avec `printf`

`printf` fonctionne comme dans un script (épisode 3) mais s'utilise ici à
l'intérieur d'un programme awk, avec un gabarit et une liste de valeurs.
Les spécificateurs utiles sont `%s` pour une chaîne, `%d` pour un entier,
`%.2f` pour un nombre à virgule flottante avec deux décimales, et `\t`, `\n`
pour la tabulation et le retour à la ligne — contrairement à `print`,
`printf` n'ajoute jamais de retour à la ligne automatiquement, il faut
l'écrire soi-même.

<!-- verif: exec-seulement -->
```bash
grep -v '^#' data/genome/annotation.gff3 | awk -F'\t' '$3 == "gene" { printf "%s\t%d\n", $9, $5 - $4 + 1 }' | head -3
```

```output
ID=gene:GENE00001;Name=arf4D;biotype=protein_coding	343
ID=gene:GENE00002;Name=eef3B;biotype=protein_coding	554
ID=gene:GENE00003;Name=rho6B;biotype=pseudogene	582
```

La dernière ligne ci-dessus illustre une erreur fréquente à surveiller vous-même : vérifiez toujours que la longueur affichée correspond bien aux coordonnées de la ligne, plutôt que de faire confiance au premier coup d'œil.

Un exemple avec `%.2f` : la fréquence allélique du VCF (`AF`, dans la colonne
INFO) est une chaîne comme `AF=0.557`, mais imaginons que vous ayez déjà
extrait la valeur numérique 0.557 — vous l'afficheriez avec deux décimales
ainsi :

```bash
awk 'BEGIN { printf "frequence : %.2f\n", 0.557 }'
```

```output
frequence : 0.56
```

## Convertir une ligne GFF3 en ligne BED

Rappel de l'épisode 5 : le GFF3 est en base 1, borne de fin incluse ; le BED
est en base 0, borne de fin exclue. Convertir une ligne demande donc de
soustraire 1 à la position de début, et de garder la fin telle quelle. Pour
un gène, en reprenant le nom depuis le champ 9 avec `split` serait plus
propre, mais vous ne verrez `split` qu'à l'épisode suivant : contentez-vous
ici du champ 9 entier comme identifiant.

```bash
grep -v '^#' data/genome/annotation.gff3 \
  | awk -F'\t' -v OFS='\t' '$3 == "gene" { print $1, $4 - 1, $5, $9, ".", $7 }' \
  > resultats/genes.bed
head -3 resultats/genes.bed
```

```output
chr1	170	513	ID=gene:GENE00001;Name=arf4D;biotype=protein_coding	.	-
chr1	955	1509	ID=gene:GENE00002;Name=eef3B;biotype=protein_coding	.	+
chr1	1725	2307	ID=gene:GENE00003;Name=rho6B;biotype=pseudogene	.	-
```

Comparez la première ligne à la ligne GFF3 d'origine (`171 513`) et à la
ligne BED correspondante de `regions/cibles.bed` pour le même gène
(`955 1509` en GFF3 devient `955 1509` en BED, puisque `eef3B` commence
exactly à 956 en base 1) : le début a bien perdu un, la fin est inchangée.
C'est exactement la logique déjà vue à l'épisode 5, mais awk vous permet
cette fois de la calculer et de l'écrire en une seule commande, sur les 128
gènes du fichier, plutôt qu'à la main sur un seul exemple.

## Afficher les champs d'un SAM

Le fichier `alignements/ech01.sam` mélange des lignes d'en-tête, qui
commencent par `@`, et des lignes d'alignement à onze champs minimum (rappel
de l'épisode 5 : QNAME, FLAG, RNAME, POS, MAPQ, CIGAR, ...). Écartez l'en-tête
et affichez le nom de la lecture, le nom de la référence et la position :

```bash
awk -F'\t' '!/^@/ { print $1, $3, $4 }' data/alignements/ech01.sam | head -3
```

```output
ECH01:1:FLOWCELL1:1:1101:2659:2711 chr1 69
ECH01:1:FLOWCELL1:1:1101:2414:2606 chr1 91
ECH01:1:FLOWCELL1:1:1101:1140:2060 chr1 355
```

`!/^@/` est un motif d'expression régulière précédé de `!` : il est vrai pour
toute ligne qui **ne** commence **pas** par `@`. Vous auriez pu écrire
`grep -v '^@' data/alignements/ech01.sam | awk -F'\t' '{ print $1, $3, $4 }'`,
mais faire porter le filtre directement par `awk` évite un tube et une
commande.

Isolez maintenant les lectures non alignées, reconnaissables à `RNAME` qui
vaut `*` (colonne 3) :

```bash
awk -F'\t' '!/^@/ && $3 == "*"' data/alignements/ech01.sam | wc -l
```

## `cut` ou `awk` : lequel choisir

Vous connaissez `cut` depuis l'épisode 8. Comparez les deux commandes
suivantes sur la même colonne du GFF3 :

```bash
grep -v '^#' data/genome/annotation.gff3 | cut -f3 | sort | uniq -c
```

```output
 295 exon
 128 gene
 128 mRNA
```

```bash
grep -v '^#' data/genome/annotation.gff3 | awk -F'\t' '{ print $3 }' | sort | uniq -c
```

```output
 295 exon
 128 gene
 128 mRNA
```

Résultat identique, et `cut -f3` est plus court à taper. C'est le bon
réflexe tant que vous vous contentez d'extraire un champ sans le
transformer. `awk` devient nécessaire dès que vous devez :

- **calculer** à partir d'un champ, comme `$5 - $4 + 1` pour une longueur ;
- **filtrer sur une condition**, numérique (`$6 > 400`) ou combinée
  (`$3 == "gene" && $9 ~ /rho/`) — `cut` ne sait pas filtrer de lignes, `grep`
  ne sait pas comparer numériquement ;
- **réordonner ou dupliquer des champs**, comme produire `$1, $4 - 1, $5` pour
  une conversion GFF3 vers BED — `cut -f1,4,5` respecte toujours l'ordre
  d'origine des colonnes, il ne peut pas les permuter ;
- **gérer plusieurs séparateurs possibles dans le même fichier**, ce que
  `cut -d` ne fait jamais (un seul délimiteur par appel).

En résumé : `cut` pour extraire tel quel, `awk` dès qu'il faut réfléchir sur
le contenu du champ.

:::::::::::::::::::::::::::::::::::::::  challenge

## Défi 1 : les exons plutôt que les gènes (imitation)

En reprenant le même principe que pour les gènes, affichez les trois premiers
identifiants (champ 9) des lignes de type `exon` du fichier
`data/genome/annotation.gff3`.

:::::::::::::::::::::::::::::::::::::::  solution

## Solution

```bash
grep -v '^#' data/genome/annotation.gff3 | awk -F'\t' '$3 == "exon" { print $9 }' | head -3
```

```output
ID=exon:GENE00001.1;Parent=transcript:GENE00001.1
ID=exon:GENE00002.1;Parent=transcript:GENE00002.1
ID=exon:GENE00002.2;Parent=transcript:GENE00002.1
```

Même motif `$3 == "exon"` que pour `"gene"`, seule la valeur comparée change.
`awk` ne connaît que les trois valeurs `gene`, `mRNA`, `exon` pour ce champ,
comme vu au tout début de l'épisode.

:::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  challenge

## Défi 2 : gènes longs et brin (transfert)

Affichez l'identifiant (champ 9) et le brin (champ 7) de tous les gènes de
`data/genome/annotation.gff3` dont la longueur dépasse 1 000 paires de bases.
Combien en trouvez-vous ?

:::::::::::::::::::::::::::::::::::::::  solution

## Solution

<!-- verif: exec-seulement -->
```bash
grep -v '^#' data/genome/annotation.gff3 \
  | awk -F'\t' '$3 == "gene" && ($5 - $4 + 1) > 1000 { print $9, $7 }' \
  | tee resultats/genes_longs.txt | wc -l
```

Le motif combine trois conditions avec `&&` : le type doit être `gene`, et la
longueur calculée à la volée, entre parenthèses pour forcer l'ordre des
opérations, doit dépasser 1 000. `tee` affiche le résultat à l'écran tout en
l'enregistrant dans `resultats/genes_longs.txt`, comme vu à l'épisode 6.

:::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  challenge

## Défi 3 : variants indels de qualité moyenne (transfert)

Dans `data/variants/cohorte.vcf`, comptez les variants dont la colonne INFO
(champ 8) contient `TYPE=indel` et dont la colonne QUAL (champ 6) est
comprise entre 300 et 500 (bornes incluses).

:::::::::::::::::::::::::::::::::::::::  solution

## Solution

<!-- verif: exec-seulement -->
```bash
grep -v '^#' data/variants/cohorte.vcf \
  | awk -F'\t' '$8 ~ /TYPE=indel/ && $6 >= 300 && $6 <= 500' \
  | wc -l
```

`~` cherche la sous-chaîne `TYPE=indel` n'importe où dans le champ 8, qui
contient aussi `DP=` et `AF=` séparés par des points-virgules — inutile de
découper le champ pour cette seule condition. Les deux comparaisons
numériques sur `$6` sont combinées par `&&` : les trois conditions doivent
être vraies simultanément.

:::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  challenge

## Défi 4 : pourquoi ce programme n'affiche rien (interprétation)

Un collègue veut les gènes situés après la position 50 000 et écrit :

```bash
grep -v '^#' data/genome/annotation.gff3 | awk -F'\t' '$3 == "gene" && $4 > "50000"'
```

La commande ne renvoie aucune erreur, mais le résultat contient des gènes que
votre collègue ne voulait pas, comme un gène commençant à la position 956.
Pourquoi ?

:::::::::::::::::::::::::::::::::::::::  solution

## Solution

`"50000"` est écrit entre guillemets doubles : awk le traite comme une
**chaîne de caractères**, pas comme un nombre, et `$4 > "50000"` devient une
comparaison alphabétique. Dans l'ordre alphabétique, `"956"` est supérieur à
`"50000"` car le premier caractère `9` est supérieur à `5` — exactement le
piège décrit dans l'encadré de mise en garde plus haut. La correction retire
les guillemets :

```bash
grep -v '^#' data/genome/annotation.gff3 | awk -F'\t' '$3 == "gene" && $4 > 50000' | head -3
```

Sans guillemets, `50000` est un littéral numérique et la comparaison devient
numérique, comme attendu.

:::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  challenge

## Défi 5 : cibles longues en BED (facultatif)

Le fichier `data/regions/cibles.bed` a six champs : chromosome, début (base
0), fin, nom, score, brin. Affichez, avec `printf`, une ligne par région dont
le score (champ 5) dépasse 500, sous la forme `nom : longueur pb (score)`,
la longueur étant calculée en tenant compte de la convention BED plutôt que
GFF3.

:::::::::::::::::::::::::::::::::::::::  solution

## Solution

```bash
awk -F'\t' '$5 > 500 { printf "%s : %d pb (%s)\n", $4, $3 - $2, $5 }' data/regions/cibles.bed
```

En BED, la borne de fin est exclue : la longueur est donc `$3 - $2`, sans le
`+ 1` nécessaire en GFF3. C'est la même distinction que dans la section sur la
conversion GFF3 vers BED, mais appliquée dans l'autre sens.

:::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

Vous savez maintenant lire un fichier tabulaire champ par champ, filtrer sur
des conditions arbitraires et recalculer des valeurs à la volée. Ce que vous
n'avez pas encore vu : comment awk garde une trace **entre** les lignes
(compter par groupe, cumuler une somme) et comment il découpe une valeur
elle-même en sous-parties. C'est l'objet du prochain épisode, avec `BEGIN`,
`END` et les tableaux associatifs.

:::::::::::::::::::::::::::::::::::::::: keypoints

- `awk` lit chaque ligne, la découpe en champs `$1`..`$NF`, et exécute
  `motif { action }` pour chaque ligne dont le motif est vrai.
- `-F` fixe le séparateur de champs d'entrée ; `-v OFS='\t'` fixe le
  séparateur de sortie utilisé par les virgules de `print`.
- Un motif peut être une expression régulière `/.../`, une condition sur un
  champ (`$6 > 400`), une combinaison avec `&&`, `||`, `!`, ou une plage
  `NR==2,NR==5`.
- `printf "%s\t%d\n", ...` donne un contrôle total sur la mise en forme,
  contrairement à `print` qui ajoute automatiquement un retour à la ligne.
- Une valeur entre guillemets doubles comme `"50000"` se compare comme une
  chaîne, pas comme un nombre : retirez les guillemets pour comparer
  numériquement.
- `cut` extrait des champs tels quels ; `awk` devient nécessaire dès qu'il
  faut calculer, filtrer sur une condition ou réordonner des champs.

::::::::::::::::::::::::::::::::::::::::::::::::::
