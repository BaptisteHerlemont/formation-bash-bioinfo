---
title: "Contribuer"
---

Cette leçon est un projet ouvert : les contributions sont bienvenues, qu'il
s'agisse d'une coquille, d'une commande qui ne fonctionne pas sur votre
système, d'un exercice mal calibré ou d'un épisode entier.

Toute contribution implique l'acceptation du [Code de conduite](CODE_OF_CONDUCT.md)
et le placement de la contribution sous les licences décrites dans
[LICENSE.md](LICENSE.md) — CC-BY 4.0 pour le contenu, MIT pour le code.

## Les contributions les plus utiles

Par ordre de valeur décroissante pour la leçon :

1. **Un retour après avoir enseigné ou suivi la formation.** Où le groupe a-t-il
   décroché ? Quel exercice a pris deux fois plus de temps que prévu ? Quelle
   explication a produit un déclic ? Ouvrez une *issue*, même longue et peu
   structurée : c'est l'information la plus difficile à obtenir.
2. **Un signalement de commande qui échoue** sur votre système. Précisez le
   système d'exploitation, la version de Bash (`bash --version`) et le message
   d'erreur exact.
3. **Une coquille, une tournure obscure, un terme mal traduit.**
4. **Un nouvel exercice** sur le jeu de données existant.
5. **Un nouvel épisode**, après discussion dans une *issue* — pour éviter que
   deux personnes écrivent la même chose, et pour vérifier que le volume horaire
   reste tenable.

## Comment procéder

### Pour une remarque ou une question

Ouvrez une *issue* sur le dépôt. Aucune connaissance de Git n'est nécessaire.

### Pour une modification du contenu

1. *Forkez* le dépôt, puis créez une branche depuis `main`.
2. Modifiez les fichiers concernés — les épisodes sont dans `episodes/`.
3. Vérifiez que les blocs de code que vous ajoutez ou modifiez fonctionnent :

   ```bash
   python3 scripts/verifier_episodes.py
   ```

4. Ouvrez une *pull request* en décrivant ce que vous changez et pourquoi.

Le rendu du site est automatique : la vérification de la *pull request* publie
un aperçu du site modifié.

## Règles d'écriture

Avant d'écrire un épisode, lisez le [guide de style](instructors/guide-de-style.md).
Les points les plus importants :

- **Portabilité** : tout le code doit fonctionner sous Bash 3.2 et avec les
  outils BSD (macOS) autant que GNU (Linux). Les particularités GNU sont
  mentionnées dans des encadrés, jamais utilisées dans le corps du texte.
- **Une commande nouvelle, un défi.** Aucune commande n'est introduite sans
  qu'un exercice ne la fasse pratiquer.
- **Les exemples portent sur `data/`**, jamais sur des fichiers inventés.
- **Le français d'abord**, avec le terme anglais entre parenthèses à sa
  première occurrence.

## Rendre le site en local

Nécessite R et Pandoc :

```r
install.packages(c("sandpaper", "varnish", "pegboard"),
                 repos = c("https://carpentries.r-universe.dev/",
                           getOption("repos")))
sandpaper::serve()
```

`sandpaper::check_lesson()` valide la structure du dépôt sans construire le site.
