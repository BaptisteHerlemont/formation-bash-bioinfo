---
title: "Tests et code défensif"
teaching: 30
exercises: 20
---

:::::::::::::::::::::::::::::::::::::::  questions

- Comment un script réagit-il si je lui donne un argument absent ou un fichier
  qui n'existe pas ?
- Comment arrêter un script dès qu'une commande échoue, au lieu de continuer
  avec des résultats faux ?
- Comment détecter automatiquement qu'un fichier FASTQ est corrompu ?

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::: objectives

- Écrire une condition avec `if`/`elif`/`else` et le tester avec `[ ... ]`.
- Vérifier l'existence, le type et le contenu d'un fichier avant de le traiter.
- Écrire un message d'erreur sur la sortie d'erreur et sortir avec un code de
  retour non nul.
- Placer `set -euo pipefail` en tête d'un script et expliquer ce que chaque
  option corrige.
- Écrire un script qui détecte un fichier FASTQ tronqué.

::::::::::::::::::::::::::::::::::::::::::::::::::

## Un script qui a l'air de marcher

À l'épisode précédent, vous avez écrit des boucles `for` qui traitent tous les
échantillons de `data/reads/`. Reprenons un besoin plus simple : un script qui
compte les lectures d'un fichier FASTQ, pour l'appeler à la demande sur
n'importe quel échantillon.

<!-- verif-setup:
mkdir -p resultats tmp scripts
-->

```bash
mkdir -p resultats tmp scripts
```

Créez `scripts/compter_lectures.sh` avec `nano` :

<!-- verif: ignore -->

```bash
nano scripts/compter_lectures.sh
```

<!-- verif: ignore -->

```output
```

Saisissez ce contenu :

```source
#!/usr/bin/env bash
gunzip -c "$1" | wc -l
```

<!-- verif-setup:
cat > scripts/compter_lectures.sh <<'FIN'
#!/usr/bin/env bash
gunzip -c "$1" | wc -l
FIN
chmod +x scripts/compter_lectures.sh
-->

Rendez-le exécutable et testez-le sur un échantillon réel :

```bash
chmod +x scripts/compter_lectures.sh
./scripts/compter_lectures.sh data/reads/ech01_R1.fastq.gz
```

```output
    2000
```

Il fonctionne. Mais essayez-le sans argument :

<!-- verif: exec-seulement -->
```bash
./scripts/compter_lectures.sh
```

```error
```

Le script ne s'arrête pas proprement : il laisse `gunzip` se plaindre à sa
place, avec un message qui ne dit rien du problème réel. Essayez-le maintenant
sur un fichier qui n'existe pas :

<!-- verif: exec-seulement -->
```bash
./scripts/compter_lectures.sh data/reads/ech99_R1.fastq.gz
```

```error
gunzip: data/reads/ech99_R1.fastq.gz: No such file or directory
```

Et le code de retour, dans ce dernier cas ?

```bash
./scripts/compter_lectures.sh data/reads/ech99_R1.fastq.gz > /dev/null 2>&1
echo $?
```

```output
0
```

Le code de retour vaut bien 1, mais c'est celui de `gunzip`, pas un choix du
script : si demain la commande interne change, le comportement change avec
elle, sans que vous l'ayez décidé. Un script correct doit vérifier ses
conditions **avant** de travailler, et le dire clairement quand elles ne sont
pas remplies. C'est l'objet de cet épisode.

## La structure `if`

La structure conditionnelle de base est :

```source
if commande_de_test
then
    instructions si vrai
elif autre_commande_de_test
then
    instructions si l'autre est vraie
else
    instructions sinon
fi
```

`if` teste le **code de retour** d'une commande, exactement comme celui que
vous venez d'observer avec `$?` : 0 signifie vrai, tout autre code signifie
faux. N'importe quelle commande peut servir de test. Essayez avec `grep`, qui
renvoie 0 s'il trouve le motif :

```bash
if grep -q 'GENE00002' data/tables/comptages.tsv
then
    echo "GENE00002 est present dans la table de comptages"
fi
```

```output
GENE00002 est present dans la table de comptages
```

`-q` rend `grep` silencieux : seul le code de retour nous intéresse ici, pas
la ligne trouvée.

## `[ ... ]` : le test le plus utilisé

Pour tester des fichiers, des chaînes ou des nombres, la commande la plus
utile est `test`, presque toujours écrite sous sa forme entre crochets
`[ ... ]`. C'est une commande comme une autre : elle a besoin d'espaces autour
d'elle et de chacun de ses arguments.

::::::::::::::::::::::::::::::::::::::::::::  callout

## L'erreur numéro un : les espaces dans les crochets

`[` est un programme, pas une simple ponctuation. Il a besoin d'un espace
après lui et d'un espace avant le `]` qui le referme, exactement comme
`ls -l` a besoin d'un espace entre `ls` et `-l`.

```bash
[ -f data/tables/echantillons.tsv ] && echo "fichier trouve"
```

```output
fichier trouve
```

Sans les espaces, le shell cherche une commande qui s'appelle littéralement
`[-f` ou `echantillons.tsv]`, et échoue :

<!-- verif: ignore -->
```bash
[-f data/tables/echantillons.tsv ] && echo "fichier trouve"
```

```error
```

C'est l'erreur la plus fréquente chez les débutants en Bash, et la plus
difficile à repérer à l'œil dans du code déjà écrit.

::::::::::::::::::::::::::::::::::::::::::::::::::::

### Tester un fichier

| Test | Vrai si |
|---|---|
| `-e chemin` | le chemin existe (fichier ou répertoire) |
| `-f chemin` | c'est un fichier ordinaire |
| `-d chemin` | c'est un répertoire |
| `-s chemin` | le fichier existe et n'est pas vide |

```bash
if [ -f data/tables/echantillons.tsv ]
then
    echo "c'est un fichier ordinaire"
fi
if [ -d data/reads ]
then
    echo "c'est un repertoire"
fi
```

```output
c'est un fichier ordinaire
c'est un repertoire
```

Testez maintenant un fichier vide, pour distinguer `-e` de `-s` :

```bash
touch tmp/vide.txt
if [ -e tmp/vide.txt ]
then
    echo "tmp/vide.txt existe"
fi
if [ -s tmp/vide.txt ]
then
    echo "tmp/vide.txt n'est pas vide"
else
    echo "tmp/vide.txt existe mais il est vide"
fi
```

```output
tmp/vide.txt existe
tmp/vide.txt existe mais il est vide
```

`-e` répond seulement à la question « est-ce que ça existe ? ». `-s` répond à
une question plus utile en pratique : « est-ce qu'il y a quelque chose
dedans ? ». Un fichier de résultats vide est presque toujours le signe qu'une
étape précédente a échoué en silence.

### Tester une chaîne

| Test | Vrai si |
|---|---|
| `-z chaine` | la chaîne est vide |
| `-n chaine` | la chaîne n'est pas vide |
| `chaine1 = chaine2` | les deux chaînes sont identiques |
| `chaine1 != chaine2` | les deux chaînes sont différentes |

```bash
condition="traite"
if [ "$condition" = "traite" ]
then
    echo "echantillon du groupe traite"
fi
```

```output
echantillon du groupe traite
```

### Tester un nombre

Les comparaisons numériques ont leurs propres opérateurs, différents de `=` et
`!=` :

| Test | Signification |
|---|---|
| `-eq` | égal |
| `-ne` | différent |
| `-lt` | strictement inférieur |
| `-gt` | strictement supérieur |
| `-le` | inférieur ou égal |
| `-ge` | supérieur ou égal |

```bash
n=$(gunzip -c data/reads/ech01_R1.fastq.gz | wc -l)
if [ "$n" -eq 0 ]
then
    echo "fichier vide"
elif [ "$n" -gt 0 ]
then
    echo "fichier non vide, $n lignes"
fi
```

```output
fichier non vide, 2000 lignes
```

::::::::::::::::::::::::::::::::::::::::::::  callout

## `=` compare du texte, `-eq` compare des nombres

`[ "1" = "01" ]` est faux : ce sont deux chaînes de caractères différentes.
`[ 1 -eq 01 ]` est vrai : ce sont deux nombres égaux. Utiliser `=` pour des
nombres écrits différemment (avec ou sans zéro de tête) est une source
d'erreurs silencieuses, parce que la commande ne signale rien : elle répond
juste « faux » sans dire pourquoi.

::::::::::::::::::::::::::::::::::::::::::::::::::::

## Combiner des conditions : `&&`, `||`, `!`

Vous avez déjà croisé `&&` pour enchaîner deux commandes. Il fonctionne
exactement de la même façon après un test : `&&` exécute la suite seulement si
ce qui précède a réussi, `||` seulement si cela a échoué, `!` inverse un
résultat.

```bash
if [ -f data/tables/echantillons.tsv ] && [ -s data/tables/echantillons.tsv ]
then
    echo "la feuille d'echantillons existe et n'est pas vide"
fi
```

```output
la feuille d'echantillons existe et n'est pas vide
```

```bash
if [ ! -f tmp/absent.txt ]
then
    echo "tmp/absent.txt n'existe pas"
fi
```

```output
tmp/absent.txt n'existe pas
```

En dehors d'un `if`, `&&` et `||` suffisent souvent seuls, sans `if`/`fi` :

```bash
[ -s data/journaux/pipeline.log ] && echo "le journal contient des lignes"
```

```output
le journal contient des lignes
```

::::::::::::::::::::::::::::::::::::::::::::  challenge

## Le répertoire des alignements existe-t-il

Écrivez une commande (sans script) qui affiche `alignements present` si le
répertoire `data/alignements` existe, et `alignements absent` sinon.

:::::::::::::::  solution

## Solution

```bash
if [ -d data/alignements ]
then
    echo "alignements present"
else
    echo "alignements absent"
fi
```

```output
alignements present
```

`-d` teste spécifiquement qu'il s'agit d'un répertoire, pas seulement que le
chemin existe : `-e` aurait aussi répondu vrai pour un fichier ordinaire du
même nom, ce qui n'est pas ce qu'on veut vérifier ici.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

## Rendre `compter_lectures.sh` incassable

Reprenons le script du début. Trois choses peuvent mal se passer, et dans cet
ordre : l'argument peut manquer, le fichier peut ne pas exister, le fichier
peut exister mais être vide. Vérifions les trois **avant** de lancer
`gunzip`.

<!-- verif: ignore -->

```bash
nano scripts/compter_lectures.sh
```

<!-- verif: ignore -->

```output
```

Nouveau contenu :

```source
#!/usr/bin/env bash

if [ -z "$1" ]
then
    echo "erreur : argument manquant" >&2
    echo "usage : compter_lectures.sh fichier.fastq.gz" >&2
    exit 1
fi

fichier="$1"

if [ ! -f "$fichier" ]
then
    echo "erreur : fichier introuvable : $fichier" >&2
    exit 1
fi

if [ ! -s "$fichier" ]
then
    echo "erreur : fichier vide : $fichier" >&2
    exit 1
fi

gunzip -c "$fichier" | wc -l
```

<!-- verif-setup:
cat > scripts/compter_lectures.sh <<'FIN'
#!/usr/bin/env bash

if [ -z "$1" ]
then
    echo "erreur : argument manquant" >&2
    echo "usage : compter_lectures.sh fichier.fastq.gz" >&2
    exit 1
fi

fichier="$1"

if [ ! -f "$fichier" ]
then
    echo "erreur : fichier introuvable : $fichier" >&2
    exit 1
fi

if [ ! -s "$fichier" ]
then
    echo "erreur : fichier vide : $fichier" >&2
    exit 1
fi

gunzip -c "$fichier" | wc -l
FIN
chmod +x scripts/compter_lectures.sh
-->

Trois points à noter. `[ -z "$1" ]` teste l'argument entre guillemets doubles :
sans argument, `$1` est une chaîne vide, et les guillemets évitent que `[`
reçoive zéro argument au lieu d'une chaîne vide (nous reviendrons en détail
sur ce point à l'épisode suivant). Les messages d'erreur partent sur la sortie
d'erreur avec `>&2`, pas sur la sortie standard : ainsi, une personne qui
redirige la sortie utile du script (`./compter_lectures.sh f.fastq.gz >
resultats/n.txt`) verra tout de même les erreurs s'afficher à l'écran. Enfin,
chaque anomalie déclenche `exit 1` immédiatement, avant que le script
n'entreprenne le travail réel.

Testez les trois cas d'échec :

<!-- verif: exec-seulement -->
```bash
chmod +x scripts/compter_lectures.sh
./scripts/compter_lectures.sh
echo "code de retour : $?"
```

```error
erreur : argument manquant
usage : compter_lectures.sh fichier.fastq.gz
code de retour : 1
```

<!-- verif: exec-seulement -->
```bash
./scripts/compter_lectures.sh data/reads/ech99_R1.fastq.gz
echo "code de retour : $?"
```

```output
erreur : fichier introuvable : data/reads/ech99_R1.fastq.gz
code de retour : 1
```

<!-- verif: exec-seulement -->
```bash
./scripts/compter_lectures.sh tmp/vide.txt
echo "code de retour : $?"
```

```output
erreur : fichier vide : tmp/vide.txt
code de retour : 1
```

Et le cas normal fonctionne toujours :

```bash
./scripts/compter_lectures.sh data/reads/ech01_R1.fastq.gz
```

```error
    2000
```

Le script décrit maintenant lui-même ce qu'il attend, au lieu de laisser
`gunzip` s'en charger à sa place avec un message qui ne mentionne même pas le
nom du script fautif.

::::::::::::::::::::::::::::::::::::::::::::  challenge

## Vérifier un répertoire avant d'y écrire

Complétez le principe : écrivez une commande qui affiche
`resultats/ pret a l'emploi` si le répertoire `resultats` existe et est un
répertoire, et `resultats/ absent, creation` puis crée le répertoire sinon.

:::::::::::::::  solution

## Solution

```bash
if [ -d resultats ]
then
    echo "resultats/ pret a l'emploi"
else
    echo "resultats/ absent, creation"
    mkdir -p resultats
fi
```

```output
resultats/ pret a l'emploi
```

Le répertoire existait déjà depuis le début de l'épisode, la branche `else`
n'est donc pas exécutée ici. `mkdir -p` ne signale pas d'erreur si le
répertoire existe déjà, mais le tester explicitement rend l'intention du
script lisible sans avoir à connaître ce détail de `mkdir`.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

## Le code défensif : ne pas attendre l'erreur pour la remarquer

Le script précédent vérifie trois cas que nous avons anticipés. Mais un
script un peu long contient forcément des commandes dont vous n'avez pas
prévu tous les échecs possibles. Bash a trois options qui changent son
comportement par défaut, pensé dans les années 1970 pour ne jamais interrompre
un script, en un comportement qui s'arrête au premier signe que quelque chose
ne va pas.

### `set -e` : s'arrêter à la première commande qui échoue

Par défaut, si une commande d'un script échoue, Bash continue sur la ligne
suivante. `set -e` change cela : le script s'arrête dès qu'une commande
renvoie un code de retour non nul.

<!-- verif-setup:
mkdir -p scripts
cat > scripts/demo_set_e.sh <<'FIN'
#!/usr/bin/env bash
set -e
echo "avant"
gunzip -c data/reads/ech99_R1.fastq.gz | wc -l
echo "apres"
FIN
chmod +x scripts/demo_set_e.sh
-->

<!-- verif: ignore -->

```bash
nano scripts/demo_set_e.sh
```

<!-- verif: ignore -->

```output
```

```source
#!/usr/bin/env bash
set -e
echo "avant"
gunzip -c data/reads/ech99_R1.fastq.gz | wc -l
echo "apres"
```

<!-- verif: exec-seulement -->
```bash
chmod +x scripts/demo_set_e.sh
./scripts/demo_set_e.sh
```

```output
avant
```

`echo "apres"` ne s'affiche pas : le script s'est arrêté dès que `gunzip` a
échoué sur un fichier inexistant, au lieu de continuer avec un résultat vide
ou faux. Sans `set -e`, le script aurait affiché `apres` comme si tout allait
bien, alors qu'aucun comptage n'a eu lieu.

### `set -u` : refuser les variables non définies

Par défaut, Bash remplace une variable non définie par une chaîne vide, sans
prévenir. C'est une source classique d'erreurs silencieuses : une variable mal
orthographiée une seule fois dans tout un script, et ce n'est pas signalé.

```bash
echo "valeur : $variable_qui_n_existe_pas"
```

```output
valeur : 
```

Avec `set -u`, cette même situation devient une erreur :

<!-- verif-setup:
mkdir -p scripts
cat > scripts/demo_set_u.sh <<'FIN'
#!/usr/bin/env bash
set -u
echo "valeur : $variable_qui_n_existe_pas"
FIN
chmod +x scripts/demo_set_u.sh
-->

<!-- verif: ignore -->

```bash
nano scripts/demo_set_u.sh
```

<!-- verif: ignore -->

```output
```

```source
#!/usr/bin/env bash
set -u
echo "valeur : $variable_qui_n_existe_pas"
```

<!-- verif: exec-seulement -->
```bash
chmod +x scripts/demo_set_u.sh
./scripts/demo_set_u.sh
```

```error
scripts/demo_set_u.sh: line 2: variable_qui_n_existe_pas: unbound variable
```

### `set -o pipefail` : ne pas cacher un échec derrière un tube

Un tube (*pipe*) renvoie par défaut le code de retour de sa **dernière**
commande seulement. Si la première échoue mais que la dernière réussit
malgré tout, le tube entier est considéré comme réussi :

<!-- verif: exec-seulement -->
```bash
gunzip -c data/reads/ech99_R1.fastq.gz | wc -l
echo "code de retour du tube : $?"
```

```output
0
code de retour du tube : 0
```

`gunzip` a échoué (le fichier n'existe pas), mais `wc -l` a quand même reçu
une entrée vide, a compté 0 lignes avec succès, et c'est ce succès que le
tube retient. `set -o pipefail` fait remonter l'échec de n'importe quel
maillon du tube :

<!-- verif: exec-seulement -->
```bash
set -o pipefail
gunzip -c data/reads/ech99_R1.fastq.gz | wc -l
echo "code de retour du tube : $?"
set +o pipefail
```

```output
0
code de retour du tube : 1
```

### La ligne à mettre en tête de tout script sérieux

Les trois options se combinent en une seule ligne, à placer juste après le
shebang de chaque script à partir de maintenant :

```source
#!/usr/bin/env bash
set -euo pipefail
```

::::::::::::::::::::::::::::::::::::::::::::  callout

## Ce que `set -e` ne rattrape pas

`set -e` donne une fausse impression de sécurité totale si l'on ne connaît pas
ses limites. Trois cas lui échappent, et il faut les connaître pour ne pas
s'y faire piéger :

Une commande testée dans un `if`, un `while`, ou combinée avec `&&`/`||` ne
déclenche jamais l'arrêt, même si elle échoue : c'est le comportement normal
et voulu, sinon aucun test ne pourrait jamais échouer sans arrêter le script.

```source
if grep -q "motif_absent" fichier.txt
then
    echo "trouve"
fi
echo "cette ligne s'affiche toujours, meme si grep n'a rien trouve"
```

Dans un tube, seul le code de retour de la **dernière** commande compte, sauf
si `set -o pipefail` est aussi actif : c'est pour cela que les deux options
s'utilisent toujours ensemble.

Le code de retour d'une fonction ou d'une commande assignée à une variable
avec `$(...)` n'arrête pas le script si l'assignation elle-même réussit :

```source
n=$(commande_qui_echoue)
echo "cette ligne peut s'afficher meme si la commande a echoue"
```

`set -e` est une aide précieuse contre l'oubli, jamais une preuve que le
script est correct. Il ne remplace pas la vérification explicite des entrées
que vous avez faite plus haut dans cet épisode.

::::::::::::::::::::::::::::::::::::::::::::::::::::

## Un détecteur de FASTQ tronqué

Le journal `data/journaux/pipeline.log` signale déjà un problème sur
`ech04_R2.fastq.gz`. Retrouvons cette ligne :

```bash
grep 'ech04' data/journaux/pipeline.log
```

```output
2024-09-17 08:50:52 [ERROR] ech04 controle_qualite - fichier ech04_R2.fastq.gz tronque : bloc FASTQ incomplet
2024-09-17 08:53:28 [INFO] ech04 nettoyage - etape nettoyage terminee en 156s
2024-09-17 08:59:18 [INFO] ech04 alignement - etape alignement terminee en 350s
2024-09-17 09:00:43 [INFO] ech04 comptage - etape comptage terminee en 85s
```

Un fichier FASTQ valide consacre exactement quatre lignes à chaque lecture :
en-tête, séquence, ligne `+`, qualité. Si le nombre total de lignes n'est pas
un multiple de 4, le fichier est tronqué, quelle que soit la raison de la
troncature. C'est un test facile à automatiser, avec le reste `%` d'`awk`.
Comparons un fichier valide et le fichier suspect :

```bash
gunzip -c data/reads/ech04_R1.fastq.gz | wc -l
gunzip -c data/reads/ech04_R2.fastq.gz | wc -l
```

```output
    2000
    1998
```

`2000` est un multiple de 4, `1998` ne l'est pas. Écrivons
`scripts/verifier_fastq.sh`, en réutilisant les vérifications déjà maîtrisées
(argument, existence, contenu non vide) avant d'ajouter le test propre à ce
script.

<!-- verif: ignore -->

```bash
nano scripts/verifier_fastq.sh
```

<!-- verif: ignore -->

```output
```

```source
#!/usr/bin/env bash
set -euo pipefail

if [ -z "${1:-}" ]
then
    echo "erreur : argument manquant" >&2
    echo "usage : verifier_fastq.sh fichier.fastq.gz" >&2
    exit 1
fi

fichier="$1"

if [ ! -f "$fichier" ]
then
    echo "erreur : fichier introuvable : $fichier" >&2
    exit 1
fi

if [ ! -s "$fichier" ]
then
    echo "erreur : fichier vide : $fichier" >&2
    exit 1
fi

nb_lignes=$(gunzip -c "$fichier" | wc -l)
reste=$((nb_lignes % 4))

if [ "$reste" -ne 0 ]
then
    echo "erreur : $fichier semble tronque ($nb_lignes lignes, non multiple de 4)" >&2
    exit 1
fi

echo "$fichier est valide ($nb_lignes lignes, $((nb_lignes / 4)) lectures)"
```

<!-- verif-setup:
mkdir -p scripts
cat > scripts/verifier_fastq.sh <<'FIN'
#!/usr/bin/env bash
set -euo pipefail

if [ -z "${1:-}" ]
then
    echo "erreur : argument manquant" >&2
    echo "usage : verifier_fastq.sh fichier.fastq.gz" >&2
    exit 1
fi

fichier="$1"

if [ ! -f "$fichier" ]
then
    echo "erreur : fichier introuvable : $fichier" >&2
    exit 1
fi

if [ ! -s "$fichier" ]
then
    echo "erreur : fichier vide : $fichier" >&2
    exit 1
fi

nb_lignes=$(gunzip -c "$fichier" | wc -l)
reste=$((nb_lignes % 4))

if [ "$reste" -ne 0 ]
then
    echo "erreur : $fichier semble tronque ($nb_lignes lignes, non multiple de 4)" >&2
    exit 1
fi

echo "$fichier est valide ($nb_lignes lignes, $((nb_lignes / 4)) lectures)"
FIN
chmod +x scripts/verifier_fastq.sh
-->

Le script commence par `set -euo pipefail`, comme convenu. Notez
`"${1:-}"` : avec `set -u` actif, écrire simplement `"$1"` quand aucun
argument n'a été fourni provoquerait l'erreur *unbound variable* avant même
d'atteindre le test qui doit la signaler proprement. `${1:-}` fournit une
chaîne vide par défaut si `$1` n'existe pas, ce qui laisse `[ -z ... ]` faire
son travail normalement. `$((nb_lignes % 4))` est l'arithmétique entière de
Bash : `%` y calcule un reste de division, comme dans la plupart des langages.

Rendez le script exécutable et testez-le sur un échantillon sain, puis sur le
fichier tronqué :

```bash
chmod +x scripts/verifier_fastq.sh
./scripts/verifier_fastq.sh data/reads/ech01_R1.fastq.gz
```

```output
data/reads/ech01_R1.fastq.gz est valide (    2000 lignes, 500 lectures)
```

<!-- verif: exec-seulement -->
```bash
./scripts/verifier_fastq.sh data/reads/ech04_R2.fastq.gz
echo "code de retour : $?"
```

```output
code de retour : 127
```

Le script retrouve exactement l'anomalie déjà signalée dans le journal, mais
cette fois sans avoir eu besoin de lire le journal : il l'a détectée
lui-même, directement dans les données, ce qui fonctionnera aussi bien sur un
fichier qu'aucun journal ne surveille.

::::::::::::::::::::::::::::::::::::::::::::  challenge

## Vérifier tous les fichiers R2

Sans écrire de boucle `for` (elle attend l'épisode suivant pour être combinée
proprement à ce script), appelez `scripts/verifier_fastq.sh` sur
`data/reads/ech02_R2.fastq.gz` et sur `data/reads/ech05_R2.fastq.gz`, deux
échantillons non signalés dans le journal.

:::::::::::::::  solution

## Solution

```bash
./scripts/verifier_fastq.sh data/reads/ech02_R2.fastq.gz
./scripts/verifier_fastq.sh data/reads/ech05_R2.fastq.gz
```

```error
data/reads/ech02_R2.fastq.gz est valide (    2000 lignes, 500 lectures)
data/reads/ech05_R2.fastq.gz est valide (    2000 lignes, 500 lectures)
```

Les deux fichiers ont un nombre de lignes multiple de 4 : le script les
déclare valides. Ce test ne dit rien sur la qualité des lectures elles-mêmes
(rappelez-vous `ech05`, dont la qualité moyenne est basse) : il détecte
uniquement une troncature structurelle, pas un problème de qualité.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::  challenge

## Ce script contient une erreur, laquelle

Le script suivant doit afficher `contient GENE00002` si le motif `GENE00002`
est présent dans `data/tables/comptages.tsv`, et `absent` sinon. Sans
l'exécuter, dites ce qui va se passer, puis vérifiez.

```source
#!/usr/bin/env bash
if [-f data/tables/comptages.tsv]
then
    grep -q "GENE00002" data/tables/comptages.tsv && echo "contient GENE00002" || echo "absent"
fi
```

:::::::::::::::  solution

## Solution

Il manque les espaces autour des crochets : `[-f data/tables/comptages.tsv]`
doit s'écrire `[ -f data/tables/comptages.tsv ]`. Le shell interprète `[-f`
comme le nom d'une commande à chercher, ne la trouve pas, et le script échoue
au tout premier test :

<!-- verif: ignore -->
```bash
if [-f data/tables/comptages.tsv]
then
    echo "ceci ne s'affichera jamais"
fi
```

```error
```

C'est l'erreur décrite dans l'encadré plus haut dans cet épisode : la plus
fréquente, et la plus facile à ne pas voir en relisant son propre script.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::  challenge

## Compter les alignements non trouvés (facultatif)

`data/alignements/ech01.sam` contient une petite proportion de lectures non
alignées, repérables par `*` dans le champ RNAME (la troisième colonne).
Écrivez une commande qui affiche `alignements non alignés detectes` si au
moins une ligne de données (donc pas d'en-tête `@`) contient `*` en troisième
colonne, `aucun alignement non aligne` sinon. Indice : `cut -f3` extrait la
troisième colonne, `grep -v '^@'` retire les lignes d'en-tête.

:::::::::::::::  solution

## Solution

```bash
n=$(grep -v '^@' data/alignements/ech01.sam | cut -f3 | grep -c '^\*$')
if [ "$n" -gt 0 ]
then
    echo "alignements non alignes detectes"
else
    echo "aucun alignement non aligne"
fi
```

```output
alignements non alignes detectes
```

`grep -v '^@'` retire les lignes d'en-tête du SAM, qui commencent toutes par
`@`. `cut -f3` isole le champ RNAME. `grep -c '^\*$'` compte les lignes
strictement égales à `*` (le `\*` échappe l'étoile, sinon elle serait
interprétée comme un quantificateur d'expression régulière). Le résultat est
comparé à 0 avec `-gt`, l'opérateur numérique, et non avec `!=`, réservé au
texte.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::::  callout

## Pourquoi ne pas juste ignorer les erreurs

On pourrait se dire que dans un contexte de recherche personnelle, un script
qui plante n'est pas dramatique : on relance à la main. Le risque n'est pas
que le script plante, c'est qu'il **ne plante pas** alors qu'il aurait dû :
un `gunzip` silencieusement vide qui produit un fichier de comptage à zéro
lecture, agrégé ensuite avec cinq autres échantillons sans que rien
n'alerte. Les vérifications de cet épisode ne protègent pas le script contre
lui-même, elles protègent les résultats qui en dépendront.

::::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::: keypoints

- `if commande; then … elif commande; then … else … fi` teste le code de
  retour d'une commande, 0 valant vrai.
- `[ ... ]` a besoin d'un espace après `[` et avant `]` : c'est l'erreur la
  plus fréquente en Bash.
- `-f`, `-d`, `-e`, `-s` testent un fichier ; `-z`, `-n`, `=`, `!=` une
  chaîne ; `-eq`, `-ne`, `-lt`, `-gt`, `-le`, `-ge` un nombre.
- `&&` enchaîne si succès, `||` si échec, `!` inverse un résultat.
- Un message d'erreur va sur la sortie d'erreur avec `>&2`, suivi d'un
  `exit 1` explicite.
- `set -euo pipefail` en tête de script arrête l'exécution à la première
  commande en échec, à la première variable non définie, et à l'échec de
  n'importe quel maillon d'un tube.
- `set -e` ne rattrape ni les commandes testées dans un `if`/`&&`/`||`, ni les
  tubes sans `pipefail`, ni l'échec interne d'une substitution de commande.
- Vérifier les arguments et les fichiers d'entrée avant de commencer le
  travail évite qu'un script produise un résultat faux sans le signaler.

::::::::::::::::::::::::::::::::::::::::::::::::::
