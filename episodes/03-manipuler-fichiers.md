---
title: "Créer, copier, déplacer, supprimer"
teaching: 35
exercises: 25
---

:::::::::::::::::::::::::::::::::::::::  questions

- Comment créer l'arborescence de travail dans laquelle je vais ranger mes
  résultats ?
- Comment copier, renommer et déplacer des fichiers sans les corrompre ?
- Comment supprimer un fichier sans risquer de perdre un fichier important ?
- Comment désigner plusieurs fichiers à la fois sans les taper un par un ?
- Pourquoi certains noms de fichiers sont-ils pénibles à manipuler, et
  comment l'éviter pour mes propres fichiers ?

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::: objectives

- Créer une arborescence de répertoires en une seule commande.
- Copier, renommer et déplacer des fichiers et des répertoires.
- Supprimer des fichiers et des répertoires en toute connaissance de cause.
- Désigner plusieurs fichiers avec les jokers `*`, `?` et `[...]`.
- Appliquer une convention de nommage qui garde les fichiers triables et
  faciles à manipuler.

::::::::::::::::::::::::::::::::::::::::::::::::::

## Où en sommes-nous

À l'épisode précédent, vous avez appris à vous déplacer dans l'arborescence
de `data/` avec `pwd`, `ls` et `cd`. Vous savez regarder, mais pas encore
agir : vous n'avez créé aucun répertoire, copié aucun fichier. C'est l'objet
de cet épisode.

Placez-vous à la racine de votre projet, celle qui contient `data/` :

<!-- verif: exec-seulement -->
```bash
pwd
```

```output
/home/apprenant/formation-bash
```

Le chemin exact dépend de votre machine ; ce qui compte est que `data/` soit
visible dans le répertoire courant :

```bash
ls
```

```output
_verif.sh
data
```

## Créer l'arborescence de travail

Un principe va guider toute la formation, et vous allez l'appliquer dès
maintenant : **on ne modifie jamais les données brutes de `data/`**. Tout
fichier créé pendant les exercices va dans un répertoire de travail, jamais
dans `data/`. Pour cela, il faut d'abord ce répertoire de travail.

La commande `mkdir` (*make directory*) crée un répertoire :

```bash
mkdir resultats
```

Aucune sortie ne s'affiche : en ligne de commande, l'absence de message est
en général bonne nouvelle, elle signifie que la commande a fait ce qu'on lui
demandait sans rien avoir à signaler. Vérifiez avec `ls` :

```bash
ls
```

```output
_verif.sh
data
resultats
```

Il vous faut encore deux répertoires : `tmp/`, où vous copierez les données
brutes avant de les modifier, et `scripts/`, où vous rangerez plus tard vos
scripts. Vous pourriez taper trois fois `mkdir`, mais l'option `-p` (*parents*)
permet de tout créer en une seule commande, y compris des répertoires
imbriqués qui n'existent pas encore :

```bash
mkdir -p tmp scripts
```

<!-- verif: ordre-libre -->
```bash
ls
```

```output
_verif.sh
data
resultats
scripts
tmp
```

`-p` a un second effet, tout aussi utile : sans elle, `mkdir` échoue si le
répertoire existe déjà. Avec `-p`, relancer la commande ne produit pas
d'erreur. C'est pourquoi `mkdir -p` est la forme que nous utiliserons partout
dans cette formation, y compris pour créer des répertoires imbriqués en une
seule fois :

```bash
mkdir -p resultats/awk resultats/grep
```

<!-- verif: ordre-libre -->
```bash
ls resultats
```

```output
awk
grep
```

::: callout

## Pourquoi toujours `-p`

Sans `-p`, `mkdir sous/dossier` échoue si `sous` n'existe pas encore : `mkdir`
ne crée qu'un niveau à la fois. Avec `-p`, tous les répertoires intermédiaires
manquants sont créés, et la commande ne proteste pas si le répertoire final
existe déjà. Prendre `mkdir -p` comme réflexe évite un message d'erreur sur
deux dans un script.

:::

## Créer un fichier vide : `touch`

`touch` crée un fichier vide s'il n'existe pas, ou met à jour sa date de
dernière modification s'il existe déjà. Dans cette formation, vous
l'utiliserez surtout pour préparer un fichier de sortie, ou pour marquer
qu'une étape est terminée :

```bash
touch resultats/notes.txt
```

<!-- verif: exec-seulement -->
```bash
ls -l resultats
```

```output
total 0
drwxr-xr-x@ 2 baptisteherlemont  staff  64 Sep  1 11:26 awk
drwxr-xr-x@ 2 baptisteherlemont  staff  64 Sep  1 11:26 grep
-rw-r--r--@ 1 baptisteherlemont  staff   0 Sep  1 11:26 notes.txt
```

Le fichier existe, sa taille est de zéro octet : `touch` ne remplit rien, elle
crée seulement une entrée.

## Copier : `cp`

`cp` (*copy*) copie un fichier. C'est la commande qui matérialise le principe
« on ne modifie jamais les données brutes » : avant de travailler sur un
fichier de `data/`, on en copie une version dans `tmp/`.

```bash
cp data/tables/echantillons.tsv tmp/echantillons.tsv
```

```bash
ls tmp
```

```output
echantillons.tsv
```

Si le nom de destination est omis et remplacé par un répertoire, `cp` garde le
nom d'origine :

```bash
cp data/regions/cibles.bed tmp/
```

<!-- verif: ordre-libre -->
```bash
ls tmp
```

```output
cibles.bed
echantillons.tsv
```

Pour copier un répertoire entier, il faut l'option `-r` (*recursive*) :
sans elle, `cp` refuse et affiche une erreur.

<!-- verif: ignore -->
```bash
cp -r data/proteines tmp/proteines_copie
```

```error
```

Le message exact varie selon le système (BSD ou GNU), mais le principe est le
même : `cp` seul ne copie que des fichiers, `cp -r` copie aussi le contenu des
répertoires. Avec `-r`, la copie réussit :

```bash
cp -r data/proteines tmp/proteines_copie
```

```bash
ls tmp/proteines_copie
```

```output
proteines.fa
```

::: caution

## Pas de corbeille

`cp` peut écraser un fichier de destination sans avertissement si celui-ci
existe déjà et que vous n'avez pas de droit de confirmation actif. Il n'y a
ni corbeille ni « annuler » en ligne de commande : un fichier écrasé ou
supprimé est perdu, sauf sauvegarde externe. C'est vrai pour `cp`, ce sera
encore plus vrai pour `mv` et `rm` dans quelques instants. Le réflexe à
prendre dès maintenant : avant toute opération qui touche un fichier
important, vérifiez avec `ls` que vous ciblez bien ce que vous croyez cibler.

:::

## Déplacer et renommer : `mv`

`mv` (*move*) sert à deux usages, qui sont en réalité la même opération : le
fichier change d'emplacement dans l'arborescence, qu'il change de répertoire,
de nom, ou des deux à la fois.

Renommer un fichier, c'est le « déplacer » vers un nouveau nom dans le même
répertoire :

```bash
mv tmp/cibles.bed tmp/cibles_travail.bed
```

<!-- verif: ordre-libre -->
```bash
ls tmp
```

```output
cibles_travail.bed
echantillons.tsv
proteines_copie
```

Déplacer un fichier vers un autre répertoire, sans changer son nom, utilise la
même commande :

```bash
mv tmp/cibles_travail.bed resultats/
```

```bash
ls resultats
```

```output
awk
cibles_travail.bed
grep
notes.txt
```

<!-- verif: ordre-libre -->

```bash
ls tmp
```

```output
echantillons.tsv  proteines_copie
```

<!-- verif: ordre-libre -->

`mv` ne laisse pas de copie derrière elle : contrairement à `cp`, il n'existe
plus qu'un seul exemplaire du fichier après le déplacement. C'est la
différence à retenir entre les deux commandes.

## Supprimer : `rm` et `rmdir`

`rm` (*remove*) supprime des fichiers. `rmdir` supprime un répertoire, mais
seulement s'il est vide :

```bash
mkdir tmp/vide
rmdir tmp/vide
```

<!-- verif: ordre-libre -->
```bash
ls tmp
```

```output
echantillons.tsv
proteines_copie
```

Pour un fichier, `rm` seul suffit :

```bash
rm resultats/cibles_travail.bed
```

<!-- verif: ordre-libre -->
```bash
ls resultats
```

```output
awk
grep
notes.txt
```

::: caution

## `rm` ne demande rien, et il n'y a pas de corbeille

`rm` supprime immédiatement, sans confirmation et sans passer par une
corbeille récupérable. Une fois la commande validée, le fichier n'est plus
récupérable par les moyens ordinaires. C'est la commande la plus risquée que
vous ayez rencontrée jusqu'ici dans cette formation.

:::

Pour se protéger de ce risque, l'option `-i` (*interactive*) demande une
confirmation avant chaque suppression :

<!-- verif: ignore -->
```bash
touch tmp/a_supprimer.txt
rm -i tmp/a_supprimer.txt
```

Le terminal attend une réponse (`y` pour confirmer, `n` pour annuler) : cette
interaction ne peut pas être rejouée automatiquement, c'est pourquoi ce bloc
n'est pas vérifié. Tapez `y` puis Entrée dans votre propre terminal pour
confirmer, ou `n` pour renoncer.

::: callout

## Prenez l'habitude de `rm -i`

Tant que vous manipulez la ligne de commande depuis peu, il est raisonnable
d'utiliser systématiquement `rm -i`, quitte à valider beaucoup de
confirmations au début. L'inconfort de valider chaque suppression est bien
plus faible que celui de reconstruire un jeu de données supprimé par erreur.
Avec l'expérience, vous choisirez vous-même les situations où vous vous en
passez.

:::

Supprimer un répertoire non vide demande l'option `-r` (*recursive*), comme
pour `cp` : elle indique à `rm` de descendre dans le répertoire et de
supprimer tout son contenu avant le répertoire lui-même.

```bash
rm -r tmp/proteines_copie
```

```bash
ls tmp
```

```output
echantillons.tsv
```

Combiner `-r` et `-i` protège des suppressions groupées mal ciblées, au prix
d'une confirmation par fichier rencontré :

<!-- verif: ignore -->
```bash
mkdir -p tmp/essai
touch tmp/essai/a.txt tmp/essai/b.txt
rm -r -i tmp/essai
```

```output
```

::: caution

## `-r` combiné à un joker mal placé

`rm -r *` exécuté dans le mauvais répertoire supprime tout son contenu, sans
distinction entre vos résultats et le reste. Il n'existe pas de commande pour
annuler l'opération après coup. Avant toute commande combinant `rm` et un
joker, vérifiez d'abord avec `ls` en utilisant exactement le même motif, pour
voir ce qui serait réellement supprimé.

:::

## Désigner plusieurs fichiers à la fois : les jokers

Copier, déplacer ou supprimer un par un tous les fichiers d'un échantillon
serait fastidieux. Les **jokers** (*wildcards*) permettent de désigner
plusieurs fichiers en une seule expression.

Le joker `*` remplace n'importe quelle suite de caractères, y compris une
suite vide :

<!-- verif: ordre-libre -->
```bash
ls data/reads/*.fastq.gz
```

```output
data/reads/ech01_R1.fastq.gz  data/reads/ech01_R2.fastq.gz
data/reads/ech02_R1.fastq.gz  data/reads/ech02_R2.fastq.gz
data/reads/ech03_R1.fastq.gz  data/reads/ech03_R2.fastq.gz
data/reads/ech04_R1.fastq.gz  data/reads/ech04_R2.fastq.gz
data/reads/ech05_R1.fastq.gz  data/reads/ech05_R2.fastq.gz
data/reads/ech06_R1.fastq.gz  data/reads/ech06_R2.fastq.gz
```

Le joker `?` remplace exactement un caractère, ni plus ni moins. Il est utile
quand la position du caractère variable est connue et fixe :

<!-- verif: ordre-libre -->
```bash
ls data/reads/ech0?_R1.fastq.gz
```

```output
data/reads/ech01_R1.fastq.gz  data/reads/ech02_R1.fastq.gz
data/reads/ech03_R1.fastq.gz  data/reads/ech04_R1.fastq.gz
data/reads/ech05_R1.fastq.gz  data/reads/ech06_R1.fastq.gz
```

La classe `[...]` remplace un seul caractère parmi ceux listés entre les
crochets. Pour ne sélectionner que les échantillons 1 et 2 :

<!-- verif: ordre-libre -->
```bash
ls data/reads/ech0[12]_R1.fastq.gz
```

```output
data/reads/ech01_R1.fastq.gz  data/reads/ech02_R1.fastq.gz
```

Ce motif se combine avec `*` : pour les deux fichiers R1 et R2 des échantillons
1 et 2 seulement :

<!-- verif: ordre-libre -->
```bash
ls data/reads/ech0[12]_R*.fastq.gz
```

```output
data/reads/ech01_R1.fastq.gz  data/reads/ech01_R2.fastq.gz
data/reads/ech02_R1.fastq.gz  data/reads/ech02_R2.fastq.gz
```

::: callout

## C'est le shell qui développe le joker, pas la commande

`ls` ne sait rien des jokers. Avant même de lancer `ls`, le shell (*shell*)
regarde `data/reads/ech0[12]_R1.fastq.gz`, cherche dans l'arborescence tous
les noms qui correspondent, et remplace le motif par la liste des fichiers
trouvés. `ls` ne reçoit alors que cette liste de noms, comme si vous l'aviez
tapée vous-même. Cela explique un comportement qui surprend souvent au
début : si aucun fichier ne correspond au motif, la plupart des shells
transmettent le motif tel quel à la commande, qui répond alors qu'elle ne
trouve pas de fichier portant ce nom littéral fait d'astérisques et de
crochets. Cela explique aussi pourquoi les jokers fonctionnent avec `cp`,
`mv`, `rm`, ou n'importe quelle autre commande, sans qu'aucune d'elles n'ait
de code spécifique pour les interpréter : le travail est déjà fait quand la
commande démarre.

:::

Cette compréhension permet d'utiliser les jokers avec `cp` pour copier
plusieurs fichiers d'un coup dans `tmp/` :

```bash
cp data/reads/ech01_R*.fastq.gz tmp/
```

<!-- verif: ordre-libre -->
```bash
ls tmp
```

```output
ech01_R1.fastq.gz
ech01_R2.fastq.gz
echantillons.tsv
```

## Des noms de fichiers qui ne posent pas de problème

Le répertoire `data/brut_desordre/` contient des fichiers volontairement
nommés de façon pénible, pour montrer ce qu'il ne faut pas reproduire :

<!-- verif: ordre-libre -->
```bash
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

Regardez ce qui rend ces noms pénibles :

- des **espaces** (`Echantillon 01 - Run mars.fastq`, `ech 03 (copie).fastq`) :
  chaque espace oblige à mettre le nom entre guillemets ou à faire précéder
  chaque espace d'un antislash, sous peine que le shell le découpe en
  plusieurs arguments ;
- des **parenthèses** (`ech 03 (copie).fastq`) : elles ont un sens particulier
  pour le shell et doivent elles aussi être protégées ;
- des **majuscules incohérentes** (`Ech04_...`, `echantillon_02.FASTQ`) : sur
  Linux, `ech01` et `ECH01` sont deux noms différents, ce qui rend le tri et
  la recherche par motif imprévisibles ;
- un **double tiret** (`ech06 -- a refaire.fastq`) : selon la commande, un nom
  commençant par un tiret peut être pris pour une option ;
- une **absence de numérotation cohérente** : rien ne dit que ces huit
  fichiers appartiennent à une même série, ni dans quel ordre les lire.

Pour voir concrètement la conséquence des espaces, essayez de copier ce
fichier sans guillemets :

<!-- verif: ignore -->
```bash
cp data/brut_desordre/Echantillon 01 - Run mars.fastq tmp/
```

```error
```

Le shell a découpé la ligne aux espaces avant même que `cp` ne s'exécute, et a
transmis cinq arguments distincts au lieu d'un seul nom de fichier. La bonne
syntaxe entoure le nom de guillemets doubles :

```bash
cp "data/brut_desordre/Echantillon 01 - Run mars.fastq" tmp/
```

<!-- verif: ordre-libre -->
```bash
ls tmp
```

```output
Echantillon 01 - Run mars.fastq
ech01_R1.fastq.gz
ech01_R2.fastq.gz
echantillons.tsv
```

Cela fonctionne, mais chaque commande sur ce fichier devra désormais porter
des guillemets, et un joker comme `data/brut_desordre/*.fastq` ne pourra
jamais désigner ce fichier proprement dans un script. C'est le prix des
mauvais noms.

::: callout

## Une convention de nommage qui évite ces pièges

Quatre règles suffisent à ne plus jamais rencontrer ce problème sur vos
propres fichiers :

- **pas d'espace** : remplacez-le par un tiret bas `_` ou un tiret `-` ;
- **pas d'accent, pas de majuscule fantaisiste** : préférez des noms
  entièrement en minuscules, comme le fait déjà `data/reads/ech01_R1.fastq.gz` ;
- **des dates au format AAAA-MM-JJ** plutôt que « mars » ou « 12 mars » : ce
  format se trie correctement par ordre chronologique, ce qu'aucun autre
  format de date ne garantit ;
- **une numérotation à zéros non significatifs** (`ech01`, `ech02`, …,
  `ech10`, et non `ech1`, `ech2`, …, `ech10`) : sans les zéros, un tri
  alphabétique classe `ech10` entre `ech1` et `ech2`, ce qui n'est jamais ce
  que l'on veut.

Le jeu de données de cette formation applique déjà cette convention partout
en dehors de `brut_desordre/` : c'est pour cela que `ls data/reads/` affiche
toujours les échantillons dans le bon ordre sans effort.

:::

## Le principe : on ne modifie jamais les données brutes

Vous avez appliqué ce principe presque sans y penser depuis le début de
l'épisode : chaque fois qu'un exercice touchait à un fichier de `data/`, vous
l'avez d'abord copié dans `tmp/`. C'est la règle à retenir pour toute la
formation :

- **`data/` ne se modifie jamais.** Aucune commande d'écriture, de
  renommage ou de suppression ne cible un chemin qui commence par `data/`.
- Un travail exploratoire ou temporaire se fait dans **`tmp/`**, sur une
  copie.
- Un résultat qu'on souhaite conserver va dans **`resultats/`**.

Cette discipline a un coût minime — une commande `cp` supplémentaire — et
un bénéfice décisif : si une manipulation tourne mal, vous recopiez le
fichier d'origine et vous recommencez, au lieu de devoir régénérer tout le
jeu de données.

:::::::::::::::::::::::::::::::::::::::  challenge

## Défi 1 : copier un autre échantillon

En vous inspirant de la commande utilisée plus haut pour `ech01`, copiez dans
`tmp/` les deux fichiers (`R1` et `R2`) de l'échantillon `ech02`.

:::::::::::::::  solution

## Solution

```bash
cp data/reads/ech02_R*.fastq.gz tmp/
```

<!-- verif: ordre-libre -->
```bash
ls tmp
```

```output
Echantillon 01 - Run mars.fastq
ech01_R1.fastq.gz
ech01_R2.fastq.gz
ech02_R1.fastq.gz
ech02_R2.fastq.gz
echantillons.tsv
```

Le joker `*` remplace `1` ou `2` selon le fichier, et `data/reads/ech02_R*.fastq.gz`
désigne donc les deux fichiers de l'échantillon 2, sans qu'il soit nécessaire
de les nommer intégralement.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  challenge

## Défi 2 : préparer un espace de travail par échantillon

Créez, en une seule commande, trois répertoires
`resultats/ech01`, `resultats/ech02` et `resultats/ech03`. Puis copiez la
feuille d'échantillons `data/tables/echantillons.tsv` dans `tmp/`, sous le
nom `echantillons_travail.tsv`.

:::::::::::::::  solution

## Solution

```bash
mkdir -p resultats/ech01 resultats/ech02 resultats/ech03
```

```bash
cp data/tables/echantillons.tsv tmp/echantillons_travail.tsv
```

<!-- verif: ordre-libre -->
```bash
ls resultats
```

```output
awk
ech01
ech02
ech03
grep
notes.txt
```

`mkdir -p` accepte plusieurs noms de répertoires en une seule commande, ce qui
évite de la répéter trois fois. `cp` avec un second argument qui n'existe pas
encore comme répertoire crée un fichier de ce nom : c'est ainsi que la copie
change de nom au passage.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  challenge

## Défi 3 : isoler les échantillons de la lane L003

Consultez `data/tables/echantillons.tsv` pour repérer quels échantillons
appartiennent à la lane `L003`. Copiez ensuite, avec un seul joker sur les
noms de fichiers, tous les fichiers de lectures correspondants dans
`resultats/lane_L003/` (que vous créerez).

:::::::::::::::  solution

## Solution

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

La lane `L003` correspond aux échantillons `ech05` et `ech06`.

```bash
mkdir -p resultats/lane_L003
cp data/reads/ech0[56]_R*.fastq.gz resultats/lane_L003/
```

<!-- verif: ordre-libre -->
```bash
ls resultats/lane_L003
```

```output
ech05_R1.fastq.gz
ech05_R2.fastq.gz
ech06_R1.fastq.gz
ech06_R2.fastq.gz
```

`[56]` désigne un caractère parmi `5` et `6`, ce qui isole précisément les
deux échantillons recherchés sans toucher aux quatre autres.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  challenge

## Défi 4 : pourquoi cette commande échoue-t-elle

Un collègue veut renommer, en une seule commande, le fichier
`data/brut_desordre/echantillon_02.FASTQ` en copie de travail
`tmp/ech02_brut.fastq`. Il tape, depuis la racine du projet :

<!-- verif: ignore -->
```bash
mv data/brut_desordre/echantillon_02.FASTQ tmp/ech02_brut.fastq
```

Cette commande fonctionne, mais votre collègue s'inquiète : « est-ce que je
viens d'abîmer les données brutes ? » Que lui répondez-vous, et que devrait-il
avoir fait avant de lancer cette commande s'il voulait vraiment garder
`data/brut_desordre/` intact ?

:::::::::::::::  solution

## Solution

`mv` déplace le fichier, il ne le duplique pas : après cette commande,
`data/brut_desordre/echantillon_02.FASTQ` n'existe plus, et seul
`tmp/ech02_brut.fastq` subsiste. Le fichier de `data/` a bel et bien été
« abîmé », au sens où il a disparu de son emplacement d'origine.

Le principe de cet épisode — ne jamais modifier `data/` — s'applique aussi
aux déplacements, pas seulement aux modifications de contenu. Pour renommer
une copie de travail sans toucher à l'original, il fallait d'abord copier
avec `cp`, puis renommer la copie avec `mv` :

```bash
cp data/brut_desordre/echantillon_02.FASTQ tmp/ech02_brut.fastq
```

Cette fois, `data/brut_desordre/echantillon_02.FASTQ` reste en place, et
`tmp/ech02_brut.fastq` en est une copie indépendante que l'on peut renommer,
modifier ou supprimer sans conséquence sur les données brutes.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  challenge

## Défi 5 : nettoyer un répertoire de travail (facultatif)

Le répertoire `tmp/` contient à présent plusieurs fichiers accumulés pendant
cet épisode, dont la copie mal nommée `"Echantillon 01 - Run mars.fastq"`.
Supprimez uniquement ce fichier, en utilisant `rm -i`, sans toucher aux
autres fichiers de `tmp/`.

:::::::::::::::  solution

## Solution

```bash
ls tmp
```

```output
Echantillon 01 - Run mars.fastq
ech01_R1.fastq.gz
ech01_R2.fastq.gz
ech02_R1.fastq.gz
ech02_R2.fastq.gz
ech02_brut.fastq
echantillons.tsv
echantillons_travail.tsv
```

<!-- verif: ignore -->

```bash
rm -i "tmp/Echantillon 01 - Run mars.fastq"
```

Comme plus haut, `rm -i` attend votre confirmation : tapez `y` puis Entrée.

Les guillemets sont indispensables ici : sans eux, le shell découperait le
nom aux espaces et `rm` chercherait à supprimer plusieurs fichiers dont aucun
n'existe. `rm -i` demande une confirmation avant d'agir, ce qui est
particulièrement bienvenu sur un nom de fichier aussi difficile à relire d'un
coup d'œil.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::: keypoints

- `mkdir -p resultats tmp scripts` crée toute l'arborescence de travail en une
  commande, sans erreur si elle existe déjà.
- `touch` crée un fichier vide ou met à jour sa date de modification.
- `cp fichier destination` copie un fichier ; `cp -r` est nécessaire pour un
  répertoire.
- `mv` renomme ou déplace, selon que la destination est dans le même
  répertoire ou non ; contrairement à `cp`, elle ne laisse pas de copie.
- `rm` supprime sans confirmation et sans corbeille ; `rm -i` demande une
  confirmation avant chaque suppression, et `rm -r` est nécessaire pour un
  répertoire non vide.
- `rmdir` ne supprime qu'un répertoire vide.
- Les jokers `*`, `?` et `[...]` sont développés par le shell avant que la
  commande ne s'exécute : ils fonctionnent donc de la même façon avec `ls`,
  `cp`, `mv` ou `rm`.
- Des noms de fichiers sans espace, sans accent, en minuscules, avec des
  dates AAAA-MM-JJ et une numérotation à zéros non significatifs, évitent les
  pièges illustrés par `data/brut_desordre/`.
- Les données de `data/` ne se modifient jamais : tout travail se fait sur une
  copie dans `tmp/`, et tout résultat à conserver va dans `resultats/`.

::::::::::::::::::::::::::::::::::::::::::::::::::
