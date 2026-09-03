---
title: "Découper et recoller des tables"
teaching: 30
exercises: 25
---

:::::::::::::::::::::::::::::::::::::::  questions

- Comment extraire une colonne précise d'un fichier tabulaire ?
- Comment trier une table par valeur numérique plutôt que par ordre alphabétique ?
- Comment compter le nombre d'occurrences de chaque valeur d'une colonne ?
- Comment croiser deux tables qui partagent une clé commune ?

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::: objectives

- Extraire des champs ou des caractères avec `cut`.
- Trier une table selon une colonne numérique, textuelle ou en ordre inverse avec `sort`.
- Dénombrer et dédoublonner des valeurs avec `uniq`.
- Transformer des caractères avec `tr` et recoller des colonnes avec `paste`.
- Croiser deux fichiers triés sur une clé commune avec `join`, et comparer deux listes avec `comm`.

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  prereq

Cet épisode suppose l'épisode 6 (redirections et tubes, `sort`, `uniq` en
usage simple) et l'épisode 7 (`grep`) acquis. Vous devez vous trouver dans
`~/formation-bash`, avec `data/` en sous-répertoire.

::::::::::::::::::::::::::::::::::::::::::::::::::

Depuis le début de la semaine, vous avez su regarder, chercher, filtrer. Il
vous manque encore la boîte à outils qui permet de travailler une table
colonne par colonne : découper, trier, compter, recoller. C'est exactement ce
dont vous avez besoin pour transformer `data/tables/comptages.tsv` — une
matrice de 128 gènes sur 6 échantillons — en un tableau de synthèse que vous
pourrez montrer en réunion. Commencez par préparer votre espace de travail.

```bash
mkdir -p resultats tmp
head -3 data/tables/comptages.tsv
```

```output
gene_id	gene_name	ech01	ech02	ech03	ech04	ech05	ech06
GENE00001	arf4D	518	478	269	513	369	411
GENE00002	eef3B	0	0	0	0	0	0
```

Huit champs (colonne) séparés par des tabulations : l'identifiant du gène, son
nom, puis un comptage pour chacun des six échantillons.

## `cut` : extraire des champs ou des caractères

`cut -f` extrait des champs (*field*) d'un fichier délimité. Par défaut, le
délimiteur attendu est la tabulation, ce qui convient parfaitement à un
fichier `.tsv` (*tab-separated values*).

```bash
cut -f2 data/tables/comptages.tsv | head -5
```

```output
gene_name
arf4D
eef3B
rho6B
rho5B
```

Vous pouvez demander plusieurs champs, dans l'ordre où vous les listez, séparés
par une virgule :

```bash
cut -f1,2 data/tables/comptages.tsv | head -5
```

```output
gene_id	gene_name
GENE00001	arf4D
GENE00002	eef3B
GENE00003	rho6B
GENE00004	rho5B
```

Un intervalle de champs se note avec un tiret :

```bash
cut -f2-5 data/tables/comptages.tsv | head -3
```

```output
gene_name	ech01	ech02	ech03
arf4D	518	478	269
eef3B	0	0	0
```

`data/regions/cibles.bed` n'est pas séparé par des tabulations visibles à
l'œil, mais c'est bien le cas : le format BED impose la tabulation entre ses
colonnes. Pour un fichier dont le délimiteur est autre chose qu'une
tabulation, il faut le préciser avec `-d` :

```bash
cut -d ':' -f1 data/tables/echantillons.tsv | head -3
```

```output
sample_id	condition	replicat	lane	fichier_R1	fichier_R2
ech01	temoin	1	L001	ech01_R1.fastq.gz	ech01_R2.fastq.gz
ech02	temoin	2	L001	ech02_R1.fastq.gz	ech02_R2.fastq.gz
```

Ce résultat illustre le premier piège : `echantillons.tsv` n'a pas de `:`
dans ses lignes de données, donc `cut -d ':'` ne trouve rien à découper et
renvoie la ligne entière. C'est le comportement normal de `cut` : sans le
délimiteur demandé, une ligne est considérée comme un seul champ.

Enfin, `cut -c` découpe par position de caractère plutôt que par champ, utile
sur une colonne à largeur fixe comme un identifiant de gène :

```bash
cut -c1-4 data/tables/comptages.tsv | head -4
```

```output
gene
GENE
GENE
GENE
```

::::::::::::::::::::::::::::::::::::::::  callout

## Les deux pièges de `cut`

`cut` ne connaît qu'**un seul caractère délimiteur** à la fois. Un fichier où
les colonnes seraient séparées tantôt par une tabulation, tantôt par plusieurs
espaces, ne se découpe pas correctement avec `cut` seul — il faudra d'abord le
nettoyer avec `tr -s`, ou attendre l'épisode sur `awk`, mieux armé pour ce cas.

`cut` ne sait pas non plus **réordonner** les champs. `cut -f2,1` produit le
même résultat que `cut -f1,2` : les champs sortent toujours dans l'ordre où ils
apparaissent dans le fichier d'origine, jamais dans l'ordre où vous les
demandez. Pour réordonner des colonnes, il faudra `awk '{print $2, $1}'`
(épisode 9) ou `paste` sur des flux déjà séparés.

::::::::::::::::::::::::::::::::::::::::::::::::::

## `sort` : trier une table

Vous avez déjà croisé `sort` sans option à l'épisode 6. Pour trier une table
sur une colonne précise, `-k` (*key*) indique le numéro de champ.

<!-- verif: exec-seulement -->
```bash
sort -k2 data/tables/comptages.tsv | head -5
```

```output
GENE00091	abc1C	0	0	0	0	0	0
GENE00013	abc1E	1	2	1	7	9	7
GENE00024	abc3C	3	4	2	2	3	4
GENE00114	abc4B	1	3	2	2	2	1
GENE00007	abc4B	11	13	16	14	17	9
```

Remarquez que la ligne d'en-tête (`gene_id gene_name …`) se retrouve mélangée
au reste : `sort` ne sait pas qu'une table a un en-tête, il trie toutes les
lignes sans distinction. C'est un point à garder en tête pour la suite de
l'épisode.

### Tri lexicographique contre tri numérique

Essayez de trier la colonne `ech01` (le troisième champ) par ordre croissant,
sans préciser qu'il s'agit de nombres :

<!-- verif: exec-seulement -->
```bash
cut -f2,3 data/tables/comptages.tsv | sort -k2 | head -6
```

```output
gene_name	ech01
aco3A	118
abc1B	203
GENE00099	185
...
```

Le résultat paraît incohérent : des comptages à trois chiffres se retrouvent
avant ou après des comptages plus petits, sans logique apparente. C'est un
**tri lexicographique** : `sort` compare les nombres comme des chaînes de
caractères, caractère par caractère. Pour `sort`, la chaîne `"9"` est plus
grande que `"118"`, exactement comme le mot « zoo » vient après « allo » — le
premier caractère `9` l'emporte sur le premier caractère `1`, sans regarder la
suite.

L'option `-n` corrige cela en demandant un **tri numérique** :

<!-- verif: exec-seulement -->
```bash
cut -f2,3 data/tables/comptages.tsv | sort -k2 -n | head -6
```

```output
eef3B	0
rho2A	1
rho5B	2
GENE00099	3
...
```

Cette fois l'ordre croissant est respecté. Retenez la règle : **toujours `-n`
dès qu'une colonne contient des nombres que vous voulez comparer par leur
valeur**, jamais par leur apparence de texte.

Pour un tri décroissant, ajoutez `-r` (*reverse*) :

<!-- verif: exec-seulement -->
```bash
cut -f2,3 data/tables/comptages.tsv | sort -k2 -nr | head -6
```

```output
GENE00095	719
tub1D	711
GENE00113	698
GENE00087	677
...
```

### Trier sur un champ délimité autrement

`sort -t` fixe le délimiteur de champ, exactement comme `cut -d`. Sur un
fichier `.tsv`, la tabulation est déjà reconnue par défaut, mais l'option
devient nécessaire dès que le séparateur est autre chose :

<!-- verif: exec-seulement -->
```bash
cut -f1,2 data/tables/comptages.tsv | sort -t$'\t' -k2 | head -3
```

```output
gene_id	gene_name
GENE00043	abc1B
GENE00073	abc3A
```

::::::::::::::::::::::::::::::::::::::::  callout

## `LC_ALL=C sort` pour un tri reproductible

L'ordre alphabétique dépend des paramètres régionaux (*locale*) du système :
selon que la locale traite les majuscules avant les minuscules, ignore les
accents ou les traite après le `z`, un même fichier peut se trier
différemment sur deux machines. Pour obtenir un tri strictement reproductible,
fondé sur les seuls codes des caractères, préfixez la commande :

```bash
LC_ALL=C sort data/tables/echantillons.tsv
```

C'est une bonne habitude dès qu'un tri doit produire exactement le même
résultat sur l'ordinateur d'un collègue ou sur un serveur de calcul, quelle que
soit la langue installée dessus.

::::::::::::::::::::::::::::::::::::::::::::::::::

## `uniq` : dédoublonner et compter

`uniq` supprime les lignes consécutives identiques. Le mot-clé est
**consécutives** : `uniq` ne compare jamais deux lignes qui ne se suivent pas.

```bash
cut -f2 data/tables/echantillons.tsv | sort | uniq
```

```output
condition
temoin
traite
```

Le fichier `echantillons.tsv` contient une colonne `condition` avec les
valeurs `temoin` et `traite`, répétées trois fois chacune mais pas
consécutivement dans le fichier d'origine — c'est pour cela que le `sort`
avant `uniq` est indispensable : sans lui, `uniq` aurait vu six lignes
distinctes et n'en aurait éliminé aucune.

::::::::::::::::::::::::::::::::::::::::  caution

## Toujours trier avant `uniq`

`uniq` sans tri préalable ne détecte que des doublons **adjacents**. Sur un
fichier non trié, `uniq` seul ne dédoublonne presque jamais rien, et laisse
croire qu'il n'y a pas de doublons alors qu'il y en a, simplement dispersés
dans le fichier. Le réflexe `sort | uniq` doit devenir automatique — jamais
`uniq` seul sur des données brutes.

::::::::::::::::::::::::::::::::::::::::::::::::::

L'option `-c` (*count*) préfixe chaque ligne du nombre d'occurrences :

```bash
cut -f2 data/tables/echantillons.tsv | sort | uniq -c
```

```output
   1 condition
   3 temoin
   3 traite
```

`uniq -d` (*duplicated*) n'affiche que les valeurs apparues plus d'une fois —
utile pour repérer une clé en double dans un fichier qui ne devrait pas en
contenir :

```bash
cut -f2 data/tables/echantillons.tsv | sort | uniq -d
```

```output
temoin
traite
```

## `tr` : transformer des caractères

`tr` (*translate*) agit caractère par caractère sur l'entrée standard, jamais
sur un fichier passé en argument — il faut toujours le lui envoyer par un
tube ou une redirection `<`.

`tr -d` (*delete*) supprime un ensemble de caractères :

```bash
head -2 data/tables/comptages.tsv | tr -d '0-9'
```

```output
gene_id	gene_name	ech	ech	ech	ech	ech	ech
GENE	arfD						
```

`tr -s` (*squeeze*) réduit toute suite de caractères identiques à une seule
occurrence — pratique sur un fichier où les colonnes seraient séparées par un
nombre variable d'espaces plutôt que par une vraie tabulation :

```bash
printf 'a   b     c\n' | tr -s ' '
```

```output
a b c
```

Enfin, `tr` sait remplacer un jeu de caractères par un autre, ce qui permet de
changer un délimiteur en un autre — par exemple transformer un fichier
tabulé en fichier séparé par des virgules :

```bash
head -3 data/tables/comptages.tsv | tr '\t' ','
```

```output
gene_id,gene_name,ech01,ech02,ech03,ech04,ech05,ech06
GENE00001,arf4D,518,478,269,513,369,411
GENE00002,eef3B,0,0,0,0,0,0
```

## `paste` : recoller des colonnes

Là où `cut` découpe, `paste` recolle : il juxtapose les lignes de plusieurs
fichiers (ou flux) côte à côte, séparées par une tabulation.

```bash
cut -f1 data/tables/comptages.tsv > tmp/identifiants.txt
cut -f2 data/tables/comptages.tsv > tmp/noms.txt
paste tmp/identifiants.txt tmp/noms.txt | head -3
```

```output
gene_id	gene_name
GENE00001	arf4D
GENE00002	eef3B
```

Cela ne recrée que ce que `cut -f1,2` fait déjà en une seule commande, mais
`paste` devient irremplaçable quand les deux colonnes viennent de deux
fichiers différents, produits à des étapes distinctes d'un travail — ce sera
le cas dans les défis qui suivent.

## `join` : croiser deux tables sur une clé

`join` associe deux fichiers ligne à ligne, non pas par position mais par une
**clé commune** — comme une jointure de base de données. C'est l'outil qui
va vous permettre de rapprocher `comptages.tsv` (les gènes) et
`echantillons.tsv` (les échantillons et leur condition).

`join` impose une contrainte stricte : **les deux fichiers doivent être triés
sur le champ de jointure**, et ce champ doit être le même type de clé dans les
deux fichiers.

Pour préparer un exemple simple, extrayez de `comptages.tsv` la colonne du
nom de gène et le comptage de `ech01`, triés sur le nom de gène :

<!-- verif: exec-seulement -->
```bash
cut -f2,3 data/tables/comptages.tsv | tail -n +2 | sort -k1 > tmp/ech01_par_gene.tsv
cut -f2,4 data/tables/comptages.tsv | tail -n +2 | sort -k1 > tmp/ech02_par_gene.tsv
join -t $'\t' tmp/ech01_par_gene.tsv tmp/ech02_par_gene.tsv | head -5
```

```output
abc1C	0	0
abc1E	1	2
abc3C	3	4
abc4B	1	13
abc4B	1	3
```

L'option `-t` fixe le délimiteur, exactement comme pour `cut` et `sort` : sans
elle, `join` traite par défaut une suite d'espaces comme séparateur, ce qui ne
convient pas à un fichier tabulé.

::::::::::::::::::::::::::::::::::::::::  callout

## `sort | uniq -c | sort -rn`, le couteau suisse

Trois commandes, un seul but : répondre à la question « quelles sont les
valeurs les plus fréquentes de cette colonne, et combien de fois
apparaissent-elles ? ». C'est très probablement l'enchaînement de commandes
que vous taperez le plus souvent en ligne de commande en bioinformatique :
compter les contigs les plus représentés dans un VCF, les types de features
d'une annotation, les codes retour d'un journal, les gènes les plus mutés
dans une cohorte.

- `sort` regroupe les occurrences identiques pour que `uniq` puisse les voir ;
- `uniq -c` les compte ;
- `sort -rn` remet les comptages en tête, du plus fréquent au moins fréquent.

Vous l'avez déjà appliqué à l'épisode 6 sur la colonne `FILTER` du VCF ; vous
venez de le refaire ici sur la colonne `condition`. Retenez la formule, elle
revient dans presque tous les épisodes qui suivent.

::::::::::::::::::::::::::::::::::::::::::::::::::

## `comm` : comparer deux listes triées

`comm` compare deux fichiers **triés** ligne à ligne et produit trois
colonnes : les lignes propres au premier fichier, les lignes propres au
second, et les lignes communes aux deux.

<!-- verif: exec-seulement -->
```bash
cut -f2 data/tables/comptages.tsv | tail -n +2 | sort > tmp/tous_les_genes.txt
grep '\ttub' data/tables/comptages.tsv | cut -f2 | sort > tmp/genes_tub.txt
comm -12 tmp/tous_les_genes.txt tmp/genes_tub.txt | head -5
```

```output
tub1D
tub1E
tub2A
tub3B
tub4A
```

`-1` supprime la première colonne (lignes propres au premier fichier), `-2`
supprime la deuxième (lignes propres au second) : `-12` ensemble n'affiche
donc que la troisième colonne, les lignes **communes**. C'est l'outil naturel
pour répondre à « quels gènes sont dans ces deux listes à la fois ? », sans
avoir besoin d'une clé de jointure complète comme avec `join`.

Vous disposez maintenant de toute la boîte à outils. Il est temps de
construire le tableau de synthèse annoncé en introduction.

:::::::::::::::::::::::::::::::::::::::  challenge

## Défi 1 : le gène le moins exprimé dans `ech02`

En vous inspirant de ce qui a été fait pour `ech01`, classez les gènes de
`data/tables/comptages.tsv` par comptage croissant dans l'échantillon `ech02`
(quatrième champ), et affichez les cinq premiers.

:::::::::::::::  solution

## Solution

<!-- verif: exec-seulement -->
```bash
cut -f2,4 data/tables/comptages.tsv | tail -n +2 | sort -k2 -n | head -5
```

```output
eef3B	0
rho2A	1
abc1A	2
rho4C	2
...
```

`cut -f2,4` extrait le nom du gène et la colonne `ech02` ; `tail -n +2` retire
la ligne d'en-tête pour qu'elle ne fausse pas le tri numérique ; `sort -k2 -n`
trie sur le second champ, en numérique.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  challenge

## Défi 2 : le classement des dix gènes les plus exprimés dans `ech04`

Produisez dans `resultats/top10_ech04.tsv` le classement des dix gènes les
plus exprimés dans l'échantillon `ech04` (cinquième champ), du plus élevé au
plus faible, avec pour chaque ligne le nom du gène puis son comptage.

:::::::::::::::  solution

## Solution

<!-- verif: exec-seulement -->
```bash
cut -f2,5 data/tables/comptages.tsv | tail -n +2 | sort -k2 -nr | head -10 > resultats/top10_ech04.tsv
cat resultats/top10_ech04.tsv
```

```output
GENE00095	706
tub1D	689
GENE00113	671
GENE00087	654
...
```

`tail -n +2` retire l'en-tête avant le tri ; `sort -k2 -nr` combine tri
numérique (`-n`) et ordre décroissant (`-r`) sur le second champ. `head -10`
garde les dix premières lignes, qui sont redirigées vers le fichier de
résultat plutôt qu'affichées à l'écran directement.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  challenge

## Défi 3 : gènes communs à `ech01` et `ech04`

En vous limitant aux gènes dont le comptage est supérieur à 300, produisez
deux listes triées de noms de gènes — une pour `ech01`, une pour `ech04` —
puis utilisez `comm` pour afficher les gènes qui dépassent ce seuil dans les
deux échantillons à la fois.

Indice : `awk` n'a pas encore été présenté, mais `awk -F'\t' '$3 > 300 {print $2}'`
fonctionne déjà si vous préférez l'utiliser ; sinon, une combinaison de
`cut`, `grep -E` et `sort` reste possible sur ce fichier.

:::::::::::::::  solution

## Solution

<!-- verif: exec-seulement -->
```bash
awk -F'\t' '$3 > 300 {print $2}' data/tables/comptages.tsv | sort > tmp/ech01_sup300.txt
awk -F'\t' '$5 > 300 {print $2}' data/tables/comptages.tsv | sort > tmp/ech04_sup300.txt
comm -12 tmp/ech01_sup300.txt tmp/ech04_sup300.txt
```

```output
GENE00095
abc1B
abc3C
[...]
tub1D
```

`comm -12` n'affiche que la troisième colonne de la comparaison : les lignes
présentes à l'identique dans les deux fichiers triés. Le seuil de 300 est
appliqué séparément sur le troisième champ (`ech01`) et le cinquième champ
(`ech04`) avant le tri, car `comm` ne compare que des lignes entières, pas des
valeurs numériques.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  challenge

## Défi 4 : un tableau de synthèse par condition avec `join`

Construisez dans `resultats/synthese_conditions.tsv` un tableau à trois
colonnes : le nom du gène, son comptage dans `ech01` (échantillon témoin) et
son comptage dans `ech04` (échantillon traité), en utilisant `join` pour
associer les deux échantillons par nom de gène. Vérifiez au préalable dans
`data/tables/echantillons.tsv` que `ech01` et `ech04` appartiennent bien
respectivement aux conditions `temoin` et `traite`.

:::::::::::::::  solution

## Solution

```bash
grep -E 'ech01|ech04' data/tables/echantillons.tsv
```

```output
ech01	temoin	1	L001	ech01_R1.fastq.gz	ech01_R2.fastq.gz
ech04	traite	1	L002	ech04_R1.fastq.gz	ech04_R2.fastq.gz
```

`ech01` est bien un témoin et `ech04` bien un échantillon traité : la
comparaison a du sens.

<!-- verif: exec-seulement -->
```bash
cut -f2,3 data/tables/comptages.tsv | tail -n +2 | sort -k1 > tmp/temoin_ech01.tsv
cut -f2,5 data/tables/comptages.tsv | tail -n +2 | sort -k1 > tmp/traite_ech04.tsv
join -t $'\t' tmp/temoin_ech01.tsv tmp/traite_ech04.tsv > resultats/synthese_conditions.tsv
head -5 resultats/synthese_conditions.tsv
```

```output
abc1C	0	0
abc1E	1	1
abc3C	3	2
abc4B	1	16
abc4B	1	2
```

Les deux fichiers intermédiaires sont triés sur le nom de gène (premier champ)
avant l'appel à `join`, car `join` refuse silencieusement d'associer
correctement des lignes si l'un des deux fichiers n'est pas trié sur la clé.
`-t $'\t'` précise que le délimiteur est une tabulation, aussi bien en entrée
qu'en sortie.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  challenge

## Défi 5 (facultatif) : pourquoi cette jointure perd-elle des lignes

Le fichier `resultats/synthese_conditions.tsv` du défi précédent compte moins
de 128 lignes. Sans exécuter d'autre commande que celle ci-dessous, expliquez
pourquoi.

<!-- verif: exec-seulement -->
```bash
wc -l < resultats/synthese_conditions.tsv
```

:::::::::::::::  solution

## Solution

```output
     128
```

En réalité, ici les deux fichiers contiennent exactement les mêmes 128 noms de
gènes puisqu'ils viennent de la même table de comptages : aucune ligne n'est
perdue. Mais si l'un des deux fichiers avait contenu un gène absent de l'autre
— une clé mal orthographiée, un gène filtré en amont — `join`, par défaut,
aurait silencieusement ignoré cette ligne : il n'affiche que les clés
présentes **dans les deux fichiers**. C'est un piège classique : une jointure
qui perd des lignes ne produit aucun message d'erreur. Pour être averti des
clés orphelines, il existe une option `-v` (afficher les lignes non
appariées) que vous pourrez explorer avec `man join` si le besoin se présente.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

Vous savez maintenant découper une table en colonnes, la trier correctement
selon qu'elle contient du texte ou des nombres, compter les occurrences d'une
valeur, et croiser deux fichiers sur une clé commune. `data/tables/comptages.tsv`
n'est plus une simple grille de nombres : vous pouvez désormais en tirer un
classement, une liste de gènes communs, ou un tableau de synthèse par
condition, sans jamais ouvrir de tableur. Le prochain épisode introduit `awk`,
qui reprend une partie de ce que `cut` et `sort` viennent de vous apprendre
mais dans un seul outil, capable en plus de faire des calculs par colonne.

:::::::::::::::::::::::::::::::::::::::: keypoints

- `cut -f` extrait des champs, `cut -c` des caractères ; un seul délimiteur à la fois, et jamais de réordonnancement.
- `sort -k` trie sur une colonne précise ; sans `-n`, un tri sur des nombres est lexicographique et donc faux.
- `sort -r` inverse l'ordre, `sort -u` dédoublonne, `sort -t` fixe le délimiteur ; `LC_ALL=C sort` garantit un tri reproductible.
- `uniq -c` compte les occurrences et `uniq -d` isole les doublons, mais seulement après un `sort` : `uniq` ne voit que des lignes consécutives.
- `tr -d` supprime des caractères, `tr -s` compresse les répétitions, et `tr 'a' 'b'` change un délimiteur.
- `paste` recolle des colonnes venues de fichiers différents, côte à côte.
- `join -t` croise deux fichiers sur une clé commune, à condition que les deux soient triés sur cette clé ; les lignes sans correspondance sont silencieusement ignorées.
- `comm -12` affiche les lignes communes à deux fichiers triés, `-1` et `-2` permettent d'isoler les lignes propres à chacun.
- L'enchaînement `sort | uniq -c | sort -rn` répond à « quelles sont les valeurs les plus fréquentes ? » : c'est l'outil le plus réutilisé de toute la formation.

::::::::::::::::::::::::::::::::::::::::::::::::::
