#!/usr/bin/env bash
# Régénère data/ puis produit l'archive distribuée aux participants.
# Usage : bash scripts/preparer_archive_donnees.sh
set -euo pipefail

racine="$(cd "$(dirname "$0")/.." && pwd)"
cd "$racine"

python3 scripts/generer_donnees.py >/dev/null
rm -f donnees-formation-bash.tar.gz
tar -czf donnees-formation-bash.tar.gz data
printf 'Archive : %s (%s)\n' donnees-formation-bash.tar.gz \
  "$(du -h donnees-formation-bash.tar.gz | cut -f1)"
