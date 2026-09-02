---
title: Aide-mémoire
---

À imprimer et à garder à côté du clavier. L'ordre suit celui de la formation.

## Se repérer et se déplacer

| Commande | Effet |
|---|---|
| `pwd` | Afficher le répertoire courant |
| `ls` | Lister le contenu du répertoire courant |
| `ls -F` | Lister en marquant les répertoires d'un `/` |
| `ls -l` | Lister en détail (droits, taille, date) |
| `ls -lh` | Idem, tailles lisibles (`4.0K`, `528K`) |
| `ls -a` | Inclure les fichiers cachés |
| `ls -R` | Descendre récursivement |
| `cd rep` | Entrer dans `rep` |
| `cd ..` | Remonter d'un niveau |
| `cd ~` ou `cd` | Aller dans son répertoire personnel |
| `cd -` | Revenir au répertoire précédent |
| `clear` | Nettoyer l'écran |
| `history` | Afficher l'historique des commandes |

**Raccourcis vitaux** : <kbd>Tab</kbd> complète un nom ; <kbd>↑</kbd> rappelle la
commande précédente ; <kbd>Ctrl</kbd>+<kbd>C</kbd> interrompt ;
<kbd>Ctrl</kbd>+<kbd>A</kbd> / <kbd>Ctrl</kbd>+<kbd>E</kbd> vont en début / fin
de ligne ; <kbd>Ctrl</kbd>+<kbd>R</kbd> cherche dans l'historique.

## Fichiers et répertoires

| Commande | Effet |
|---|---|
| `mkdir rep` | Créer un répertoire |
| `mkdir -p a/b/c` | Créer toute l'arborescence |
| `touch f` | Créer un fichier vide |
| `cp f g` | Copier |
| `cp -r a b` | Copier un répertoire |
| `mv f g` | Déplacer ou renommer |
| `rm f` | Supprimer (définitivement) |
| `rm -i f` | Supprimer en demandant confirmation |
| `rm -r rep` | Supprimer un répertoire et son contenu |
| `rmdir rep` | Supprimer un répertoire vide |

**Jokers** : `*` (n'importe quelle suite de caractères), `?` (un caractère),
`[123]` (l'un de ces caractères), `[a-z]` (intervalle).

## Regarder un fichier

| Commande | Effet |
|---|---|
| `cat f` | Tout afficher |
| `head f` / `head -n 20 f` | Les 10 (ou 20) premières lignes |
| `tail f` / `tail -n 20 f` | Les 10 (ou 20) dernières lignes |
| `less f` | Feuilleter (`espace`, `b`, `/motif`, `n`, `g`, `G`, `q`) |
| `wc -l f` | Compter les lignes |
| `wc -c f` | Compter les octets |
| `file f` | Deviner le type du fichier |
| `du -h f` | Taille sur le disque |
| `gzip f` / `gunzip f.gz` | Compresser / décompresser |
| `gunzip -c f.gz` | Décompresser vers la sortie standard, sans toucher au fichier |

## Redirections et tubes

| Forme | Effet |
|---|---|
| `cmd > f` | Sortie standard dans `f` (écrase) |
| `cmd >> f` | Sortie standard ajoutée à la fin de `f` |
| `cmd < f` | `f` comme entrée standard |
| `cmd 2> f` | Sortie d'erreur dans `f` |
| `cmd > f 2>&1` | Sortie standard et erreurs dans `f` |
| `cmd 2> /dev/null` | Jeter les messages d'erreur |
| `cmd1 \| cmd2` | Sortie de `cmd1` en entrée de `cmd2` |
| `cmd \| tee f` | Afficher **et** écrire dans `f` |

## Chercher : grep

| Commande | Effet |
|---|---|
| `grep 'motif' f` | Lignes contenant le motif |
| `grep -c 'motif' f` | Les compter |
| `grep -i` | Ignorer la casse |
| `grep -v` | Inverser (lignes qui **ne** contiennent pas) |
| `grep -n` | Afficher le numéro de ligne |
| `grep -w` | Mot entier |
| `grep -o` | N'afficher que ce qui correspond |
| `grep -l` | N'afficher que les noms de fichiers |
| `grep -r 'motif' rep` | Chercher récursivement |
| `grep -A 2 -B 2` | Avec 2 lignes de contexte après / avant |
| `grep -E 'motif étendu' f` | Expressions régulières étendues |

**Motifs** : `^` début de ligne, `$` fin de ligne, `.` un caractère quelconque,
`[abc]`, `[^abc]`, `*` zéro ou plus, `+` un ou plus, `?` zéro ou un,
`{2,4}` de 2 à 4 fois, `|` ou, `( )` groupe.

**Classes POSIX** (portables, à préférer à `\d`, `\w`, `\s`) :
`[[:digit:]]`, `[[:alpha:]]`, `[[:alnum:]]`, `[[:space:]]`, `[[:upper:]]`.

## Tables

| Commande | Effet |
|---|---|
| `cut -f 1,3 f` | Champs 1 et 3 (séparateur : tabulation) |
| `cut -d ',' -f 2 f` | Champ 2, séparateur virgule |
| `sort f` | Trier |
| `sort -n` | Trier numériquement |
| `sort -r` | Ordre décroissant |
| `sort -u` | Trier et dédoublonner |
| `sort -k 3 -n` | Trier sur la 3ᵉ colonne, numériquement |
| `sort -t ',' -k 2` | Séparateur virgule |
| `uniq` | Supprimer les doublons **consécutifs** (trier avant) |
| `uniq -c` | Compter les occurrences |
| `uniq -d` | N'afficher que les lignes en doublon |
| `tr 'a' 'b'` | Remplacer des caractères |
| `tr -d '\r'` | Supprimer des caractères |
| `tr -s ' '` | Réduire les répétitions |
| `paste a b` | Coller côte à côte |
| `join -t '\t' -1 1 -2 1 a b` | Jointure sur une clé (fichiers triés) |
| `comm -12 a b` | Lignes communes à deux fichiers triés |

**Le couteau suisse** : `... | sort | uniq -c | sort -rn | head`

## awk

```
awk -F'\t' 'motif { action }' fichier
```

| Élément | Sens |
|---|---|
| `$0`, `$1`, `$2` | Ligne entière, champ 1, champ 2 |
| `NF` | Nombre de champs de la ligne |
| `NR` | Numéro de la ligne courante |
| `-F'\t'` | Séparateur d'entrée |
| `OFS` | Séparateur de sortie |
| `-v x=3` | Passer une variable |
| `BEGIN { }` / `END { }` | Avant la première ligne / après la dernière |
| `print a, b` | Afficher, séparé par `OFS` |
| `printf "%s\t%.2f\n", a, b` | Affichage formaté |
| `t[$3]++` | Tableau associatif (comptage) |
| `for (k in t)` | Parcourir un tableau |
| `split($9, x, ";")` | Découper une chaîne |
| `sub(/a/, "b")` / `gsub(...)` | Remplacer une / toutes les occurrences |
| `length($0)`, `substr($0, 2, 5)`, `index($0, "AT")` | Chaînes |

Recettes fréquentes :

```
awk -F'\t' '$3 == "gene"' annotation.gff3            # filtrer
awk -F'\t' '{ s += $5 } END { print s }' f           # somme d'une colonne
awk -F'\t' '{ c[$3]++ } END { for (k in c) print k, c[k] }' f   # compter par catégorie
awk -F'\t' 'NR > 1 { print $1 "\t" $4 - $3 }' f      # calcul, en sautant l'en-tête
```

## sed

| Commande | Effet |
|---|---|
| `sed 's/a/b/' f` | Remplacer la 1ʳᵉ occurrence de chaque ligne |
| `sed 's/a/b/g' f` | Toutes les occurrences |
| `sed 's|a|b|g' f` | Autre délimiteur (utile pour les chemins) |
| `sed -E 's/(x)(y)/\2\1/' f` | Groupes de capture |
| `sed -n '3p' f` | N'afficher que la ligne 3 |
| `sed -n '/motif/p' f` | N'afficher que les lignes correspondantes |
| `sed '1,10d' f` | Supprimer les lignes 1 à 10 |
| `sed '/^#/d' f` | Supprimer les lignes de commentaire |
| `sed '$d' f` | Supprimer la dernière ligne |

**Jamais `sed -i`** : la syntaxe diffère entre GNU et BSD.

```
sed 's/a/b/g' f > tmp/f.corrige && mv tmp/f.corrige f
```

## Scripts

```bash
#!/usr/bin/env bash
# objet : ...
# usage : ./script.sh fichier.fastq.gz
set -euo pipefail

if [ "$#" -lt 1 ]; then
    echo "usage : $0 fichier.fastq.gz" >&2
    exit 1
fi

entree="$1"
[ -f "$entree" ] || { echo "fichier introuvable : $entree" >&2; exit 1; }

echo "$(( $(gunzip -c "$entree" | wc -l) / 4 ))"
```

| Élément | Sens |
|---|---|
| `#!/usr/bin/env bash` | Shebang : quel interpréteur utiliser |
| `chmod +x script.sh` | Rendre exécutable |
| `./script.sh` | Lancer (le `./` est obligatoire) |
| `$1`, `$2` | Premier, deuxième argument |
| `$@` | Tous les arguments |
| `$#` | Nombre d'arguments |
| `$0` | Nom du script |
| `$?` | Code de retour de la dernière commande (0 = succès) |
| `exit 1` | Sortir en signalant une erreur |
| `echo "..." >&2` | Écrire sur la sortie d'erreur |
| `set -e` | Arrêter à la première erreur |
| `set -u` | Arrêter si une variable est indéfinie |
| `set -o pipefail` | Une erreur au milieu d'un tube fait échouer le tube |

## Boucles, tests, fonctions

```bash
for f in data/reads/*_R1.fastq.gz; do
    ech=$(basename "$f" _R1.fastq.gz)
    echo "$ech"
done

if [ -f "$f" ] && [ -s "$f" ]; then
    echo "présent et non vide"
elif [ -d "$f" ]; then
    echo "c'est un répertoire"
else
    echo "absent" >&2
fi

compter() {
    local fichier="$1"
    gunzip -c "$fichier" | wc -l
}

while IFS=$'\t' read -r ech condition replicat; do
    echo "$ech : $condition"
done < data/tables/echantillons.tsv
```

| Test | Vrai si |
|---|---|
| `-f f` | `f` existe et est un fichier |
| `-d f` | `f` existe et est un répertoire |
| `-e f` | `f` existe |
| `-s f` | `f` existe et n'est pas vide |
| `-z "$v"` | `$v` est vide |
| `-n "$v"` | `$v` n'est pas vide |
| `"$a" = "$b"` | Chaînes égales |
| `"$a" -eq "$b"` | Nombres égaux (`-ne`, `-lt`, `-le`, `-gt`, `-ge`) |

Les espaces à l'intérieur de `[ ]` sont **obligatoires**.

## Variables et guillemets

| Forme | Effet |
|---|---|
| `v=valeur` | Affectation (aucun espace autour du `=`) |
| `"$v"` | Valeur, protégée des espaces et des jokers — **la forme normale** |
| `'$v'` | La chaîne littérale `$v`, sans substitution |
| `${v}` | Accolades quand le nom touche d'autres caractères |
| `$(cmd)` | Substitution de commandes |
| `${v:-def}` | `$v`, ou `def` si `$v` est vide ou indéfinie |
| `${v:?msg}` | `$v`, ou erreur avec `msg` si indéfinie |
| `${#v}` | Longueur |
| `${f%.gz}` | Sans le suffixe `.gz` |
| `${f##*/}` | Sans le chemin (comme `basename`) |
| `export v` | Transmettre aux processus enfants |

Règle : **mettez toujours vos variables entre guillemets doubles.**

## find et xargs

| Commande | Effet |
|---|---|
| `find rep -type f` | Tous les fichiers sous `rep` |
| `find rep -name '*.fastq'` | Par nom (motif entre apostrophes) |
| `find rep -iname '*.FASTQ'` | Sans tenir compte de la casse |
| `find rep -maxdepth 1` | Sans descendre |
| `find rep -size +1M` | Plus gros qu'un mégaoctet |
| `find rep -type f -exec cmd {} +` | Exécuter une commande sur les résultats |
| `find rep -print0 \| xargs -0 cmd` | Sûr même avec des espaces dans les noms |
| `xargs -I{} cmd {} suite` | Placer l'argument où l'on veut |
| `xargs -P 4 -n 1 cmd` | Quatre exécutions en parallèle |

## Environnement

| Commande | Effet |
|---|---|
| `echo "$PATH"` | Où le shell cherche les commandes |
| `which cmd` / `type cmd` / `command -v cmd` | Localiser une commande |
| `export PATH="$HOME/bin:$PATH"` | Ajouter un répertoire au `PATH` |
| `env` | Toutes les variables d'environnement |
| `tar -tzf a.tar.gz` | Lister le contenu d'une archive |
| `tar -xzf a.tar.gz` | Extraire |
| `chmod +x f` | Rendre exécutable |
| `chmod a-w f` | Protéger contre l'écriture |

## Formats : le minimum à retenir

| Format | Structure | Coordonnées |
|---|---|---|
| FASTA | `>en-tête` puis séquence sur une ou plusieurs lignes | — |
| FASTQ | 4 lignes par lecture : `@nom`, séquence, `+`, qualités | — |
| GFF3 | 9 colonnes, attributs `clé=valeur` en colonne 9 | 1-based, fermé |
| BED | au moins 3 colonnes : contig, début, fin | **0-based, demi-ouvert** |
| VCF | en-tête `##`, ligne `#CHROM`, 8 colonnes + FORMAT + échantillons | 1-based |
| SAM | en-tête `@`, 11 colonnes obligatoires | 1-based |

Conversion GFF3 → BED : `debut_bed = debut_gff - 1`, `fin_bed = fin_gff`.

## Les cinq réflexes de dépannage

1. `pwd` — suis-je où je crois être ?
2. `ls` — le fichier existe-t-il, et sous ce nom exactement ?
3. `head` sur chaque étage du tube — où la chaîne casse-t-elle ?
4. Le séparateur est-il bien celui que je crois (`-F'\t'`, `cut -d`) ?
5. Mes variables sont-elles entre guillemets doubles ?
