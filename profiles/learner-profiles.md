---
title: Profils d'apprenants
---

Ces quatre profils décrivent le public pour lequel la leçon a été écrite. Ils
servent à trancher les arbitrages de contenu : si une addition ne sert aucun de
ces quatre profils, elle n'entre pas dans la leçon.

## Camille, doctorante en écologie moléculaire — deuxième année

Camille séquence le microbiote intestinal de poissons d'altitude. Elle a reçu
il y a trois semaines un disque dur contenant 240 fichiers FASTQ compressés et
un tableur de métadonnées. Elle a essayé d'ouvrir un fichier avec un éditeur de
texte : l'ordinateur a mis quatre minutes et a affiché du charabia. Sa directrice
lui a dit « il faut que tu apprennes le shell », sans plus de précision.

Camille sait très bien ce qu'elle veut savoir faire, et elle a déjà un projet
réel qui l'attend. Ce qui la bloque n'est pas la motivation mais l'entrée : elle
ne sait pas ouvrir un terminal, et les tutoriels qu'elle trouve commencent tous
par « supposons que vous ayez déjà cloné le dépôt ».

**Ce que la leçon lui apporte** : les quatre premiers épisodes lui donnent
l'entrée qui manque, et l'épisode 14 lui donne la boucle qui traite ses 240
fichiers. À la fin de la journée 4 elle peut écrire son propre contrôle qualité.

**Ce qu'elle risque** : vouloir appliquer immédiatement les commandes à ses
propres données pendant la formation, et se perdre dans un problème de format
particulier. Le jeu de données commun est là pour l'en empêcher pendant les
vingt heures.

## Karim, ingénieur d'études en génétique humaine — huit ans de métier

Karim maîtrise très bien son sujet biologique et un logiciel graphique
d'analyse de variants. Il a appris trois commandes par imitation — `cd`, `ls`,
et une longue ligne de `bcftools` qu'un collègue parti depuis lui a laissée dans
un fichier texte. Il la recopie sans la comprendre, et quand elle échoue, il
attend.

Karim n'est pas débutant en informatique mais son savoir est en pièces
détachées, sans modèle mental : il ne fait pas la différence entre ce que fait
le shell et ce que fait la commande, ce qui l'empêche de diagnostiquer une
erreur. Il est aussi celui qui, dans la salle, pose la question qui fait
progresser tout le monde.

**Ce que la leçon lui apporte** : le modèle mental. L'épisode 3 (le shell
développe les jokers), l'épisode 6 (les trois flux) et l'épisode 16 (les
guillemets) transforment ses recettes en compréhension. Il repart capable de
lire la ligne de son collègue et de la modifier.

**Ce qu'il risque** : s'ennuyer pendant la journée 1. Confiez-lui un rôle
d'aidant — cela profite à la salle et le maintient présent.

## Léa, post-doctorante en biologie du développement — reconversion vers l'analyse

Léa a fait de la microscopie pendant six ans et bascule vers l'analyse de
données de séquençage. Elle a suivi un cours de Python en ligne et sait écrire
une boucle et une fonction dans un carnet de notes interactif. Elle n'a jamais
utilisé de terminal autrement que pour lancer ce carnet.

Léa apprend vite les concepts mais surestime la proximité entre Python et le
shell : elle écrit `if x == 1 :` dans un test bash, met des espaces autour du
`=` d'une affectation, et s'attend à ce que les variables soient typées. Elle a
aussi l'habitude d'un environnement où l'exécution est réversible, et n'a pas
encore intégré qu'il n'y a pas de corbeille.

**Ce que la leçon lui apporte** : la journée 4 en entier, et particulièrement
les épisodes 15 et 16, où ses réflexes Python sont explicitement confrontés à
la syntaxe du shell. Le projet final lui donne le squelette de pipeline qu'elle
cherchait.

**Ce qu'elle risque** : vouloir tout faire en Python. L'épisode 12 est le bon
endroit pour discuter honnêtement de la frontière — un tube de trois commandes
contre trente lignes de Python — sans en faire une querelle.

## Bruno, technicien de plateforme de séquençage — quatorze ans d'ancienneté

Bruno prépare les librairies, lance les séquenceurs et livre les données aux
équipes. Il connaît les formats mieux que quiconque dans la salle : il sait ce
qu'est un indice de multiplexage, pourquoi un R2 est parfois de moins bonne
qualité, et à quoi ressemble un run qui a mal tourné. Il travaille
exclusivement avec les interfaces graphiques fournies par le constructeur, sur
un poste Windows.

Bruno vient parce qu'on lui demande de plus en plus de vérifier les livraisons
avant de les envoyer, et qu'il en a assez de compter des fichiers à la main. Il
n'a aucune ambition de programmer ; il veut un petit nombre d'outils fiables
qu'il puisse appliquer chaque semaine.

**Ce que la leçon lui apporte** : l'épisode 4 (le fichier tronqué) et l'épisode
5 (les formats vus depuis la ligne de commande) valident ce qu'il sait déjà et
lui donnent le moyen de le vérifier. Les épisodes 13 et 15 lui donnent les deux
scripts qu'il utilisera vraiment, et l'épisode 21 lui donne la discipline de
projet qui lui permettra de les retrouver dans six mois.

**Ce qu'il risque** : l'installation. C'est lui qui, sous Windows, doit
installer WSL — d'où l'insistance de la page d'installation et la permanence
recommandée la veille. C'est aussi lui qui, si personne ne l'aide, décroche
avant l'épisode 1.

## Ce que ces profils excluent

- Personne dans cette salle n'a d'accès à un serveur de calcul pendant la
  formation, ni l'intention d'en obtenir un dans le mois. Le travail à distance
  est donc hors sujet.
- Personne n'a besoin d'administrer une machine. Aucune commande de la leçon ne
  requiert les droits administrateur.
- Personne ne vient apprendre un langage de programmation généraliste. Le shell
  est enseigné comme un outil d'assemblage, pas comme un langage dans lequel on
  écrirait un algorithme.
- Personne ne dispose d'un environnement de travail identique à celui du voisin :
  la salle mélange Linux, macOS et WSL. C'est la raison pour laquelle tout le
  contenu est écrit en POSIX portable.
