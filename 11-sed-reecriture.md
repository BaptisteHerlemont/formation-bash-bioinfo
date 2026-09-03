---
title: "sed : réécrire du texte"
teaching: 25
exercises: 15
---

:::::::::::::::::::::::::::::::::::::::  questions

- Comment remplacer un motif par un autre dans un fichier, sans ouvrir d'éditeur ?
- Comment supprimer certaines lignes selon leur position ou leur contenu ?
- Comment modifier un fichier « sur place » sans risquer de le corrompre ?

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::: objectives

- Substituer un motif par un texte de remplacement avec `sed 's/motif/remplacement/'`.
- Choisir un délimiteur adapté au motif et utiliser des groupes de capture avec `-E`.
- Afficher ou supprimer des lignes précises à l'aide d'adresses.
- Modifier un fichier de façon portable en passant par un fichier temporaire.

::::::::::::::::::::::::::::::::::::::::::::::::::

## Réécrire du texte en une commande

Vous savez déjà chercher un motif (`grep`) et découper des colonnes (`cut`,
`awk`). Il vous manque un outil pour une opération très fréquente : remplacer
un morceau de texte par un autre, partout dans un fichier, sans l'ouvrir dans
un éditeur. C'est le rôle de `sed`, l'éditeur de flux (*stream editor*) : il
lit un fichier ligne par ligne et applique à chacune une commande d'édition.

Placez-vous à la racine du projet et créez les répertoires de travail de cet
épisode.

```bash
mkdir -p resultats tmp
```

## La substitution de base

La commande la plus utilisée de `sed` s'écrit `s/motif/remplacement/` : `s`
pour *substitute*, puis le motif à chercher et le texte de remplacement,
séparés par `/`. Regardez l'en-tête des séquences protéiques :

```bash
head -1 data/proteines/proteines.fa
```

```output
>sp|P27322|PROT01_TOY ribosomal protein OS=Escherichia coli OX=69275 GN=prot1 PE=1 SV=1
```

Remplaçons le mot `protein` par `proteine` sur cette seule ligne, pour voir le
principe :

```bash
head -1 data/proteines/proteines.fa | sed 's/protein/proteine/'
```

```output
>sp|P27322|PROT01_TOY ribosomal proteine OS=Escherichia coli OX=69275 GN=prot1 PE=1 SV=1
```

Par défaut, `sed` remplace uniquement la **première** occurrence trouvée sur
chaque ligne. Sur les 40 en-têtes du fichier, le mot `protein` apparaît parfois
deux fois (dans `hypothetical protein` et ailleurs) : sans drapeau, seule la
première serait changée.

::: callout

## `sed` ne modifie rien par défaut

`sed 's/motif/remplacement/' fichier` lit `fichier` et écrit le résultat sur
la sortie standard (*stdout*). Le fichier d'origine n'est pas touché. C'est ce
comportement qui permet de vérifier une substitution avant de la rendre
définitive — nous y revenons plus bas.

:::

## Remplacer toutes les occurrences : le drapeau `g`

Le drapeau `g` (*global*) demande à `sed` de remplacer toutes les occurrences
d'une ligne, pas seulement la première. Comparez sur une ligne du fichier
d'annotation, qui contient deux fois le point-virgule séparant les attributs :

```bash
head -6 data/genome/annotation.gff3 | tail -1
```

```output
chr1	formation	gene	171	513	.	-	.	ID=gene:GENE00001;Name=arf4D;biotype=protein_coding
```

```bash
head -6 data/genome/annotation.gff3 | tail -1 | sed 's/;/ | /'
```

```output
chr1	formation	gene	171	513	.	-	.	ID=gene:GENE00001 | Name=arf4D;biotype=protein_coding
```

Seul le premier `;` a été remplacé. Avec `g` :

```bash
head -6 data/genome/annotation.gff3 | tail -1 | sed 's/;/ | /g'
```

```output
chr1	formation	gene	171	513	.	-	.	ID=gene:GENE00001 | Name=arf4D | biotype=protein_coding
```

## Remplacer une occurrence précise : le drapeau numérique

Un chiffre après le motif de remplacement indique à `sed` de ne toucher qu'à
l'occurrence de ce rang. Pour ne remplacer que le **deuxième** `;` de la
ligne :

```bash
head -6 data/genome/annotation.gff3 | tail -1 | sed 's/;/ | /2'
```

```output
chr1	formation	gene	171	513	.	-	.	ID=gene:GENE00001;Name=arf4D | biotype=protein_coding
```

Ce drapeau se combine avec `g` : `s/;/ | /2g` remplacerait la deuxième
occurrence et toutes celles qui suivent sur la ligne.

## Choisir un autre délimiteur

Le caractère `/` sert de séparateur par défaut, mais rien n'impose de
l'utiliser. C'est gênant lorsque le motif ou le remplacement contient lui-même
des `/` — par exemple un chemin de fichier. `sed` accepte n'importe quel
caractère comme délimiteur, à condition d'être cohérent : `s|motif|remplacement|`
fonctionne aussi bien que `s/motif/remplacement/`.

Imaginons que vous vouliez faire apparaître le chemin complet du génome de
référence dans une note. Avec `/` comme délimiteur, il faudrait l'échapper :

```bash
echo "reference: ref_toy.fa" | sed 's/ref_toy\.fa/genome\/ref_toy.fa/'
```

```output
reference: genome/ref_toy.fa
```

Avec `|` comme délimiteur, aucune barre oblique n'a besoin d'être échappée :

```bash
echo "reference: ref_toy.fa" | sed 's|ref_toy\.fa|genome/ref_toy.fa|'
```

```output
reference: genome/ref_toy.fa
```

## Motifs plus riches : `-E` et les groupes de capture

Le drapeau `-E` active les expressions régulières étendues (*extended regular
expressions*), les mêmes que vous avez rencontrées avec `grep -E` : `+`, `?`,
`{}`, `|` et les parenthèses de groupement fonctionnent sans être échappés.

Les parenthèses ont un second usage : elles délimitent un **groupe de
capture**, dont le contenu peut être réutilisé dans le remplacement avec
`\1`, `\2`, etc. Regardez la colonne d'attributs du GFF3 : chaque ligne de type
`gene` contient un identifiant `ID=gene:GENE00001` suivi d'un nom
`Name=arf4D`. Pour extraire le nom du gène entouré de crochets :

```bash
grep $'\tgene\t' data/genome/annotation.gff3 | head -3 | sed -E 's/.*Name=([a-zA-Z0-9]+);.*/[\1]/'
```

```output
[arf4D]
[eef3B]
[rho6B]
```

Le groupe `([a-zA-Z0-9]+)` capture le nom du gène, et `\1` le réinjecte seul
dans le remplacement : tout le reste de la ligne, capturé par les `.*` non
groupés, disparaît.

## Réutiliser tout le motif trouvé : `&`

Dans le remplacement, `&` représente l'intégralité du texte qui a été trouvé
par le motif, sans qu'il soit nécessaire de le capturer entre parenthèses.
C'est pratique pour entourer un motif sans le retaper :

```bash
head -6 data/genome/annotation.gff3 | tail -1 | sed -E 's/GENE[0-9]+/<<&>>/'
```

```output
chr1	formation	gene	171	513	.	-	.	ID=gene:<<GENE00001>>;Name=arf4D;biotype=protein_coding
```

## Le fil : nettoyer les en-têtes des protéines

Reprenons les en-têtes de `data/proteines/proteines.fa`. Ils contiennent
beaucoup d'informations (accession UniProt, nom, organisme), mais pour la
suite du travail vous n'avez besoin que de l'identifiant `PROT01_TOY`,
`PROT02_TOY`, etc.

```bash
grep '^>' data/proteines/proteines.fa | head -3
```

```output
>sp|P27322|PROT01_TOY ribosomal protein OS=Escherichia coli OX=69275 GN=prot1 PE=1 SV=1
>sp|P11645|PROT02_TOY hypothetical protein OS=Homo sapiens OX=48404 GN=prot2 PE=1 SV=1
>sp|P98339|PROT03_TOY cytochrome c oxidase subunit OS=Mus musculus OX=3086 GN=prot3 PE=1 SV=1
```

L'identifiant est le second champ séparé par `|`, jusqu'au premier espace.
Une expression avec un groupe de capture permet de ne garder que lui :

```bash
grep '^>' data/proteines/proteines.fa | sed -E 's/^>sp\|[A-Z0-9]+\|([A-Za-z0-9_]+) .*/>\1/' | head -3
```

```output
>PROT01_TOY
>PROT02_TOY
>PROT03_TOY
```

Le motif décompose la ligne en trois parties : `>sp|`, l'accession
`[A-Z0-9]+`, un `|`, puis le groupe capturé `([A-Za-z0-9_]+)` qui s'arrête au
premier espace, et enfin tout le reste avec `.*`. Seul le groupe capturé
survit dans le remplacement.

::: caution

## Une substitution mal ancrée abîme les données

Le motif précédent commence par `^>sp\|` : il n'agit que sur les lignes
d'en-tête, reconnaissables au `>` en tout début de ligne. Sans cette ancre, un
motif comme `s/[A-Z0-9]+\|([A-Za-z0-9_]+) .*/\1/` pourrait aussi correspondre
à du texte trouvé ailleurs dans une ligne, y compris dans une séquence si elle
contenait par hasard des caractères similaires. Plus généralement, une
substitution globale (`g`) sur un motif trop permissif — par exemple
`s/A/N/g` sur un fichier FASTA pour « corriger une base », appliqué sans
réfléchir à la ligne d'en-tête aussi — remplace des `A` dans les identifiants
et les noms d'organismes, pas seulement dans la séquence. Vérifiez toujours le
résultat sur quelques lignes avant de l'appliquer au fichier entier, et
ancrez vos motifs (`^`, `$`, contexte de colonnes) autant que possible.

:::

::::::::::::::::::::::::::::::::::::::  challenge

## Harmoniser les noms d'échantillons

`data/tables/echantillons.tsv` nomme les échantillons `ech01`, `ech02`, etc.
Un collaborateur préfère la convention `ECH_01`, `ECH_02`, avec un tiret bas et
des majuscules. Écrivez une commande `sed` qui transforme `ech01` en `ECH_01`
dans la première colonne, et affichez le résultat sur les trois premières
lignes de données (donc les quatre premières lignes du fichier, en-tête
compris).

:::::::::::::::  solution

## Solution

```bash
head -4 data/tables/echantillons.tsv | sed -E 's/^ech([0-9]+)/ECH_\1/'
```

```output
sample_id	condition	replicat	lane	fichier_R1	fichier_R2
ECH_01	temoin	1	L001	ech01_R1.fastq.gz	ech01_R2.fastq.gz
ECH_02	temoin	2	L001	ech02_R1.fastq.gz	ech02_R2.fastq.gz
ECH_03	temoin	3	L002	ech03_R1.fastq.gz	ech03_R2.fastq.gz
```

L'ancre `^` garantit que seul un `ech` en tout début de ligne est transformé
(donc uniquement la première colonne) : les noms de fichiers plus loin sur la
ligne, comme `ech01_R1.fastq.gz`, ne sont pas touchés puisqu'ils ne sont pas en
début de ligne.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

## N'afficher que certaines lignes : `-n` et `p`

Par défaut, `sed` affiche chaque ligne après l'avoir traitée, qu'elle ait été
modifiée ou non. Le drapeau `-n` supprime cet affichage automatique ; combiné
à la commande `p` (*print*), il permet de choisir précisément quelles lignes
apparaissent.

Pour n'afficher que la troisième ligne du fichier BED des régions cibles :

```bash
sed -n '3p' data/regions/cibles.bed
```

```output
chr1	6782	7339	fbx4D	605	+
```

Sans `-n`, la commande `3p` afficherait la ligne 3 **deux fois** : une fois
par l'effet de `p`, une fois par l'affichage automatique. C'est une source
d'erreur fréquente à surveiller.

## Supprimer des lignes : `d`

La commande `d` (*delete*) fait l'inverse de `p` : elle retire les lignes
concernées du flux, et ces lignes ne sont donc jamais affichées. Comme `p`,
elle s'utilise seule ou avec une adresse.

Le fichier VCF de la cohorte commence par des lignes de commentaires,
reconnaissables au `#` initial :

```bash
head -3 data/variants/cohorte.vcf
```

```output
##fileformat=VCFv4.2
##fileDate=20240917
##source=formation-bash-bioinfo
```

Pour supprimer toutes les lignes commençant par `#`, on combine `d` avec une
adresse fondée sur un motif :

```bash
sed '/^#/d' data/variants/cohorte.vcf | head -3
```

```output
chr1	218	.	A	AGG	482.1	PASS	DP=35;AF=0.557;TYPE=indel	GT:DP:GQ	0/0:19:17	0/1:7:53	0/1:6:29	1/1:16:85	0/0:51:37	1/1:51:34
chr1	1435	var0002	T	C	427.9	PASS	DP=20;AF=0.82;TYPE=snp	GT:DP:GQ	1/1:57:36	0/1:14:33	1/1:46:75	./.:45:20	1/1:6:83	0/0:53:29
chr1	1696	.	T	A	259.1	PASS	DP=77;AF=0.547;TYPE=snp	GT:DP:GQ	1/1:35:23	1/1:4:89	0/1:11:98	1/1:16:59	0/0:58:14	./.:35:96
```

::: callout

## Vous connaissiez déjà cette opération avec `grep`

`grep -v '^#'` produit exactement le même résultat que `sed '/^#/d'` : les deux
retirent les lignes qui correspondent au motif. Ce n'est pas une coïncidence
— voir le tableau de synthèse en fin d'épisode.

:::

## Les adresses de `sed`

Une adresse précède une commande et sélectionne les lignes sur lesquelles
elle s'applique. Vous en avez déjà utilisé deux formes : un numéro de ligne
(`3p`) et un motif entre `/` (`/^#/d`). Il en existe d'autres :

| Adresse | Sélectionne |
|---|---|
| `3p` | la ligne 3 |
| `1,10d` | les lignes 1 à 10 |
| `/motif/d` | toute ligne contenant `motif` |
| `$d` | la dernière ligne |
| `2,$p` | de la ligne 2 jusqu'à la dernière |

Le symbole `$` désigne toujours la dernière ligne, quel que soit le nombre
total de lignes du fichier. Sur le fichier d'index du génome, qui ne compte
que deux lignes :

```bash
cat data/genome/ref_toy.fa.fai
```

```output
chr1	100000	56	60	61
chrM	5000	101785	60	61
```

```bash
sed '$d' data/genome/ref_toy.fa.fai
```

```output
chr1	100000	56	60	61
```

Et pour tout afficher sauf la première ligne :

```bash
sed -n '2,$p' data/genome/ref_toy.fa.fai
```

```output
chrM	5000	101785	60	61
```

Sur un fichier plus long, une plage numérique se lit de la même façon.
Supprimons les dix premières lignes d'en-tête et de commentaires de
`annotation.gff3`, puis affichons ce qu'il reste :

```bash
sed '1,5d' data/genome/annotation.gff3 | head -3
```

```output
chr1	formation	gene	171	513	.	-	.	ID=gene:GENE00001;Name=arf4D;biotype=protein_coding
chr1	formation	mRNA	171	513	.	-	.	ID=transcript:GENE00001.1;Parent=gene:GENE00001;Name=arf4D-201
chr1	formation	exon	171	513	.	-	.	ID=exon:GENE00001.1;Parent=transcript:GENE00001.1
```

## Le fil : renommer `chr1` en `1`

Certains outils bioinformatiques attendent des noms de chromosomes sans le
préfixe `chr` (convention Ensembl) alors que d'autres l'exigent (convention
UCSC). Passer d'une convention à l'autre est une opération classique et
justement risquée : elle doit remplacer `chr1` par `1` **au tout début de la
ligne**, jamais ailleurs — un attribut comme `Parent=gene:GENE00001` ne doit
pas être touché.

Travaillez sur une copie, jamais sur l'original :

```bash
cp data/genome/annotation.gff3 tmp/annotation_copie.gff3
sed -E 's/^chr1/1/' tmp/annotation_copie.gff3 > resultats/annotation_ucsc_vers_ensembl.gff3
grep -v '^#' resultats/annotation_ucsc_vers_ensembl.gff3 | head -3
```

```output
1	formation	gene	171	513	.	-	.	ID=gene:GENE00001;Name=arf4D;biotype=protein_coding
1	formation	mRNA	171	513	.	-	.	ID=transcript:GENE00001.1;Parent=gene:GENE00001;Name=arf4D-201
1	formation	exon	171	513	.	-	.	ID=exon:GENE00001.1;Parent=transcript:GENE00001.1
```

L'ancre `^` est ici indispensable : sans elle, `s/chr1/1/` laisserait
`chr1` inchangé (aucune ligne de données ne contient `chr1` ailleurs qu'en
première colonne dans ce fichier), mais dans un fichier où un attribut
contiendrait la chaîne `chr1` en plein milieu d'une valeur, la substitution
non ancrée l'aurait modifiée aussi.

## Plusieurs commandes en une seule invocation

Deux syntaxes permettent d'enchaîner plusieurs commandes `sed` sans relancer
`sed` plusieurs fois : répéter `-e` devant chaque commande, ou les séparer par
un point-virgule `;` à l'intérieur d'une même chaîne entre apostrophes.

Pour renommer `chr1` en `1` et `chrM` en `MT` (autre convention fréquente pour
le génome mitochondrial) en une seule commande :

<!-- verif: ordre-libre -->
```bash
sed -e 's/^chr1/1/' -e 's/^chrM/MT/' tmp/annotation_copie.gff3 | grep -v '^#' | sort -u -k1,1
```

```output
1	formation	gene	171	513	.	-	.	ID=gene:GENE00001;Name=arf4D;biotype=protein_coding
MT	formation	gene	152	563	.	+	.	ID=gene:GENE00121;Name=cox6B;biotype=protein_coding
```

La même commande s'écrit aussi avec des points-virgules :

<!-- verif: ordre-libre -->
```bash
sed 's/^chr1/1/; s/^chrM/MT/' tmp/annotation_copie.gff3 | grep -v '^#' | sort -u -k1,1
```

```output
1	formation	gene	171	513	.	-	.	ID=gene:GENE00001;Name=arf4D;biotype=protein_coding
MT	formation	gene	152	563	.	+	.	ID=gene:GENE00121;Name=cox6B;biotype=protein_coding
```

Les deux syntaxes sont équivalentes ; `-e` répété est parfois plus lisible
quand les commandes sont longues, `;` est plus compact pour des commandes
courtes.

## Modifier un fichier sur place : le piège `-i`

Jusqu'ici, chaque commande `sed` a écrit son résultat sur la sortie standard,
que nous avons redirigée vers un fichier avec `>` ou affichée directement.
`sed` propose aussi une option `-i` pour modifier le fichier **sur place**,
sans passer par une redirection. C'est ici que se cache le piège le plus
sérieux de cet épisode.

::: caution

## `sed -i` n'a pas la même syntaxe partout

Sous Linux (GNU sed), `sed -i 's/a/b/' fichier` modifie `fichier`
immédiatement. Sous macOS (BSD sed), la même commande produit une erreur,
parce que BSD `-i` exige un argument explicite — même vide — pour le suffixe
de sauvegarde : il faut écrire `sed -i '' 's/a/b/' fichier`. Un script écrit
et testé sur macOS échouera donc différemment sur un serveur Linux, et
réciproquement une commande copiée depuis une documentation Linux échouera
sur macOS.

Cette leçon n'utilise donc **jamais `-i`**. La règle est systématique :
écrire le résultat dans un fichier temporaire, vérifier ce fichier, puis le
déplacer à la place de l'original avec `mv` si le résultat convient.

```bash
sed -E 's/^chr1/1/' data/genome/annotation.gff3 > tmp/annotation_renommee.gff3
head -6 tmp/annotation_renommee.gff3 | tail -1
mv tmp/annotation_renommee.gff3 resultats/annotation_renommee.gff3
```

```output
1	formation	gene	171	513	.	-	.	ID=gene:GENE00001;Name=arf4D;biotype=protein_coding
```

Cette séquence — rediriger, vérifier, déplacer — fonctionne à l'identique sur
toutes les machines, et elle a un avantage supplémentaire : si la commande
`sed` échoue en cours de route, ou si le résultat est faux, le fichier
d'origine n'a jamais été touché. `mv` ne s'exécute qu'après vérification.

:::

## Le fil : supprimer les commentaires d'un VCF, proprement

Reprenons la suppression des lignes de commentaires du VCF vue plus haut, mais
en écrivant cette fois un vrai fichier de résultat, avec la méthode sûre :

```bash
sed '/^##/d' data/variants/cohorte.vcf > tmp/cohorte_sans_meta.vcf
wc -l tmp/cohorte_sans_meta.vcf
mv tmp/cohorte_sans_meta.vcf resultats/cohorte_sans_meta.vcf
```

```output
     201 tmp/cohorte_sans_meta.vcf
```

Le motif `/^##/` ne retire que les lignes de métadonnées (`##...`), pas la
ligne d'en-tête des colonnes qui commence par un seul `#CHROM`. Vérifiez-le :

```bash
head -1 resultats/cohorte_sans_meta.vcf
```

```output
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	ech01	ech02	ech03	ech04	ech05	ech06
```

::::::::::::::::::::::::::::::::::::::::::::::::::  challenge

## Isoler les seules lignes de données du VCF

Écrivez une commande qui supprime, en plus des lignes `##`, la ligne d'en-tête
`#CHROM`, pour ne garder que les 200 lignes de variants. Enregistrez le
résultat dans `resultats/cohorte_donnees_seules.vcf` en passant par un fichier
temporaire, puis vérifiez son nombre de lignes.

:::::::::::::::  solution

## Solution

```bash
sed '/^#/d' data/variants/cohorte.vcf > tmp/cohorte_donnees.vcf
wc -l tmp/cohorte_donnees.vcf
mv tmp/cohorte_donnees.vcf resultats/cohorte_donnees_seules.vcf
```

```output
     200 tmp/cohorte_donnees.vcf
```

Le motif `/^#/` (un seul `#`) englobe à la fois les lignes `##...` et la ligne
`#CHROM...`, puisque toutes deux commencent par au moins un `#`. Il n'était
pas nécessaire d'enchaîner deux commandes `d` : une seule adresse suffit ici,
contrairement au fil de l'épisode où l'on voulait garder `#CHROM`.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::  challenge

## Compter les gènes pseudogènes sans les afficher

Le champ `biotype` des lignes de type `gene` de `annotation.gff3` vaut soit
`protein_coding` soit `pseudogene`. En combinant `sed -n` avec `p` et une
adresse fondée sur un motif, affichez uniquement les lignes de gènes dont le
biotype est `pseudogene`, puis comptez-les avec `wc -l`.

:::::::::::::::  solution

## Solution

<!-- verif: exec-seulement -->
```bash
sed -n '/pseudogene/p' data/genome/annotation.gff3 | wc -l
```

```output
       7
```

L'adresse `/pseudogene/` sélectionne toute ligne contenant ce mot ; comme le
mot n'apparaît que dans la colonne d'attributs des lignes `gene`, il n'était
pas nécessaire de filtrer aussi sur la colonne 3. `-n` empêche l'affichage
automatique des autres lignes, et `p` n'affiche que celles sélectionnées.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::  challenge

## Ce script contient une erreur : laquelle

Un collègue veut remplacer, dans `data/tables/echantillons.tsv`, le mot
`temoin` par `controle`, uniquement pour la deuxième colonne. Il propose :

```bash
sed 's/t/controle/g' data/tables/echantillons.tsv
```

Que va réellement produire cette commande, et pourquoi n'est-ce pas ce qu'il
voulait ?

:::::::::::::::  solution

## Solution

<!-- verif: exec-seulement -->
```bash
sed 's/t/controle/g' data/tables/echantillons.tsv | head -2
```

```output
sample_id	condicontroleion	replicacontrole	lane	fichier_R1	fichier_R2
ech01	controleemoin	1	L001	ech01_R1.fascontroleq.gz	ech01_R2.fascontroleq.gz
```

Le motif `t` correspond à **toutes** les lettres `t` du fichier, pas
seulement au mot `temoin` : avec `g`, chaque `t` de chaque ligne — dans
`sample_id`, dans `replicat`, dans les noms de fichiers — est remplacé par
`controle`, ce qui produit un texte illisible. C'est l'illustration directe
de l'encadré de mise en garde : le motif n'est pas assez spécifique. La bonne
commande cible le mot entier, par exemple `sed 's/\btemoin\b/controle/'` ou,
plus sûr encore ici, `sed -E 's/^([^\t]*\t)temoin\t/\1controle\t/'` qui
n'agit que sur la deuxième colonne.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

## Quand `sed`, quand `awk`, quand `grep`

Les trois outils lisent un fichier ligne par ligne et partagent des points
communs (motifs, expressions régulières), mais chacun a un terrain de
prédilection.

| Besoin | Outil | Exemple |
|---|---|---|
| Savoir si un motif existe, l'afficher, le compter | `grep` | `grep -c pseudogene data/genome/annotation.gff3` |
| Remplacer du texte, supprimer des lignes, renommer une valeur | `sed` | `sed 's/^chr1/1/' fichier` |
| Calculer, agréger par colonne, réorganiser des champs | `awk` | `awk -F'\t' '{s+=$3} END{print s}' fichier` |

Une règle simple pour trancher : si la tâche se décrit comme « remplacer X par
Y » ou « garder/retirer les lignes qui... », pensez `sed` ou `grep`. Si elle
se décrit comme « calculer », « pour chaque groupe », ou nécessite de
raisonner sur plusieurs colonnes en même temps, pensez `awk`. Beaucoup de
tâches se résolvent d'ailleurs avec les deux : `grep` ou `sed` pour isoler les
bonnes lignes, `awk` pour les colonnes qui suivent — c'est le sujet du
prochain épisode.

::::::::::::::::::::::::::::::::::::::::::::::::::  challenge

## Retrouver la même chose avec chaque outil (facultatif)

Le fichier `data/regions/cibles.bed` contient 25 régions. Écrivez trois
commandes différentes — une avec `grep`, une avec `sed`, une avec `awk` — qui
affichent toutes les trois uniquement les lignes dont le brin (colonne 6) est
`-`.

:::::::::::::::  solution

## Solution

<!-- verif: exec-seulement -->
```bash
grep -c $'\t-$' data/regions/cibles.bed
sed -n '/\t-$/p' data/regions/cibles.bed | wc -l
awk -F'\t' '$6 == "-"' data/regions/cibles.bed | wc -l
```

```output
14
14
14
```

`grep` et `sed` cherchent ici le même motif textuel (une tabulation suivie
d'un `-` en fin de ligne) : ils ne savent pas que ce `-` est « la colonne 6 »,
seulement qu'il termine la ligne après une tabulation. `awk`, lui, raisonne
directement en colonnes avec `$6 == "-"`, ce qui est plus robuste si le
fichier changeait de nombre de colonnes. C'est exactement la nuance du
tableau ci-dessus.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::::: keypoints

- `sed 's/motif/remplacement/'` remplace la première occurrence de `motif` par ligne ; ajoutez `g` pour toutes les occurrences, ou un chiffre pour une occurrence précise.
- Le délimiteur `/` peut être remplacé par un autre caractère, par exemple `s|a|b|`, quand le motif contient des `/`.
- Avec `-E`, les parenthèses créent des groupes de capture réutilisables avec `\1`, `\2` ; `&` réutilise tout le texte trouvé.
- `sed -n` combiné à `p` n'affiche que les lignes sélectionnées ; `d` les supprime ; les adresses (`3p`, `1,10d`, `/motif/d`, `$d`, `2,$p`) précisent lesquelles.
- Plusieurs commandes s'enchaînent avec `-e` répété ou avec `;` dans une même chaîne.
- `sed -i` n'a pas la même syntaxe sous GNU et sous BSD : cette leçon écrit toujours vers un fichier temporaire puis utilise `mv`.
- Une substitution mal ancrée modifie du texte qui n'aurait pas dû l'être : ancrez vos motifs (`^`, `$`) et vérifiez le résultat avant de l'appliquer au fichier entier.
- `grep` cherche et filtre des lignes, `sed` réécrit et supprime des lignes, `awk` calcule et raisonne en colonnes.

::::::::::::::::::::::::::::::::::::::::::::::::::
