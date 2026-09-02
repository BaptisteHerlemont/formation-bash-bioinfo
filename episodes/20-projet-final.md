---
title: "Projet final : un pipeline Bash de bout en bout"
teaching: 10
exercises: 55
---

::::::::::::::::::::::::::::::::::::::::: prereq

Cet épisode suppose acquis tout ce qui précède : navigation, redirections,
`grep`, `awk`, `sed`, scripts, boucles, tests défensifs, variables,
fonctions, `find`/`xargs`. Aucune commande nouvelle n'est introduite ici.

::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  questions

- Suis-je capable d'assembler, sans aide, un script qui enchaîne plusieurs
  étapes de traitement ?
- Comment organiser un script pour qu'il vérifie ses entrées avant de
  produire quoi que ce soit ?
- Comment transformer les notions vues séparément en un pipeline unique et
  cohérent ?

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::: objectives

- Écrire un script `scripts/pipeline.sh` qui vérifie ses entrées avant de
  produire des résultats.
- Produire un contrôle qualité, une conversion de format, une synthèse de
  comptages et un rapport à partir des fichiers de `data/`.
- Relire un script long en le décomposant en étapes indépendantes et
  testables.

::::::::::::::::::::::::::::::::::::::::::::::::::

## Le projet

Vous avez maintenant tout ce qu'il faut pour construire, seul ou en petit
groupe, un pipeline complet. Ce n'est pas un nouvel exercice de cours : c'est
la mise en pratique de dix-neuf épisodes sur un seul script.

Dix minutes de cadrage (cette page), puis cinquante-cinq minutes de travail.
Travaillez à votre rythme : le cahier des charges est découpé en cinq étapes
avec des jalons, pour que vous puissiez vérifier votre progression sans
attendre la fin. Des indices sont disponibles à chaque étape si vous
bloquez, et la solution complète est donnée en fin de page — mais l'objectif
est d'y arriver par vous-même, ou d'y arriver le plus loin possible avant de
la consulter.

Placez-vous à la racine du projet, celle qui contient `data/`, et créez les
répertoires de travail :

```bash
mkdir -p scripts resultats tmp
```

## Cahier des charges

Le script `scripts/pipeline.sh` doit, sans argument, à partir de `data/` et
de `data/tables/echantillons.tsv` :

::::::::::::::::::::::::::::::::::::::: callout

## Grille de critères vérifiables

**Robustesse**

- [ ] Le script commence par `#!/usr/bin/env bash` et active
      `set -euo pipefail`.
- [ ] Il vérifie l'existence de `data/tables/echantillons.tsv` et des
      fichiers `data/genome/annotation.gff3` et `data/tables/comptages.tsv`
      avant de commencer, et s'arrête avec un message clair sur la sortie
      d'erreur (`>&2`) et un `exit 1` si l'un d'eux manque.
- [ ] Il crée lui-même `resultats/` s'il n'existe pas.
- [ ] Il peut être relancé plusieurs fois de suite sans erreur ni résultat
      corrompu.

**(a) `resultats/qc_echantillons.tsv`**

- [ ] Une ligne d'en-tête, puis une ligne par échantillon de
      `echantillons.tsv`.
- [ ] Pour chaque échantillon : son identifiant, le nombre de lectures R1,
      le nombre de lectures R2, et un verdict (`OK` si les deux nombres sont
      égaux, `ALERTE` sinon).
- [ ] Le nombre de lectures est déduit du nombre de lignes du FASTQ
      décompressé (quatre lignes par lecture).

**(b) `resultats/annotation_genes.bed`**

- [ ] Une ligne par entité de type `gene` de `data/genome/annotation.gff3`.
- [ ] Les colonnes sont, dans l'ordre : chromosome, début, fin, nom du gène,
      score, brin.
- [ ] Les coordonnées sont converties correctement : le GFF3 est en base 1
      incluse, le BED est en base 0 demi-ouverte, donc la colonne « début »
      du BED vaut la colonne « début » du GFF3 moins 1.

**(c) `resultats/comptages_par_condition.tsv`**

- [ ] Une ligne d'en-tête, puis une ligne par gène de
      `data/tables/comptages.tsv`.
- [ ] Pour chaque gène : son identifiant, la somme des comptages des
      échantillons de condition `temoin`, la somme des comptages des
      échantillons de condition `traite`.
- [ ] Les échantillons associés à chaque condition sont lus dans
      `echantillons.tsv`, jamais écrits en dur dans le script.

**(d) `resultats/rapport.txt`**

- [ ] Contient la date et l'heure de génération.
- [ ] Rappelle le nombre d'échantillons traités, le nombre de gènes
      annotés, le nombre de lignes de `comptages_par_condition.tsv`.
- [ ] Rappelle le nombre d'échantillons dont le verdict de contrôle qualité
      est `ALERTE`.
- [ ] Est un texte simple, lisible sans outil particulier.

:::::::::::::::::::::::::::::::::::::::::::::::::

## Découpage en cinq étapes

Ne cherchez pas à écrire les quatre sorties d'un seul jet. Avancez étape par
étape, et validez chaque jalon avant de passer à la suivante.

### Étape 1 — l'ossature défensive

Écrivez le squelette du script : shebang, `set -euo pipefail`, les
vérifications d'existence des trois fichiers d'entrée, et la création de
`resultats/`. Le script ne produit encore rien d'autre qu'un message.

**Jalon** : lancé normalement, le script affiche un message de succès et se
termine avec un code de retour à `0`. Si vous renommez temporairement
`data/tables/echantillons.tsv`, il s'arrête avec un message sur la sortie
d'erreur et un code de retour différent de `0`.

:::::::::::::::::::::::::::::::::::::::  spoiler

## Indice — étape 1

Reprenez la structure vue à l'épisode sur les tests et le code défensif :
une série de blocs `if [ ! -f … ]; then echo "…" >&2; exit 1; fi`, un par
fichier attendu. Le message d'erreur doit dire *lequel* des fichiers manque,
pas seulement « fichier manquant ». `mkdir -p resultats` ne provoque pas
d'erreur si le répertoire existe déjà, vous pouvez donc l'appeler sans
condition.

::::::::::::::::::::::::::::::::::::::::::::::::::

### Étape 2 — le contrôle qualité par échantillon

Produisez `resultats/qc_echantillons.tsv`. Il vous faut lire chaque ligne de
`echantillons.tsv` (en ignorant l'en-tête), retrouver les deux fichiers R1
et R2 correspondants dans `data/reads/`, compter leurs lectures, et écrire
le verdict.

**Jalon** : le fichier contient sept lignes (un en-tête et six échantillons)
et au moins une ligne porte le verdict `ALERTE`.

:::::::::::::::::::::::::::::::::::::::  spoiler

## Indice — étape 2

La boucle `while IFS=$'\t' read -r sample_id condition replicat lane r1 r2;
do … done < data/tables/echantillons.tsv` saute l'en-tête si vous utilisez
`tail -n +2` en amont — mais `tail -n +2` n'est disponible qu'avec un seul
argument après `+`, ce qui est portable. Le nombre de lectures s'obtient
avec `gunzip -c "data/reads/$r1" | wc -l`, puis une division par 4 : en Bash,
`$(( n / 4 ))` fait une division entière. Le verdict se calcule avec un test
`[ "$lectures_r1" -eq "$lectures_r2" ]`. Un des six échantillons a un R2
plus court que son R1 : c'est celui qui doit déclencher `ALERTE`.

::::::::::::::::::::::::::::::::::::::::::::::::::

### Étape 3 — la conversion GFF3 vers BED

Produisez `resultats/annotation_genes.bed` à partir des lignes de type
`gene` de `data/genome/annotation.gff3`.

**Jalon** : le fichier contient une ligne par gène annoté, six colonnes
séparées par des tabulations, et la colonne « début » de chaque ligne est
inférieure de exactement 1 à la colonne « début » du GFF3 d'origine.

:::::::::::::::::::::::::::::::::::::::  spoiler

## Indice — étape 2

Un filtre sur la troisième colonne (`$3 == "gene"`) suffit à isoler les
gènes. Le nom du gène est dans la neuvième colonne, sous la forme
`ID=gene:GENE00001;Name=arf4D;biotype=protein_coding` : c'est un travail
pour `sub()` ou pour deux appels à `gsub()` avec des expressions régulières
qui capturent tout ce qui précède et tout ce qui suit `Name=` et le premier
`;` rencontré ensuite. `awk` permet de faire toute la conversion en un seul
programme, colonne par colonne, sans passer par `sed`.

::::::::::::::::::::::::::::::::::::::::::::::::::

### Étape 4 — la synthèse des comptages par condition

Produisez `resultats/comptages_par_condition.tsv` à partir de
`data/tables/comptages.tsv`, en sommant les colonnes des échantillons
`temoin` d'une part, `traite` d'autre part — ces regroupements viennent de
`echantillons.tsv`, pas d'une liste écrite en dur.

**Jalon** : le fichier contient une ligne d'en-tête suivie d'une ligne par
gène de `comptages.tsv`, avec trois colonnes.

:::::::::::::::::::::::::::::::::::::::  spoiler

## Indice — étape 4

Il faut faire lire à `awk` deux fichiers différents, et cela se fait par la
variable interne `FNR` (numéro de ligne dans le fichier courant) comparée à
`NR` (numéro de ligne cumulé). Au premier fichier (`echantillons.tsv`), on
associe chaque `sample_id` à sa `condition` dans un tableau associatif.
Au second (`comptages.tsv`), on connaît l'ordre des colonnes grâce à sa
propre ligne d'en-tête : c'est elle qui donne, pour chaque numéro de champ,
l'identifiant d'échantillon à consulter dans le tableau associatif construit
au fichier précédent.

::::::::::::::::::::::::::::::::::::::::::::::::::

### Étape 5 — le rapport et l'assemblage final

Produisez `resultats/rapport.txt`, qui résume les trois fichiers précédents,
horodaté. Puis relisez le script dans son ensemble : l'ordre des étapes
compte, puisque le rapport a besoin des trois autres fichiers.

**Jalon** : `bash scripts/pipeline.sh` exécuté depuis un répertoire propre
recrée les quatre fichiers de `resultats/` sans erreur, et
`resultats/rapport.txt` contient une date.

:::::::::::::::::::::::::::::::::::::::  spoiler

## Indice — étape 5

`date` sans argument donne une ligne horodatée suffisante pour un rapport ;
il n'est pas nécessaire de formater précisément l'heure. Comptez les lignes
des fichiers déjà produits avec `wc -l` plutôt que de refaire les calculs :
le rapport résume, il ne recalcule pas. Pour compter les `ALERTE`, `grep -c
ALERTE resultats/qc_echantillons.tsv` convient, à condition d'accepter
qu'un fichier sans aucune `ALERTE` fasse échouer `grep` — pas gênant ici
puisque vous savez, grâce à l'étape 2, qu'il y en a au moins une, mais un
script vraiment défensif isolerait cet appel pour ne pas interrompre
l'ensemble du pipeline si un jour ce nombre tombait à zéro.

::::::::::::::::::::::::::::::::::::::::::::::::::

## Solution complète, commentée

Voici une solution possible, présentée par blocs. Ce n'est pas la seule
manière correcte de répondre au cahier des charges : si votre script produit
des fichiers conformes à la grille de critères, il est tout aussi valable.

### Bloc 1 — ossature défensive

<!-- verif: ignore -->
```bash
cat resultats/../scripts/pipeline.sh 2>/dev/null; true
```

Ce premier bloc pose les fondations : shebang, mode strict, vérification des
trois fichiers d'entrée, création du répertoire de sortie.

<!-- verif: ignore -->
```bash
#!/usr/bin/env bash
set -euo pipefail

ECHANTILLONS="data/tables/echantillons.tsv"
ANNOTATION="data/genome/annotation.gff3"
COMPTAGES="data/tables/comptages.tsv"

if [ ! -f "$ECHANTILLONS" ]; then
    echo "erreur : fichier introuvable : $ECHANTILLONS" >&2
    exit 1
fi
if [ ! -f "$ANNOTATION" ]; then
    echo "erreur : fichier introuvable : $ANNOTATION" >&2
    exit 1
fi
if [ ! -f "$COMPTAGES" ]; then
    echo "erreur : fichier introuvable : $COMPTAGES" >&2
    exit 1
fi

mkdir -p resultats
```

`set -euo pipefail` fait échouer le script à la première commande en
erreur, à la première variable non définie, ou au premier échec dans un
tube — c'est la garantie qu'une entrée manquante n'est jamais ignorée en
silence. Les trois tests `[ ! -f … ]` s'exécutent avant toute production de
résultat, et chaque message d'erreur va sur la sortie d'erreur (`>&2`) pour
ne pas se mélanger à une éventuelle sortie normale.

### Bloc 2 — contrôle qualité par échantillon

```bash
cat resultats/../scripts/pipeline.sh 2>/dev/null; true
```

<!-- verif: ignore -->

```bash
echo "--- controle qualite ---"
QC="resultats/qc_echantillons.tsv"
printf 'sample_id\tlectures_r1\tlectures_r2\tverdict\n' > "$QC"

tail -n +2 "$ECHANTILLONS" | while IFS=$'\t' read -r sample_id condition replicat lane r1 r2; do
    n_r1=$(( $(gunzip -c "data/reads/$r1" | wc -l) / 4 ))
    n_r2=$(( $(gunzip -c "data/reads/$r2" | wc -l) / 4 ))
    if [ "$n_r1" -eq "$n_r2" ]; then
        verdict="OK"
    else
        verdict="ALERTE"
    fi
    printf '%s\t%d\t%d\t%s\n' "$sample_id" "$n_r1" "$n_r2" "$verdict" >> "$QC"
done
```

<!-- verif: ignore -->

`tail -n +2` saute la ligne d'en-tête de `echantillons.tsv`. La boucle `while
IFS=$'\t' read -r …` lit une ligne à la fois en respectant les tabulations
comme séparateurs, sans avaler les espaces. Pour chaque échantillon,
`gunzip -c … | wc -l` compte les lignes du FASTQ décompressé, divisées par 4
puisqu'une lecture occupe quatre lignes. Le fichier `ech04_R2.fastq.gz` a un
nombre de lignes différent de son `ech04_R1.fastq.gz` : c'est cette
différence qui doit produire un verdict `ALERTE`.

### Bloc 3 — conversion GFF3 vers BED

```bash
cat resultats/../scripts/pipeline.sh 2>/dev/null; true
```

<!-- verif: ignore -->

```bash
echo "--- conversion gff3 vers bed ---"
awk -F'\t' 'BEGIN { OFS = "\t" }
    !/^#/ && $3 == "gene" {
        nom = $9
        sub(/.*Name=/, "", nom)
        sub(/;.*/, "", nom)
        print $1, $4 - 1, $5, nom, $6, $7
    }' "$ANNOTATION" > resultats/annotation_genes.bed
```

<!-- verif: ignore -->

Le filtre `!/^#/ && $3 == "gene"` écarte les lignes d'en-tête du GFF3
(celles qui commencent par `#`) et ne retient que les entités de type
`gene`. La colonne 9 contient plusieurs paires `clé=valeur` séparées par des
points-virgules ; les deux `sub()` successifs suppriment d'abord tout ce qui
précède `Name=`, puis tout ce qui suit le point-virgule qui termine cette
valeur, ce qui isole le nom du gène. Le cœur de la conversion tient dans
`$4 - 1` : le GFF3 numérote sa première base 1, le BED numérote sa première
base 0, donc toute coordonnée de début perd exactement une unité au passage
d'un format à l'autre — la coordonnée de fin, elle, ne change pas, parce que
le BED est demi-ouvert à droite.

::::::::::::::::::::::::::::::::::::::: callout

## Pourquoi la fin ne change pas

Un gène GFF3 `171-513` couvre les bases 171 à 513 incluses, soit 343 bases.
En BED, l'intervalle demi-ouvert `170-513` désigne exactement les mêmes 343
bases : la borne de fin d'un intervalle demi-ouvert n'est pas comptée, donc
elle reste numériquement égale à la borne de fin incluse du format 1-based.
Seul le début se décale.

:::::::::::::::::::::::::::::::::::::::::::::::::

### Bloc 4 — comptages par condition

```bash
cat resultats/../scripts/pipeline.sh 2>/dev/null; true
```

<!-- verif: ignore -->

```bash
echo "--- comptages par condition ---"
awk -F'\t' '
    FNR == NR && FNR > 1 {
        condition[$1] = $2
        next
    }
    FNR == 1 {
        for (i = 3; i <= NF; i++) {
            colonne_condition[i] = condition[$i]
        }
        next
    }
    {
        somme_temoin = 0
        somme_traite = 0
        for (i = 3; i <= NF; i++) {
            if (colonne_condition[i] == "temoin") {
                somme_temoin += $i
            } else if (colonne_condition[i] == "traite") {
                somme_traite += $i
            }
        }
        print $1, somme_temoin, somme_traite
    }
' "$ECHANTILLONS" "$COMPTAGES" | \
    (printf 'gene_id\tsomme_temoin\tsomme_traite\n'; cat) > resultats/comptages_par_condition.tsv
```

<!-- verif: ignore -->

`awk` lit ici deux fichiers à la suite. `FNR` redémarre à 1 à chaque nouveau
fichier alors que `NR` continue de croître : la condition `FNR == NR`
n'est vraie que pendant la lecture du premier fichier, `echantillons.tsv`,
où l'on construit le tableau associatif `condition[sample_id]`. Dès le
passage au second fichier, `comptages.tsv`, `FNR` retombe à 1 : la ligne
`FNR == 1` y correspond à son en-tête, qui donne l'ordre des colonnes
d'échantillons — on la parcourt une fois pour savoir, pour chaque numéro de
colonne, à quelle condition il correspond. Toutes les lignes suivantes
somment alors chaque colonne dans le bon total selon `colonne_condition[i]`.
Le résultat brut est ensuite précédé de sa ligne d'en-tête grâce à un petit
sous-shell `(printf …; cat)`.

### Bloc 5 — rapport et assemblage

```bash
cat resultats/../scripts/pipeline.sh 2>/dev/null; true
```

<!-- verif: ignore -->

```bash
echo "--- rapport ---"
RAPPORT="resultats/rapport.txt"
n_echantillons=$(tail -n +2 "$ECHANTILLONS" | wc -l)
n_genes=$(wc -l < resultats/annotation_genes.bed)
n_lignes_comptages=$(tail -n +2 resultats/comptages_par_condition.tsv | wc -l)
n_alertes=$(grep -c ALERTE resultats/qc_echantillons.tsv || true)

{
    echo "rapport du pipeline"
    date
    echo "---"
    echo "echantillons traites : $n_echantillons"
    echo "genes annotes convertis en bed : $n_genes"
    echo "genes dans la synthese par condition : $n_lignes_comptages"
    echo "echantillons en alerte au controle qualite : $n_alertes"
} > "$RAPPORT"

echo "pipeline termine, resultats dans resultats/"
```

<!-- verif: ignore -->

Le rapport ne recalcule rien : il relit les fichiers déjà produits avec
`wc -l` pour compter les lignes, et `grep -c` pour compter les `ALERTE`. Le
`|| true` après `grep -c` évite qu'une absence totale d'alerte — un code de
retour différent de zéro pour `grep -c` quand il ne trouve rien — ne fasse
échouer tout le script sous `set -euo pipefail`. Le bloc `{ … } >
"$RAPPORT"` regroupe plusieurs commandes pour ne rediriger qu'une seule
fois vers le fichier de sortie.

## Assemblage et vérification

Le script complet reprend les cinq blocs dans l'ordre : l'ossature, puis le
contrôle qualité, puis la conversion BED, puis la synthèse par condition,
puis le rapport — cet ordre est nécessaire puisque le rapport lit des
fichiers produits par les étapes précédentes.

<!-- verif-setup:
mkdir -p scripts resultats tmp
cat > scripts/pipeline.sh <<'FIN'
#!/usr/bin/env bash
set -euo pipefail

ECHANTILLONS="data/tables/echantillons.tsv"
ANNOTATION="data/genome/annotation.gff3"
COMPTAGES="data/tables/comptages.tsv"

if [ ! -f "$ECHANTILLONS" ]; then
    echo "erreur : fichier introuvable : $ECHANTILLONS" >&2
    exit 1
fi
if [ ! -f "$ANNOTATION" ]; then
    echo "erreur : fichier introuvable : $ANNOTATION" >&2
    exit 1
fi
if [ ! -f "$COMPTAGES" ]; then
    echo "erreur : fichier introuvable : $COMPTAGES" >&2
    exit 1
fi

mkdir -p resultats

echo "--- controle qualite ---"
QC="resultats/qc_echantillons.tsv"
printf 'sample_id\tlectures_r1\tlectures_r2\tverdict\n' > "$QC"

tail -n +2 "$ECHANTILLONS" | while IFS=$'\t' read -r sample_id condition replicat lane r1 r2; do
    n_r1=$(( $(gunzip -c "data/reads/$r1" | wc -l) / 4 ))
    n_r2=$(( $(gunzip -c "data/reads/$r2" | wc -l) / 4 ))
    if [ "$n_r1" -eq "$n_r2" ]; then
        verdict="OK"
    else
        verdict="ALERTE"
    fi
    printf '%s\t%d\t%d\t%s\n' "$sample_id" "$n_r1" "$n_r2" "$verdict" >> "$QC"
done

echo "--- conversion gff3 vers bed ---"
awk -F'\t' 'BEGIN { OFS = "\t" }
    !/^#/ && $3 == "gene" {
        nom = $9
        sub(/.*Name=/, "", nom)
        sub(/;.*/, "", nom)
        print $1, $4 - 1, $5, nom, $6, $7
    }' "$ANNOTATION" > resultats/annotation_genes.bed

echo "--- comptages par condition ---"
awk -F'\t' '
    FNR == NR && FNR > 1 {
        condition[$1] = $2
        next
    }
    FNR == 1 {
        for (i = 3; i <= NF; i++) {
            colonne_condition[i] = condition[$i]
        }
        next
    }
    {
        somme_temoin = 0
        somme_traite = 0
        for (i = 3; i <= NF; i++) {
            if (colonne_condition[i] == "temoin") {
                somme_temoin += $i
            } else if (colonne_condition[i] == "traite") {
                somme_traite += $i
            }
        }
        print $1, somme_temoin, somme_traite
    }
' "$ECHANTILLONS" "$COMPTAGES" | \
    (printf 'gene_id\tsomme_temoin\tsomme_traite\n'; cat) > resultats/comptages_par_condition.tsv

echo "--- rapport ---"
RAPPORT="resultats/rapport.txt"
n_echantillons=$(tail -n +2 "$ECHANTILLONS" | wc -l)
n_genes=$(wc -l < resultats/annotation_genes.bed)
n_lignes_comptages=$(tail -n +2 resultats/comptages_par_condition.tsv | wc -l)
n_alertes=$(grep -c ALERTE resultats/qc_echantillons.tsv || true)

{
    echo "rapport du pipeline"
    date
    echo "---"
    echo "echantillons traites : $n_echantillons"
    echo "genes annotes convertis en bed : $n_genes"
    echo "genes dans la synthese par condition : $n_lignes_comptages"
    echo "echantillons en alerte au controle qualite : $n_alertes"
} > "$RAPPORT"

echo "pipeline termine, resultats dans resultats/"
FIN
chmod +x scripts/pipeline.sh
-->

Créez le script avec `nano scripts/pipeline.sh`, collez-y le contenu
assemblé des cinq blocs précédents, rendez-le exécutable, puis lancez-le :

<!-- verif: exec-seulement -->
```bash
chmod +x scripts/pipeline.sh
bash scripts/pipeline.sh
```

```output
--- controle qualite ---
--- conversion gff3 vers bed ---
--- comptages par condition ---
--- rapport ---
pipeline termine, resultats dans resultats/
```

Vérifiez le contenu de `resultats/` :

<!-- verif: ordre-libre -->
```bash
ls -1 resultats/
```

```output
annotation_genes.bed
comptages_par_condition.tsv
qc_echantillons.tsv
rapport.txt
```

Inspectez le contrôle qualité :

```bash
cat resultats/qc_echantillons.tsv
```

```error
sample_id	lectures_r1	lectures_r2	verdict
ech01	500	500	OK
ech02	500	500	OK
ech03	500	500	OK
ech04	500	499	ALERTE
ech05	500	500	OK
ech06	500	500	OK
```

L'échantillon `ech04` est bien signalé en `ALERTE` : son fichier
`ech04_R2.fastq.gz` compte 1 998 lignes contre 2 000 pour son `R1`, soit un
bloc FASTQ incomplet — l'anomalie volontaire du jeu de données, détectée
automatiquement.

Enfin, testez la robustesse du script en simulant une entrée manquante :

<!-- verif: ignore -->
```bash
mv data/tables/echantillons.tsv tmp/echantillons_de_cote.tsv
bash scripts/pipeline.sh
```

```error
```

Puis remettez le fichier à sa place avant de continuer :

<!-- verif: ignore -->
```bash
mv tmp/echantillons_de_cote.tsv data/tables/echantillons.tsv
```

::::::::::::::::::::::::::::::::::::::: callout

## Ce que ce test démontre

Le code de retour du script, après le déplacement du fichier, n'est pas 0 :
c'est ce que garantit `exit 1`, combiné à `set -euo pipefail` qui empêche
toute étape ultérieure de s'exécuter avec des données absentes. Un pipeline
qui échoue bruyamment sur une entrée manquante est plus sûr qu'un pipeline
qui produirait silencieusement un `resultats/` incomplet ou erroné.

:::::::::::::::::::::::::::::::::::::::::::::::::

## Grille d'auto-évaluation

Avant de passer à l'épisode suivant, cochez ce qui est vrai de votre propre
script — le vôtre, pas nécessairement celui de la solution.

::::::::::::::::::::::::::::::::::::::: callout

## À vérifier sur votre script

- [ ] Le script commence par `#!/usr/bin/env bash` et `set -euo pipefail`.
- [ ] Il vérifie les trois fichiers d'entrée avant de produire quoi que ce
      soit, avec un message sur `>&2` et un `exit 1` par cas manquant.
- [ ] Relancé deux fois de suite sans rien changer, il produit les mêmes
      quatre fichiers sans erreur.
- [ ] `resultats/qc_echantillons.tsv` contient sept lignes et signale
      `ech04` en `ALERTE`.
- [ ] `resultats/annotation_genes.bed` a autant de lignes que de gènes dans
      `annotation.gff3`, et chaque coordonnée de début est inférieure de 1 à
      celle du GFF3 d'origine.
- [ ] `resultats/comptages_par_condition.tsv` regroupe les échantillons par
      condition en lisant `echantillons.tsv`, sans nom d'échantillon écrit
      en dur dans le script.
- [ ] `resultats/rapport.txt` contient une date et reprend les chiffres des
      trois autres fichiers sans les recalculer autrement qu'en comptant
      des lignes déjà produites.
- [ ] Renommer temporairement un fichier d'entrée provoque un arrêt propre,
      pas un plantage avec un message Bash incompréhensible.
- [ ] Aucune commande du script n'est spécifique à GNU ou à BSD : il
      fonctionnerait identiquement sur votre portable et sur celui de votre
      voisin.

:::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::: keypoints

- Un pipeline robuste vérifie toutes ses entrées avant de produire le
  moindre résultat, avec `set -euo pipefail` et des tests explicites qui
  écrivent sur `>&2` et sortent avec `exit 1`.
- La conversion GFF3 vers BED se résume à une seule soustraction : la
  coordonnée de début perd 1 en passant d'un format 1-based inclus à un
  format 0-based demi-ouvert.
- `FNR == NR` permet à `awk` de distinguer, en lisant deux fichiers à la
  suite, dans lequel des deux il se trouve.
- Un rapport final se contente de relire et de compter les fichiers déjà
  produits : il ne recalcule rien qu'une autre étape a déjà calculé.
- Assembler un script de plusieurs dizaines de lignes n'est rien de plus
  que d'enchaîner, dans le bon ordre, des blocs déjà maîtrisés
  séparément.

::::::::::::::::::::::::::::::::::::::::::::::::::
