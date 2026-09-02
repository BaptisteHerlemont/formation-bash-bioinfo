---
title: Installation et configuration
---

Avant la formation, vous avez besoin de **trois choses** : un terminal qui
exécute Bash, un éditeur de texte, et le jeu de données. Comptez vingt minutes.

Si quelque chose bloque, ne restez pas seul : écrivez à l'adresse de contact de
la formation **avant** le premier jour. Passer la première heure à réparer une
installation est la meilleure façon de décrocher.

## 1. Un terminal qui exécute Bash

::::::::::::::::::::::::::::::::::::::: discussion

### Linux

Rien à installer. Ouvrez l'application **Terminal** (souvent
<kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>T</kbd>).

:::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::: discussion

### macOS

Rien à installer. Ouvrez **Terminal** (dans `Applications ▸ Utilitaires`, ou par
Spotlight : <kbd>Cmd</kbd>+<kbd>Espace</kbd> puis « Terminal »).

Deux particularités, dont la formation tient compte :

- Le shell par défaut de macOS est **zsh**, pas Bash. Pour la formation, tapez
  `bash` au début de chaque session, ou changez le shell par défaut dans les
  réglages du Terminal. Presque tout est identique ; les différences sont
  signalées dans les épisodes.
- macOS fournit **Bash 3.2** et les outils **BSD** (`sed`, `awk`, `grep`), dont
  certaines options diffèrent des versions GNU installées sur les serveurs
  Linux. La formation n'utilise que des commandes qui fonctionnent dans les deux
  mondes, et signale les différences dans des encadrés « GNU / BSD ».

:::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::: discussion

### Windows

Installez **WSL 2** (« Windows Subsystem for Linux »), qui vous donne un vrai
Linux dans Windows. Dans un PowerShell ouvert **en administrateur** :

```
wsl --install -d Ubuntu
```

Redémarrez, puis lancez **Ubuntu** depuis le menu Démarrer et créez votre nom
d'utilisateur et votre mot de passe Linux. Vous obtenez un terminal Bash
complet, avec les outils GNU.

::: callout

Git Bash (fourni avec Git pour Windows) fonctionne pour la plupart des
épisodes, mais il lui manque des outils utilisés en fin de formation. WSL 2 est
nettement préférable.

:::

Vos fichiers Windows sont accessibles depuis WSL sous `/mnt/c/Users/VotreNom/`.
Travaillez plutôt dans votre répertoire personnel Linux (`~`) : c'est beaucoup
plus rapide.

:::::::::::::::::::::::::::::::::::::::::::::::::::

### Vérifier

Dans le terminal, tapez ceci puis <kbd>Entrée</kbd> :

```bash
bash --version
```

Vous devez voir une ligne commençant par `GNU bash, version`. Le numéro importe
peu : tout ce qui est ≥ 3.2 convient.

## 2. Un éditeur de texte

Nous écrirons des scripts. Il faut un éditeur qui manipule du texte brut — pas
un traitement de texte.

- **Recommandé** : [Visual Studio Code](https://code.visualstudio.com/), gratuit
  et disponible sur les trois systèmes. Sous Windows, ajoutez l'extension
  « WSL » pour éditer vos fichiers Linux.
- **Dans le terminal** : `nano` est installé partout et s'apprend en deux
  minutes. C'est celui que la formation utilise pour les démonstrations, parce
  qu'il fonctionne aussi sur un serveur distant.

::: callout

## N'utilisez pas Word, LibreOffice Writer, Pages ou TextEdit en mode enrichi

Ils insèrent des guillemets typographiques (`"` au lieu de `"`) et des
caractères invisibles qui rendent les scripts inexécutables, avec des messages
d'erreur incompréhensibles.

:::

## 3. Le jeu de données

Téléchargez `donnees-formation-bash.tar.gz` (lien fourni par la formation), puis,
dans le terminal :

```bash
cd ~
mkdir -p formation-bash
cd formation-bash
```

Déplacez l'archive téléchargée dans ce répertoire — vous pouvez le faire avec
votre gestionnaire de fichiers habituel — puis décompressez-la :

```bash
tar -xzf donnees-formation-bash.tar.gz
```

### Vérifier l'installation

<!-- verif: ordre-libre -->

```bash
ls data
```

```output
README.md      brut_desordre  journaux       reads          tables
alignements    genome         proteines      regions        variants
```

La disposition en colonnes dépend de la largeur de votre fenêtre : seuls les
dix noms comptent.

Et un test plus précis :

```bash
wc -l data/genome/annotation.gff3
```

```output
     556 data/genome/annotation.gff3
```

Si vous obtenez ces deux résultats, vous êtes prêt.

::: spoiler

### Le nombre de lignes ne correspond pas ?

Vérifiez que vous êtes bien dans `~/formation-bash` : la commande `pwd` doit
répondre quelque chose qui se termine par `/formation-bash`. Si l'archive a été
décompressée deux fois, vous avez peut-être un `data/data/`. Sous macOS, `wc`
affiche le nombre précédé d'espaces (`     556`) alors que sous Linux il l'affiche
collé à gauche (`556`) : c'est normal, la valeur est la même.

:::

## 4. Facultatif : les outils GNU sur macOS

Les serveurs de calcul utilisent presque tous les outils GNU. Si vous voulez
travailler avec les mêmes versions que celles que vous rencontrerez plus tard,
et que vous avez [Homebrew](https://brew.sh/) :

```bash
brew install coreutils gnu-sed gawk grep bash
```

Ces outils s'installent alors sous les noms `gsed`, `gawk`, `ggrep`, etc., sans
remplacer ceux du système. **Ce n'est pas nécessaire pour la formation** : tous
les exemples fonctionnent avec les outils BSD d'origine.

## Le jeu de données, en deux mots

Il est **entièrement synthétique** : aucune donnée réelle, aucune donnée
sensible, moins de 1 Mio au total. Il imite la forme des données de séquençage
(un petit génome de référence, six échantillons de lectures appariées, une
annotation, des variants, une matrice de comptages) et contient plusieurs
défauts volontaires que les exercices vous feront trouver.

Le détail de chaque fichier est décrit dans `data/README.md`.
