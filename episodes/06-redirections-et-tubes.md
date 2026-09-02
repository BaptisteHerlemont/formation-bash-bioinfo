---
title: "Redirections et tubes"
teaching: 30
exercises: 20
---

:::::::::::::::::::::::::::::::::::::::  questions

- Comment envoyer la sortie d'une commande dans un fichier plutôt que sur l'écran ?
- Comment séparer les messages d'erreur du résultat utile ?
- Comment enchaîner plusieurs commandes pour que chacune traite le résultat de la précédente ?

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::: objectives

- Rediriger la sortie standard d'une commande vers un fichier, en écrasant ou en ajoutant.
- Rediriger la sortie d'erreur séparément de la sortie standard, et l'ignorer avec `/dev/null`.
- Construire un tube de plusieurs commandes en vérifiant chaque étage avec `head`.
- Dupliquer un flux vers l'écran et vers un fichier avec `tee`.

::::::::::::::::::::::::::::::::::::::::::::::::::

## Trois flux, et pas un seul

Depuis l'épisode 4, vous utilisez des commandes comme `cat` ou `head` sans vous
poser la question de ce qui se passe entre la commande et l'écran. En réalité,
chaque commande dispose de trois flux de données, ouverts automatiquement dès
qu'elle démarre :

```
                 ┌──────────────────┐
   entrée        │                  │        sortie
   standard  --> │     commande     │ -->    standard
   (stdin)       │                  │        (stdout)
                 └──────────────────┘
                          |
                          v
                     sortie d'erreur
                       (stderr)
```

- l'**entrée standard** (*standard input*, `stdin`) : ce que la commande lit,
  par défaut le clavier ;
- la **sortie standard** (*standard output*, `stdout`) : ce que la commande
  affiche comme résultat, par défaut l'écran ;
- la **sortie d'erreur** (*standard error*, `stderr`) : ce que la commande
  affiche comme message de diagnostic, par défaut l'écran aussi.

`stdout` et `stderr` s'affichent tous les deux à l'écran, ce qui les rend
indiscernables à l'œil. C'est justement ce que les redirections permettent de
séparer.

Préparez votre espace de travail pour cet épisode :

```bash
mkdir -p resultats tmp
```

## Rediriger la sortie standard : `>` et `>>`

Le chevron `>` envoie la sortie standard d'une commande dans un fichier, à la
place de l'écran :

```bash
grep 'gene' data/genome/annotation.gff3 > resultats/lignes_gene.txt
```

Aucune sortie à l'écran : `grep` a bien produit ses lignes, mais elles sont
allées dans le fichier plutôt que dans le terminal. Vérifiez avec `head` :

```bash
head -n 3 resultats/lignes_gene.txt
```

```output
chr1	formation	gene	171	513	.	-	.	ID=gene:GENE00001;Name=arf4D;biotype=protein_coding
chr1	formation	mRNA	171	513	.	-	.	ID=transcript:GENE00001.1;Parent=gene:GENE00001;Name=arf4D-201
chr1	formation	gene	956	1509	.	+	.	ID=gene:GENE00002;Name=eef3B;biotype=protein_coding
```

Le point important, et la source d'erreur la plus fréquente : `>` **écrase**
le fichier de destination sans avertissement s'il existe déjà.

::::::::::::::::::::::::::::::::::::: caution

## `>` écrase en silence

```bash
echo "premiere ligne" > resultats/notes.txt
echo "deuxieme ligne" > resultats/notes.txt
cat resultats/notes.txt
```

```output
deuxieme ligne
```

La « première ligne » a disparu, sans message, sans confirmation. `>` ne
demande jamais votre avis avant d'écraser. Si vous vouliez conserver les deux
lignes, il fallait `>>`. Une fois le contenu écrasé, il est perdu : la seule
prévention est de vérifier, en cas de doute, si le fichier de destination
existe déjà (`ls` ou un `test -f`, vu à l'épisode 15).

:::::::::::::::::::::::::::::::::::::::::::::

Le double chevron `>>` **ajoute** à la fin du fichier au lieu de l'écraser :

```bash
echo "premiere ligne" > resultats/notes.txt
echo "deuxieme ligne" >> resultats/notes.txt
cat resultats/notes.txt
```

```output
premiere ligne
deuxieme ligne
```

Le fichier a été créé par le premier `>` (il n'existait pas encore), puis
complété par `>>`. Si vous relancez le deuxième `echo` plusieurs fois, la
ligne « deuxieme ligne » s'ajoutera à chaque fois : `>>` n'empêche pas les
doublons, il empêche seulement l'écrasement.

## Rediriger l'entrée standard : `<`

Le chevron simple `<` fait l'inverse : il fournit le contenu d'un fichier
comme entrée standard d'une commande, au lieu du clavier.

```bash
wc -l < data/regions/cibles.bed
```

```output
25
```

Comparez avec la même commande sans redirection :

```bash
wc -l data/regions/cibles.bed
```

```output
25 data/regions/cibles.bed
```

La différence est visible : avec `<`, `wc` ne connaît pas le nom du fichier
(il a seulement reçu un flux de caractères sur son entrée standard), et
n'affiche donc que le nombre. Sans `<`, `wc` reçoit le nom en argument et
l'affiche à côté du résultat.

::::::::::::::::::::::::::::::::::::: callout

## `wc -l < fichier` plutôt que `cat fichier | wc -l`

Les deux commandes suivantes affichent le même nombre :

```bash
wc -l < data/regions/cibles.bed
cat data/regions/cibles.bed | wc -l
```

La seconde fonctionne, mais elle lance deux processus (`cat` et `wc`) là où
un seul (`wc`, alimenté par `<`) suffit. `cat` n'a ici aucun rôle : il ne
transforme rien, il se contente de faire passer le fichier à la commande
suivante. Ce schéma est si courant qu'il porte un nom moqueur dans la
communauté Unix, *useless use of cat* (« usage inutile de `cat` »). `cat`
reste indispensable pour concaténer plusieurs fichiers ou pour afficher un
contenu à l'écran ; il est superflu dès qu'une seule commande sait lire un
fichier directement, via un argument ou via `<`.

:::::::::::::::::::::::::::::::::::::::::::::

## Rediriger la sortie d'erreur : `2>`

Essayez de lire un fichier qui n'existe pas :

```bash
cat data/genome/absent.fa
```

```error
```

Ce message n'est pas allé sur la sortie standard : il est sorti par le canal
`stderr`. Vous pouvez le rediriger séparément avec `2>` (le `2` est le numéro
du flux d'erreur ; `1` désigne la sortie standard, et c'est le numéro par
défaut de `>`) :

<!-- verif: ignore -->
```bash
cat data/genome/absent.fa 2> resultats/erreurs.txt
```

Rien ne s'affiche à l'écran cette fois : le message d'erreur est parti dans
`resultats/erreurs.txt`. Vérifiez :

```bash
cat resultats/erreurs.txt
```

```error
```

Le bloc précédent est marqué comme non vérifié automatiquement, car le texte
exact d'un message d'erreur système (« No such file or directory ») dépend
du système d'exploitation et de sa langue. L'idée à retenir ne dépend pas de
ce détail : `2>` isole les diagnostics du résultat utile.

C'est particulièrement utile quand une commande produit à la fois un résultat
et des avertissements, et que vous ne voulez garder que le résultat :

```bash
gunzip -c data/reads/ech04_R2.fastq.gz > resultats/ech04_R2.fastq 2> resultats/erreurs_ech04.txt
wc -l resultats/ech04_R2.fastq
```

```output
    1998 resultats/ech04_R2.fastq
```

`ech04_R2.fastq.gz` est le fichier tronqué signalé au README du jeu de
données : 1 998 lignes au lieu de 2 000, donc un dernier bloc FASTQ
incomplet. Vous retrouverez cette anomalie plus loin dans la formation,
lorsqu'il s'agira d'écrire du code qui la détecte automatiquement.

## Jeter ce qu'on ne veut pas : `/dev/null`

`/dev/null` est un fichier spécial qui absorbe tout ce qu'on y écrit, sans
rien stocker. C'est la destination habituelle pour se débarrasser d'un flux
qu'on ne veut ni voir ni garder :

<!-- verif: exec-seulement -->
```bash
cat data/genome/absent.fa 2> /dev/null
```

Rien ne s'affiche : ni résultat (il n'y en avait pas), ni message d'erreur
(jeté dans `/dev/null`). Le code de retour, lui, garde la trace de l'échec
(vous manipulerez `$?` à l'épisode 15).

## Fusionner les deux sorties : `2>&1`

Parfois on veut au contraire tout garder ensemble, résultat et erreurs, dans
le même fichier — typiquement pour un journal de commande. La syntaxe `2>&1`
signifie « rediriger le flux 2 (stderr) vers là où pointe actuellement le
flux 1 (stdout) » :

```bash
{ cat data/genome/ref_toy.fa.fai data/genome/absent.fa ; } > resultats/journal.txt 2>&1
cat resultats/journal.txt
```

```error
chr1	100000	56	60	61
chrM	5000	101785	60	61
cat: data/genome/absent.fa: No such file or directory
```

L'ordre des redirections compte : `> fichier 2>&1` fonctionne (la sortie
standard part vers `fichier`, puis l'erreur suit le même chemin), alors que
`2>&1 > fichier` ne ferait pas ce qu'on attend, car au moment où `2>&1` est
lu, `1` pointe encore vers l'écran.

## Tout garder et tout voir à la fois : `tee`

Les redirections envoient un flux à un seul endroit. `tee` fait passer un
flux tel quel vers la sortie standard, tout en en écrivant une copie dans un
fichier — comme un raccord en T sur une canalisation.

```bash
grep 'ERROR' data/journaux/pipeline.log | tee resultats/erreurs_pipeline.txt
```

```output
2024-09-17 08:50:52 [ERROR] ech04 controle_qualite - fichier ech04_R2.fastq.gz tronque : bloc FASTQ incomplet
```

La ligne s'affiche à l'écran, et se retrouve aussi dans
`resultats/erreurs_pipeline.txt` :

```bash
cat resultats/erreurs_pipeline.txt
```

```output
2024-09-17 08:50:52 [ERROR] ech04 controle_qualite - fichier ech04_R2.fastq.gz tronque : bloc FASTQ incomplet
```

`tee` sert surtout à s'insérer au milieu d'un tube pour inspecter un résultat
intermédiaire sans casser la suite de la chaîne — c'est justement le sujet de
la section suivante.

## Le tube : composer de petits outils

Jusqu'ici, chaque commande a travaillé seule. L'idée centrale de cette
journée est différente : au lieu d'écrire un gros programme qui ferait tout
d'un coup, on relie plusieurs commandes simples, chacune spécialisée dans une
seule tâche, en branchant la sortie standard de l'une sur l'entrée standard
de la suivante. C'est le tube (*pipe*), noté `|`.

```
   fichier -->[ commande1 ]-->[ commande2 ]-->[ commande3 ]--> écran ou fichier
               stdout|stdin    stdout|stdin
```

Chaque `|` relie le `stdout` de la commande à sa gauche au `stdin` de la
commande à sa droite. `grep`, `cut`, `sort`, `wc`... toutes les commandes que
vous connaissez depuis les épisodes 4 et 5 savent lire sur leur entrée
standard et écrire sur leur sortie standard : c'est précisément ce qui permet
de les enchaîner sans jamais créer de fichier intermédiaire.

Reprenons un besoin concret : combien de gènes l'annotation contient-elle ?
Vous savez déjà répondre en deux commandes séparées :

```bash
grep -c $'\tgene\t' data/genome/annotation.gff3
```

```output
128
```

Avec un tube, la même question s'écrit en une ligne, sans fichier
intermédiaire :

```bash
grep $'\tgene\t' data/genome/annotation.gff3 | wc -l
```

```output
128
```

`grep` cherche les lignes contenant `gene` entouré de tabulations et les
écrit sur sa sortie standard ; au lieu de finir à l'écran, cette sortie
devient directement l'entrée standard de `wc -l`, qui compte les lignes
reçues. Aucune des deux commandes n'a été modifiée pour l'occasion : `grep`
ignore qu'il parle à `wc`, et `wc` ignore qu'il reçoit les lignes de `grep`.

::::::::::::::::::::::::::::::::::::: callout

## `commande1 | commande2 > fichier` contre `commande1 > fichier | commande2`

Ces deux écritures se ressemblent mais ne font pas du tout la même chose.

`commande1 | commande2 > fichier` : la sortie de `commande1` alimente
`commande2`, et c'est le résultat final de `commande2` qui part dans
`fichier`. C'est presque toujours ce que l'on veut.

`commande1 > fichier | commande2` : la sortie de `commande1` part entièrement
dans `fichier`, et `commande2` reçoit une entrée standard vide (celle du
terminal, non redirigée) — elle ne reçoit rien de `commande1`. Le shell
interprète le `>` comme une redirection de `commande1` isolée, et le `|`
comme un lien vers une deuxième commande qui n'a plus rien à lire.

En cas de doute sur l'endroit où va réellement un résultat, la méthode sûre
est de construire le tube par étapes et de vérifier chaque étage, comme dans
la section suivante.

:::::::::::::::::::::::::::::::::::::::::::::

## Construire un tube étage par étage

Un tube de trois ou quatre commandes qui ne donne pas le résultat attendu est
difficile à corriger d'un coup : laquelle des commandes a fait quelque chose
d'inattendu ? La méthode qui évite ce problème est simple : **on ajoute un
étage à la fois, et on vérifie avec `head` avant d'ajouter le suivant.**

Reprenons l'exemple des gènes de l'annotation, et allons plus loin : quels
sont les noms des gènes situés sur le brin `-` (colonne 7 du GFF3) ?

**Étage 1**, isoler les lignes de type `gene` — on regarde les premières
lignes obtenues avant de continuer :

```bash
awk -F'\t' '$3 == "gene"' data/genome/annotation.gff3 | head -n 3
```

```output
chr1	formation	gene	171	513	.	-	.	ID=gene:GENE00001;Name=arf4D;biotype=protein_coding
chr1	formation	gene	956	1509	.	+	.	ID=gene:GENE00002;Name=eef3B;biotype=protein_coding
chr1	formation	gene	1726	2307	.	-	.	ID=gene:GENE00003;Name=rho6B;biotype=pseudogene
```

C'est bien ce qu'on attendait : uniquement des lignes `gene`. On ajoute
l'étage suivant.

**Étage 2**, garder seulement le brin `-` (colonne 7), en repartant de
l'étage validé :

```bash
awk -F'\t' '$3 == "gene"' data/genome/annotation.gff3 | awk -F'\t' '$7 == "-"' | head -n 3
```

```output
chr1	formation	gene	171	513	.	-	.	ID=gene:GENE00001;Name=arf4D;biotype=protein_coding
chr1	formation	gene	1726	2307	.	-	.	ID=gene:GENE00003;Name=rho6B;biotype=pseudogene
chr1	formation	gene	2634	3257	.	-	.	ID=gene:GENE00004;Name=rho5B;biotype=lncRNA
```

Toujours des lignes `gene`, et cette fois uniquement du brin `-`. On continue.

**Étage 3**, ne garder que le champ 9 (les attributs, qui contiennent le
nom) :

```bash
awk -F'\t' '$3 == "gene"' data/genome/annotation.gff3 | awk -F'\t' '$7 == "-"' | cut -f9 | head -n 3
```

```output
ID=gene:GENE00001;Name=arf4D;biotype=protein_coding
ID=gene:GENE00003;Name=rho6B;biotype=pseudogene
ID=gene:GENE00004;Name=rho5B;biotype=lncRNA
```

Chaque étage a été vérifié avant qu'on en ajoute un nouveau. Si le résultat
final n'était pas celui espéré, il suffirait de retirer le dernier `| head`
et de regarder à quel étage le contenu cesse de correspondre à ce qu'on
attend — plutôt que de relire les quatre commandes à la fois en espérant
repérer l'erreur.

Une fois le tube validé, retirez le `head` final pour obtenir le résultat
complet, et redirigez-le vers un fichier si vous voulez le conserver :

<!-- verif: exec-seulement -->
```bash
awk -F'\t' '$3 == "gene"' data/genome/annotation.gff3 | awk -F'\t' '$7 == "-"' | cut -f9 > resultats/genes_brin_moins.txt
wc -l resultats/genes_brin_moins.txt
```

```output
      55 resultats/genes_brin_moins.txt
```

## Trier et compter : un aperçu de `sort` et `uniq -c`

Pour construire un tube à trois étages vraiment utile, il manque encore deux
outils : `sort`, qui trie les lignes, et `uniq -c`, qui compte les lignes
identiques consécutives. Ces deux commandes seront étudiées en détail à
l'épisode 8 ; nous n'en voyons ici que l'usage minimal nécessaire pour
terminer un tube.

Combien de variants la cohorte contient-elle par contig
(`data/variants/cohorte.vcf`) ? La colonne 1 donne le contig.

**Étage 1**, extraire la colonne 1 des lignes de données (sans les lignes
d'en-tête qui commencent par `#`) :

```bash
grep -v '^#' data/variants/cohorte.vcf | cut -f1 | head -n 3
```

```output
chr1
chr1
chr1
```

**Étage 2**, trier ces valeurs pour que les identiques se retrouvent côte à
côte — condition nécessaire pour que l'étage suivant fonctionne :

```bash
grep -v '^#' data/variants/cohorte.vcf | cut -f1 | sort | head -n 3
```

```output
chr1
chr1
chr1
```

**Étage 3**, compter les lignes identiques consécutives avec `uniq -c` :

```bash
grep -v '^#' data/variants/cohorte.vcf | cut -f1 | sort | uniq -c
```

```output
180 chr1
 20 chrM
```

Un tube à trois étages, construit et vérifié un morceau à la fois, répond à
la question : `chr1` porte 180 variants, `chrM` en porte 20. Remarquez que
`uniq -c` ne fonctionne correctement qu'après un `sort` : il ne regroupe que
des lignes identiques *consécutives*, jamais des lignes identiques dispersées
dans le fichier.

## Défis

::::::::::::::::::::::::::::::::::::: challenge

## Défi 1 : rediriger un comptage (imitation)

En vous inspirant de l'exemple sur `cibles.bed`, écrivez dans
`resultats/nb_variants.txt` le nombre de lignes de données (hors en-têtes) de
`data/variants/cohorte.vcf`.

:::::::::::::::  solution

## Solution

```bash
grep -vc '^#' data/variants/cohorte.vcf > resultats/nb_variants.txt
cat resultats/nb_variants.txt
```

```output
200
```

`grep -vc '^#'` compte (`-c`) les lignes qui ne commencent pas par `#`
(`-v`). Le résultat, un seul nombre, part dans le fichier grâce à `>` plutôt
que de s'afficher à l'écran.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: challenge

## Défi 2 : un tube à deux étages sur le SAM (transfert)

Combien de lectures de `data/alignements/ech01.sam` sont alignées sur `chrM`
(colonne 3 des lignes d'alignement, celles qui ne commencent pas par `@`) ?
Construisez le tube étage par étage, en vérifiant chaque étage avec `head`
avant de passer au suivant.

:::::::::::::::  solution

## Solution

Étage 1, écarter les lignes d'en-tête :

```bash
grep -v '^@' data/alignements/ech01.sam | head -n 3
```

```output
ECH01:1:FLOWCELL1:1:1101:2659:2711	0	chr1	69	60	60M3D40M	*	0	0	GTGACTTCTTTAAATTCGCGGGTTGCACCGTCCTTTGGTTCAATACAAATATGGACTTAACTAATTTATGCAAATTACAGTAGGTACTCTAAGCTCCGAG	?C==DG?E=?AFBCG>CAHIECGEC@FG?=ABEFGEHI=F=CHCA?D?E?EEI=?FFC>DDC=@CABCIFCBDGDHFGCGE?HB=GHEBBGH??FBHG=I	NM:i:1	RG:Z:ech01	AS:i:95
ECH01:1:FLOWCELL1:1:1101:2414:2606	16	chr1	91	60	100M	*	0	0	ATTGCATATGACCAGCCTACATCTCGGAGCTTAGAGTACCTACTGTAATTTGCATAAATTAGTTAAGTCCATATTTGTATTGAACCAAAGGACGGTGCAA	>I=ED?B=IGE>I?GD@EB=IBD@G=>>>B?HFFCHFAF>>GIDFI?GD?>FHBDA>FBF>AE>ADCGBB>?=AHAG=HD?@ACFII?=FFA@GFGHDGD	NM:i:2	RG:Z:ech01	AS:i:90
ECH01:1:FLOWCELL1:1:1101:1140:2060	16	chr1	355	42	100M	*	0	0	TAACTAATATTCGACCTCACCTGGTGGCATCCGCAACGGGTGGATGCTAACAGAAGACAATTTCGATGCTGAATAACCGTTTAACCGATTTGGATAACGA	FFDI=IB=>G@A?AI@IEFD=B>CDHDD@G>E@E=I=D>AF?H>IDBDEHDIB>AAAD>F@@>CFE@I=H?B?H@E?B?IB>CAAEFIIAFD>IG??EBG	NM:i:0	RG:Z:ech01	AS:i:100
```

Étage 2, garder les lignes dont la colonne 3 vaut `chrM`, puis compter :

<!-- verif: exec-seulement -->
```bash
grep -v '^@' data/alignements/ech01.sam | awk -F'\t' '$3 == "chrM"' | wc -l
```

```output
      10
```

`grep -v '^@'` élimine les lignes d'en-tête `@HD`, `@SQ`, `@RG`, `@PG`. `awk`
sélectionne ensuite les lignes où le troisième champ vaut exactement `chrM`.
`wc -l` compte ce qui reste. Le nombre exact dépend du contenu réel du
fichier ; ce qui compte est la démarche par étages.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: challenge

## Défi 3 : un tube à trois étages sur le VCF (transfert)

Combien de variants de `data/variants/cohorte.vcf` sont de type `indel`
(regardez la colonne INFO, champ 8, qui contient `TYPE=indel` ou
`TYPE=snp`) ? Construisez un tube `grep` puis comptez.

:::::::::::::::  solution

## Solution

<!-- verif: exec-seulement -->
```bash
grep -v '^#' data/variants/cohorte.vcf | grep -c 'TYPE=indel'
```

```output
```

`grep -v '^#'` écarte les lignes d'en-tête, `grep -c 'TYPE=indel'` compte
ensuite, parmi les lignes restantes, celles qui contiennent ce motif dans la
colonne INFO. Deux `grep` enchaînés forment déjà un tube à deux étages ; on
aurait pu ajouter un troisième étage avec `wc -l` à la place de `-c`, pour le
même résultat.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: challenge

## Défi 4 : un tube à quatre étages sur les FASTQ (transfert)

En reprenant l'étage `sort | uniq -c` vu plus haut, combien y a-t-il de lanes
de séquençage différentes (troisième `:`-champ de l'identifiant, ex.
`FLOWCELL1` ou le numéro de lane qui suit) dans les en-têtes de
`data/reads/ech01_R1.fastq.gz` ? Contentez-vous de compter les occurrences du
quatrième champ séparé par `:` (numéro de lane) parmi les lignes d'en-tête
(celles qui commencent par `@ECH`).

:::::::::::::::  solution

## Solution

Étage 1, décompresser et isoler les en-têtes :

```bash
gunzip -c data/reads/ech01_R1.fastq.gz | grep '^@ECH' | head -n 3
```

```output
@ECH01:1:FLOWCELL1:1:1101:1000:2000 1:N:0:ATCACG
@ECH01:1:FLOWCELL1:1:1101:1007:2003 1:N:0:ATCACG
@ECH01:1:FLOWCELL1:1:1101:1014:2006 1:N:0:ATCACG
```

Étage 2, extraire le quatrième champ (numéro de lane) :

```bash
gunzip -c data/reads/ech01_R1.fastq.gz | grep '^@ECH' | cut -d':' -f4 | head -n 3
```

```output
1
1
1
```

Étages 3 et 4, trier puis compter les valeurs identiques :

<!-- verif: exec-seulement -->
```bash
gunzip -c data/reads/ech01_R1.fastq.gz | grep '^@ECH' | cut -d':' -f4 | sort | uniq -c
```

```output
    500 1
```

Quatre étages, ajoutés un par un et vérifiés avec `head` avant les deux
derniers : décompression, sélection des en-têtes, extraction du champ, puis
tri et comptage. Toutes les lectures de cet échantillon proviennent de la
même lane, ce qui explique une seule ligne de résultat.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: challenge

## Défi 5 : que fait vraiment cette commande (interprétation, facultatif)

Une collègue a tapé :

<!-- verif: ignore -->
```bash
grep 'gene' data/genome/annotation.gff3 > resultats/genes.txt | wc -l
```

Elle s'attendait à voir le nombre de lignes trouvées s'afficher à l'écran,
mais rien ne s'est affiché. Pourquoi ? Que contient réellement
`resultats/genes.txt` ?

:::::::::::::::  solution

## Solution

La redirection `>` s'applique à `grep`, pas à l'ensemble de la ligne : c'est
`grep 'gene' data/genome/annotation.gff3 > resultats/genes.txt` qui forme la
première commande du tube, et son `stdout` est entièrement détourné vers le
fichier — il ne reste donc rien à envoyer à `wc -l` par le `|`. `wc -l` reçoit
une entrée standard vide et affiche `0` s'il affiche quelque chose, ou reste
simplement silencieux selon le contexte, alors que `resultats/genes.txt`,
lui, contient bien toutes les lignes trouvées par `grep`. C'est l'exact
inverse de ce qu'on veut :

```bash
grep 'gene' data/genome/annotation.gff3 | wc -l > resultats/genes.txt
```

Ici, `grep` alimente `wc -l` via le tube, et c'est le compte final qui part
dans le fichier.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::: keypoints

- `>` redirige la sortie standard vers un fichier et l'écrase sans avertissement ; `>>` ajoute à la fin.
- `<` fournit le contenu d'un fichier comme entrée standard, sans passer par un argument.
- `2>` redirige la sortie d'erreur séparément de la sortie standard ; `2>&1` fusionne les deux.
- `/dev/null` absorbe un flux qu'on veut ignorer sans le stocker.
- `tee` copie un flux vers un fichier tout en le laissant continuer vers la sortie standard.
- `|` relie la sortie standard d'une commande à l'entrée standard de la suivante, sans fichier intermédiaire.
- On construit un tube un étage à la fois, en vérifiant chaque étage avec `head` avant d'ajouter le suivant.
- `sort` puis `uniq -c` comptent les lignes identiques ; `uniq -c` exige des lignes identiques consécutives, donc un tri préalable (détails à l'épisode 8).

::::::::::::::::::::::::::::::::::::::::::::::::::
