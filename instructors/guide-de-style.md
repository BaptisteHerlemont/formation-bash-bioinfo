---
title: Guide de style de la leçon
---

Ce guide fixe les conventions de rédaction de la leçon. Il s'adresse à toute
personne qui écrit ou modifie un épisode. Il est volontairement directif : c'est
ce qui permet à 21 épisodes écrits à plusieurs mains de se lire comme un seul
texte.

## 1. Le principe directeur

**Le fil conducteur est un projet, pas un catalogue de commandes.** Une personne
a reçu six échantillons de séquençage et doit les traiter. Chaque épisode
répond à une question concrète qu'elle se pose à ce moment-là. Une commande
n'est jamais introduite « parce qu'elle existe » mais parce qu'elle résout le
problème du moment.

Corollaire : **aucune commande sans un défi qui la fait pratiquer.**

## 2. Structure d'un épisode

### En-tête

```markdown
---
title: "Titre de l'épisode"
teaching: 30
exercises: 20
---
```

`teaching` et `exercises` sont en minutes et doivent correspondre à
`plan_formation.csv`, qui fait référence pour le volume horaire.

### Bloc questions / objectifs, immédiatement après l'en-tête

```markdown
:::::::::::::::::::::::::::::::::::::::  questions

- Comment savoir où je me trouve dans l'arborescence ?
- Comment atteindre un répertoire sans le chercher à la souris ?

::::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::: objectives

- Afficher le répertoire de travail courant.
- Distinguer un chemin absolu d'un chemin relatif.

::::::::::::::::::::::::::::::::::::::::::::::::::
```

Les **questions** sont formulées du point de vue de l'apprenant, à la première
personne. Les **objectifs** commencent par un verbe à l'infinitif et décrivent
une action observable : « afficher », « extraire », « écrire un script qui… ».
Jamais « comprendre », « connaître », « être familier avec » — ce ne sont pas
des objectifs vérifiables.

Trois à cinq entrées par bloc. Au-delà, l'épisode est trop gros : découpez-le.

### Points clés, en toute fin d'épisode

```markdown
:::::::::::::::::::::::::::::::::::::::: keypoints

- `pwd` affiche le répertoire courant.
- Un chemin qui commence par `/` est absolu.

::::::::::::::::::::::::::::::::::::::::::::::::::
```

Un point clé par objectif, formulé comme une phrase mémorisable, avec la
commande en `code`.

### Encadrés disponibles

| Bloc | Usage dans cette leçon |
|---|---|
| `challenge` | Un exercice. Contient toujours une `solution` imbriquée. |
| `solution` | Imbriquée dans `challenge`. Donne la commande **et** l'explication. |
| `callout` | Une précision utile mais non essentielle au fil. |
| `caution` | Un piège qui fait perdre des données ou du temps. Usage rare, donc efficace. |
| `spoiler` | Contenu replié : dépannage, digression, réponse à « et si ça ne marche pas ? ». |
| `instructor` | Note visible uniquement dans la vue formateur. |
| `prereq` | Ce qu'il faut avoir acquis avant l'épisode. Au plus un par épisode. |
| `discussion` | Variante selon le système d'exploitation, question ouverte au groupe. |

Syntaxe exacte d'un défi, à recopier telle quelle :

```markdown
:::::::::::::::::::::::::::::::::::::::  challenge

## Combien de lectures dans l'échantillon 1 ?

Un fichier FASTQ consacre quatre lignes à chaque lecture. Trouvez le nombre de
lectures de `data/reads/ech01_R1.fastq.gz`.

:::::::::::::::  solution

## Solution

```bash
gunzip -c data/reads/ech01_R1.fastq.gz | wc -l
```

```output
    2000
```

2 000 lignes, donc 2 000 / 4 = **500 lectures**. `gunzip -c` écrit le contenu
décompressé sur la sortie standard sans toucher au fichier ; `wc -l` compte les
lignes reçues.

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::
```

La longueur des `:` n'a pas d'importance pour Pandoc (minimum trois), mais
gardez ces longueurs-là : elles rendent l'imbrication lisible dans l'éditeur.

## 3. Blocs de code

- La commande va dans un bloc ```` ```bash ````, **sans l'invite** `$` : elle est
  déjà à l'écran, et la recopier empêche le copier-coller.
- La sortie va dans un bloc ```` ```output ```` **immédiatement après**.
- Un message d'erreur va dans un bloc ```` ```error ````.
- Une commande, un bloc. N'enchaînez pas cinq commandes dans un même bloc si
  vous en commentez les sorties une par une.
- Les sorties sont **réelles**, copiées depuis un terminal, jamais reconstituées
  de mémoire. Une sortie inventée finit toujours par se voir.
- Les sorties longues sont tronquées explicitement, avec une ligne `[...]`, et
  le bloc est marqué `<!-- verif: ordre-libre -->` ou `<!-- verif: exec-seulement -->`
  (voir §6).

## 4. Portabilité : la règle la plus contraignante

Les participants arrivent avec Linux, macOS et WSL. macOS fournit **Bash 3.2**
et les outils **BSD** ; les serveurs de calcul fournissent Bash 5 et les outils
**GNU**. Le corps du texte n'utilise que ce qui fonctionne partout.

### Interdit dans le corps du texte

| À ne pas utiliser | Pourquoi | À utiliser à la place |
|---|---|---|
| `zcat fichier.gz` | Échoue sous macOS (cherche `fichier.gz.Z`) | `gunzip -c fichier.gz` |
| `sed -i` | Syntaxe incompatible : GNU `-i`, BSD `-i ''` | `sed … > tmp && mv tmp fichier` |
| `grep -P` | Absent des BSD grep | `grep -E` avec les classes POSIX |
| `\d`, `\w`, `\s` dans les motifs | Extensions GNU | `[[:digit:]]`, `[[:alnum:]_]`, `[[:space:]]` |
| `head -n -1`, `tail -n +2` (le premier seulement) | `head -n -1` est GNU | `sed '$d'` ou `awk` |
| `readlink -f`, `realpath` | Absents des macOS anciens | `cd … && pwd` |
| `date -d`, `date --date` | GNU ; BSD utilise `-v` | Éviter l'arithmétique de dates |
| `sort -V`, `sort --parallel` | GNU | `sort -k…n` |
| `declare -A` (tableau associatif) | Bash 4+ ; macOS a Bash 3.2 | Tableau associatif d'`awk` |
| `mapfile`, `readarray` | Bash 4+ | `while read` |
| `${var^^}`, `${var,,}` | Bash 4+ | `tr '[:lower:]' '[:upper:]'` |
| `shopt -s globstar` (`**`) | Bash 4+ | `find` |
| `gawk`/`awk` : `gensub`, `asort`, `length(tableau)` | Extensions GNU awk | `gsub`, compteur explicite |
| `xargs -r` | GNU | `find … -exec … +` |
| `stat -c`, `stat -f` | Syntaxes opposées | `wc -c`, `ls -l` |
| `seq` avec options | Variable | `seq 1 10` seulement, ou boucle `while` |

### Autorisé et encouragé

`ls`, `cd`, `pwd`, `mkdir -p`, `cp`, `mv`, `rm`, `cat`, `head`, `tail`, `less`,
`wc`, `file`, `gzip`/`gunzip`, `sort` (`-k`, `-n`, `-r`, `-u`, `-t`), `uniq`
(`-c`, `-d`), `cut` (`-f`, `-d`, `-c`), `tr`, `paste`, `join`, `grep`
(`-c`, `-i`, `-v`, `-n`, `-o`, `-E`, `-w`, `-A`/`-B`/`-C`, `-l`, `-r`),
`sed` (`s`, `d`, `p` avec `-n`, `-E`), `awk` POSIX, `find` (`-name`, `-type`,
`-maxdepth`, `-size`, `-print0`, `-exec`), `xargs` (`-0`, `-I`, `-n`, `-P`),
`tee`, `basename`, `dirname`, `mktemp`, `chmod`, `printf`, `date +FORMAT`.

### Signaler les différences

Quand la différence GNU/BSD est intéressante à connaître — et elle l'est
souvent, parce que les participants travailleront ensuite sur un serveur Linux —
utilisez un encadré :

```markdown
::: callout

## GNU et BSD : `sed -i`

Sur les serveurs Linux, `sed -i 's/a/b/' fichier` modifie le fichier sur place.
Sous macOS, la même commande exige un argument vide : `sed -i '' 's/a/b/' fichier`.
Un script écrit sur macOS échouera donc sur le serveur, et réciproquement.
C'est pourquoi cette leçon écrit toujours dans un fichier temporaire.

:::
```

## 5. Langue

- **Français**, avec le terme anglais entre parenthèses à sa première
  occurrence dans la leçon : « le tube (*pipe*) », « la sortie standard
  (*stdout*) ».
- **Vouvoiement** de l'apprenant. « Tapez », « vous obtenez », jamais « on tape ».
- Les **noms de commandes, d'options, de fichiers et de variables restent en
  anglais** et en `code` : on écrit `grep`, pas « grep » en italique.
- Vocabulaire normalisé — utilisez la colonne de gauche :

| Terme retenu | Traductions à éviter | Anglais |
|---|---|---|
| terminal | console, invite de commandes | terminal |
| shell | interpréteur de commandes | shell |
| invite | prompt | prompt |
| répertoire | dossier (réservé au gestionnaire de fichiers graphique) | directory |
| chemin | path | path |
| tube | pipeline (réservé aux gestionnaires de flux de travaux), pipe | pipe |
| redirection | — | redirection |
| entrée standard / sortie standard / sortie d'erreur | — | stdin / stdout / stderr |
| motif | pattern, masque | pattern |
| expression régulière | regex, regexp | regular expression |
| joker | wildcard | wildcard |
| lecture | read (le mot anglais est admis au pluriel : « les reads ») | read |
| feuille d'échantillons | samplesheet | sample sheet |
| en-tête | header | header |
| champ | colonne (réservé aux tables), field | field |
| guillemets doubles / apostrophes | quotes simples/doubles | double/single quotes |
| script | programme | script |
| argument | paramètre | argument |
| code de retour | code de sortie, exit code | exit status |

- Pas d'emoji. Pas de point d'exclamation dans les titres.
- Les nombres de plus de quatre chiffres prennent une espace insécable
  (`10 000`), sauf dans les blocs de code.

## 6. Marqueurs de vérification

`scripts/verifier_episodes.py` extrait tous les blocs ```` ```bash ```` des
épisodes, les exécute dans l'ordre dans un bac à sable contenant une copie de
`data/`, et compare le résultat au bloc ```` ```output ```` qui suit, s'il y en a
un. Un commentaire HTML placé **sur la ligne précédant le bloc** modifie ce
comportement :

| Marqueur | Effet |
|---|---|
| *(aucun)* | Le bloc est exécuté ; sa sortie est comparée au bloc `output` suivant, après normalisation des espaces. |
| `<!-- verif: exec-seulement -->` | Le bloc est exécuté, la sortie n'est pas comparée. Pour les sorties tronquées, longues ou variables (horodatages, chemins absolus). |
| `<!-- verif: ordre-libre -->` | La sortie est comparée sans tenir compte de l'ordre des mots. Pour `ls` en colonnes. |
| `<!-- verif: ignore -->` | Le bloc n'est pas exécuté du tout. Pour les commandes interactives (`less`, `nano`), destructrices, ou dont l'exécution abîmerait la suite de l'épisode. |
| `<!-- verif: fichier CHEMIN -->` | Le bloc n'est pas une commande mais le **contenu** d'un fichier : il est écrit dans `CHEMIN`, et rendu exécutable s'il commence par un shebang. |

Le marqueur se place **sur la ligne qui précède la clôture ouvrante du bloc
`bash`**, jamais après le bloc ni devant le bloc de sortie : il s'appliquerait
au mauvais bloc.

Un bloc volontairement fautif dont on montre le message d'erreur se garde tel
quel et son message va dans un bloc ```` ```error ```` : le vérificateur accepte
alors un code de retour non nul et corrige le message si la réalité diffère. On
ne le marque `ignore` que si son exécution aurait un effet de bord (création
d'un fichier parasite, déplacement d'une donnée brute).

Une commande qui échoue exprès **sans message à comparer** — parce que sa sortie
d'erreur est redirigée — se marque `exec-seulement` : ce marqueur dispense aussi
du contrôle du code de retour.

### Contenu d'un script montré dans la leçon

Quand un épisode demande de saisir un script dans l'éditeur, le bloc `bash`
qui montre le contenu du script porte `<!-- verif: fichier scripts/xxx.sh -->`.
Le fichier réellement testé par les blocs suivants est donc **exactement** celui
que l'apprenant lit : aucune divergence n'est possible entre la leçon et ce qui
fonctionne. Le bloc `nano scripts/xxx.sh` qui le précède se marque `ignore`.

### Blocs de préparation invisibles

Un épisode doit pouvoir s'exécuter **de zéro** dans un répertoire ne contenant
que `data/` : le vérificateur repart d'un bac à sable neuf pour chaque épisode.
Or certains épisodes s'appuient sur un fichier créé « à la main » dans l'éditeur
(`nano scripts/mon_script.sh`), commande qu'on ne peut pas exécuter
automatiquement.

Pour cela, un bloc de préparation peut être placé **dans un commentaire HTML** :
il est exécuté par le vérificateur et n'apparaît pas dans le site.

```markdown
<!-- verif-setup:
mkdir -p scripts
cat > scripts/compter_lectures.sh <<'FIN'
#!/usr/bin/env bash
gunzip -c "$1" | wc -l
FIN
chmod +x scripts/compter_lectures.sh
-->
```

Le contenu placé là doit être **strictement identique** à celui que la leçon
demande à l'apprenant de saisir dans son éditeur : c'est ce qui garantit que le
texte de l'épisode est juste. Le corps de l'épisode continue donc d'enseigner
`nano`, et le vérificateur teste bien le script tel qu'il est écrit dans la
leçon.

**Tout bloc `bash` non marqué doit donc réellement fonctionner**, dans le
répertoire de travail `~/formation-bash` contenant `data/`, sur une machine BSD
comme sur une machine GNU. C'est la contrainte qui garantit qu'un participant
qui recopie la leçon n'est jamais bloqué.

## 7. Jeu de données

- Les exemples portent **toujours** sur les fichiers de `data/`. Aucun fichier
  inventé, aucun `mon_fichier.txt` abstrait.
- Les fichiers créés par les exercices vont dans `resultats/` ou `tmp/`, jamais
  dans `data/` : les données brutes ne se modifient pas. Ce principe est
  enseigné explicitement à l'épisode 3 et rappelé à l'épisode 21.
- Les chemins sont **relatifs** à `~/formation-bash` : on écrit
  `data/reads/ech01_R1.fastq.gz`, pas `~/formation-bash/data/…`.

## 8. Calibrage des exercices

Trois à cinq défis par épisode, dans cet ordre :

1. **Un défi d'imitation** — même commande, autre fichier. Deux minutes.
   Personne ne doit être bloqué ici.
2. **Un ou deux défis de transfert** — il faut combiner deux notions vues.
   Cinq à dix minutes.
3. **Un défi d'interprétation** — « pourquoi cette commande donne-t-elle ce
   résultat ? », « ce script contient une erreur, laquelle ? ». C'est là que
   les mauvais modèles mentaux se corrigent.
4. Facultatif : **un défi étoilé** `## … (facultatif)` pour ceux qui vont vite,
   afin qu'ils n'attendent pas.

La solution donne la commande **et** la raison. Une solution qui n'est qu'un
bloc de code est incomplète.

## 9. Ce qu'on ne fait pas dans cette leçon

- Pas de Git, de conteneurs, de gestionnaires de flux de travaux, de soumission
  de tâches sur un cluster, de rapports reproductibles : c'est la seconde
  formation. On peut y faire allusion en fin d'épisode, sous forme de renvoi.
- Pas d'installation d'outils bioinformatiques réels (aligneurs, appelants de
  variants) : le jeu de données est conçu pour qu'aucun outil externe ne soit
  nécessaire. Seul l'épisode 19 montre le *principe* d'une installation dans
  `~/bin`.
- Pas de vi/vim comme éditeur imposé : `nano` pour les démonstrations, l'éditeur
  de son choix pour le travail.
