#!/bin/sh
# Remplace les valeurs à personnaliser avant la première publication.
#
#   sh scripts/preparer_publication.sh MON-COMPTE-GITHUB moi@exemple.fr "Prenom Nom"
#
# Idempotent : relancer ne fait rien de plus. Fonctionne avec le sed de macOS
# comme avec celui de GNU (on écrit dans un fichier temporaire, on remplace).

set -eu

if [ $# -lt 2 ]; then
    echo "usage : sh scripts/preparer_publication.sh COMPTE_GITHUB COURRIEL [\"Prenom Nom\"]" >&2
    exit 2
fi

compte="$1"
courriel="$2"
nom="${3:-}"
prenom=""
if [ -n "$nom" ]; then
    prenom=$(printf '%s\n' "$nom" | cut -d' ' -f1)
    famille=$(printf '%s\n' "$nom" | cut -d' ' -f2-)
    [ "$famille" = "$prenom" ] && famille="$nom"
fi

remplacer() {
    motif="$1"; valeur="$2"; fichier="$3"
    [ -f "$fichier" ] || return 0
    sed "s|$motif|$valeur|g" "$fichier" > "$fichier.tmp"
    mv "$fichier.tmp" "$fichier"
}

for f in config.yaml README.md CITATION.cff .zenodo.json instructors/publier.md \
         learners/setup.md CONTRIBUTING.md
do
    remplacer 'VOTRE-COMPTE' "$compte" "$f"
    remplacer 'vous@exemple\.fr' "$courriel" "$f"
    if [ -n "$nom" ]; then
        remplacer 'VOTRE-NOM, VOTRE-PRÉNOM' "$famille, $prenom" "$f"
        remplacer 'VOTRE-PRÉNOM' "$prenom" "$f"
        remplacer 'VOTRE-NOM' "$famille" "$f"
    fi
done

echo "Valeurs restantes à personnaliser (doit être vide) :"
grep -rn 'VOTRE-COMPTE\|vous@exemple\.fr\|VOTRE-NOM\|VOTRE-PRÉNOM' \
     --exclude-dir=.git --exclude-dir=.github --exclude-dir=data \
     --exclude=preparer_publication.sh . || echo "  (aucune)"

echo
echo "Contrôle des blocs de code des épisodes :"
python3 scripts/verifier_episodes.py --strict > /dev/null && echo "  tous conformes"

echo
echo "Prêt. Étapes suivantes :"
echo "  git init -b main && git add . && git commit -m 'Version initiale'"
echo "  git remote add origin https://github.com/$compte/formation-bash-bioinfo.git"
echo "  git push -u origin main"
echo "  puis Settings > Pages > Deploy from a branch > gh-pages / (root)"
