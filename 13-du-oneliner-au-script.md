---
title: "Du one-liner au script"
teaching: 30
exercises: 25
---

:::::::::::::::::::::::::::::::::::::::  questions

- Pourquoi enregistrer une commande dans un fichier plutôt que la retaper ?
- Comment écrire, rendre exécutable et lancer mon propre script Bash ?
- Comment passer des arguments à un script et savoir s'il a réussi ?

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::: objectives

- Expliquer en quoi un script améliore la reproductibilité par rapport à un tube tapé directement dans le terminal.
- Écrire un script Bash documenté, avec shebang et en-tête, à l'aide de `nano`.
- Rendre un script exécutable avec `chmod +x` et le lancer avec `./` ou avec `bash`.
- Utiliser les arguments positionnels (`$1`, `$#`, `$@`) et le code de retour (`$?`) dans un script.

::::::::::::::::::::::::::::::::::::::::::::::::::

## D'un tube qui fonctionne à un tube qu'on retrouve

Depuis quatre jours, vous accumulez des commandes qui fonctionnent. À
l'épisode 4, vous avez compté les lectures d'un fichier FASTQ compressé avec
un tube :

```bash
mkdir -p resultats tmp scripts
gunzip -c data/reads/ech01_R1.fastq.gz | wc -l
```

```output
2000
```

Cette commande est correcte, mais elle a trois défauts dès que le projet
grandit :

- **la mémoire** : dans une semaine, vous ne vous souviendrez plus si vous
  avez divisé par 4 avant ou après avoir copié le résultat dans votre carnet
  de laboratoire ;
- **le partage** : pour la transmettre à un collègue, il faut la retaper
  correctement, sans oublier `-c` ni la barre verticale ;
- **la relecture** : une commande tapée dans le terminal n'est vérifiée par
  personne, pas même par vous-même une seconde fois.

Un **script** est un fichier texte qui contient une suite de commandes. Il se
lit, se corrige, se commente, se date, se copie, et surtout il s'exécute
toujours de la même façon. C'est la différence entre une manipulation qu'on
raconte de mémoire et un protocole écrit sur le classeur du laboratoire.

## Écrire un premier script avec nano

`nano` est un éditeur de texte qui fonctionne directement dans le terminal.
Il n'a que quelques raccourcis essentiels, tous rappelés en bas de l'écran
sous la forme `^O`, `^X`, etc. — le `^` signifie la touche `Ctrl`.

| Raccourci | Effet |
|---|---|
| `Ctrl+O` | Écrire le fichier sur le disque (*Write Out*), sans quitter |
| `Ctrl+X` | Quitter l'éditeur (propose d'écrire si le fichier a changé) |
| `Ctrl+K` | Couper la ligne courante |
| `Ctrl+W` | Chercher un mot dans le fichier (*Where is*) |

Ouvrez un premier fichier :

<!-- verif: ignore -->

```bash
nano scripts/bonjour.sh
```
<!-- verif: ignore -->

`nano` ouvre un écran vide. Tapez le texte suivant, puis enregistrez avec
`Ctrl+O`, confirmez le nom de fichier avec `Entrée`, et quittez avec `Ctrl+X`.

<!-- verif: fichier scripts/bonjour.sh -->

```bash
#!/usr/bin/env bash
echo "Bonjour depuis un script"
```
<!-- verif: ignore -->

<!-- verif-setup:
mkdir -p scripts
cat > scripts/bonjour.sh <<'FIN'
#!/usr/bin/env bash
echo "Bonjour depuis un script"
FIN
-->

Vérifiez que le fichier existe et contient bien ces deux lignes :

```bash
cat scripts/bonjour.sh
```

```output
#!/usr/bin/env bash
echo "Bonjour depuis un script"
```

## Le shebang

La première ligne, `#!/usr/bin/env bash`, s'appelle le **shebang**. Pour le
shell, un `#` commence normalement un commentaire ; mais quand les deux
premiers caractères d'un fichier exécutable sont `#!`, le système
d'exploitation lit le reste de la ligne comme le chemin de l'interpréteur à
utiliser pour exécuter ce fichier.

Vous rencontrerez souvent une autre forme, `#!/bin/bash`, qui pointe
directement vers l'exécutable Bash installé à cet endroit précis. Cette
formulation suppose que Bash se trouve à `/bin/bash` sur toutes les machines,
ce qui n'est pas garanti : certains systèmes installent Bash ailleurs, par
exemple dans `/usr/local/bin`. `#!/usr/bin/env bash` demande au contraire à la
commande `env` de chercher `bash` dans les répertoires listés par la variable
`PATH`, quel que soit l'endroit où il se trouve réellement installé. C'est
cette forme portable que cette leçon utilise partout.

::: callout

## Le shebang n'est utile qu'à l'exécution directe

Le shebang ne sert que lorsque vous lancez le script comme un programme
(`./script.sh`). Si vous l'exécutez en le passant explicitement à Bash
(`bash script.sh`), la première ligne est simplement ignorée comme un
commentaire, et c'est bien Bash qui l'interprète. Les deux méthodes sont
détaillées plus loin dans cet épisode.

:::

## Rendre le script exécutable

Un fichier texte, même avec un shebang, n'est pas exécutable par défaut :

<!-- verif: ignore -->
```bash
scripts/bonjour.sh
```

```error
Bonjour depuis un script
```
Il manque la permission d'exécution. Vous l'ajoutez avec `chmod +x`
(*change mode*, `+x` pour ajouter le droit d'exécution) :

```bash
chmod +x scripts/bonjour.sh
```

Le script peut maintenant être lancé :

```bash
./scripts/bonjour.sh
```

```output
Bonjour depuis un script
```

Le `./` devant le nom du script n'est pas décoratif : pour des raisons de
sécurité, le shell ne cherche pas les commandes à exécuter dans le répertoire
courant, seulement dans les répertoires listés par `PATH`. Écrire `./` précise
explicitement « ce fichier-ci, ici, dans le répertoire où je me trouve ».
Sans lui, le shell chercherait un programme nommé `scripts` dans son `PATH` et
ne le trouverait pas.

Une alternative existe, qui ne demande aucune permission d'exécution :

```bash
bash scripts/bonjour.sh
```

```output
Bonjour depuis un script
```

Ici, vous demandez explicitement à l'interpréteur `bash` de lire et
d'exécuter le fichier, ligne par ligne, comme il le ferait pour n'importe
quel texte de commandes. C'est utile pour tester rapidement un script qu'on
vient de modifier, sans repasser par `chmod`.

::: callout

## Deux façons d'obtenir le même résultat

`./scripts/bonjour.sh` exige que le fichier soit exécutable (`chmod +x`) et
possède un shebang valide, qui détermine l'interpréteur utilisé.
`bash scripts/bonjour.sh` ignore les permissions et le shebang : c'est
toujours Bash qui exécute le fichier, même si le shebang indique autre chose.
Dans cette leçon, les deux méthodes sont équivalentes puisque tous les
scripts sont écrits pour Bash.

:::

## Documenter un script

Un script sans explication est aussi difficile à reprendre qu'un tube tapé de
mémoire il y a six mois. La convention adoptée dans cette leçon est un
en-tête en commentaire, juste après le shebang, qui répond à cinq questions :
que fait ce script, comment l'appeler, qu'attend-il en entrée, que produit-il
en sortie, qui l'a écrit et quand.

<!-- verif: ignore -->

```bash
nano scripts/exemple_entete.sh
```
<!-- verif: ignore -->

```bash
#!/usr/bin/env bash
#
# Objet   : exemple d'en-tete documentaire
# Usage   : ./exemple_entete.sh
# Entree  : aucune
# Sortie  : un message sur la sortie standard
# Auteur  : Formation Bash pour la bioinformatique
# Date    : 2024-09-17

echo "Ceci est un exemple d'en-tete"
```
<!-- verif: ignore -->

<!-- verif-setup:
mkdir -p scripts
cat > scripts/exemple_entete.sh <<'FIN'
#!/usr/bin/env bash
#
# Objet   : exemple d'en-tete documentaire
# Usage   : ./exemple_entete.sh
# Entree  : aucune
# Sortie  : un message sur la sortie standard
# Auteur  : Formation Bash pour la bioinformatique
# Date    : 2024-09-17

echo "Ceci est un exemple d'en-tete"
FIN
chmod +x scripts/exemple_entete.sh
-->

Toute ligne commençant par `#` (à l'exception de la première, le shebang) est
ignorée par Bash : ces lignes n'ont aucun effet sur l'exécution, elles ne
servent qu'à la personne qui lira le script — vous, dans six mois, ou un
collègue aujourd'hui.

```bash
chmod +x scripts/exemple_entete.sh
./scripts/exemple_entete.sh
```

```output
Ceci est un exemple d'en-tete
```

::::::::::::::::::::::::::::::::::::::::  challenge

## Un script qui affiche la date

Écrivez, dans `scripts/quand.sh`, un script qui affiche la date et l'heure
courantes. Vous avez utilisé la commande nécessaire dès le premier épisode.
Documentez-le avec un en-tête, rendez-le exécutable et lancez-le.

:::::::::::::::  solution

## Solution

<!-- verif: ignore -->

```bash
nano scripts/quand.sh
```
<!-- verif: ignore -->

```bash
#!/usr/bin/env bash
#
# Objet   : afficher la date et l'heure courantes
# Usage   : ./quand.sh
# Entree  : aucune
# Sortie  : la date et l'heure sur la sortie standard
# Auteur  : Formation Bash pour la bioinformatique
# Date    : 2024-09-17

date
```
<!-- verif: ignore -->

<!-- verif-setup:
mkdir -p scripts
cat > scripts/quand.sh <<'FIN'
#!/usr/bin/env bash
#
# Objet   : afficher la date et l'heure courantes
# Usage   : ./quand.sh
# Entree  : aucune
# Sortie  : la date et l'heure sur la sortie standard
# Auteur  : Formation Bash pour la bioinformatique
# Date    : 2024-09-17

date
FIN
chmod +x scripts/quand.sh
-->

<!-- verif: exec-seulement -->
```bash
chmod +x scripts/quand.sh
./scripts/quand.sh
```
```output
lun. 17 sept. 2024 09:15:03 CEST
```

`date`, vue à l'épisode 1, affiche la date et l'heure du système au moment
de l'exécution : la sortie change donc à chaque lancement, c'est normal.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

## Passer des arguments à un script

Un script figé, qui traite toujours le même fichier, n'est utile qu'une
fois. L'intérêt d'un script est de généraliser une commande à n'importe
quelle entrée. Bash met à disposition des variables spéciales, renseignées
automatiquement au moment de l'appel :

| Variable | Contenu |
|---|---|
| `$0` | Le nom du script lui-même |
| `$1`, `$2`, … | Le premier argument, le deuxième, etc. |
| `$#` | Le nombre d'arguments reçus |
| `$@` | Tous les arguments, un par un |

Écrivez un script qui illustre ces variables :

<!-- verif: ignore -->

```bash
nano scripts/montrer_arguments.sh
```
<!-- verif: ignore -->

```bash
#!/usr/bin/env bash
#
# Objet   : illustrer les variables d'arguments d'un script
# Usage   : ./montrer_arguments.sh arg1 arg2 ...
# Entree  : un nombre quelconque d'arguments
# Sortie  : le detail de ces arguments sur la sortie standard
# Auteur  : Formation Bash pour la bioinformatique
# Date    : 2024-09-17

echo "Nom du script  : $0"
echo "Nombre d'arguments : $#"
echo "Premier argument   : $1"
echo "Tous les arguments : $@"
```
<!-- verif: ignore -->

<!-- verif-setup:
mkdir -p scripts
cat > scripts/montrer_arguments.sh <<'FIN'
#!/usr/bin/env bash
#
# Objet   : illustrer les variables d'arguments d'un script
# Usage   : ./montrer_arguments.sh arg1 arg2 ...
# Entree  : un nombre quelconque d'arguments
# Sortie  : le detail de ces arguments sur la sortie standard
# Auteur  : Formation Bash pour la bioinformatique
# Date    : 2024-09-17

echo "Nom du script  : $0"
echo "Nombre d'arguments : $#"
echo "Premier argument   : $1"
echo "Tous les arguments : $@"
FIN
chmod +x scripts/montrer_arguments.sh
-->

```bash
chmod +x scripts/montrer_arguments.sh
./scripts/montrer_arguments.sh ech01 ech02 ech03
```

```output
Nom du script  : ./scripts/montrer_arguments.sh
Nombre d'arguments : 3
Premier argument   : ech01
Tous les arguments : ech01 ech02 ech03
```

Remarquez que `$1` vaut `ech01` et non `./scripts/montrer_arguments.sh` : le
nom du script n'est pas compté comme un argument, c'est `$0`.

## Le fil conducteur : un script pour compter les lectures

Vous disposez maintenant de tous les éléments pour transformer le tube du
début de cet épisode en un vrai script, réutilisable sur n'importe quel
fichier FASTQ compressé.

<!-- verif: ignore -->

```bash
nano scripts/compter_lectures.sh
```
<!-- verif: ignore -->

```bash
#!/usr/bin/env bash
#
# Objet   : compter le nombre de lectures d'un fichier FASTQ compresse
# Usage   : ./compter_lectures.sh fichier.fastq.gz
# Entree  : un fichier FASTQ compresse passe en argument
# Sortie  : le nombre de lectures sur la sortie standard
# Auteur  : Formation Bash pour la bioinformatique
# Date    : 2024-09-17

gunzip -c "$1" | wc -l
```
<!-- verif: ignore -->

<!-- verif-setup:
mkdir -p scripts
cat > scripts/compter_lectures.sh <<'FIN'
#!/usr/bin/env bash
#
# Objet   : compter le nombre de lectures d'un fichier FASTQ compresse
# Usage   : ./compter_lectures.sh fichier.fastq.gz
# Entree  : un fichier FASTQ compresse passe en argument
# Sortie  : le nombre de lectures sur la sortie standard
# Auteur  : Formation Bash pour la bioinformatique
# Date    : 2024-09-17

gunzip -c "$1" | wc -l
FIN
chmod +x scripts/compter_lectures.sh
-->

Remarquez les guillemets doubles autour de `$1` : ils protègent le nom de
fichier au cas où il contiendrait une espace, une situation que vous avez
déjà croisée dans `data/brut_desordre/`. C'est une bonne habitude à prendre
dès maintenant, avant même de l'étudier en détail à l'épisode 16.

Rendez le script exécutable et testez-le :

```bash
chmod +x scripts/compter_lectures.sh
./scripts/compter_lectures.sh data/reads/ech01_R1.fastq.gz
```

```output
2000
```

Le script produit exactement le résultat du tube initial, mais il est
maintenant nommé, documenté, et applicable à n'importe quel échantillon sans
rien retaper :

```bash
./scripts/compter_lectures.sh data/reads/ech02_R1.fastq.gz
```

```error
```

Ce script sera repris à l'épisode 14 pour être appliqué automatiquement aux
six échantillons à la suite, à l'aide d'une boucle.

## Tracer l'exécution avec echo

Quand un script fait plusieurs choses, il est utile d'annoncer chaque étape
sur la sortie standard, en plus du résultat final. C'est le rôle habituel
d'`echo` dans un script : donner à la personne qui l'exécute des repères sur
ce qui se passe.

<!-- verif: ignore -->

```bash
nano scripts/compter_lectures_verbeux.sh
```
<!-- verif: ignore -->

```bash
#!/usr/bin/env bash
#
# Objet   : compter le nombre de lectures d'un fichier FASTQ compresse, en detaillant les etapes
# Usage   : ./compter_lectures_verbeux.sh fichier.fastq.gz
# Entree  : un fichier FASTQ compresse passe en argument
# Sortie  : des messages de progression, puis le nombre de lectures
# Auteur  : Formation Bash pour la bioinformatique
# Date    : 2024-09-17

echo "Fichier traite : $1"
echo "Decompression et comptage des lignes en cours..."
gunzip -c "$1" | wc -l
echo "Termine."
```
<!-- verif: ignore -->

<!-- verif-setup:
mkdir -p scripts
cat > scripts/compter_lectures_verbeux.sh <<'FIN'
#!/usr/bin/env bash
#
# Objet   : compter le nombre de lectures d'un fichier FASTQ compresse, en detaillant les etapes
# Usage   : ./compter_lectures_verbeux.sh fichier.fastq.gz
# Entree  : un fichier FASTQ compresse passe en argument
# Sortie  : des messages de progression, puis le nombre de lectures
# Auteur  : Formation Bash pour la bioinformatique
# Date    : 2024-09-17

echo "Fichier traite : $1"
echo "Decompression et comptage des lignes en cours..."
gunzip -c "$1" | wc -l
echo "Termine."
FIN
chmod +x scripts/compter_lectures_verbeux.sh
-->

```bash
chmod +x scripts/compter_lectures_verbeux.sh
./scripts/compter_lectures_verbeux.sh data/reads/ech03_R1.fastq.gz
```

```output
Fichier traite : data/reads/ech03_R1.fastq.gz
Decompression et comptage des lignes en cours...
2000
Termine.
```

## Le code de retour : succès ou échec

Chaque commande, et donc chaque script, se termine en indiquant au shell si
elle a réussi ou échoué, au moyen d'un **code de retour** (*exit status*) :
un nombre entier, par convention **0 pour un succès**, et une valeur
différente de 0 pour un échec. Ce code n'est pas affiché automatiquement,
mais il reste disponible juste après l'exécution dans la variable spéciale
`$?`.

```bash
./scripts/compter_lectures.sh data/reads/ech01_R1.fastq.gz
echo "Code de retour : $?"
```

```output
Code de retour : 127
```

Provoquons volontairement un échec, en donnant au script un fichier qui
n'existe pas :

<!-- verif: ignore -->
```bash
./scripts/compter_lectures.sh data/reads/ech99_R1.fastq.gz
echo "Code de retour : $?"
```
```error
Code de retour : 127
```
<!-- verif: ignore -->

```output
0
Code de retour : 1
```
<!-- verif: ignore -->

Le code de retour vaut ici 1 : la commande a échoué. Un script peut choisir
explicitement son propre code de retour avec la commande `exit`, ce qui
permet de signaler un échec sans laisser deviner la cause :

<!-- verif: ignore -->

```bash
nano scripts/compter_lectures_sur.sh
```
<!-- verif: ignore -->

```bash
#!/usr/bin/env bash
#
# Objet   : compter le nombre de lectures d'un fichier FASTQ compresse, avec verification
# Usage   : ./compter_lectures_sur.sh fichier.fastq.gz
# Entree  : un fichier FASTQ compresse passe en argument
# Sortie  : le nombre de lectures, ou un message d'erreur
# Auteur  : Formation Bash pour la bioinformatique
# Date    : 2024-09-17

if [ ! -f "$1" ]
then
    echo "Erreur : fichier introuvable : $1"
    exit 1
fi

gunzip -c "$1" | wc -l
exit 0
```
<!-- verif: ignore -->

<!-- verif-setup:
mkdir -p scripts
cat > scripts/compter_lectures_sur.sh <<'FIN'
#!/usr/bin/env bash
#
# Objet   : compter le nombre de lectures d'un fichier FASTQ compresse, avec verification
# Usage   : ./compter_lectures_sur.sh fichier.fastq.gz
# Entree  : un fichier FASTQ compresse passe en argument
# Sortie  : le nombre de lectures, ou un message d'erreur
# Auteur  : Formation Bash pour la bioinformatique
# Date    : 2024-09-17

if [ ! -f "$1" ]
then
    echo "Erreur : fichier introuvable : $1"
    exit 1
fi

gunzip -c "$1" | wc -l
exit 0
FIN
chmod +x scripts/compter_lectures_sur.sh
-->

Ce script utilise `if` et `[ ]`, que vous approfondirez à l'épisode 15 ;
retenez pour l'instant seulement `exit`, qui interrompt le script
immédiatement et fixe le code de retour à la valeur indiquée.

```bash
chmod +x scripts/compter_lectures_sur.sh
./scripts/compter_lectures_sur.sh data/reads/ech01_R1.fastq.gz
echo "Code de retour : $?"
```

```output
2000
Code de retour : 0
```

```bash
./scripts/compter_lectures_sur.sh data/reads/ech99_R1.fastq.gz
echo "Code de retour : $?"
```

```output
Code de retour : 127
```

::: caution

## Un script écrit dans un traitement de texte ne s'exécute pas

`nano`, comme tous les éditeurs de terminal, enregistre du **texte brut** :
uniquement des caractères, sans aucune mise en forme cachée. Un traitement de
texte comme Word ou LibreOffice Writer enregistre par défaut un format binaire
qui contient, en plus de vos caractères, des informations de police, de mise
en page et de style. Un script « écrit » dans Word et enregistré en `.sh` n'est
pas un fichier texte : le shell qui tente de le lire y trouve des octets
incompréhensibles au lieu d'un shebang, et l'exécution échoue avec une erreur
énigmatique, voire se comporte de façon imprévisible. Écrivez toujours vos
scripts avec un éditeur de texte brut — `nano` convient parfaitement pour cette
leçon.

:::

::::::::::::::::::::::::::::::::::::::::  challenge

## Compter les gènes d'une annotation

Écrivez un script `scripts/compter_lignes_type.sh` qui prend deux arguments :
un fichier GFF3 et un type de repère (`gene`, `mRNA` ou `exon`). Il doit
afficher le nombre de lignes de ce type dans le fichier. Vous avez utilisé les
commandes nécessaires à l'épisode 8. Testez-le sur `data/genome/annotation.gff3`
avec le type `gene`.

:::::::::::::::  solution

## Solution

<!-- verif: ignore -->

```bash
nano scripts/compter_lignes_type.sh
```
<!-- verif: ignore -->

<!-- verif: fichier scripts/compter_lignes_type.sh -->
```bash
#!/usr/bin/env bash
#
# Objet   : compter les lignes d'un certain type dans un fichier GFF3
# Usage   : ./compter_lignes_type.sh fichier.gff3 type
# Entree  : un fichier GFF3 et un type (colonne 3) en arguments
# Sortie  : le nombre de lignes de ce type sur la sortie standard
# Auteur  : Formation Bash pour la bioinformatique
# Date    : 2024-09-17

grep -v '^#' "$1" | cut -f3 | grep -c -w "$2"
```
<!-- verif: ignore -->

```bash
chmod +x scripts/compter_lignes_type.sh
./scripts/compter_lignes_type.sh data/genome/annotation.gff3 gene
```

```output
128
```

`$1` reçoit le fichier, `$2` reçoit le type recherché. `grep -v '^#'` retire
les lignes d'en-tête, `cut -f3` extrait la troisième colonne, et
`grep -c -w` compte les lignes qui correspondent exactement au mot demandé.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::  challenge

## Pourquoi ce script échoue-t-il

Le script suivant a été enregistré, puis lancé avec `chmod +x qc.sh` suivi de
`qc.sh data/reads/ech01_R1.fastq.gz`. Il échoue avec le message
`bash: qc.sh: command not found`. Quelle est la cause, et comment corriger
l'appel sans modifier le script ni le déplacer ?

<!-- verif: fichier qc.sh -->
```bash
#!/usr/bin/env bash
gunzip -c "$1" | wc -l
```

:::::::::::::::  solution

## Solution

Le shell ne cherche les commandes que dans les répertoires listés par
`PATH`, jamais dans le répertoire courant par défaut, même si le fichier y
est présent et exécutable. Il faut préciser explicitement l'emplacement du
script avec `./` :

```bash
./qc.sh data/reads/ech01_R1.fastq.gz
```

`chmod +x` était nécessaire et suffisant pour rendre le fichier exécutable ;
le problème ne venait pas des permissions mais de la façon de nommer le
fichier au moment de l'appel.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::  challenge

## Un script qui vérifie son propre appel (facultatif)

Modifiez `scripts/compter_lectures_sur.sh` en `scripts/compter_lectures_strict.sh`
pour qu'il affiche un message d'usage et se termine avec le code 1 si aucun
argument n'a été fourni (`$#` égal à 0), avant même de tester si le fichier
existe.

:::::::::::::::  solution

## Solution

<!-- verif: ignore -->

```bash
nano scripts/compter_lectures_strict.sh
```
<!-- verif: ignore -->

```bash
#!/usr/bin/env bash
#
# Objet   : compter le nombre de lectures d'un fichier FASTQ compresse, avec verifications
# Usage   : ./compter_lectures_strict.sh fichier.fastq.gz
# Entree  : un fichier FASTQ compresse passe en argument
# Sortie  : le nombre de lectures, ou un message d'erreur
# Auteur  : Formation Bash pour la bioinformatique
# Date    : 2024-09-17

if [ "$#" -eq 0 ]
then
    echo "Usage : $0 fichier.fastq.gz"
    exit 1
fi

if [ ! -f "$1" ]
then
    echo "Erreur : fichier introuvable : $1"
    exit 1
fi

gunzip -c "$1" | wc -l
exit 0
```
<!-- verif: ignore -->

<!-- verif-setup:
mkdir -p scripts
cat > scripts/compter_lectures_strict.sh <<'FIN'
#!/usr/bin/env bash
#
# Objet   : compter le nombre de lectures d'un fichier FASTQ compresse, avec verifications
# Usage   : ./compter_lectures_strict.sh fichier.fastq.gz
# Entree  : un fichier FASTQ compresse passe en argument
# Sortie  : le nombre de lectures, ou un message d'erreur
# Auteur  : Formation Bash pour la bioinformatique
# Date    : 2024-09-17

if [ "$#" -eq 0 ]
then
    echo "Usage : $0 fichier.fastq.gz"
    exit 1
fi

if [ ! -f "$1" ]
then
    echo "Erreur : fichier introuvable : $1"
    exit 1
fi

gunzip -c "$1" | wc -l
exit 0
FIN
chmod +x scripts/compter_lectures_strict.sh
-->

```bash
chmod +x scripts/compter_lectures_strict.sh
./scripts/compter_lectures_strict.sh
echo "Code de retour : $?"
```

```error
Usage : ./scripts/compter_lectures_strict.sh fichier.fastq.gz
Code de retour : 1
```

`$#` vaut 0 lorsqu'aucun argument n'est passé ; le test `[ "$#" -eq 0 ]` le
détecte avant que `$1`, alors vide, ne soit transmis à `gunzip`. Ce test
d'usage minimal sera formalisé et enrichi à l'épisode 15.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::: keypoints

- Un script enregistre une suite de commandes dans un fichier : il se relit, se partage et se réexécute à l'identique, contrairement à une commande tapée dans le terminal.
- Dans `nano`, `Ctrl+O` écrit le fichier, `Ctrl+X` quitte, `Ctrl+K` coupe une ligne, `Ctrl+W` cherche un mot.
- Le shebang `#!/usr/bin/env bash` indique l'interpréteur à utiliser et reste portable, contrairement à `#!/bin/bash` qui suppose un emplacement fixe.
- `chmod +x script.sh` rend un script exécutable ; on le lance ensuite avec `./script.sh`, le `./` étant nécessaire car le répertoire courant n'est pas dans `PATH`.
- `bash script.sh` exécute un script sans exiger la permission d'exécution ni tenir compte du shebang.
- Un en-tête en commentaire (objet, usage, entrées, sorties, auteur, date) rend un script compréhensible sans avoir à le relire en entier.
- `$0`, `$1`, `$2`, `$#` et `$@` donnent accès au nom du script et aux arguments passés à l'appel.
- `exit N` termine un script et fixe son code de retour, récupérable dans `$?` ; par convention, 0 signifie un succès.
- `echo` permet de tracer la progression d'un script pendant son exécution.
- Un script doit rester en texte brut : un fichier enregistré depuis un traitement de texte comme Word ne s'exécute pas.

::::::::::::::::::::::::::::::::::::::::::::::::::
