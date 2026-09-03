---
title: "Fonctions et pilotage par feuille d'échantillons"
teaching: 25
exercises: 25
---

:::::::::::::::::::::::::::::::::::::::  questions

- Comment éviter de recopier dix fois le même bloc de commandes dans mes scripts ?
- Comment faire lire mes scripts directement dans `data/tables/echantillons.tsv`, sans écrire les noms d'échantillons dans le script lui-même ?
- Comment lire un fichier ligne par ligne, et pourquoi mes variables disparaissent-elles parfois après une boucle ?

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::: objectives

- Écrire une fonction Bash avec des variables locales et une valeur de retour explicite.
- Distinguer le code de retour d'une fonction (`return`) de la valeur qu'elle affiche (`echo`).
- Lire une feuille d'échantillons ligne par ligne avec `while IFS=$'\t' read -r`, en évitant le piège du sous-shell.
- Brancher un traitement selon une valeur de champ avec `case`.
- Produire `resultats/synthese_par_condition.tsv` sans écrire aucun nom d'échantillon en dur dans le script.

::::::::::::::::::::::::::::::::::::::::::::::::::

Depuis l'épisode 13, vos scripts traitent les échantillons un par un, ou en
boucle avec `for` (épisode 14), avec des tests défensifs (épisode 15) et des
variables correctement protégées par des guillemets (épisode 16). Il reste
deux problèmes. D'abord, certains blocs de commandes reviennent identiques à
plusieurs endroits d'un même script — les copier-coller finissent toujours par
diverger. Ensuite, vos scripts contiennent encore des noms d'échantillons
écrits en toutes lettres, alors que la liste complète existe déjà dans
`data/tables/echantillons.tsv`. Cet épisode règle les deux : les fonctions
pour ne plus répéter de code, et la lecture d'une feuille d'échantillons pour
ne plus jamais écrire un nom d'échantillon à la main.

Préparez votre espace de travail :

```bash
mkdir -p resultats tmp scripts
```

## Pourquoi une fonction

Reprenez le script `scripts/verifier_lecture.sh` de l'épisode 15 : il teste
qu'un fichier FASTQ existe, n'est pas vide, et affiche un message. Si demain
vous devez faire ce même test pour un fichier BED, puis pour un fichier GFF3,
vous recopierez le même bloc `if [[ -f … ]]` trois fois. La règle est simple :
**dès la deuxième répétition d'un même bloc, on l'extrait en fonction.** La
première fois, un copier-coller est acceptable ; la deuxième fois, c'est un
signal qu'il faut arrêter et écrire une fonction une fois pour toutes.

Une fonction se déclare avec un nom suivi de parenthèses vides, puis un bloc
d'instructions entre accolades :

```bash
saluer() {
    echo "Bonjour depuis une fonction"
}
```

Tapez cette déclaration dans le terminal, puis appelez la fonction par son nom,
comme une commande ordinaire :

```bash
saluer
```

```output
Bonjour depuis une fonction
```

Une fonction doit être **déclarée avant d'être appelée** : Bash lit le script
de haut en bas et ne connaît une fonction qu'à partir du moment où il a lu sa
déclaration. Dans un script, la convention est donc de regrouper toutes les
fonctions en haut du fichier, juste après le shebang et les commentaires
d'en-tête, et de réserver le bas du fichier au programme principal qui les
appelle.

## Arguments d'une fonction

Une fonction reçoit ses arguments exactement comme un script reçoit les siens
(épisode 13) : `$1` pour le premier, `$2` pour le second, `$#` pour le nombre
d'arguments. Il n'y a pas de liste de paramètres nommés entre les parenthèses,
qui restent toujours vides.

```bash
compter_lignes_fastq() {
    local fichier="$1"
    local nb_lignes
    nb_lignes=$(gunzip -c "$fichier" | wc -l)
    echo "$fichier contient $((nb_lignes / 4)) lectures"
}
```

```bash
compter_lignes_fastq data/reads/ech01_R1.fastq.gz
```

```output
data/reads/ech01_R1.fastq.gz contient 500 lectures
```

::: callout

## `local` : pourquoi c'est important

Sans `local`, une variable affectée dans une fonction est une variable du
shell tout entier : elle écrase silencieusement toute variable de même nom qui
existait avant l'appel, et elle continue d'exister après le retour de la
fonction. Avec `local`, la variable n'existe que pendant l'exécution de la
fonction, et un même nom (`fichier`, `nb_lignes`, `i`…) peut être réutilisé
dans plusieurs fonctions sans qu'elles se perturbent entre elles. Déclarez
systématiquement en `local` toute variable créée à l'intérieur d'une fonction,
sauf celle que vous construisez délibérément pour la faire survivre à l'appel.

:::

## Renvoyer une valeur : `echo` contre `return`

Une fonction Bash n'a pas de valeur de retour au sens d'un langage de
programmation classique. Elle dispose de deux canaux bien distincts, et les
confondre est la source d'erreurs la plus fréquente sur les fonctions :

- **`echo` (ou `printf`)** écrit du texte sur la sortie standard. C'est ce
  qu'on récupère avec une substitution de commande `$(...)` (épisode 16), pour
  transporter une valeur — un nombre, un nom de fichier, une chaîne.
- **`return`** fixe le **code de retour** de la fonction, un entier entre 0 et
  255, récupérable dans `$?` juste après l'appel. Il ne sert jamais à
  transporter une donnée, seulement à indiquer un succès (`0`) ou un type
  d'échec (toute autre valeur), exactement comme le code de retour d'une
  commande externe vu à l'épisode 13 et testé avec `&&`/`||` à l'épisode 15.

```bash
fichier_est_lisible() {
    local fichier="$1"
    if [[ -f "$fichier" && -s "$fichier" ]]; then
        return 0
    else
        return 1
    fi
}
```

```bash
if fichier_est_lisible data/reads/ech01_R1.fastq.gz; then
    echo "ech01_R1 est lisible"
fi
```

```output
ech01_R1 est lisible
```

Remarquez qu'on appelle directement `fichier_est_lisible ...` comme condition
d'un `if`, sans passer par `$(...)` : c'est exactement le même mécanisme que
`if [[ ... ]]` ou `if grep -q ... ; then`, un `if` teste le code de retour de
n'importe quelle commande, fonction comprise. Si vous aviez besoin à la fois
d'un résultat texte et d'un code d'erreur, vous combineriez les deux canaux :
`echo` pour la valeur, `return` pour signaler si elle a pu être calculée.

::: caution

## Une fonction qui `return` un nombre n'est pas une calculette

`return 42` ne fait pas de `$?` la valeur 42 d'un calcul : c'est un code de
retour, limité à l'intervalle 0-255, et réservé aux quatre ou cinq états
qu'une commande peut signaler. Une fonction qui compte des lectures ou calcule
une moyenne doit **toujours** transmettre ce résultat par `echo` et une
substitution de commande, jamais par `return`.

:::

::::::::::::::::::::::::::::::::::::::  challenge

## Une fonction pour compter les lectures

Écrivez une fonction `compter_lectures` qui prend un chemin de fichier FASTQ
compressé en argument et **affiche** (avec `echo`) uniquement le nombre de
lectures qu'il contient, sans phrase autour. Utilisez-la pour comparer
`data/reads/ech01_R1.fastq.gz` et `data/reads/ech05_R1.fastq.gz`.

:::::::::::::::  solution

## Solution

```bash
compter_lectures() {
    local fichier="$1"
    local nb_lignes
    nb_lignes=$(gunzip -c "$fichier" | wc -l)
    echo $((nb_lignes / 4))
}
```

```bash
compter_lectures data/reads/ech01_R1.fastq.gz
compter_lectures data/reads/ech05_R1.fastq.gz
```

```output
500
500
```

La fonction affiche un entier nu, ce qui permet de la capturer directement :
`n=$(compter_lectures data/reads/ech01_R1.fastq.gz)`. Les deux échantillons
comptent le même nombre de lectures ; ech05 est dégradé en qualité, pas en
profondeur (rappel de l'épisode 15).

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

## Piloter un script par une feuille d'échantillons

Jusqu'ici, quand un script devait traiter les six échantillons, il itérait sur
des fichiers présents sur le disque (`for f in data/reads/*_R1.fastq.gz`,
épisode 14). Cela suffit pour compter des lectures, mais pas pour associer
chaque échantillon à sa condition expérimentale ou son réplicat : ces
informations n'existent pas dans le nom du fichier, elles sont dans
`data/tables/echantillons.tsv`. À partir de maintenant, c'est ce fichier — et
lui seul — qui pilote vos scripts.

```bash
cat data/tables/echantillons.tsv
```

```output
sample_id	condition	replicat	lane	fichier_R1	fichier_R2
ech01	temoin	1	L001	ech01_R1.fastq.gz	ech01_R2.fastq.gz
ech02	temoin	2	L001	ech02_R1.fastq.gz	ech02_R2.fastq.gz
ech03	temoin	3	L002	ech03_R1.fastq.gz	ech03_R2.fastq.gz
ech04	traite	1	L002	ech04_R1.fastq.gz	ech04_R2.fastq.gz
ech05	traite	2	L003	ech05_R1.fastq.gz	ech05_R2.fastq.gz
ech06	traite	3	L003	ech06_R1.fastq.gz	ech06_R2.fastq.gz
```

Six échantillons, une ligne d'en-tête, deux conditions (`temoin`, `traite`),
un réplicat et une lane par échantillon. La commande naturelle pour lire un
fichier ligne par ligne est `while read`.

## `while IFS= read -r` : lire une ligne à la fois

```bash
while IFS= read -r ligne; do
    echo "ligne lue : $ligne"
done < data/tables/echantillons.tsv
```

```output
ligne lue : sample_id	condition	replicat	lane	fichier_R1	fichier_R2
ligne lue : ech01	temoin	1	L001	ech01_R1.fastq.gz	ech01_R2.fastq.gz
ligne lue : ech02	temoin	2	L001	ech02_R1.fastq.gz	ech02_R2.fastq.gz
ligne lue : ech03	temoin	3	L002	ech03_R1.fastq.gz	ech03_R2.fastq.gz
ligne lue : ech04	traite	1	L002	ech04_R1.fastq.gz	ech04_R2.fastq.gz
ligne lue : ech05	traite	2	L003	ech05_R1.fastq.gz	ech05_R2.fastq.gz
ligne lue : ech06	traite	3	L003	ech06_R1.fastq.gz	ech06_R2.fastq.gz
```

Deux détails de cette commande méritent d'être expliqués, car les oublier
casse silencieusement la lecture :

- **`-r`** empêche `read` d'interpréter l'antislash (`\`) comme un caractère
  d'échappement. Sans lui, un chemin ou une séquence contenant `\` serait
  altéré à la lecture.
- **`IFS=`** (vide, avant `read`, sans rien après le signe égal) empêche
  `read` de supprimer les espaces et tabulations en début et fin de ligne. Le
  variable `IFS` (*Internal Field Separator*, vue à l'épisode 16) est
  normalement utilisée par `read` pour découper la ligne en champs ; la vider
  ici fait que toute la ligne est capturée telle quelle dans `ligne`, sans
  rien retrancher.

## Lire plusieurs champs à la fois

`read` peut affecter plusieurs variables en une seule ligne : donnez-lui
autant de noms de variables que vous voulez de champs, et fixez `IFS` au
séparateur du fichier — ici une tabulation, notée `$'\t'` (guillemets simples
précédés d'un `$`, une notation qui transforme `\t` en véritable caractère de
tabulation, à distinguer de `"$VAR"` vu à l'épisode 16).

```bash
while IFS=$'\t' read -r ech condition replicat lane r1 r2; do
    echo "$ech est en condition $condition, réplicat $replicat"
done < data/tables/echantillons.tsv
```

```output
sample_id est en condition condition, réplicat replicat
ech01 est en condition temoin, réplicat 1
ech02 est en condition temoin, réplicat 2
ech03 est en condition temoin, réplicat 3
ech04 est en condition traite, réplicat 1
ech05 est en condition traite, réplicat 2
ech06 est en condition traite, réplicat 3
```

La première ligne affichée est l'en-tête, traité comme une ligne de données
ordinaire : ce n'est pas ce que l'on veut. Deux solutions se combinent :
utiliser `tail -n +2` (vu à l'épisode 8 via `sed '$d'`... non, ici il s'agit
de sauter le début, pas la fin) est en réalité couvert par `sed` de l'épisode
11 avec une plage d'adresses, ou plus simplement en testant le contenu du
premier champ à l'intérieur de la boucle :

```bash
while IFS=$'\t' read -r ech condition replicat lane r1 r2; do
    if [[ "$ech" == "sample_id" ]]; then
        continue
    fi
    echo "$ech est en condition $condition, réplicat $replicat"
done < data/tables/echantillons.tsv
```

```output
ech01 est en condition temoin, réplicat 1
ech02 est en condition temoin, réplicat 2
ech03 est en condition temoin, réplicat 3
ech04 est en condition traite, réplicat 1
ech05 est en condition traite, réplicat 2
ech06 est en condition traite, réplicat 3
```

`continue` interrompt l'itération courante de la boucle et passe directement
à la ligne suivante, sans exécuter le reste du corps.

## Le piège du tube : les variables qui disparaissent

Une manière tentante d'écarter l'en-tête est de le retirer avant la boucle
avec un tube, en s'appuyant sur `grep -v` (épisode 7) :

```bash
total=0
grep -v '^sample_id' data/tables/echantillons.tsv | while IFS=$'\t' read -r ech condition replicat lane r1 r2; do
    total=$((total + 1))
    echo "compteur dans la boucle : $total"
done
echo "compteur après la boucle : $total"
```

```output
compteur dans la boucle : 1
compteur dans la boucle : 2
compteur dans la boucle : 3
compteur dans la boucle : 4
compteur dans la boucle : 5
compteur dans la boucle : 6
compteur après la boucle : 0
```

Le compteur progresse bien à l'intérieur de la boucle, puis retombe à `0`
juste après. Ce n'est pas un bogue de Bash mais une conséquence directe du
tube (épisode 6) : chaque commande d'un tube s'exécute dans son propre
sous-shell, une copie du shell qui hérite des variables mais ne peut jamais
transmettre ses propres modifications au shell parent. La boucle `while`
placée après le `|` tourne dans ce sous-shell ; tout ce qu'elle modifie
(`total`, ou n'importe quelle autre variable) est perdu dès que le sous-shell
se termine.

::: caution

## `commande | while read` perd toujours ses variables

Toute boucle `while read` alimentée par un tube s'exécute dans un sous-shell.
Les variables qu'elle modifie ne survivent pas à la fin de la boucle. C'est
un piège classique et silencieux : aucun message d'erreur, juste une variable
revenue à sa valeur initiale.

:::

La solution est la redirection `done < fichier` déjà utilisée plus haut : elle
fait lire le fichier par le `while` lui-même, sans tube et donc sans
sous-shell, si bien que les variables modifiées dans la boucle restent
valables après elle.

```bash
total=0
while IFS=$'\t' read -r ech condition replicat lane r1 r2; do
    if [[ "$ech" == "sample_id" ]]; then
        continue
    fi
    total=$((total + 1))
done < data/tables/echantillons.tsv
echo "compteur après la boucle : $total"
```

```output
compteur après la boucle : 6
```

Cette fois le compteur vaut bien 6 après la boucle : la règle à retenir est
d'écrire systématiquement `done < fichier` pour lire un fichier, et de
réserver le tube aux cas où l'on n'a besoin d'aucune variable après la boucle.

::::::::::::::::::::::::::::::::::::::::::::::::::  challenge

## Compter les échantillons par condition

Sans utiliser `awk` ni `sort | uniq -c` (épisodes 9 et 8), comptez le nombre
d'échantillons de condition `temoin` et de condition `traite` en lisant
`data/tables/echantillons.tsv` avec `while IFS=$'\t' read -r ... ; done <
fichier`.

:::::::::::::::  solution

## Solution

```bash
nb_temoin=0
nb_traite=0
while IFS=$'\t' read -r ech condition replicat lane r1 r2; do
    if [[ "$ech" == "sample_id" ]]; then
        continue
    fi
    if [[ "$condition" == "temoin" ]]; then
        nb_temoin=$((nb_temoin + 1))
    elif [[ "$condition" == "traite" ]]; then
        nb_traite=$((nb_traite + 1))
    fi
done < data/tables/echantillons.tsv
echo "temoin : $nb_temoin, traite : $nb_traite"
```

```output
temoin : 3, traite : 3
```

La redirection `done < data/tables/echantillons.tsv` est indispensable :
sans elle (avec un tube à la place), `nb_temoin` et `nb_traite` seraient
revenus à 0 après la boucle, pour la raison vue plus haut.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

## `case` pour brancher selon un champ

`if`/`elif`/`else` (épisode 15) fonctionne pour deux conditions, mais devient
vite lourd dès qu'il faut tester une même variable contre plusieurs valeurs
possibles. `case` est fait pour cela : il compare une valeur à une série de
motifs et exécute le premier bloc qui correspond, jusqu'au `;;` qui le
termine.

```bash
decrire_condition() {
    local condition="$1"
    case "$condition" in
        temoin)
            echo "groupe de référence"
            ;;
        traite)
            echo "groupe expérimental"
            ;;
        *)
            echo "condition inconnue : $condition"
            ;;
    esac
}
```

```bash
decrire_condition temoin
decrire_condition traite
decrire_condition inconnue
```

```output
groupe de référence
groupe expérimental
condition inconnue : inconnue
```

Le motif `*)` joue le rôle du `else` final : il capture tout ce qui n'a
correspondu à aucun motif précédent. C'est une sécurité utile pour repérer une
valeur inattendue dans une feuille d'échantillons, plutôt que de la laisser
passer silencieusement.

## Assembler : la synthèse par condition, pilotée par la feuille d'échantillons

Il est temps de combiner fonctions, lecture de la feuille d'échantillons et
`case` dans un seul script, qui ne contient plus aucun nom d'échantillon écrit
en dur. Le script va, pour chaque échantillon de
`data/tables/echantillons.tsv`, compter ses lectures R1, puis produire une
ligne de synthèse par condition dans
`resultats/synthese_par_condition.tsv`.

Créez le script avec `nano` :

<!-- verif: ignore -->

```bash
nano scripts/synthese_par_condition.sh
```

<!-- verif: ignore -->

Saisissez ce contenu :

<!-- verif: fichier scripts/synthese_par_condition.sh -->

```bash
#!/usr/bin/env bash
set -euo pipefail

# Compte les lectures d'un fichier FASTQ compresse.
compter_lectures() {
    local fichier="$1"
    local nb_lignes
    nb_lignes=$(gunzip -c "$fichier" | wc -l)
    echo $((nb_lignes / 4))
}

# Ajoute le nombre de lectures d'un echantillon au total de sa condition.
# Les totaux sont transmis par variable globale (pas de local), car ils
# doivent survivre a l'appel de fonction.
cumuler_par_condition() {
    local condition="$1"
    local nb_lectures="$2"
    case "$condition" in
        temoin)
            total_temoin=$((total_temoin + nb_lectures))
            n_temoin=$((n_temoin + 1))
            ;;
        traite)
            total_traite=$((total_traite + nb_lectures))
            n_traite=$((n_traite + 1))
            ;;
        *)
            echo "condition inconnue ignoree : $condition" >&2
            ;;
    esac
}

feuille="data/tables/echantillons.tsv"
repertoire_reads="data/reads"

total_temoin=0
n_temoin=0
total_traite=0
n_traite=0

while IFS=$'\t' read -r ech condition replicat lane fichier_r1 fichier_r2; do
    if [[ "$ech" == "sample_id" ]]; then
        continue
    fi

    chemin_r1="$repertoire_reads/$fichier_r1"
    if [[ ! -s "$chemin_r1" ]]; then
        echo "fichier manquant ou vide, echantillon ignore : $chemin_r1" >&2
        continue
    fi

    nb_lectures=$(compter_lectures "$chemin_r1")
    cumuler_par_condition "$condition" "$nb_lectures"
done < "$feuille"

{
    printf 'condition\tnb_echantillons\ttotal_lectures_R1\n'
    printf 'temoin\t%d\t%d\n' "$n_temoin" "$total_temoin"
    printf 'traite\t%d\t%d\n' "$n_traite" "$total_traite"
} > resultats/synthese_par_condition.tsv

echo "synthese ecrite dans resultats/synthese_par_condition.tsv"
```

Enregistrez et quittez, puis rendez le script exécutable :

```bash
chmod +x scripts/synthese_par_condition.sh
```

<!-- verif-setup:
mkdir -p scripts
cat > scripts/synthese_par_condition.sh <<'FIN'
#!/usr/bin/env bash
set -euo pipefail

# Compte les lectures d'un fichier FASTQ compresse.
compter_lectures() {
    local fichier="$1"
    local nb_lignes
    nb_lignes=$(gunzip -c "$fichier" | wc -l)
    echo $((nb_lignes / 4))
}

# Ajoute le nombre de lectures d'un echantillon au total de sa condition.
# Les totaux sont transmis par variable globale (pas de local), car ils
# doivent survivre a l'appel de fonction.
cumuler_par_condition() {
    local condition="$1"
    local nb_lectures="$2"
    case "$condition" in
        temoin)
            total_temoin=$((total_temoin + nb_lectures))
            n_temoin=$((n_temoin + 1))
            ;;
        traite)
            total_traite=$((total_traite + nb_lectures))
            n_traite=$((n_traite + 1))
            ;;
        *)
            echo "condition inconnue ignoree : $condition" >&2
            ;;
    esac
}

feuille="data/tables/echantillons.tsv"
repertoire_reads="data/reads"

total_temoin=0
n_temoin=0
total_traite=0
n_traite=0

while IFS=$'\t' read -r ech condition replicat lane fichier_r1 fichier_r2; do
    if [[ "$ech" == "sample_id" ]]; then
        continue
    fi

    chemin_r1="$repertoire_reads/$fichier_r1"
    if [[ ! -s "$chemin_r1" ]]; then
        echo "fichier manquant ou vide, echantillon ignore : $chemin_r1" >&2
        continue
    fi

    nb_lectures=$(compter_lectures "$chemin_r1")
    cumuler_par_condition "$condition" "$nb_lectures"
done < "$feuille"

{
    printf 'condition\tnb_echantillons\ttotal_lectures_R1\n'
    printf 'temoin\t%d\t%d\n' "$n_temoin" "$total_temoin"
    printf 'traite\t%d\t%d\n' "$n_traite" "$total_traite"
} > resultats/synthese_par_condition.tsv

echo "synthese ecrite dans resultats/synthese_par_condition.tsv"
FIN
chmod +x scripts/synthese_par_condition.sh
-->

Exécutez-le :

```bash
./scripts/synthese_par_condition.sh
```

```output
synthese ecrite dans resultats/synthese_par_condition.tsv
```

```bash
cat resultats/synthese_par_condition.tsv
```

```output
condition	nb_echantillons	total_lectures_R1
temoin	3	1500
traite	3	1500
```

Remarquez ce qui a disparu de ce script par rapport à ceux des épisodes
précédents : aucun `ech01`, `ech02`, ni aucun nom de fichier FASTQ n'y est
écrit en dur. La seule source de vérité est
`data/tables/echantillons.tsv` ; ajouter un septième échantillon à ce
fichier suffirait à ce que le script le traite, sans modifier une seule ligne
de code.

::: callout

## Ce que vous venez de refaire, en plus petit

Un script qui lit une feuille d'échantillons, appelle une fonction pour
chaque ligne, et agrège des résultats selon une catégorie, c'est exactement
le principe sur lequel repose un gestionnaire de flux de travaux
(*workflow manager*) tel que Nextflow ou Snakemake — en plus robuste et en
plus lisible pour de gros volumes d'échantillons. La seconde formation de ce
programme y est consacrée.

:::

::::::::::::::::::::::::::::::::::::::::::::::::::  challenge

## Ajouter le nombre de lectures R2

Modifiez `scripts/synthese_par_condition.sh` pour que la fonction
`compter_lectures` soit aussi appelée sur `fichier_r2`, et que le total de
lectures R2 par condition s'ajoute comme quatrième colonne du fichier de
sortie. Ne modifiez rien d'autre que ce qui est nécessaire.

:::::::::::::::  solution

## Solution

Il faut étendre `cumuler_par_condition` pour qu'elle reçoive et cumule un
deuxième nombre de lectures, ajouter les variables de total R2, et ajouter la
colonne dans la sortie finale. Voici les parties modifiées :

```bash
cumuler_par_condition() {
    local condition="$1"
    local nb_lectures_r1="$2"
    local nb_lectures_r2="$3"
    case "$condition" in
        temoin)
            total_temoin=$((total_temoin + nb_lectures_r1))
            total_temoin_r2=$((total_temoin_r2 + nb_lectures_r2))
            n_temoin=$((n_temoin + 1))
            ;;
        traite)
            total_traite=$((total_traite + nb_lectures_r1))
            total_traite_r2=$((total_traite_r2 + nb_lectures_r2))
            n_traite=$((n_traite + 1))
            ;;
        *)
            echo "condition inconnue ignoree : $condition" >&2
            ;;
    esac
}
```

Dans la boucle, on calcule aussi `nb_lectures_r2` et on l'ajoute à l'appel :

```bash
    nb_lectures=$(compter_lectures "$chemin_r1")
    chemin_r2="$repertoire_reads/$fichier_r2"
    nb_lectures_r2=$(compter_lectures "$chemin_r2")
    cumuler_par_condition "$condition" "$nb_lectures" "$nb_lectures_r2"
```

et les nouvelles variables `total_temoin_r2` et `total_traite_r2` doivent être
initialisées à `0` au même endroit que les autres totaux. Cet exercice montre
pourquoi extraire `compter_lectures` en fonction était utile : il suffit de
l'appeler une seconde fois avec un autre argument, sans dupliquer son corps.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::  challenge

## Ce script contient une erreur, laquelle

Une collègue vous montre cette fonction, censée renvoyer le nombre de
lectures d'un échantillon pour qu'on le stocke dans une variable :

```bash
compter_lectures_bogue() {
    local fichier="$1"
    local nb_lignes
    nb_lignes=$(gunzip -c "$fichier" | wc -l)
    return $((nb_lignes / 4))
}
```

```bash
n=$(compter_lectures_bogue data/reads/ech02_R1.fastq.gz)
echo "lectures : $n"
```

Que va afficher ce dernier `echo`, et pourquoi ce n'est pas 500 ?

:::::::::::::::  solution

## Solution

```output
lectures : 
```

`n` sera vide. La fonction utilise `return` au lieu d'`echo` : elle ne place
rien sur la sortie standard, donc la substitution de commande `$(...)` ne
capture rien. De plus, même si l'auteur avait voulu récupérer la valeur via
`$?` juste après l'appel, `return` tronque toute valeur à l'intervalle 0-255 :
avec 500 lectures ici, `$?` vaudrait `500 % 256`, soit `244`, une valeur
fausse et silencieusement incorrecte. La correction est de remplacer `return`
par `echo` dans le corps de la fonction, comme dans `compter_lectures` plus
haut.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

## Ce qu'il faut retenir avant l'épisode suivant

L'épisode suivant reprend `find` et `xargs` pour traiter en parallèle les
fichiers désordonnés de `data/brut_desordre/` ; les fonctions écrites ici
pourront être réutilisées telles quelles à l'intérieur d'un `-exec` ou d'un
appel `xargs -I`.

:::::::::::::::::::::::::::::::::::::::: keypoints

- Une fonction se déclare avec `nom() { ... }` et se place avant le code qui l'appelle, généralement en haut du script.
- Extrayez une fonction dès qu'un même bloc de commandes apparaît une deuxième fois.
- `local` confine une variable à sa fonction ; sans lui, elle modifie le shell entier.
- `echo` transporte une valeur via `$(...)` ; `return` ne transporte qu'un code de retour entier entre 0 et 255, récupéré dans `$?`.
- `while IFS= read -r ligne; do ... done < fichier` lit un fichier ligne par ligne sans en altérer les espaces ni les antislashs.
- `IFS=$'\t' read -r a b c` découpe une ligne en plusieurs champs selon la tabulation.
- Une boucle `while read` alimentée par un tube tourne dans un sous-shell : ses variables sont perdues après elle. Utilisez `done < fichier`.
- `case "$valeur" in motif) ... ;; esac` remplace une longue chaîne de `if`/`elif` pour brancher selon un champ, avec `*)` comme filet de sécurité.
- Un script piloté par `data/tables/echantillons.tsv` ne contient plus aucun nom d'échantillon écrit en dur.

::::::::::::::::::::::::::::::::::::::::::::::::::
