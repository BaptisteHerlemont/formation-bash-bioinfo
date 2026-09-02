---
title: Notes pour les formateurs
---

## Ce que cette formation est, et ce qu'elle n'est pas

Vingt heures pour amener des biologistes n'ayant jamais ouvert un terminal au
point où ils écrivent un script qui traite une série d'échantillons de bout en
bout. Ce n'est pas un panorama de la bioinformatique : aucun outil réel n'est
installé, aucun alignement n'est calculé. Le sujet est le **shell**, et les
formats bioinformatiques ne servent que de matière à manipuler — ce qui est
précisément ce qui manque aux formations généralistes du même volume.

Git, conda, les conteneurs, les gestionnaires de flux de travaux, le travail sur
serveur et le reporting reproductible relèvent de la **seconde formation**, dont
celle-ci est le prérequis. Résistez à la tentation d'en parler : chaque
digression coûte un exercice, et les exercices sont ce qui fait apprendre.

## Format recommandé

Cinq demi-journées de quatre heures, réparties sur deux semaines
(lundi–mercredi–vendredi puis lundi–mercredi, par exemple). Deux raisons : la
charge cognitive de la journée 1 est élevée, et l'intervalle laisse le temps de
pratiquer sur ses propres données entre les séances.

Chaque demi-journée : 210 minutes d'épisodes, deux pauses de 15 minutes. Les
pauses sont **obligatoires** ; la ligne de commande est fatigante.

Le total des durées annoncées dans les épisodes est de **17 h 30** d'enseignement
et d'exercices. Avec les pauses, l'accueil de chaque demi-journée et les
questions, comptez **20 heures de présence** : c'est le format sur lequel la
formation est calibrée. Si une séance déborde, coupez dans les défis facultatifs
signalés épisode par épisode ci-dessous, jamais dans les exercices principaux.

| Journée | Épisodes | Thème | Moment critique |
|---|---|---|---|
| 1 | 1 à 4 | Premiers pas, navigation, fichiers, inspection | Vérifier que tout le monde a une invite avant d'avancer |
| 2 | 5 à 8 | Formats, redirections, `grep`, tables | Le tube, à l'épisode 6 |
| 3 | 9 à 12 | `awk`, `sed`, atelier | L'atelier de l'épisode 12 ne doit pas être sacrifié |
| 4 | 13 à 16 | Scripts, boucles, tests, quoting | L'épisode 16 est celui qu'on croit pouvoir abréger : ne l'abrégez pas |
| 5 | 17 à 21 | Fonctions, `find`, environnement, projet | Le projet doit démarrer à l'heure |

## Avant la première séance

- Envoyez `learners/setup.md` **dix jours avant** et proposez une permanence
  d'installation d'une demi-heure la veille. Une salle où trois personnes
  installent WSL pendant la première heure est une salle perdue.
- Demandez à chacun d'indiquer son système d'exploitation. S'il y a des
  utilisateurs de macOS, prévoyez d'insister sur les encadrés GNU/BSD ; s'il n'y
  a que du Linux, vous pouvez les survoler.
- Vérifiez vous-même l'archive de données sur une machine neuve.
- Préparez un moyen de projeter votre terminal avec une **grande police**
  (au moins 18 points) et un thème à fort contraste.

## Conduite de séance

**Tapez tout, tout le temps.** Ne collez jamais une commande depuis vos notes :
les apprenants doivent voir le rythme réel de la frappe, les fautes et leur
correction. Vos fautes de frappe sont un contenu pédagogique — commentez-les.

**Attendez.** Après avoir lancé un défi, laissez le temps annoncé sans rien
dire. Le silence est inconfortable pour le formateur, pas pour l'apprenant qui
réfléchit.

**Utilisez des pastilles** (deux couleurs collées sur l'écran : « ça va » /
« bloqué »), c'est la méthode Carpentries et elle fonctionne. Un aidant circule.

**Ne réparez pas le clavier de quelqu'un.** Dites la commande, laissez la
personne la taper. Sinon elle ne l'écrira jamais seule.

**Faites un point de reprise à chaque début d'épisode** : une commande à taper
tous ensemble qui remet tout le monde dans le bon répertoire.

```bash
cd ~/formation-bash
pwd
ls
```

## Points de vigilance, par épisode

- **Épisode 1** — La moitié de la salle n'a jamais vu d'invite. Ne montrez pas
  plus de quatre commandes. La « bande-annonce » de fin est là pour créer une
  attente, pas pour être comprise : n'expliquez rien.
- **Épisode 2** — Dessinez l'arborescence au tableau et laissez-la affichée
  toute la journée. La confusion chemin absolu / chemin relatif est la
  principale source d'échec de la journée 1.
- **Épisode 3** — Annoncez avant tout exercice qu'il n'y a pas de corbeille.
  Certains formateurs font mettre `alias rm='rm -i'` ; cette leçon préfère
  enseigner `rm -i` explicitement, parce qu'un alias ne suit pas l'apprenant sur
  un serveur.
- **Épisode 4** — Le premier vrai moment de bascule : les apprenants
  découvrent seuls que `ech04_R2.fastq.gz` est tronqué. Ne le dites pas avant.
- **Épisode 5** — Épisode dense et peu interactif. Découpez-le en allers-retours
  courts : un format, un `head`, une question à la salle. La distinction
  0-based / 1-based sera oubliée ; c'est normal, elle sera réactivée au projet.
- **Épisode 6** — Le tube est le concept central de la formation. Faites-le
  vivre au tableau avec des flèches avant de le taper. Prévoyez du temps.
- **Épisode 7** — Les expressions régulières provoquent des décrochages. Tenez
  la ligne : classes POSIX seulement, pas de `\d`, pas de raffinement.
  Mieux vaut cinq métacaractères maîtrisés que quinze survolés.
- **Épisode 8** — L'exercice avec `join` échoue si les fichiers ne sont pas
  triés ; laissez-le échouer, c'est l'enseignement.
- **Épisodes 9 et 10** — awk est le meilleur retour sur investissement de toute
  la formation. Si vous devez perdre du temps quelque part, perdez-le ailleurs.
- **Épisode 11** — Restez sur `s///` et `d`. `sed` mérite trente minutes, pas
  plus, dans une formation où `awk` fait déjà le travail.
- **Épisode 12** — L'atelier. Binômes imposés, mise en commun toutes les quinze
  minutes, solutions distribuées seulement à la fin. C'est la séance que les
  participants citent dans les évaluations.
- **Épisode 13** — Beaucoup n'ont jamais utilisé d'éditeur en terminal.
  Consacrez cinq minutes à `nano` seul, sans autre objectif.
- **Épisode 14** — Imposez le passage par `echo` avant toute boucle qui écrit.
  C'est une habitude, elle s'installe ici ou jamais.
- **Épisode 15** — `set -euo pipefail` doit devenir un réflexe de première
  ligne. Expliquez aussi ses limites : un formateur qui le présente comme
  magique prépare une désillusion.
- **Épisode 16** — L'épisode le plus rentable de la journée 4. Le défi
  d'interprétation sur les noms de `data/brut_desordre/` doit être fait en
  entier, à voix haute, ensemble.
- **Épisode 17** — Le passage « plus aucun nom d'échantillon écrit en dur » est
  le moment où la formation prend son sens pour un biologiste.
- **Épisode 18** — Ne survendez pas la parallélisation. Une phrase suffit sur
  les gestionnaires de flux de travaux.
- **Épisode 19** — Ne modifiez jamais le `~/.bashrc` de quelqu'un en séance.
  Montrez, faites copier, laissez appliquer chez soi.
- **Épisode 20** — Annoncez le projet dès la journée 4 pour que les
  participants y pensent. Circulez sans donner de solution ; distribuez les
  indices en blocs `spoiler` à la demande.
- **Épisode 21** — Vingt minutes, pas plus, et terminez par la liste de
  contrôle « ce que je sais faire maintenant » : c'est ce que les participants
  emportent.

## Adaptations

**Public déjà à l'aise avec le terminal.** Traitez les épisodes 1 à 4 en une
heure et demie sous forme de révision guidée, et réinvestissez le temps gagné
dans les épisodes 9, 10 et 12.

**Formation en 14 heures.** Supprimez l'épisode 11 (`sed`, en le remplaçant par
un encadré dans l'épisode 12), l'épisode 18, et réduisez le projet final à ses
deux premières livraisons. Ne supprimez ni l'épisode 6, ni l'épisode 16.

**Formation en distanciel.** Comptez 25 % de temps supplémentaire, faites des
séances de trois heures et non quatre, et prévoyez deux formateurs : l'un
enseigne, l'autre suit le fil de discussion. Les pastilles sont remplacées par
des réactions.

**Public disposant d'un serveur.** N'utilisez pas le serveur pendant ces vingt
heures — sauf en démonstration finale de cinq minutes. Le débogage à distance
consomme un temps considérable et le sujet est traité dans la seconde formation.

## Vérifier le matériel avant une session

```bash
python3 scripts/generer_donnees.py
python3 scripts/verifier_episodes.py --strict
```

Le second script réexécute tous les blocs de code des épisodes et échoue si
l'un d'eux ne produit plus le résultat annoncé. Lancez-le sur votre propre
machine avant chaque session : c'est la meilleure garantie contre la
démonstration qui tombe à plat.


## Portabilité BSD / GNU

Les sorties montrées dans les épisodes ont été vérifiées sur les deux familles
d'outils, macOS (BSD) et GNU/Linux, par le workflow `verifier-code.yaml` qui
rejoue tous les blocs sur les deux systèmes à chaque contribution. Quatre
divergences réelles ont été trouvées et corrigées de cette façon : `\t` dans un
motif `grep -E`, l'ordre de parcours d'un tableau associatif en awk, l'alignement
en colonnes de `wc -l`, et le chemin rendu par `command -v`.

Conséquence pour vous en salle : si un apprenant obtient une sortie légèrement
différente de celle projetée, la première question est celle de son système, et
la réponse se trouve en général dans l'encadré de portabilité de l'épisode en
cours. N'ajoutez jamais une sortie observée sur votre seule machine dans un
épisode sans faire passer le contrôle sur les deux systèmes.
