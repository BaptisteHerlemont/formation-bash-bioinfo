---
title: Dépannage
---

Les messages d'erreur du shell sont brefs et rarement aimables, mais ils sont
presque toujours exacts. Cette page recense ceux que vous rencontrerez pendant
la formation, dans l'ordre de fréquence.

## Le terminal ne répond plus

| Symptôme | Cause probable | Solution |
|---|---|---|
| Rien ne se passe, pas d'invite | Une commande tourne encore | <kbd>Ctrl</kbd>+<kbd>C</kbd> |
| L'invite est devenue `>` | Une apostrophe ou un guillemet n'est pas fermé | <kbd>Ctrl</kbd>+<kbd>C</kbd>, puis retapez la commande |
| Un texte défile sans fin | `cat` sur un gros fichier | <kbd>Ctrl</kbd>+<kbd>C</kbd>, utilisez `head` ou `less` |
| Écran figé, plus rien ne s'affiche | <kbd>Ctrl</kbd>+<kbd>S</kbd> a été tapé par erreur | <kbd>Ctrl</kbd>+<kbd>Q</kbd> |
| Bloqué dans un afficheur plein écran | Vous êtes dans `less` ou `man` | `q` |
| Bloqué dans un éditeur inconnu | C'est `vi` | <kbd>Échap</kbd> puis `:q!` puis <kbd>Entrée</kbd> |

::: callout

## <kbd>Ctrl</kbd>+<kbd>C</kbd> est sans danger

Il interrompt la commande en cours, il ne casse ni le terminal ni vos fichiers.
Prenez l'habitude de l'utiliser dès que quelque chose vous échappe.

:::

## Les messages d'erreur les plus fréquents

### `No such file or directory`

```error
ls: data/read: No such file or directory
```

Dans neuf cas sur dix, vous n'êtes pas dans le répertoire que vous croyez, ou le
nom comporte une faute. Le réflexe, dans cet ordre :

```bash
pwd
ls
```

Puis retapez le nom en utilisant la **complétion par tabulation** : si
<kbd>Tab</kbd> ne complète pas, c'est que le nom n'existe pas tel que vous
l'avez commencé.

Attention aussi à la casse : `Data` et `data` sont deux noms différents (y
compris sous macOS, où le comportement dépend du disque — ne comptez pas sur la
tolérance).

### `command not found`

```error
bash: gzcat: command not found
```

Soit la commande n'existe pas sur votre système (c'est le cas de plusieurs
commandes GNU sous macOS), soit il y a une faute de frappe, soit elle est
installée mais pas dans le `PATH`. Vérifiez :

```bash
type gunzip
```

### `Permission denied`

```error
bash: ./mon_script.sh: Permission denied
```

Le fichier n'est pas exécutable :

```bash
chmod +x mon_script.sh
```

Si le message concerne un fichier de `data/` que vous essayez de modifier :
c'est **volontaire**. Les données brutes ne se modifient pas ; travaillez sur
une copie dans `tmp/`.

### `Is a directory`

Vous avez passé un répertoire à une commande qui attend un fichier
(`cat data/`). Ajoutez le nom du fichier, ou utilisez `ls`.

### `Too many levels of symbolic links` ou `Argument list too long`

Vous avez lancé un joker sur une arborescence énorme. Restreignez avec
`find … -maxdepth 1` ou un chemin plus précis.

### `syntax error near unexpected token`

```error
bash: syntax error near unexpected token `done'
```

Presque toujours un `;` ou un `do` manquant dans une boucle, ou une accolade
non fermée. Recopiez la structure canonique :

```bash
for f in *.txt; do
    echo "$f"
done
```

### `[: missing ']'` ou `[: too many arguments`

Les espaces à l'intérieur des crochets sont obligatoires, et la variable doit
être entre guillemets :

```bash
if [ -f "$fichier" ]; then
```

Sans guillemets, une variable vide fait disparaître un argument et le test
devient incompréhensible pour le shell.

### `unary operator expected`

Même cause : une variable vide ou indéfinie dans un test. Ajoutez les
guillemets, et `set -u` en tête de script pour être averti tôt.

### `ambiguous redirect`

Vous avez écrit `> $fichier` alors que `$fichier` contient un espace ou est
vide. Guillemets doubles.

### `gzip: … not in gzip format`

Le fichier n'est pas compressé, malgré son nom, ou il est tronqué.
Vérifiez :

```bash
file data/reads/ech01_R1.fastq.gz
```

### `zcat: can't stat: … .gz.Z`

Vous êtes sous macOS. Utilisez `gunzip -c` à la place de `zcat` — c'est la forme
que la formation emploie partout, précisément pour cette raison.

### `sed: 1: "…": invalid command code`

Vous avez utilisé `sed -i` sous macOS. La formation n'utilise jamais `sed -i` :

```bash
sed 's/a/b/g' fichier > tmp/sortie && mv tmp/sortie fichier
```

### `grep: repetition-operator operand invalid`

Vous utilisez une syntaxe étendue sans `-E`, ou une extension GNU
(`\d`, `\w`) absente de votre `grep`. Utilisez `grep -E` et les classes POSIX
`[[:digit:]]`.

### `awk: syntax error at source line 1`

Le programme awk doit être entre **apostrophes**, pas entre guillemets doubles :
les guillemets doubles laissent le shell interpréter `$1` avant awk.

```bash
awk -F'\t' '{ print $3 }' data/genome/annotation.gff3
```

## Symptômes sans message d'erreur

Ce sont les plus dangereux : la commande réussit et le résultat est faux.

| Symptôme | Cause | Vérification |
|---|---|---|
| `cut -f 2` renvoie la ligne entière | Le séparateur n'est pas une tabulation | `head -1 f \| cat -t` ou `awk -F'\t' '{print NF}'` |
| `sort` classe `10` avant `9` | Tri lexicographique | Ajoutez `-n` |
| `uniq -c` compte mal | Le fichier n'était pas trié | `sort f \| uniq -c` |
| `join` ne renvoie presque rien | Fichiers non triés sur la clé, ou séparateurs différents | Trier les deux fichiers, préciser `-t` |
| Une boucle traite un seul « fichier » | Nom contenant un espace, variable sans guillemets | `for f in *; do echo "$f"; done` |
| Un fichier de sortie est vide | Le tube a échoué en amont, ou `>` a écrasé l'entrée | Reconstruire le tube étage par étage |
| Le nombre de lectures est absurde | Vous avez compté les lignes, pas les lectures | Diviser par 4 |
| `wc -l` renvoie un de moins qu'attendu | Le fichier ne finit pas par un retour à la ligne | `tail -c 1 f \| od -c` |

::: caution

## L'erreur qui coûte le plus cher

```bash
grep '>' data/genome/ref_toy.fa
```

Le `>` n'est pas passé à `grep` : le shell le lit comme une redirection et
**vide** `data/genome/ref_toy.fa`. La forme correcte met le motif entre
apostrophes et ancre la recherche :

```bash
grep -c '^>' data/genome/ref_toy.fa
```

C'est l'une des raisons pour lesquelles les données brutes doivent être en
lecture seule.

:::

## Réinstaller le jeu de données

Si vos fichiers de `data/` ont été modifiés ou supprimés, repartez de l'archive :

```bash
cd ~/formation-bash
rm -rf data
tar -xzf donnees-formation-bash.tar.gz
ls data
```

Vos scripts et vos résultats, s'ils sont bien dans `scripts/` et `resultats/`,
ne sont pas touchés.

## La méthode générale, quand rien de tout cela ne s'applique

1. Lisez le message en entier, y compris le nom de la commande au début : il
   vous dit **qui** se plaint.
2. Ajoutez `echo` devant la commande pour voir ce que le shell a réellement
   construit après substitution des variables et des jokers.
3. Coupez le tube et exécutez les étages un par un, en terminant chacun par
   `| head`.
4. Réduisez le problème : la même commande sur un fichier de trois lignes,
   fabriqué avec `head -3`.
5. Demandez à un voisin de relire votre ligne à voix haute. Les guillemets
   manquants s'entendent.
