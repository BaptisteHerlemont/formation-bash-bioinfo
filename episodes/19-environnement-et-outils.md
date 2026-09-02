---
title: "Environnement de travail et installation d'outils"
teaching: 25
exercises: 15
---

::::::::::::::::::::::::::::::::::::::::::::::::: questions

- Comment le shell trouve-t-il la commande que je viens de taper ?
- Comment installer un petit outil sans avoir les droits administrateur ?
- Où dois-je écrire mes réglages pour qu'ils soient chargés à chaque ouverture de terminal ?

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::::::::::: objectives

- Afficher et interpréter la variable `PATH`.
- Distinguer `which`, `type` et `command -v` selon ce qu'ils recherchent.
- Créer un répertoire personnel `~/bin` et l'ajouter au `PATH`.
- Extraire une archive `tar`, rendre un script exécutable et l'installer sans droits administrateur.
- Expliquer la différence entre `~/.bashrc`, `~/.bash_profile` et `~/.profile`.

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::: prereq

Cet épisode suppose que vous savez écrire un script avec un shebang et le
rendre exécutable (épisode 13), et que vous êtes à l'aise avec les variables
et les guillemets (épisode 16).

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

Depuis dix-huit épisodes, vous utilisez `grep`, `awk`, `sed`, ou vos propres
scripts, en tapant simplement leur nom. Vous ne vous êtes jamais demandé
comment le shell (*shell*) savait où aller les chercher. C'est la question de
cet épisode : comprendre comment une commande est trouvée, puis utiliser cette
compréhension pour installer vous-même un outil, sans droits administrateur,
dans un répertoire qui vous appartient.

Préparez un espace de travail pour cet épisode :

```bash
mkdir -p resultats tmp scripts
```

## L'environnement du shell

Chaque fois que vous ouvrez un terminal, le shell dispose d'un ensemble de
variables déjà définies : elles forment son environnement (*environment*). La
commande `env` les affiche toutes.

<!-- verif: exec-seulement -->
```bash
env | head -n 5
```

```output
OPERON_CPU_COUNT=10
SHELL=/bin/zsh
PYTHONNOUSERSITE=1
TMPDIR=/Users/baptisteherlemont/.claude-science/orgs/a574fbaa-f6e5-4d9e-b619-e4b37377a653/workspaces/bbb0279d-6beb-4970-bcb6-1cd1e7a13dc6/.tmp
OPENBLAS_NUM_THREADS=8
```

Le contenu exact dépend de votre machine, de votre système et de la façon
dont vous avez ouvert le terminal : ne vous étonnez pas si vos cinq premières
lignes diffèrent de l'exemple. Une variable en particulier va nous occuper
tout cet épisode : `PATH`.

<!-- verif: exec-seulement -->
```bash
echo "$PATH"
```

```output
/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
```

`PATH` est une liste de répertoires séparés par des deux-points (`:`). Quand
vous tapez une commande, le shell parcourt cette liste, dans l'ordre, et
exécute la première commande de ce nom qu'il trouve. C'est pour cela que
l'ordre des répertoires dans `PATH` a de l'importance : si deux répertoires
contiennent chacun un programme nommé `compter`, celui du répertoire le plus
à gauche dans `PATH` gagne.

::: callout

## Pourquoi `./script.sh` mais jamais `script.sh` seul

À l'épisode 13, vous avez appris à lancer un script avec `./nom_du_script.sh`.
La barre oblique n'est pas décorative : elle dit au shell « ne cherche pas
dans `PATH`, va directement à ce chemin ». Sans elle, le shell chercherait un
programme nommé `nom_du_script.sh` dans les répertoires de `PATH` — et, sauf
cas particulier, ne le trouverait pas, puisque le répertoire courant n'y
figure pas.

:::

## which, type et command -v : trois façons de demander « qu'est-ce que c'est »

Ces trois commandes répondent à la même question — « que va-t-il se passer si
je tape ce nom ? » — mais elles ne regardent pas au même endroit.

<!-- verif: exec-seulement -->
```bash
which grep
```

```output
/usr/bin/grep
```

`which` cherche uniquement dans les répertoires de `PATH` et affiche le
chemin du premier exécutable trouvé. Il ne sait rien des alias ni des
fonctions du shell.

<!-- verif: exec-seulement -->
```bash
type grep
```

```output
grep est /usr/bin/grep
```

`type` est une commande interne du shell (*builtin*) : elle sait dire si un
nom désigne un exécutable sur le disque, un alias, une fonction, ou une
commande interne du shell elle-même. Essayez-la sur une commande interne :

```bash
type cd
```

```output
cd is a shell builtin
```

`which cd` ne donnerait rien d'utile, puisque `cd` n'est pas un fichier
exécutable dans `PATH` : c'est une primitive intégrée au shell.

Enfin, `command -v` rend un résultat proche de `type`, mais dans un format
pensé pour être lu par un script plutôt que par un œil humain — c'est celui
que vous utiliserez dans vos propres scripts pour vérifier qu'un outil est
disponible avant de l'utiliser.

```bash
command -v grep
```

```output
/usr/bin/grep
```

```bash
command -v cd
```

```output
cd
```

::: callout

## Lequel utiliser

Pour une vérification manuelle rapide, `which` suffit. Pour comprendre
pourquoi une commande se comporte de façon inattendue (un alias qui
interfère, par exemple), `type` donne la réponse complète. Dans un script,
préférez toujours `command -v`, car son comportement est standardisé
et fonctionne même quand `which` est absent du système.

:::

:::::::::::::::::::::::::::::::::::::::::::::::::::: challenge

## Où se trouve awk

Sans consulter la documentation, trouvez le chemin absolu de l'exécutable
`awk` sur votre machine, avec deux commandes différentes.

::::::::::::::::: solution

## Solution

```bash
which awk
```

```bash
command -v awk
```

Les deux devraient afficher le même chemin, par exemple `/usr/bin/awk`.
`which` le trouve en parcourant `PATH` ; `command -v` fait la même recherche
mais dans un format stable, conçu pour être utilisé par un script plutôt que
lu à l'écran.

:::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

## export : faire passer une variable aux commandes que vous lancez

Vous avez rencontré `export` à l'épisode 16, pour transmettre une variable à
des sous-processus. `PATH` est exactement ce genre de variable : elle doit
être exportée pour que les programmes que vous lancez — pas seulement le
shell lui-même — sachent où chercher, à leur tour, d'autres programmes.

```bash
MON_REPERTOIRE=tmp
export MON_REPERTOIRE
```

Une variable non exportée reste privée au shell courant ; une variable
exportée est copiée dans l'environnement de chaque commande lancée depuis ce
shell. C'est cette même mécanique que nous allons utiliser pour ajouter un
répertoire à `PATH`.

## Créer son propre répertoire de commandes

Vous n'avez pas les droits administrateur sur votre portable professionnel,
et vous ne les aurez peut-être jamais. Cela ne vous empêche pas d'installer
des outils : il suffit de les placer dans un répertoire qui vous appartient,
et d'ajouter ce répertoire à `PATH`. La convention, sur toutes les machines
Unix, est d'appeler ce répertoire `~/bin`.

```bash
mkdir -p ~/bin
```

Ajoutons-le à `PATH`, pour le shell courant :

```bash
export PATH="$HOME/bin:$PATH"
```

<!-- verif: exec-seulement -->
```bash
echo "$PATH"
```

```output
/home/apprenant/bin:/Users/baptisteherlemont/.claude-science/orgs/a574fbaa-f6e5-4d9e-b619-e4b37377a653/workspaces/bbb0279d-6beb-4970-bcb6-1cd1e7a13dc6/.venv/python/bin:/Users/baptisteherlemont/.claude-science/conda/envs/python/bin:/usr/bin:/bin:/usr/sbin:/sbin
```

Notez la construction : `"$HOME/bin:$PATH"` place le nouveau répertoire
**avant** l'ancien contenu de `PATH`. Si vous installez dans `~/bin` un
programme qui porte le même nom qu'un programme déjà installé sur le système,
c'est le vôtre qui sera trouvé en premier — ce qui est en général ce que
vous voulez pendant que vous développez un outil.

::: caution

## N'ajoutez jamais `.` au `PATH`

Il peut être tentant d'ajouter le répertoire courant au `PATH` avec
`export PATH=".:$PATH"`, pour pouvoir taper `mon_script.sh` au lieu de
`./mon_script.sh`. Ne le faites pas. Le répertoire courant change sans cesse
selon l'endroit où vous vous trouvez ; un fichier nommé `ls`, `cd` ou `cp`
déposé — par erreur ou par malveillance — dans un répertoire où vous vous
déplacez ensuite s'exécuterait à la place de la vraie commande, sans que rien
ne vous avertisse. C'est une faille de sécurité connue et documentée, pas une
simple maladresse : aucune distribution Unix ne met `.` dans `PATH` par
défaut, et cette leçon ne le fait pas non plus.

:::

Cet `export` ne vaut que pour le shell actuellement ouvert : si vous fermez
le terminal, il disparaît. Pour qu'il soit rétabli à chaque nouvelle session,
il doit être écrit dans un fichier de démarrage — c'est l'objet de la section
suivante.

## Les fichiers de démarrage du shell : `~/.bashrc`, `~/.bash_profile`, `~/.profile`

Bash lit un fichier de configuration à chaque démarrage, mais lequel dépend
de la façon dont il a été lancé.

Un **shell de connexion** (*login shell*) est celui que vous obtenez quand
vous vous connectez : par une ouverture de session texte, par `ssh`, ou —
particularité à connaître — par l'application Terminal de macOS, qui ouvre
systématiquement un shell de connexion pour chaque nouvelle fenêtre. Un shell
de connexion lit, dans cet ordre, le premier de ces fichiers qu'il trouve :
`~/.bash_profile`, puis à défaut `~/.bash_login`, puis à défaut `~/.profile`.

Un **shell non-connexion** (*non-login shell*) est celui que vous obtenez en
ouvrant un nouvel onglet dans un terminal déjà lancé sous Linux, ou en
exécutant `bash` depuis un shell existant. Celui-ci lit `~/.bashrc`.

| Fichier | Lu par | Cas typique |
|---|---|---|
| `~/.bashrc` | shell interactif non-connexion | nouvel onglet, nouveau terminal sous Linux/WSL |
| `~/.bash_profile` | shell de connexion | connexion texte, `ssh`, **chaque fenêtre du Terminal macOS** |
| `~/.profile` | shell de connexion, si `~/.bash_profile` est absent | shells compatibles POSIX autres que Bash |

::: callout

## La particularité macOS

Sous Linux et sous WSL, ouvrir un nouveau terminal donne le plus souvent un
shell non-connexion : c'est `~/.bashrc` qui est lu. Sous macOS, l'application
Terminal ouvre un shell de connexion à **chaque nouvelle fenêtre**, ce qui
signifie que c'est `~/.bash_profile` qui est lu, et que `~/.bashrc` serait
ignoré si on y écrivait quoi que ce soit. La pratique la plus répandue, sur
toutes les plates-formes, consiste à écrire ses réglages dans `~/.bashrc`,
puis à faire en sorte que `~/.bash_profile` le charge explicitement, par ces
trois lignes :

```
if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi
```

Ainsi, où que vous soyez, `~/.bashrc` est toujours lu, et vous n'avez qu'un
seul fichier à tenir à jour.

:::

C'est dans `~/.bashrc` que vous ajouteriez, en temps normal, la ligne
`export PATH="$HOME/bin:$PATH"`, pour ne pas avoir à la retaper à chaque
ouverture de terminal. Nous ne modifions pas votre fichier réel dans cette
leçon — vous le ferez vous-même, une fois, en dehors de ce cours — mais voici
exactement ce que vous y ajouteriez :

<!-- verif: ignore -->
```bash
# Ajout personnel : mes outils installés sans droits administrateur
export PATH="$HOME/bin:$PATH"
```

Pour observer le contenu actuel de votre fichier sans le modifier, vous
pouvez l'ouvrir en lecture avec `less ~/.bashrc` (touche `q` pour sortir) ou
l'éditer avec `nano ~/.bashrc` si vous souhaitez y ajouter la ligne
ci-dessus.

<!-- verif: ignore -->
```bash
less ~/.bashrc
```

## alias : un raccourci, mais seulement pour vous, et seulement interactivement

Une commande souvent répétée peut être raccourcie par un alias.

```bash
alias ll='ls -l -h'
```

<!-- verif: ordre-libre -->
<!-- verif: ignore -->
```bash
ll data
```

```output
total 40
drwxr-xr-x  2 utilisateur utilisateur  4096 alignements
drwxr-xr-x  2 utilisateur utilisateur  4096 brut_desordre
drwxr-xr-x  2 utilisateur utilisateur  4096 genome
drwxr-xr-x  2 utilisateur utilisateur  4096 journaux
-rw-r--r--  1 utilisateur utilisateur  4096 README.md
drwxr-xr-x  2 utilisateur utilisateur  4096 proteines
drwxr-xr-x  2 utilisateur utilisateur  4096 reads
drwxr-xr-x  2 utilisateur utilisateur  4096 regions
drwxr-xr-x  2 utilisateur utilisateur  4096 tables
drwxr-xr-x  2 utilisateur utilisateur  4096 variants
```

Un alias est pratique, mais il a une limite importante à connaître avant de
s'y fier : il n'existe que dans le shell interactif où il a été défini. Un
script qui utilise `ll` échouera, même exécuté par vous, même sur la machine
où l'alias est défini — parce qu'un script s'exécute dans un nouveau shell,
qui ne connaît pas les alias définis ailleurs.

<!-- verif: ignore -->
```bash
printf '#!/usr/bin/env bash\nll data\n' > tmp/test_alias.sh
chmod +x tmp/test_alias.sh
./tmp/test_alias.sh
```

```error
```

C'est une différence essentielle avec une fonction shell, vue à l'épisode 17 :
une fonction peut être exportée à des sous-shells, un alias jamais. Pour tout
ce qui doit fonctionner dans un script, écrivez la commande en entier, ou
utilisez une fonction — jamais un alias.

::::::::::::::::::::::::::::::::::::::::::::::::::::: challenge

## Un alias pour compter les lectures

Créez un alias nommé `nblectures` qui affiche le nombre de lignes d'un fichier
FASTQ compressé passé en argument, en utilisant `gunzip -c` et `wc -l`. Testez-le
sur `data/reads/ech02_R1.fastq.gz`. Un alias accepte-t-il des arguments comme une
fonction ?

::::::::::::::::: solution

## Solution

```bash
alias nblectures='gunzip -c'
```

En réalité, un alias ne peut recevoir un argument qu'en fin de ligne, ajouté
tel quel après le texte de l'alias : il ne peut pas, comme une fonction,
placer cet argument où on le souhaite ni le combiner avec un tube. Pour ce
besoin précis, une fonction shell (épisode 17) est le bon outil :

```bash
nblectures() {
    gunzip -c "$1" | wc -l
}
nblectures data/reads/ech02_R1.fastq.gz
```

```output
    2000
```

C'est une bonne illustration de la limite des alias : dès qu'il faut combiner
plusieurs commandes ou positionner un argument autrement qu'à la fin, il faut
une fonction, pas un alias.

:::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

## Installer un outil dans `~/bin`, sans droits administrateur

Voici la situation que vous rencontrerez régulièrement : un collègue vous
envoie une petite archive contenant un script utile. Vous n'avez pas les
droits pour l'installer « proprement » avec un gestionnaire de paquets
système, et vous n'en avez pas besoin : `~/bin` suffit.

Fabriquons cette archive nous-mêmes, pour reproduire la situation sans avoir
besoin d'une connexion réseau. Il s'agit d'un petit outil qui compte le
nombre de lectures d'un fichier FASTQ compressé — exactement la fonction que
vous venez d'écrire, mais sous la forme d'un outil autonome.

<!-- verif-setup:
mkdir -p tmp
cat > tmp/compter_lectures.sh <<'FIN'
#!/usr/bin/env bash
# Compte le nombre de lectures d'un fichier FASTQ compresse
# Usage : compter_lectures.sh fichier.fastq.gz
set -euo pipefail
lignes=$(gunzip -c "$1" | wc -l)
echo $((lignes / 4))
FIN
cd tmp && tar -czf outil-compte-lectures.tar.gz compter_lectures.sh && cd ..
-->

Créez ce script avec `nano tmp/compter_lectures.sh` :

```
#!/usr/bin/env bash
# Compte le nombre de lectures d'un fichier FASTQ compresse
# Usage : compter_lectures.sh fichier.fastq.gz
set -euo pipefail
lignes=$(gunzip -c "$1" | wc -l)
echo $((lignes / 4))
```

Puis empaquetez-le en archive (*archive*), pour simuler ce que vous recevriez
d'un collègue :

```bash
cd tmp
tar -czf outil-compte-lectures.tar.gz compter_lectures.sh
cd ..
```

L'option `-c` crée une archive, `-z` la compresse avec `gzip`, `-f` indique
le nom de fichier de l'archive. Avant d'extraire quoi que ce soit, il est
prudent de regarder ce qu'elle contient, avec `-t` (tester, lister) au lieu
de `-x` (extraire) :

```bash
tar -tzf tmp/outil-compte-lectures.tar.gz
```

```output
compter_lectures.sh
```

Une seule entrée, un simple fichier : rien d'inquiétant, on peut extraire. Une
archive reçue d'ailleurs pourrait contenir des chemins commençant par `/` ou
remontant avec `..`, ce qui écrirait hors du répertoire d'extraction — un
bon réflexe est toujours de lister avant d'extraire.

```bash
mkdir -p tmp/extraction
tar -xzf tmp/outil-compte-lectures.tar.gz -C tmp/extraction
ls tmp/extraction
```

```output
compter_lectures.sh
```

`-x` extrait, `-C tmp/extraction` indique dans quel répertoire — sans cette
option, `tar` extrairait dans le répertoire courant. Le fichier extrait n'est,
pour l'instant, pas exécutable :

<!-- verif: exec-seulement -->
```bash
ls -l tmp/extraction/compter_lectures.sh
```

```output
-rw-r--r--@ 1 baptisteherlemont  staff  199 Sep  1 11:26 tmp/extraction/compter_lectures.sh
```

Deux étapes restent à faire : le rendre exécutable, puis le déplacer dans
`~/bin` pour qu'il devienne une commande disponible partout, comme `grep` ou
`awk`.

```bash
chmod +x tmp/extraction/compter_lectures.sh
cp tmp/extraction/compter_lectures.sh ~/bin/compter_lectures.sh
```

```bash
command -v compter_lectures.sh
```

```output
/home/apprenant/bin/compter_lectures.sh
```

L'outil est trouvé, exactement comme `grep` ou `awk`, parce qu'il se trouve
dans un répertoire listé dans `PATH` — celui que vous avez ajouté plus tôt
dans cet épisode. Utilisons-le :

```bash
compter_lectures.sh data/reads/ech03_R1.fastq.gz
```

```output
500
```

Vous venez d'installer un outil sans droits administrateur, sans gestionnaire
de paquets, et sans rien modifier hors de votre répertoire personnel. C'est
exactement ainsi que fonctionnent, en substance, la plupart des outils
bioinformatiques distribués sous forme d'archives à compiler ou de binaires
précompilés.

::::::::::::::::::::::::::::::::::::::::::::::::::::: challenge

## Un deuxième outil

Reprenez les mêmes étapes pour installer, sous le nom `~/bin/compter_variants_pass.sh`,
un script qui compte le nombre de variants dont la colonne `FILTER` vaut exactement
`PASS` dans un fichier VCF passé en argument. Testez-le sur
`data/variants/cohorte.vcf`.

::::::::::::::::: solution

## Solution

Créez le script avec `nano tmp/compter_variants_pass.sh` :

```
#!/usr/bin/env bash
# Compte les variants dont la colonne FILTER vaut PASS
# Usage : compter_variants_pass.sh fichier.vcf
set -euo pipefail
grep -v '^#' "$1" | awk -F'\t' '$7 == "PASS"' | wc -l
```

<!-- verif: exec-seulement -->
```bash
chmod +x tmp/compter_variants_pass.sh
cp tmp/compter_variants_pass.sh ~/bin/compter_variants_pass.sh
compter_variants_pass.sh data/variants/cohorte.vcf
```

```output
     165
```

L'archive n'était ici qu'une étape de démonstration : ce qui compte, dans
l'installation, ce sont les trois gestes toujours identiques — rendre le
script exécutable avec `chmod +x`, le placer dans un répertoire de `PATH`, et
vérifier avec `command -v` qu'il est bien trouvé.

:::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::::::::::::::: challenge

## Pourquoi cette installation échoue-t-elle

Un collègue vous décrit sa méthode : il a copié son script dans
`~/bin/mon_outil.sh`, mais quand il tape `mon_outil.sh`, le shell répond
`command not found`. Il a bien vérifié que le fichier existe avec `ls ~/bin`.
Quelles sont les deux causes possibles, et comment les diagnostiquer sans
rien réinstaller ?

::::::::::::::::: solution

## Solution

Deux causes indépendantes peuvent produire ce message, et il faut les
distinguer avant d'agir :

```bash
echo "$PATH"
```

Si `$HOME/bin` n'apparaît pas dans le résultat, `~/bin` n'a jamais été ajouté
à `PATH` dans ce shell — la commande `export PATH="$HOME/bin:$PATH"` n'a
peut-être été tapée que dans un terminal précédent, ou écrite dans le mauvais
fichier de démarrage (par exemple `~/.bashrc` sous macOS, jamais lu par un
shell de connexion).

<!-- verif: ignore -->
```bash
ls -l ~/bin/mon_outil.sh
```

Si le `x` n'apparaît pas dans les permissions affichées (par exemple
`-rw-r--r--` au lieu de `-rwxr-xr-x`), le fichier existe bien mais n'est pas
exécutable : il manque `chmod +x ~/bin/mon_outil.sh`. Les deux causes sont
indépendantes : un fichier exécutable dans un répertoire absent de `PATH` ne
sera pas trouvé, et un fichier non exécutable dans un répertoire présent dans
`PATH` produira aussi `command not found`.

:::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

## Et pour des besoins plus complexes

Installer un script isolé dans `~/bin` fonctionne bien pour un outil simple,
sans dépendance particulière. Dès qu'un outil bioinformatique nécessite une
version précise d'un langage, des bibliothèques partagées, ou doit coexister
avec une autre version de lui-même pour un autre projet, cette méthode
artisanale atteint ses limites. Des gestionnaires d'environnements comme
conda ou mamba automatisent l'installation d'outils et de leurs dépendances
dans des environnements isolés et reproductibles. Sur les serveurs de calcul
partagés, les modules d'environnement offrent un mécanisme comparable, propre
à chaque infrastructure. Ces outils, ainsi que les conteneurs, qui isolent un
outil avec l'intégralité de son système, font l'objet de la seconde
formation.

::::::::::::::::::::::::::::::::::::::::::::::::::::: keypoints

- `echo "$PATH"` affiche la liste ordonnée des répertoires où le shell cherche les commandes.
- `which` interroge `PATH`, `type` interroge aussi les alias et fonctions, `command -v` donne une réponse stable pour les scripts.
- `export PATH="$HOME/bin:$PATH"` ajoute un répertoire personnel en tête de `PATH`, sans droits administrateur.
- N'ajoutez jamais `.` au `PATH` : c'est une faille de sécurité connue.
- `~/.bashrc` est lu par un shell interactif non-connexion ; `~/.bash_profile` par un shell de connexion, ce qui inclut chaque fenêtre du Terminal macOS.
- Un `alias` n'existe que dans le shell interactif qui l'a défini : il est invisible dans un script.
- Installer un outil sans droits administrateur suit toujours les mêmes étapes : `tar -tzf` pour inspecter, `tar -xzf` pour extraire, `chmod +x` pour rendre exécutable, puis copie dans un répertoire de `PATH`.
- conda/mamba, les modules d'environnement et les conteneurs automatisent cette gestion pour des cas plus complexes : ils font l'objet de la seconde formation.

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
