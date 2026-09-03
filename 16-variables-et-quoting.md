---
title: "Variables, guillemets et substitution de commandes"
teaching: 30
exercises: 20
---

:::::::::::::::::::::::::::::::::::::::  questions

- Comment garder une valeur en mémoire dans un script pour la réutiliser ?
- Pourquoi mon script échoue-t-il dès qu'un nom de fichier contient un espace ?
- Comment récupérer dans une variable le résultat d'une commande ?
- Comment donner une valeur par défaut à une variable qui pourrait être vide ?

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::: objectives

- Créer et utiliser une variable de shell sans espace parasite autour du `=`.
- Protéger une variable avec des guillemets doubles pour éviter le découpage
  en mots et le développement des jokers.
- Distinguer l'effet des apostrophes, des guillemets doubles et de l'absence
  de guillemets sur `$`, `*`, les espaces et les caractères spéciaux.
- Récupérer la sortie d'une commande dans une variable avec `$(...)`.
- Fournir une valeur par défaut ou interrompre un script avec `${VAR:-defaut}`
  et `${VAR:?message}`.
- Extraire une extension ou un nom de fichier avec les manipulations de
  chaînes portables (`%`, `%%`, `#`, `##`).
- Distinguer une variable de shell d'une variable d'environnement exportée.

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::: prereq

Cet épisode suppose que vous savez écrire un script avec un shebang, le rendre
exécutable, et lui passer des arguments (`$1`, `$@`, `$#`), vu à l'épisode 13.
Il suppose aussi les structures `if`/`test` de l'épisode 15.

::::::::::::::::::::::::::::::::::::::::::::::::::

## Le piège qui attend tout le monde

Depuis l'épisode 13, vous écrivez des scripts qui utilisent `$1`, `$2`, `$@`.
Ce sont déjà des variables. Cet épisode explique comment en créer vous-même,
et surtout comment s'en servir sans se faire piéger — parce que le piège est
systématique, silencieux, et il attend précisément le jour où vous traiterez
un fichier dont le nom contient un espace.

Justement, `data/brut_desordre/` en contient plusieurs. Commençons par
regarder ce qui s'y trouve.

<!-- verif: ordre-libre -->
```bash
mkdir -p resultats tmp scripts
ls -1 data/brut_desordre/
```

```output
Ech04_final_VRAIMENT_final.fastq
Echantillon 01 - Run mars.fastq
RESUME Manip.txt
ech 03 (copie).fastq
ech05.resultats.fastq
ech06 -- a refaire.fastq
echantillon_02.FASTQ
notes du 12 mars.txt
```

Des espaces, des majuscules incohérentes, des parenthèses, un double tiret.
Ce répertoire porte bien son nom : c'est exactement ce que produit un
séquenceur, un collègue pressé, ou vous-même un vendredi soir. Nous allons y
revenir tout au long de l'épisode.

## Créer une variable : la règle qui ne se discute pas

Une variable de shell se crée en écrivant son nom, un signe `=`, et une
valeur, **sans aucun espace** autour du `=`.

```bash
ECHANTILLON=ech01
echo $ECHANTILLON
```

```output
ech01
```

Si vous mettez un espace, le shell ne voit plus une affectation mais une
commande nommée `ECHANTILLON` à laquelle vous passez les arguments `=` et
`ech01` :

<!-- verif: ignore -->
```bash
ECHANTILLON = ech01
```

```error
```

Retenez cette explication plutôt que la règle brute : le shell interprète
`ECHANTILLON = ech01` comme trois mots séparés, exactement comme il lirait
`ls -l -a`. C'est parce que le shell découpe une ligne en mots séparés par des
espaces *avant* de se demander si le premier mot est une affectation. Sans
espace, `ECHANTILLON=ech01` est un seul mot, reconnu comme une affectation.

Par convention, cette leçon écrit les noms de variables que vous créez
vous-même en majuscules, pour les distinguer visuellement des commandes et des
noms de fichiers. Ce n'est qu'une convention : le shell accepterait des
minuscules.

::::::::::::::::::::::::::::::::::::::::: callout

## `$NOM` lit, `NOM=` écrit

On retrouve la même dissymétrie qu'avec `$1` depuis l'épisode 13 : on écrit la
variable sans `$` (`NOM=valeur`), on la lit avec `$` (`echo $NOM`). Le `$` dit
au shell « remplace ceci par la valeur de la variable » ; sans lui, `NOM` est
juste un nom.

::::::::::::::::::::::::::::::::::::::::::::::::::

## Le problème : l'absence de guillemets a deux conséquences

Reprenons `$ECHANTILLON`, mais avec une valeur qui contient un espace — comme
le premier fichier de `brut_desordre/`.

<!-- verif: ignore -->
```bash
FICHIER=data/brut_desordre/Echantillon 01 - Run mars.fastq
```

```error
bash: -: command not found
```

L'affectation elle-même échoue déjà : le shell découpe la ligne en mots dès
qu'il rencontre un espace non protégé, y compris à droite du `=`. Pour
affecter une valeur contenant des espaces, il faut la mettre entre guillemets
doubles au moment de l'affectation :

```bash
FICHIER="data/brut_desordre/Echantillon 01 - Run mars.fastq"
echo "$FICHIER"
```

```output
data/brut_desordre/Echantillon 01 - Run mars.fastq
```

Maintenant que la variable contient la bonne valeur, regardons ce qui se
passe si on l'utilise **sans** guillemets :

<!-- verif: ignore -->
```bash
wc -l $FICHIER
```

```error
       0
```

C'est la première conséquence de l'absence de guillemets : le **découpage en
mots** (*word splitting*). Quand le shell développe `$FICHIER` sans
guillemets, il ne remet pas la valeur entre guillemets à votre place : il la
traite comme si vous aviez tapé les caractères directement sur la ligne de
commande, espaces compris, et découpe donc en cinq arguments distincts. `wc`
reçoit cinq noms de fichiers qui n'existent pas, plutôt qu'un seul nom
correct.

Avec les guillemets doubles, la valeur de la variable est transmise comme un
bloc unique, quel que soit son contenu :

```bash
wc -l "$FICHIER"
```

```output
     100 data/brut_desordre/Echantillon 01 - Run mars.fastq
```

Cette ligne résume l'épisode entier. `"$FICHIER"` avec guillemets doubles :
un seul argument, toujours. `$FICHIER` sans guillemets : découpé en autant de
mots qu'il y a d'espaces, avec toutes les conséquences que cela implique.

::::::::::::::::::::::::::::::::::::::::: caution

## `rm $FICHIER` quand `FICHIER` est vide

Le découpage en mots devient dangereux dès qu'une variable peut être vide.
Si `FICHIER` n'a jamais été affectée, ou si une commande précédente a échoué
sans que vous l'ayez vérifié (rappelez-vous `set -e` de l'épisode 15),
`rm $FICHIER` sans guillemets et sans valeur ne développe littéralement rien :
la ligne devient `rm`, sans argument. Cela semble inoffensif, mais dans un
script qui construit un chemin avec plusieurs variables, le même mécanisme
peut transformer `rm "$REP/$FICHIER"` en un `rm -rf $REP/*` accidentel si
`FICHIER` est vide et que le reste de la ligne contient un joker. La leçon à
retenir : une variable non protégée qui se trouve vide au mauvais moment ne
provoque pas une erreur visible, elle change le sens de la commande. Guillemets
partout, et `${FICHIER:?message}` — plus loin dans cet épisode — quand une
variable ne doit jamais être vide.

::::::::::::::::::::::::::::::::::::::::::::::::::

Il existe une seconde conséquence de l'absence de guillemets, plus discrète :
le **développement des jokers** (*wildcard expansion*, épisode 3). Une
variable non protégée qui contient un caractère `*` ou `?` est développée par
le shell comme un joker si elle se trouve dans un répertoire où elle
correspond à des fichiers.

<!-- verif: ordre-libre -->
```bash
MOTIF="*.fastq"
cd data/brut_desordre
echo $MOTIF
cd ../..
```

```output
Ech04_final_VRAIMENT_final.fastq Echantillon 01 - Run mars.fastq ech 03 (copie).fastq ech05.resultats.fastq ech06 -- a refaire.fastq
```

`$MOTIF` sans guillemets ne s'affiche pas comme le texte `*.fastq` : le shell
le développe en la liste des fichiers du répertoire courant qui correspondent
à ce motif, exactement comme il l'aurait fait si vous aviez tapé `*.fastq`
directement. Avec des guillemets doubles, la variable reste un texte littéral :

```bash
cd data/brut_desordre
echo "$MOTIF"
cd ../..
```

```output
*.fastq
```

Découpage en mots et développement des jokers sont deux mécanismes distincts,
mais un seul remède : les guillemets doubles.

## Le tableau à retenir : apostrophes contre guillemets doubles

Le shell offre deux façons de citer du texte, et elles ne se comportent pas du
tout de la même manière face aux caractères spéciaux.

| Caractère | Entre apostrophes `'...'` | Entre guillemets doubles `"..."` |
|---|---|---|
| Espace | conservé littéralement | conservé littéralement |
| `$VAR` | affiché tel quel, **non développé** | remplacé par la valeur de `VAR` |
| `*` | affiché tel quel, **non développé** | affiché tel quel, **non développé** |
| `` ` `` (substitution de commande) | affiché tel quel, **non exécutée** | exécutée et remplacée par le résultat |
| Apostrophe `'` | ne peut pas apparaître dans le texte | s'écrit normalement |
| Guillemet double `"` | s'écrit normalement | doit être protégé par `\"` |

```bash
VILLE=Lyon
echo 'Echantillon preleve a $VILLE, cout : *.fastq'
echo "Echantillon preleve a $VILLE, cout : *.fastq"
```

```output
Echantillon preleve a $VILLE, cout : *.fastq
Echantillon preleve a Lyon, cout : *.fastq
```

Notez que même entre guillemets doubles, `*.fastq` reste littéral : les
guillemets doubles empêchent le développement des jokers, ils n'empêchent que
le développement des variables et des substitutions de commandes. C'est
exactement le comportement recherché la plupart du temps : on veut que `$VAR`
soit remplacé, mais on ne veut jamais qu'un `*` tapé par erreur ou présent
dans un nom de variable se transforme en liste de fichiers.

Règle pratique : les apostrophes servent à afficher du texte fixe, souvent
pour illustrer une syntaxe ou écrire un message qui ne doit rien interpréter.
Les guillemets doubles servent à tout le reste — c'est-à-dire, dans cette
leçon, à peu près partout où une variable est utilisée.

## `${VAR}` : quand l'accolade devient nécessaire

`$VAR` et `${VAR}` désignent la même variable. La forme avec accolades sert à
délimiter précisément où le nom de la variable s'arrête, ce qui devient
indispensable dès qu'un texte suit immédiatement sans séparateur.

```bash
ECH=ech01
echo "Fichier : $ECH_R1.fastq.gz"
```

```output
Fichier : .fastq.gz
```

Le shell a cherché une variable nommée `ECH_R1`, qui n'existe pas et se
développe donc en une chaîne vide — `_` est un caractère valide dans un nom de
variable, donc `$ECH_R1` est lu comme un seul nom. Avec des accolades, la
limite est explicite :

```bash
echo "Fichier : ${ECH}_R1.fastq.gz"
```

```output
Fichier : ech01_R1.fastq.gz
```

Dans cette leçon, prenez l'habitude d'utiliser `${VAR}` chaque fois qu'un
caractère alphanumérique ou un tiret bas suit immédiatement la variable dans
la même chaîne. Devant un espace, un `/` ou un `.`, les accolades ne changent
rien et restent facultatives — `$ECH/R1` et `${ECH}/R1` sont strictement
équivalents parce que `/` ne peut pas faire partie d'un nom de variable.

## Récupérer la sortie d'une commande : `$(...)`

Jusqu'ici, les variables ont reçu des valeurs écrites à la main. On peut aussi
leur affecter le résultat d'une commande, avec la substitution de commandes
`$(...)`.

```bash
NB_LECTURES=$(gunzip -c data/reads/ech01_R1.fastq.gz | wc -l)
echo "Nombre de lignes : $NB_LECTURES"
```

```output
Nombre de lignes : 2000
```

Le shell exécute la commande entre parenthèses, capture ce qu'elle écrit sur
la sortie standard, puis remplace `$(...)` par ce texte — exactement comme il
remplacerait `$VAR` par une valeur. Vous pouvez donc écrire directement :

```bash
echo "Le fichier ech01_R1 contient $(gunzip -c data/reads/ech01_R1.fastq.gz | wc -l) lignes"
```

```output
Le fichier ech01_R1 contient 2000 lignes
```

Une syntaxe plus ancienne existe, avec des accents graves : `` `commande` ``.
Évitez-la. Elle ne s'imbrique pas proprement — chaque niveau d'accents graves
doit être protégé par des antislashs, ce qui devient illisible — alors que
`$(...)` s'imbrique sans effort :

```bash
EXTENSION_GZ=$(basename "$(ls data/reads/ech01_R1.fastq.gz)")
echo "$EXTENSION_GZ"
```

```output
ech01_R1.fastq.gz
```

Ici, `$(ls data/reads/ech01_R1.fastq.gz)` est évalué en premier et son
résultat sert d'argument à `basename`, lui-même dans un `$(...)` externe. Deux
substitutions de commandes imbriquées, sans confusion possible sur les
limites — ce que les accents graves ne permettent pas.

::::::::::::::::::::::::::::::::::::::::: callout

## Toujours entre guillemets, même une substitution de commande

`$(...)` est développé exactement comme `$VAR` : sans guillemets, son
résultat subit le même découpage en mots et le même développement des jokers
si le résultat contient des espaces ou des caractères `*`. Écrivez
`"$(commande)"`, pas `$(commande)`, par réflexe.

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  challenge

## Défi d'imitation : compter les gènes de l'annotation

Affectez à une variable `NB_GENES` le nombre de lignes de type `gene` dans
`data/genome/annotation.gff3` (colonne 3), en utilisant `$(...)`, puis
affichez un message complet avec `echo`.

:::::::::::::::  solution

## Solution

```bash
NB_GENES=$(awk -F'\t' '$3 == "gene"' data/genome/annotation.gff3 | wc -l)
echo "L'annotation contient $NB_GENES genes"
```

```output
L'annotation contient 128 genes
```

`$(...)` capture la sortie du tube `awk | wc -l`, c'est-à-dire un nombre suivi
d'un saut de ligne ; le saut de ligne final est retiré automatiquement par la
substitution de commandes, ce qui permet d'insérer directement le résultat
dans une phrase.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

## Valeurs par défaut et variables obligatoires

Un script robuste (épisode 15) doit anticiper le cas où une variable attendue
est vide ou n'existe pas. `${VAR:-defaut}` fournit une valeur de repli sans
modifier la variable :

```bash
unset DOSSIER_SORTIE
echo "On ecrit dans : ${DOSSIER_SORTIE:-resultats}"
```

```output
On ecrit dans : resultats
```

Si `DOSSIER_SORTIE` est vide ou absente, l'expression entière se développe en
`resultats` ; si elle est définie, sa valeur est utilisée normalement. C'est
la manière portable d'écrire un script qui accepte un paramètre optionnel :

<!-- verif: exec-seulement -->
```bash
REPERTOIRE="${1:-resultats}"
echo "Sortie dans : $REPERTOIRE"
```

```output
Sortie dans : resultats
```

À l'inverse, `${VAR:?message}` interrompt le script immédiatement, avec le
message donné, si la variable est vide ou absente. C'est le bon choix quand
une valeur manquante rendrait la suite du script dangereuse plutôt que
simplement incomplète — exactement le risque décrit dans l'encadré `caution`
sur `rm $FICHIER` plus haut.

<!-- verif: ignore -->
```bash
unset ECHANTILLON_CIBLE
echo "${ECHANTILLON_CIBLE:?variable ECHANTILLON_CIBLE non definie, arret}"
```

```error
bash: ECHANTILLON_CIBLE: variable ECHANTILLON_CIBLE non definie, arret
```

Utilisé en tête de script, `${FICHIER:?fichier non specifie}` remplace un
`if [ -z "$FICHIER" ]; then echo "erreur" >&2; exit 1; fi` complet par une
seule ligne, avec le même effet protecteur.

## `${#VAR}` : la longueur d'une chaîne

`${#VAR}` se développe en le nombre de caractères contenus dans `VAR`, ce qui
est utile pour valider une entrée avant de s'en servir.

```bash
IDENTIFIANT=ech01
echo "Longueur de l'identifiant : ${#IDENTIFIANT}"
```

```output
Longueur de l'identifiant : 5
```

## Manipuler des chaînes sans dépendre d'un outil externe

Le shell sait retirer un préfixe ou un suffixe d'une variable, directement
dans le développement de paramètres, sans lancer `sed` ni `cut`. C'est
portable — Bash 3.2 de macOS le comprend aussi bien que Bash 5 — et cela évite
un tube entier pour une opération simple. Il y a quatre opérateurs, qui se
distinguent par la direction (`%` retire à la fin, `#` retire au début) et la
gourmandise (un seul caractère retire le plus court motif, deux caractères le
plus long).

```bash
F=ech04_R1.fastq.gz
echo "${F%.gz}"
echo "${F%%.*}"
```

```output
ech04_R1.fastq
ech04_R1
```

`${F%.gz}` retire le plus court suffixe qui correspond au motif `.gz` : on
obtient le nom sans l'extension de compression. `${F%%.*}` retire le plus
long suffixe qui correspond à `.*` — c'est-à-dire tout ce qui suit le premier
point — et il ne reste que le nom de base sans aucune extension.

```bash
CHEMIN=data/reads/ech04_R1.fastq.gz
echo "${CHEMIN#*/}"
echo "${CHEMIN##*/}"
```

```output
reads/ech04_R1.fastq.gz
ech04_R1.fastq.gz
```

`${CHEMIN#*/}` retire le plus court préfixe qui correspond à `*/` : le
premier répertoire disparaît. `${CHEMIN##*/}` retire le plus long préfixe
correspondant à `*/` : tous les répertoires disparaissent, il ne reste que le
nom de fichier — c'est l'équivalent de `basename` écrit sans lancer de
commande externe.

| Opérateur | Direction | Gourmandise | Effet sur `data/reads/ech04_R1.fastq.gz` |
|---|---|---|---|
| `${F%.gz}` | depuis la fin | le plus court | `data/reads/ech04_R1.fastq` |
| `${F%%.*}` | depuis la fin | le plus long | `data/reads/ech04_R1` |
| `${F#*/}` | depuis le début | le plus court | `reads/ech04_R1.fastq.gz` |
| `${F##*/}` | depuis le début | le plus long | `ech04_R1.fastq.gz` |

Retenez le symbole plutôt que l'exemple : `#` est en haut à gauche du clavier,
il retire par la gauche (le début) ; `%` est à droite, il retire par la
droite (la fin). Doubler le symbole rend l'opérateur gourmand.

:::::::::::::::::::::::::::::::::::::::  challenge

## Défi de transfert : un nom de sortie propre

À partir de la variable `F=data/reads/ech03_R1.fastq.gz`, construisez, sans
`basename` ni `sed`, le nom `ech03_R1` seul, puis affichez le chemin d'un
fichier de sortie `resultats/ech03_R1_compte.txt`.

:::::::::::::::  solution

## Solution

```bash
F=data/reads/ech03_R1.fastq.gz
NOM="${F##*/}"
NOM="${NOM%%.*}"
echo "$NOM"
echo "resultats/${NOM}_compte.txt"
```

```output
ech03_R1
resultats/ech03_R1_compte.txt
```

`${F##*/}` retire d'abord tous les répertoires, il reste `ech03_R1.fastq.gz`.
`${NOM%%.*}` retire ensuite tout ce qui suit le premier point, il reste
`ech03_R1`. Les accolades autour de `${NOM}` dans la dernière ligne sont
nécessaires : sans elles, le shell chercherait une variable `NOM_compte`.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

## Défi d'interprétation : pourquoi ce script échoue-t-il

Le fichier `data/brut_desordre/Echantillon 01 - Run mars.fastq` porte un nom
particulièrement chargé : espaces, majuscule, tiret. Le script suivant est
censé compter ses lignes, mais il échoue. Créons-le tel quel :

<!-- verif-setup:
mkdir -p scripts
cat > scripts/compter_brut.sh <<'FIN'
#!/usr/bin/env bash
FICHIER=$1
wc -l $FICHIER
FIN
chmod +x scripts/compter_brut.sh
-->

```bash
cat scripts/compter_brut.sh
```

```output
#!/usr/bin/env bash
FICHIER=$1
wc -l $FICHIER
```

<!-- verif: ignore -->
```bash
./scripts/compter_brut.sh "data/brut_desordre/Echantillon 01 - Run mars.fastq"
```

```error
wc: data/brut_desordre/Echantillon: No such file or directory
wc: 01: No such file or directory
wc: -: No such file or directory
wc: Run: No such file or directory
wc: mars.fastq: No such file or directory
```

L'appel du script protège pourtant bien l'argument avec des guillemets
doubles. L'erreur n'est donc pas là.

:::::::::::::::::::::::::::::::::::::::  challenge

## Défi d'interprétation : où est le problème, et comment le corriger

Expliquez pourquoi `wc` reçoit cinq noms de fichiers différents alors que
l'argument passé au script était correctement protégé, puis corrigez
`scripts/compter_brut.sh` pour qu'il fonctionne sur ce fichier.

:::::::::::::::  solution

## Solution

L'argument arrive intact dans `$1` — les guillemets à l'appel garantissent
cela. Mais **à l'intérieur** du script, deux lignes utilisent des variables
sans guillemets : `FICHIER=$1` (l'affectation fonctionne même sans guillemets
tant qu'il n'y a qu'un seul mot à droite, ici transmis tel quel par `$1`) puis
surtout `wc -l $FICHIER`. C'est cette seconde ligne qui découpe la valeur en
mots au moment où `wc` reçoit ses arguments — le fait que la valeur ait
transité intacte jusqu'ici ne protège pas son utilisation finale. Chaque
lecture de variable doit être protégée indépendamment ; une paire de
guillemets à l'appel du script n'a aucun effet sur ce qui se passe trois
lignes plus loin.

La correction ajoute des guillemets aux deux endroits où `FICHIER` est lu :

<!-- verif-setup:
mkdir -p scripts
cat > scripts/compter_brut.sh <<'FIN'
#!/usr/bin/env bash
FICHIER="$1"
wc -l "$FICHIER"
FIN
chmod +x scripts/compter_brut.sh
-->

```bash
cat scripts/compter_brut.sh
```

```output
#!/usr/bin/env bash
FICHIER="$1"
wc -l "$FICHIER"
```

```bash
./scripts/compter_brut.sh "data/brut_desordre/Echantillon 01 - Run mars.fastq"
```

```output
     100 data/brut_desordre/Echantillon 01 - Run mars.fastq
```

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  challenge

## Défi de transfert : compter tous les fichiers de `brut_desordre/`

En utilisant le script corrigé, ou une commande équivalente, affichez le
nombre de lignes de `data/brut_desordre/ech06 -- a refaire.fastq` et de
`data/brut_desordre/ech 03 (copie).fastq`. Rappelez-vous que les parenthèses
n'ont besoin d'aucun traitement particulier tant que le nom entier reste entre
guillemets doubles.

:::::::::::::::  solution

## Solution

```bash
wc -l "data/brut_desordre/ech06 -- a refaire.fastq"
wc -l "data/brut_desordre/ech 03 (copie).fastq"
```

```output
     100 data/brut_desordre/ech06 -- a refaire.fastq
     100 data/brut_desordre/ech 03 (copie).fastq
```

Les guillemets doubles protègent absolument tout ce qu'ils contiennent — les
espaces, le double tiret, les parenthèses — sans qu'aucun caractère n'ait
besoin d'un traitement séparé. C'est plus simple que de protéger chaque
caractère spécial individuellement, et c'est pourquoi la règle « guillemets
partout » suffit dans l'immense majorité des cas.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

## `readonly` : interdire la modification

Une variable qui ne doit jamais changer de valeur pendant l'exécution d'un
script — un chemin de référence, une version attendue — peut être déclarée
`readonly`. Toute tentative de la réaffecter ensuite échoue avec une erreur,
plutôt que de modifier silencieusement une valeur que le reste du script
suppose fixe.

<!-- verif: ignore -->
```bash
readonly GENOME_REF=data/genome/ref_toy.fa
echo "$GENOME_REF"
GENOME_REF=data/genome/autre.fa
```

```error
bash: GENOME_REF: readonly variable
```

## `export` : variable de shell contre variable d'environnement

Jusqu'ici, toutes les variables créées ne sont visibles que dans le shell
courant, y compris à l'intérieur d'un script que ce shell exécute : un script
lancé avec `./script.sh` s'exécute dans un shell séparé et ne voit pas les
variables ordinaires du shell qui l'a lancé.

```bash
LABO=genopole
echo "$LABO"
bash -c 'echo "dans le sous-shell : $LABO"'
```

```output
genopole

dans le sous-shell : 
```

`LABO` existe dans le shell courant, mais le `bash -c '...'` de la deuxième
ligne démarre un nouveau processus shell, qui ne connaît rien des variables de
son parent : la ligne s'affiche vide. `export` change cela en marquant la
variable comme faisant partie de l'**environnement**, transmis à tout
processus lancé depuis ce shell.

```bash
export LABO=genopole
bash -c 'echo "dans le sous-shell : $LABO"'
```

```output
dans le sous-shell : genopole
```

La distinction à retenir : une variable de shell ordinaire vit dans le shell
qui l'a créée et disparaît dès qu'on lance autre chose depuis ce shell ; une
variable exportée est copiée dans l'environnement de chaque processus lancé
ensuite, y compris un script, un `awk`, ou tout autre programme. C'est
pourquoi `$PATH` — qui doit être visible par tous les programmes que vous
lancez — est exportée, alors qu'une variable temporaire comme `NOM` dans un
défi précédent n'a aucune raison de l'être.

::::::::::::::::::::::::::::::::::::::::: callout

## `env`, pour voir ce qui est réellement exporté

La commande `env`, vue à l'épisode 19, affiche la liste des variables
exportées visibles par un nouveau processus. Une variable créée sans `export`
n'y apparaît jamais, même si `echo "$VAR"` fonctionne parfaitement dans le
shell courant.

::::::::::::::::::::::::::::::::::::::::::::::::::

## Récapitulatif : faut-il des guillemets

| Situation | Faut-il des guillemets doubles | Exemple |
|---|---|---|
| Lire une variable (`echo`, argument de commande) | **oui, toujours** | `wc -l "$FICHIER"` |
| Affecter une valeur contenant des espaces | **oui** | `FICHIER="Echantillon 01.fastq"` |
| Substitution de commande | **oui, toujours** | `N="$(wc -l < "$FICHIER")"` |
| Passer un argument à un script ou une fonction | **oui, toujours** | `./script.sh "$1"` |
| Comparaison dans `[ ... ]` (épisode 15) | **oui, toujours** | `[ -f "$FICHIER" ]` |
| Texte fixe sans variable, où l'on veut voir `$` ou `*` littéralement | non, apostrophes | `echo 'prix : $VAR'` |
| On veut délibérément découper une liste de mots séparés par des espaces | non | rare, cas volontaire uniquement |

La réponse courte, dans la quasi-totalité des cas que vous rencontrerez : oui,
toujours. Le seul cas légitime où l'on omet les guillemets est le cas
volontaire et rare où l'on souhaite explicitement le découpage en mots — et ce
cas ne s'est pas encore présenté dans cette leçon.

:::::::::::::::::::::::::::::::::::::::  challenge

## Défi étoilé : une variable pour chaque champ de la feuille d'échantillons (facultatif)

En combinant `$(...)` et `cut` (épisode 8), affectez à une variable
`PREMIER_ECH` l'identifiant du premier échantillon listé dans
`data/tables/echantillons.tsv` (colonne `sample_id`, en excluant l'en-tête),
puis affichez une phrase le mentionnant.

:::::::::::::::  solution

## Solution

```bash
PREMIER_ECH=$(cut -f1 data/tables/echantillons.tsv | grep -v sample_id | head -n 1)
echo "Le premier echantillon de la feuille est ${PREMIER_ECH}"
```

```output
Le premier echantillon de la feuille est ech01
```

`cut -f1` isole la colonne `sample_id`, `grep -v sample_id` retire la ligne
d'en-tête, `head -n 1` garde la première ligne restante. Le résultat entier
est capturé par `$(...)` sans qu'aucun guillemet ne soit nécessaire à
l'intérieur de la substitution elle-même — les guillemets protègent
l'utilisation de `$PREMIER_ECH` ensuite, pas la commande qui produit sa
valeur.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

Le prochain épisode s'appuie directement sur cette leçon : les fonctions et la
lecture ligne à ligne d'un fichier avec `while read -r` demandent exactement
la même discipline de guillemets, appliquée cette fois à chaque ligne de
`data/tables/echantillons.tsv`.

:::::::::::::::::::::::::::::::::::::::: keypoints

- `VAR=valeur` sans aucun espace autour du `=` ; un espace transforme
  l'affectation en appel de commande.
- Lisez toujours une variable entre guillemets doubles, `"$VAR"` : sans eux,
  le shell découpe la valeur en mots et développe les jokers qu'elle contient.
- `${VAR}` délimite explicitement le nom de la variable quand du texte le
  suit immédiatement sans séparateur, comme `${ECH}_R1`.
- Entre apostrophes, rien n'est développé ; entre guillemets doubles, `$VAR`
  et `$(commande)` sont développés mais `*` reste littéral.
- `$(commande)` capture la sortie d'une commande dans une variable et
  s'imbrique proprement ; préférez-la toujours aux accents graves.
- `${VAR:-defaut}` fournit une valeur de repli, `${VAR:?message}` interrompt
  le script si la variable est vide, `${#VAR}` donne sa longueur.
- `${F%.gz}`, `${F%%.*}`, `${F#*/}`, `${F##*/}` retirent un suffixe ou un
  préfixe sans lancer de commande externe, de façon portable.
- `readonly VAR=valeur` interdit toute réaffectation ultérieure.
- Une variable de shell ordinaire n'existe que dans le shell qui l'a créée ;
  `export` la copie dans l'environnement de tout processus lancé ensuite.
- Face à une variable, la question « faut-il des guillemets » a presque
  toujours la même réponse : oui.

::::::::::::::::::::::::::::::::::::::::::::::::::
