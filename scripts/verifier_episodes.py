#!/usr/bin/env python3
"""Vérifie que les blocs de code des épisodes fonctionnent réellement.

Pour chaque épisode :
  1. un bac à sable neuf est créé, contenant une copie de `data/` ;
  2. tous les blocs ```bash de l'épisode y sont exécutés, dans l'ordre, au sein
     d'un seul processus bash (les `cd` et les variables persistent donc d'un
     bloc au suivant, comme dans une séance réelle) ;
  3. la sortie obtenue est comparée au bloc ```output (ou ```error) qui suit
     immédiatement le bloc, s'il y en a un.

Un commentaire HTML placé sur la ligne précédant le bloc modifie ce
comportement (voir instructors/guide-de-style.md, §6) :

    <!-- verif: exec-seulement -->   exécuter, ne rien vérifier (ni la sortie,
                                     ni le code de retour)
    <!-- verif: ordre-libre -->      comparer sans tenir compte de l'ordre
    <!-- verif: ignore -->           ne pas exécuter
    <!-- verif: fichier chemin -->   écrire le bloc dans ce fichier, ne pas
                                     l'exécuter (contenu d'un script montré
                                     dans la leçon ; rendu exécutable si le
                                     bloc commence par un shebang)

Un bloc de préparation invisible est exécuté avant le bloc suivant :

    <!-- verif-setup:
    mkdir -p scripts
    ...
    -->

Usage :
    python3 scripts/verifier_episodes.py                 # rapport complet
    python3 scripts/verifier_episodes.py --strict        # code de retour 1 si échec
    python3 scripts/verifier_episodes.py --corriger      # réécrit les blocs output
    python3 scripts/verifier_episodes.py 09-awk-premiers-pas.md
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import shlex
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
EPISODES = RACINE / "episodes"
DONNEES = RACINE / "data"

DEBUT = "@@@BLOC:%d@@@"
FIN = "@@@FIN:%d:"
TRONQUE = ("[...]", "[…]", "...")
DELAI = 180


# --------------------------------------------------------------------------- #
# Analyse du markdown
# --------------------------------------------------------------------------- #

@dataclass
class Bloc:
    langage: str            # "bash", "output", "error"
    code: str
    ligne: int              # ligne d'ouverture du bloc (1-based)
    fin_ligne: int          # ligne de fermeture du bloc (1-based)
    mode: str = "normal"    # normal | exec-seulement | ordre-libre | ignore | fichier
    arg: str = ""           # argument du marqueur (chemin, pour « fichier »)
    setup: str = ""         # blocs verif-setup accumulés avant celui-ci


@dataclass
class Resultat:
    episode: str
    total_bash: int = 0
    executes: int = 0
    ok: int = 0
    echecs: list = field(default_factory=list)   # (ligne, code, attendu, obtenu, cause)
    ignores: int = 0
    non_atteints: int = 0


MAISON_FICTIVE = "/home/apprenant"

MARQUEUR = re.compile(r"<!--\s*verif:\s*([a-z\-]+)(?:\s+(\S+))?\s*-->")
SETUP_DEBUT = re.compile(r"<!--\s*verif-setup:\s*$")
FENCE = re.compile(r"^(\s*)(`{3,})\s*([A-Za-z0-9_-]*)\s*$")


def analyser(texte: str) -> list[Bloc]:
    """Extrait les blocs de code d'un épisode, avec leurs marqueurs."""
    lignes = texte.splitlines()
    blocs: list[Bloc] = []
    i = 0
    mode_en_attente = None
    arg_en_attente = ""
    setup_en_attente: list[str] = []

    while i < len(lignes):
        ligne = lignes[i]

        m = MARQUEUR.search(ligne)
        if m:
            mode_en_attente = m.group(1)
            arg_en_attente = m.group(2) or ""
            i += 1
            continue

        if SETUP_DEBUT.search(ligne):
            j = i + 1
            corps = []
            while j < len(lignes) and lignes[j].strip() != "-->":
                corps.append(lignes[j])
                j += 1
            setup_en_attente.append("\n".join(corps))
            i = j + 1
            continue

        f = FENCE.match(ligne)
        if f:
            indent, ticks, langage = f.group(1), f.group(2), f.group(3)
            j = i + 1
            corps = []
            while j < len(lignes):
                if lignes[j].strip() == ticks:
                    break
                corps.append(lignes[j])
                j += 1
            if langage in ("bash", "output", "error"):
                blocs.append(
                    Bloc(
                        langage=langage,
                        code="\n".join(corps),
                        ligne=i + 1,
                        fin_ligne=j + 1,
                        mode=(mode_en_attente or "normal") if langage == "bash" else "normal",
                        setup="\n".join(setup_en_attente) if langage == "bash" else "",
                        arg=arg_en_attente if langage == "bash" else "",
                    )
                )
                mode_en_attente = None
                arg_en_attente = ""
                if langage == "bash":
                    setup_en_attente = []
            i = j + 1
            continue

        i += 1

    return blocs


# --------------------------------------------------------------------------- #
# Normalisation et comparaison
# --------------------------------------------------------------------------- #

def normaliser(texte: str) -> list[str]:
    out = []
    for l in texte.splitlines():
        l = re.sub(r"[ \t]+", " ", l.strip())
        if l:
            out.append(l)
    return out


def comparer(attendu: str, obtenu: str, mode: str) -> tuple[bool, str]:
    a, o = normaliser(attendu), normaliser(obtenu)

    if mode == "ordre-libre":
        ja = sorted(" ".join(a).split())
        jo = sorted(" ".join(o).split())
        return (ja == jo, "" if ja == jo else "jeux de mots différents")

    tronque = [k for k, l in enumerate(a) if l in TRONQUE]
    if tronque:
        avant, apres = a[: tronque[0]], a[tronque[-1] + 1 :]
        if o[: len(avant)] != avant:
            return False, "début différent (sortie tronquée par [...])"
        if apres and o[-len(apres) :] != apres:
            return False, "fin différente (sortie tronquée par [...])"
        return True, ""

    if a == o:
        return True, ""

    for k, (la, lo) in enumerate(zip(a, o)):
        if la != lo:
            return False, f"ligne {k + 1} : attendu « {la} », obtenu « {lo} »"
    if len(a) != len(o):
        return False, f"{len(a)} ligne(s) attendue(s), {len(o)} obtenue(s)"
    return False, "différence"


# --------------------------------------------------------------------------- #
# Exécution
# --------------------------------------------------------------------------- #

def construire_script(blocs: list[Bloc]) -> tuple[str, list[int]]:
    """Construit un script bash unique ; renvoie le script et les indices exécutés."""
    morceaux = ["set +e", "export LC_ALL=C", "export LANG=C", ""]
    executes = []
    for k, b in enumerate(blocs):
        if b.langage != "bash" or b.mode == "ignore":
            continue
        if b.mode == "fichier":
            # Le bloc n'est pas une commande : c'est le contenu d'un fichier que
            # la leçon demande de saisir dans un éditeur. On l'écrit tel quel.
            morceaux.append(f'mkdir -p "$(dirname {shlex.quote(b.arg)})"')
            morceaux.append(f"cat > {shlex.quote(b.arg)} <<'FIN_DU_BLOC_VERIF'")
            morceaux.append(b.code)
            morceaux.append("FIN_DU_BLOC_VERIF")
            if b.code.lstrip().startswith("#!"):
                morceaux.append(f"chmod +x {shlex.quote(b.arg)}")
            morceaux.append("")
            continue
        if b.setup:
            morceaux.append("# --- préparation invisible ---")
            morceaux.append(b.setup)
        morceaux.append(f'printf "\\n{DEBUT % k}\\n"')
        morceaux.append(b.code)
        morceaux.append(f'printf "{FIN % k}%s@@@\\n" "$?"')
        executes.append(k)
    return "\n".join(morceaux) + "\n", executes


def decouper(sortie: str, executes: list[int]) -> dict[int, tuple[str, int]]:
    """Découpe la sortie globale en (texte, code de retour) par bloc."""
    res: dict[int, tuple[str, int]] = {}
    for k in executes:
        d = sortie.find(DEBUT % k)
        if d < 0:
            continue
        d = sortie.find("\n", d) + 1
        mfin = re.search(re.escape(FIN % k) + r"(\d+)@@@", sortie[d:])
        if not mfin:
            res[k] = (sortie[d:], -1)
            continue
        res[k] = (sortie[d : d + mfin.start()], int(mfin.group(1)))
    return res


def verifier_episode(chemin: Path, corriger: bool) -> Resultat:
    texte = chemin.read_text(encoding="utf-8")
    blocs = analyser(texte)
    r = Resultat(episode=chemin.name)
    r.total_bash = sum(1 for b in blocs if b.langage == "bash")
    r.ignores = sum(1 for b in blocs if b.langage == "bash"
                    and b.mode in ("ignore", "fichier"))

    script, executes = construire_script(blocs)
    if not executes:
        return r

    # Le bac à sable imite le poste de l'apprenant : un répertoire personnel
    # contenant `formation-bash/`, de sorte que `cd ~/formation-bash` et
    # `~/bin` fonctionnent sans jamais toucher au vrai répertoire personnel.
    maison = Path(tempfile.mkdtemp(prefix="verif-"))
    bac = maison / "formation-bash"
    bac.mkdir()
    try:
        shutil.copytree(DONNEES, bac / "data")
        (bac / "_verif.sh").write_text(script, encoding="utf-8")
        proc = subprocess.run(
            ["bash", "_verif.sh"],
            cwd=bac,
            capture_output=True,
            text=True,
            timeout=DELAI,
            env={**os.environ, "LC_ALL": "C", "LANG": "C", "COLUMNS": "80",
                 "HOME": str(maison)},
        )
        # Le bac à sable a un nom aléatoire : on le remplace par un chemin
        # stable, sans quoi aucune sortie de `pwd` ne serait comparable.
        sortie = (proc.stdout + proc.stderr).replace(str(maison), MAISON_FICTIVE)
    except subprocess.TimeoutExpired:
        r.echecs.append((0, "(épisode entier)", "", "", f"délai de {DELAI} s dépassé"))
        shutil.rmtree(maison, ignore_errors=True)
        return r

    par_bloc = decouper(sortie, executes)
    r.executes = len(par_bloc)
    r.non_atteints = len(executes) - len(par_bloc)

    corrections: list[tuple[int, int, str]] = []   # (debut, fin, nouveau corps)

    for k in executes:
        if k not in par_bloc:
            continue
        b = blocs[k]
        obtenu, code = par_bloc[k]
        suivant = blocs[k + 1] if k + 1 < len(blocs) else None
        attendu_bloc = suivant if suivant and suivant.langage in ("output", "error") else None

        if code != 0 and b.mode != "exec-seulement" and not (
                attendu_bloc and attendu_bloc.langage == "error"):
            r.echecs.append((b.ligne, b.code, "", obtenu.strip()[:900],
                             f"code de retour {code}"))
            continue
        attendu_est_erreur = bool(attendu_bloc and attendu_bloc.langage == "error")

        if b.mode == "exec-seulement" or attendu_bloc is None:
            r.ok += 1
            continue

        bon, cause = comparer(attendu_bloc.code, obtenu, b.mode)
        if bon:
            r.ok += 1
        else:
            r.echecs.append((b.ligne, b.code, attendu_bloc.code.strip()[:900],
                             obtenu.strip()[:900], cause))
            if corriger and (code == 0 or attendu_est_erreur) and not any(
                l.strip() in TRONQUE for l in attendu_bloc.code.splitlines()
            ):
                corps = "\n".join(obtenu.strip("\n").splitlines()[:30])
                corrections.append((attendu_bloc.ligne, attendu_bloc.fin_ligne, corps))

    shutil.rmtree(maison, ignore_errors=True)

    if corriger and corrections:
        lignes = texte.splitlines()
        # `debut` = ligne de la clôture ouvrante (1-based), `fin` = ligne de
        # la clôture fermante : le corps occupe donc les indices
        # [debut, fin-1[ dans la liste 0-based.
        for debut, fin, corps in sorted(corrections, reverse=True):
            lignes[debut : fin - 1] = corps.splitlines()
        chemin.write_text("\n".join(lignes) + "\n", encoding="utf-8")

    return r


# --------------------------------------------------------------------------- #
# Rapport
# --------------------------------------------------------------------------- #

def rapport(resultats: list[Resultat]) -> str:
    L = ["# Rapport de vérification des blocs de code", ""]
    plateforme = subprocess.run(["uname", "-s"], capture_output=True, text=True).stdout.strip()
    bash_v = subprocess.run(["bash", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    L += [f"- Plateforme : `{plateforme}`", f"- Shell : `{bash_v}`", ""]
    L += ["| Épisode | blocs bash | exécutés | conformes | ignorés | échecs |",
          "|---|---:|---:|---:|---:|---:|"]
    for r in resultats:
        L.append(f"| `{r.episode}` | {r.total_bash} | {r.executes} | {r.ok} | "
                 f"{r.ignores} | {len(r.echecs)} |")
    tb = sum(r.total_bash for r in resultats)
    to = sum(r.ok for r in resultats)
    te = sum(len(r.echecs) for r in resultats)
    L += ["", f"**Total : {tb} blocs bash, {to} conformes, {te} en échec.**", ""]

    for r in resultats:
        if not r.echecs:
            continue
        L += [f"## {r.episode}", ""]
        for ligne, code, attendu, obtenu, cause in r.echecs:
            L += [f"### ligne {ligne} — {cause}", "", "Commande :", "",
                  "```", code.strip(), "```", ""]
            if attendu:
                L += ["Attendu :", "", "```", attendu, "```", ""]
            L += ["Obtenu :", "", "```", obtenu or "(rien)", "```", ""]
    return "\n".join(L) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("episodes", nargs="*", help="fichiers à vérifier (défaut : tous)")
    p.add_argument("--strict", action="store_true", help="code de retour 1 si un bloc échoue")
    p.add_argument("--corriger", action="store_true",
                   help="remplace les blocs output erronés par la sortie réelle")
    p.add_argument("--sortie", default="rapport_verification.md")
    args = p.parse_args()

    if not DONNEES.is_dir():
        print("data/ absent : lancez d'abord scripts/generer_donnees.py", file=sys.stderr)
        return 2

    cibles = ([EPISODES / n for n in args.episodes] if args.episodes
              else sorted(EPISODES.glob("*.md")))
    cibles = [c for c in cibles if c.is_file()]
    if not cibles:
        print("aucun épisode trouvé", file=sys.stderr)
        return 2

    resultats = []
    for c in cibles:
        r = verifier_episode(c, args.corriger)
        resultats.append(r)
        etat = "OK" if not r.echecs else f"{len(r.echecs)} ÉCHEC(S)"
        print(f"{c.name:45s} {r.ok}/{r.executes} conformes  {etat}")

    (RACINE / args.sortie).write_text(rapport(resultats), encoding="utf-8")
    print(f"\nrapport : {args.sortie}")

    total_echecs = sum(len(r.echecs) for r in resultats)
    return 1 if (args.strict and total_echecs) else 0


if __name__ == "__main__":
    sys.exit(main())
