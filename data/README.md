# Jeu de données de la formation

Toutes ces données sont **synthétiques**. Elles ont été produites par
`scripts/generer_donnees.py` avec une graine aléatoire fixe (`20240917`) : le jeu
est donc strictement reproductible, il ne contient aucune donnée réelle de
patient ni d'organisme, et il pèse moins de 1 Mio.

Les fichiers imitent la *forme* des données de séquençage réelles (en-têtes,
colonnes, conventions de coordonnées, défauts de qualité) mais leur *contenu*
biologique n'a aucun sens : ne cherchez pas à interpréter les résultats
biologiquement, ils servent uniquement à s'exercer sur la ligne de commande.

## Arborescence

```
data/
├── genome/
│   ├── ref_toy.fa          Génome de référence, 2 contigs (chr1 100 000 pb, chrM 5 000 pb)
│   ├── ref_toy.fa.fai       Index du FASTA (nom, longueur, décalage, ...)
│   └── annotation.gff3      128 gènes avec leurs transcrits et exons
├── reads/
│   └── ech0N_R{1,2}.fastq.gz   6 échantillons appariés, 500 lectures de 100 pb chacun
├── alignements/
│   └── ech01.sam            300 alignements, en-tête @HD/@SQ/@RG/@PG, trié par coordonnée
├── variants/
│   └── cohorte.vcf          200 variants (SNP et indels) génotypés sur les 6 échantillons
├── tables/
│   ├── comptages.tsv        Matrice de comptages 128 gènes × 6 échantillons
│   └── echantillons.tsv     Feuille d'échantillons (identifiant, condition, réplicat, lane)
├── regions/
│   └── cibles.bed           25 régions d'intérêt au format BED
├── proteines/
│   └── proteines.fa         40 séquences protéiques à en-têtes de type UniProt
├── journaux/
│   └── pipeline.log         Journal d'exécution horodaté, avec INFO / WARNING / ERROR
└── brut_desordre/           Fichiers aux noms « pénibles » : espaces, majuscules, parenthèses
```

## Anomalies volontaires

Elles sont là pour être trouvées : plusieurs exercices consistent précisément à
les détecter.

| Fichier | Anomalie | Épisode concerné |
|---|---|---|
| `reads/ech04_R2.fastq.gz` | Fichier tronqué : 1 998 lignes, donc dernier bloc FASTQ incomplet | Formats bioinfo, code défensif |
| `reads/ech05_R*.fastq.gz` | Qualité moyenne très basse (≈ Q22) | Formats bioinfo, awk |
| `variants/cohorte.vcf` | Colonne `FILTER` contenant `LowQual` et `LowDepth`, identifiants `.` manquants | grep, awk |
| `alignements/ech01.sam` | ~6 % de lectures non alignées (`FLAG 4`, `RNAME *`, `MAPQ 0`) | awk, formats |
| `tables/comptages.tsv` | Gènes à comptage nul sur tous les échantillons | awk, tri |
| `journaux/pipeline.log` | Une ligne `ERROR` et une ligne `WARNING` noyées dans les `INFO` | grep |
| `brut_desordre/` | Espaces, majuscules, parenthèses et doubles tirets dans les noms | quoting, renommage par lots |

## Régénérer le jeu de données

```bash
python3 scripts/generer_donnees.py
```

La commande réécrit `data/` à l'identique. Aucune connexion réseau n'est
nécessaire, et seule la bibliothèque standard de Python 3 est utilisée.
