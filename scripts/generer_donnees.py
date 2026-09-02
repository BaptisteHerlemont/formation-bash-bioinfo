#!/usr/bin/env python3
"""Génère le jeu de données pédagogique de la formation Bash pour la bioinformatique.

Toutes les données sont SYNTHÉTIQUES et produites avec une graine fixe : le jeu
est donc strictement reproductible et ne nécessite aucun téléchargement.

Usage :
    python3 generer_donnees.py [répertoire_de_sortie]

Par défaut, écrit dans ../data relativement à ce script.
"""

from __future__ import annotations

import gzip
import random
import sys
from pathlib import Path

GRAINE = 20240917
RNG = random.Random(GRAINE)

# ---------------------------------------------------------------------------
# Paramètres du « génome » jouet
# ---------------------------------------------------------------------------
CONTIGS = {"chr1": 100_000, "chrM": 5_000}
N_GENES = {"chr1": 120, "chrM": 8}
LARGEUR_FASTA = 60

ECHANTILLONS = [
    # (identifiant, condition, replicat, lane, n_reads, qualite_moyenne)
    ("ech01", "temoin", 1, "L001", 500, 36),
    ("ech02", "temoin", 2, "L001", 500, 35),
    ("ech03", "temoin", 3, "L002", 500, 36),
    ("ech04", "traite", 1, "L002", 500, 34),
    ("ech05", "traite", 2, "L003", 500, 22),  # qualité volontairement dégradée
    ("ech06", "traite", 3, "L003", 500, 35),
]
LONGUEUR_READ = 100

BASES = "ACGT"
COMPLEMENT = str.maketrans("ACGTN", "TGCAN")


# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------
def ecrire(chemin: Path, texte: str) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(texte, encoding="utf-8")


def ecrire_gz(chemin: Path, texte: str) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(chemin, "wt", encoding="utf-8", compresslevel=6) as f:
        f.write(texte)


def replier(sequence: str, largeur: int = LARGEUR_FASTA) -> str:
    return "\n".join(sequence[i : i + largeur] for i in range(0, len(sequence), largeur))


def reverse_complement(sequence: str) -> str:
    return sequence.translate(COMPLEMENT)[::-1]


def phred(qualite: int) -> str:
    """Convertit un score Phred en caractère ASCII (offset 33)."""
    return chr(min(max(qualite, 2), 41) + 33)


# ---------------------------------------------------------------------------
# 1. Génome de référence (FASTA)
# ---------------------------------------------------------------------------
def construire_genome() -> dict:
    genome = {}
    for nom, longueur in CONTIGS.items():
        # Composition en bases légèrement biaisée, plus réaliste qu'un tirage uniforme.
        genome[nom] = "".join(RNG.choices(BASES, weights=[30, 20, 20, 30], k=longueur))
    return genome


DESCRIPTIONS = {
    "chr1": "chromosome 1, assemblage jouet v1.0",
    "chrM": "genome mitochondrial, assemblage jouet v1.0",
}


def ecrire_fasta_genome(genome: dict, racine: Path) -> None:
    morceaux = []
    for nom, sequence in genome.items():
        morceaux.append(f">{nom} {DESCRIPTIONS[nom]} length={len(sequence)}")
        morceaux.append(replier(sequence))
    ecrire(racine / "genome" / "ref_toy.fa", "\n".join(morceaux) + "\n")

    # Un index .fai, utile pour montrer un fichier tabulé « d'accompagnement ».
    lignes_fai = []
    decalage = 0
    for nom, sequence in genome.items():
        entete = f">{nom} {DESCRIPTIONS[nom]} length={len(sequence)}\n"
        decalage += len(entete)
        lignes_fai.append(
            f"{nom}\t{len(sequence)}\t{decalage}\t{LARGEUR_FASTA}\t{LARGEUR_FASTA + 1}"
        )
        n_lignes = -(-len(sequence) // LARGEUR_FASTA)
        decalage += len(sequence) + n_lignes
    ecrire(racine / "genome" / "ref_toy.fa.fai", "\n".join(lignes_fai) + "\n")


# ---------------------------------------------------------------------------
# 2. Annotation (GFF3) + gènes
# ---------------------------------------------------------------------------
PREFIXES_NOMS = [
    "abc", "aco", "adh", "ago", "arf", "atp", "bcl", "cad", "cbp", "cdk",
    "cox", "cyp", "dhr", "dna", "eef", "efl", "fbx", "gap", "gst", "hsp",
    "ino", "kif", "lsm", "mad", "mcm", "myb", "nad", "nfk", "orc", "pol",
    "rad", "rbp", "rho", "rpl", "rps", "sod", "srp", "tbp", "tub", "ubq",
]
BIOTYPES = (
    ["protein_coding"] * 14 + ["lncRNA"] * 3 + ["tRNA"] * 2 + ["rRNA"] + ["pseudogene"]
)


def construire_genes(genome: dict) -> list:
    genes = []
    compteur = 0
    for contig, longueur in CONTIGS.items():
        n = N_GENES[contig]
        pas = longueur // n
        for i in range(n):
            compteur += 1
            marge_debut = RNG.randint(40, max(60, pas // 4))
            debut = i * pas + marge_debut
            taille = RNG.randint(300, max(400, pas - marge_debut - 40))
            fin = min(debut + taille, (i + 1) * pas - 10, longueur)
            if fin - debut < 200:
                fin = min(debut + 200, longueur)
            genes.append(
                {
                    "id": f"GENE{compteur:05d}",
                    "nom": f"{RNG.choice(PREFIXES_NOMS)}{RNG.randint(1, 9)}"
                           f"{RNG.choice('ABCDE')}",
                    "contig": contig,
                    "debut": debut,  # 1-based inclusif (convention GFF3)
                    "fin": fin,
                    "brin": RNG.choice("+-"),
                    "biotype": RNG.choice(BIOTYPES),
                }
            )
    return genes


def ecrire_gff3(genes: list, racine: Path) -> None:
    lignes = ["##gff-version 3"]
    for nom, longueur in CONTIGS.items():
        lignes.append(f"##sequence-region {nom} 1 {longueur}")
    lignes.append("#!genome-build assemblage-jouet v1.0")
    lignes.append("#!genome-date 2024-09")
    for g in genes:
        lignes.append(
            "\t".join(
                [
                    g["contig"], "formation", "gene", str(g["debut"]), str(g["fin"]),
                    ".", g["brin"], ".",
                    f"ID=gene:{g['id']};Name={g['nom']};biotype={g['biotype']}",
                ]
            )
        )
        lignes.append(
            "\t".join(
                [
                    g["contig"], "formation", "mRNA", str(g["debut"]), str(g["fin"]),
                    ".", g["brin"], ".",
                    f"ID=transcript:{g['id']}.1;Parent=gene:{g['id']};"
                    f"Name={g['nom']}-201",
                ]
            )
        )
        longueur_gene = g["fin"] - g["debut"] + 1
        n_exons = 1 if longueur_gene < 350 else RNG.randint(2, 3)
        bornes = (
            sorted(RNG.sample(range(g["debut"] + 30, g["fin"] - 30), k=2 * n_exons - 2))
            if n_exons > 1
            else []
        )
        points = [g["debut"]] + bornes + [g["fin"]]
        for k in range(n_exons):
            lignes.append(
                "\t".join(
                    [
                        g["contig"], "formation", "exon",
                        str(points[2 * k]), str(points[2 * k + 1]),
                        ".", g["brin"], ".",
                        f"ID=exon:{g['id']}.{k + 1};Parent=transcript:{g['id']}.1",
                    ]
                )
            )
    ecrire(racine / "genome" / "annotation.gff3", "\n".join(lignes) + "\n")


# ---------------------------------------------------------------------------
# 3. Lectures de séquençage (FASTQ)
# ---------------------------------------------------------------------------
def profil_qualite(qualite_moyenne: int, longueur: int) -> list:
    """Qualité qui démarre bas, plafonne, puis décroît en fin de lecture."""
    profil = []
    for i in range(longueur):
        if i < 5:
            base = qualite_moyenne - (5 - i)
        elif i > longueur - 20:
            base = qualite_moyenne - int((i - (longueur - 20)) * 0.6)
        else:
            base = qualite_moyenne
        profil.append(max(2, base + RNG.randint(-2, 2)))
    return profil


def bloc_fastq(genome, identifiant, lane, n_reads, qualite_moyenne, sens, index):
    lignes = []
    for i in range(n_reads):
        contig = "chr1" if RNG.random() < 0.95 else "chrM"
        sequence_contig = genome[contig]
        pos = RNG.randint(0, len(sequence_contig) - LONGUEUR_READ - 1)
        seq = sequence_contig[pos : pos + LONGUEUR_READ]
        if sens == 2:
            seq = reverse_complement(seq)
        qualites = profil_qualite(qualite_moyenne, LONGUEUR_READ)
        seq_liste = list(seq)
        for j, q in enumerate(qualites):
            if RNG.random() < 10 ** (-q / 10):
                seq_liste[j] = RNG.choice(BASES)
        if RNG.random() < 0.02:
            seq_liste[RNG.randrange(LONGUEUR_READ)] = "N"
        lignes.append(
            f"@{identifiant.upper()}:1:FLOWCELL1:{lane[-1]}:1101:"
            f"{1000 + i * 7}:{2000 + i * 3} {sens}:N:0:{index}"
        )
        lignes.append("".join(seq_liste))
        lignes.append("+")
        lignes.append("".join(phred(q) for q in qualites))
    return "\n".join(lignes) + "\n"


INDEX_ILLUMINA = ["ATCACG", "CGATGT", "TTAGGC", "TGACCA", "ACAGTG", "GCCAAT"]


def ecrire_fastq(genome: dict, racine: Path) -> None:
    for (ident, _c, _r, lane, n_reads, qual), index in zip(ECHANTILLONS, INDEX_ILLUMINA):
        for sens in (1, 2):
            texte = bloc_fastq(genome, ident, lane, n_reads, qual, sens, index)
            # ech04_R2 est volontairement tronqué (dernier bloc incomplet) :
            # il sert d'exemple de fichier corrompu à détecter.
            if ident == "ech04" and sens == 2:
                texte = "\n".join(texte.rstrip("\n").split("\n")[:-2]) + "\n"
            ecrire_gz(racine / "reads" / f"{ident}_R{sens}.fastq.gz", texte)


# ---------------------------------------------------------------------------
# 4. Variants (VCF)
# ---------------------------------------------------------------------------
def ecrire_vcf(genome: dict, racine: Path) -> None:
    noms = [e[0] for e in ECHANTILLONS]
    entete = [
        "##fileformat=VCFv4.2",
        "##fileDate=20240917",
        "##source=formation-bash-bioinfo",
        "##reference=ref_toy.fa",
    ]
    for nom, longueur in CONTIGS.items():
        entete.append(f"##contig=<ID={nom},length={longueur}>")
    entete += [
        '##FILTER=<ID=PASS,Description="Variant retenu">',
        '##FILTER=<ID=LowQual,Description="Qualite insuffisante">',
        '##FILTER=<ID=LowDepth,Description="Profondeur inferieure a 10">',
        '##INFO=<ID=DP,Number=1,Type=Integer,Description="Profondeur totale">',
        '##INFO=<ID=AF,Number=A,Type=Float,Description="Frequence allelique">',
        '##INFO=<ID=TYPE,Number=1,Type=String,Description="snp ou indel">',
        '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">',
        '##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Profondeur par echantillon">',
        '##FORMAT=<ID=GQ,Number=1,Type=Integer,Description="Qualite du genotype">',
        "#"
        + "\t".join(
            ["CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO", "FORMAT"]
            + noms
        ),
    ]

    lignes = []
    compteur = 0
    for contig, n in [("chr1", 180), ("chrM", 20)]:
        for pos in sorted(RNG.sample(range(100, CONTIGS[contig] - 100), n)):
            compteur += 1
            ref_base = genome[contig][pos - 1]
            if RNG.random() < 0.15:
                if RNG.random() < 0.5:  # insertion
                    ref = ref_base
                    alt = ref_base + "".join(RNG.choices(BASES, k=RNG.randint(1, 4)))
                else:  # délétion
                    ref = genome[contig][pos - 1 : pos - 1 + RNG.randint(2, 5)]
                    alt = ref_base
                type_variant = "indel"
            else:
                ref = ref_base
                alt = RNG.choice([b for b in BASES if b != ref_base])
                type_variant = "snp"
            dp = RNG.randint(4, 90)
            qual = round(RNG.uniform(3, 900), 1)
            if qual < 30:
                filtre = "LowQual"
            elif dp < 10:
                filtre = "LowDepth"
            else:
                filtre = "PASS"
            genotypes = [
                f"{RNG.choices(['0/0', '0/1', '1/1', './.'], weights=[45, 30, 20, 5])[0]}"
                f":{RNG.randint(3, 60)}:{RNG.randint(5, 99)}"
                for _ in noms
            ]
            lignes.append(
                "\t".join(
                    [
                        contig, str(pos),
                        f"var{compteur:04d}" if RNG.random() < 0.6 else ".",
                        ref, alt, f"{qual}", filtre,
                        f"DP={dp};AF={round(RNG.uniform(0.05, 0.95), 3)};"
                        f"TYPE={type_variant}",
                        "GT:DP:GQ",
                    ]
                    + genotypes
                )
            )
    ecrire(racine / "variants" / "cohorte.vcf", "\n".join(entete + lignes) + "\n")


# ---------------------------------------------------------------------------
# 5. Alignements (SAM)
# ---------------------------------------------------------------------------
def ecrire_sam(genome: dict, racine: Path) -> None:
    entete = ["@HD\tVN:1.6\tSO:coordinate"]
    for nom, longueur in CONTIGS.items():
        entete.append(f"@SQ\tSN:{nom}\tLN:{longueur}")
    entete.append("@RG\tID:ech01\tSM:ech01\tLB:lib1\tPL:ILLUMINA")
    entete.append("@PG\tID:aligneur-jouet\tPN:aligneur-jouet\tVN:0.1")

    enregistrements = []
    for i in range(300):
        contig = "chr1" if RNG.random() < 0.95 else "chrM"
        pos = RNG.randint(1, CONTIGS[contig] - LONGUEUR_READ)
        seq = genome[contig][pos - 1 : pos - 1 + LONGUEUR_READ]
        non_aligne = RNG.random() < 0.06
        brin_inverse = RNG.random() < 0.5
        flag = 4 if non_aligne else (16 if brin_inverse else 0)
        mapq = 0 if non_aligne else RNG.choice([0, 3, 23, 42, 60, 60, 60])
        cigar = (
            "*"
            if non_aligne
            else RNG.choice(
                ["100M", "100M", "100M", "5S95M", "98M2S", "60M3D40M", "45M2I53M"]
            )
        )
        nm = RNG.randint(0, 4)
        enregistrements.append(
            (
                "*" if non_aligne else contig,
                0 if non_aligne else pos,
                "\t".join(
                    [
                        f"ECH01:1:FLOWCELL1:1:1101:{1000 + i * 7}:{2000 + i * 3}",
                        str(flag),
                        "*" if non_aligne else contig,
                        str(0 if non_aligne else pos),
                        str(mapq),
                        cigar,
                        "*", "0", "0",
                        reverse_complement(seq) if brin_inverse else seq,
                        "".join(phred(RNG.randint(28, 40)) for _ in range(LONGUEUR_READ)),
                        f"NM:i:{nm}", "RG:Z:ech01", f"AS:i:{100 - 5 * nm}",
                    ]
                ),
            )
        )
    ordre = {"chr1": 0, "chrM": 1, "*": 2}
    enregistrements.sort(key=lambda r: (ordre[r[0]], r[1]))
    ecrire(
        racine / "alignements" / "ech01.sam",
        "\n".join(entete + [r[2] for r in enregistrements]) + "\n",
    )


# ---------------------------------------------------------------------------
# 6. Tables : comptages, feuille d'échantillons, régions BED
# ---------------------------------------------------------------------------
def ecrire_tables(genes: list, racine: Path) -> None:
    noms = [e[0] for e in ECHANTILLONS]
    conditions = {e[0]: e[1] for e in ECHANTILLONS}

    lignes = ["gene_id\tgene_name\t" + "\t".join(noms)]
    for g in genes:
        base = RNG.choice([0, 1, 3, 12, 40, 120, 400, 1500])
        effet = RNG.choice([1.0] * 17 + [0.25, 4.0, 8.0])
        valeurs = []
        for nom in noms:
            mu = base * (effet if conditions[nom] == "traite" else 1.0)
            valeurs.append(
                "0" if mu == 0 else str(max(0, int(RNG.gauss(mu, max(1.0, mu * 0.25)))))
            )
        lignes.append(f"{g['id']}\t{g['nom']}\t" + "\t".join(valeurs))
    ecrire(racine / "tables" / "comptages.tsv", "\n".join(lignes) + "\n")

    lignes = ["sample_id\tcondition\treplicat\tlane\tfichier_R1\tfichier_R2"]
    for ident, cond, rep, lane, _n, _q in ECHANTILLONS:
        lignes.append(
            f"{ident}\t{cond}\t{rep}\t{lane}\t{ident}_R1.fastq.gz\t{ident}_R2.fastq.gz"
        )
    ecrire(racine / "tables" / "echantillons.tsv", "\n".join(lignes) + "\n")

    selection = sorted(RNG.sample(genes, 25), key=lambda g: (g["contig"], g["debut"]))
    lignes = [
        "\t".join(
            [
                g["contig"], str(g["debut"] - 1), str(g["fin"]), g["nom"],
                str(RNG.randint(100, 1000)), g["brin"],
            ]
        )
        for g in selection
    ]
    ecrire(racine / "regions" / "cibles.bed", "\n".join(lignes) + "\n")


# ---------------------------------------------------------------------------
# 7. Protéines (FASTA à en-têtes descriptifs) — pratique pour grep
# ---------------------------------------------------------------------------
ACIDES_AMINES = "ACDEFGHIKLMNPQRSTVWY"
ORGANISMES = [
    "Escherichia coli", "Saccharomyces cerevisiae", "Arabidopsis thaliana",
    "Drosophila melanogaster", "Homo sapiens", "Mus musculus",
]
FONCTIONS = [
    "DNA polymerase subunit", "ribosomal protein", "heat shock protein",
    "ATP synthase subunit", "cytochrome c oxidase subunit",
    "superoxide dismutase", "hypothetical protein", "transcription factor",
    "ABC transporter permease", "glutathione S-transferase",
]


def ecrire_proteines(racine: Path) -> None:
    morceaux = []
    for i in range(40):
        longueur = RNG.randint(80, 400)
        morceaux.append(
            f">sp|P{RNG.randint(10000, 99999)}|PROT{i + 1:02d}_TOY "
            f"{RNG.choice(FONCTIONS)} OS={RNG.choice(ORGANISMES)} "
            f"OX={RNG.randint(1000, 99999)} GN=prot{i + 1} PE=1 SV=1"
        )
        morceaux.append(replier("M" + "".join(RNG.choices(ACIDES_AMINES, k=longueur - 1))))
    ecrire(racine / "proteines" / "proteines.fa", "\n".join(morceaux) + "\n")


# ---------------------------------------------------------------------------
# 8. Répertoire « brut » aux noms de fichiers pénibles
# ---------------------------------------------------------------------------
NOMS_PENIBLES = [
    "Echantillon 01 - Run mars.fastq",
    "echantillon_02.FASTQ",
    "ech 03 (copie).fastq",
    "Ech04_final_VRAIMENT_final.fastq",
    "ech05.resultats.fastq",
    "ech06 -- a refaire.fastq",
    "notes du 12 mars.txt",
    "RESUME Manip.txt",
]


def ecrire_brut_penible(genome: dict, racine: Path) -> None:
    dossier = racine / "brut_desordre"
    dossier.mkdir(parents=True, exist_ok=True)
    for nom in NOMS_PENIBLES:
        if nom.lower().endswith(".fastq"):
            texte = bloc_fastq(genome, "brut", "L001", 25, 34, 1, "ATCACG")
        else:
            texte = (
                "Notes de manipulation\n"
                "=====================\n"
                "Extraction ARN le 12 mars, kit standard.\n"
                "Attention : la lane 3 a du etre relancee.\n"
            )
        (dossier / nom).write_text(texte, encoding="utf-8")


# ---------------------------------------------------------------------------
# 9. Journal d'exécution (pour les épisodes grep / awk)
# ---------------------------------------------------------------------------
def ecrire_journal(racine: Path) -> None:
    lignes = []
    horloge = 0
    for ident, _c, _r, _l, _n, _q in ECHANTILLONS:
        for etape, duree in [
            ("controle_qualite", RNG.randint(20, 60)),
            ("nettoyage", RNG.randint(60, 200)),
            ("alignement", RNG.randint(300, 900)),
            ("comptage", RNG.randint(40, 120)),
        ]:
            horloge += duree
            niveau, message = "INFO", f"etape {etape} terminee en {duree}s"
            if ident == "ech05" and etape == "nettoyage":
                niveau = "WARNING"
                message = "qualite moyenne inferieure au seuil (Q22), poursuite forcee"
            if ident == "ech04" and etape == "controle_qualite":
                niveau = "ERROR"
                message = "fichier ech04_R2.fastq.gz tronque : bloc FASTQ incomplet"
            h, reste = divmod(horloge, 3600)
            m, s = divmod(reste, 60)
            lignes.append(
                f"2024-09-17 {8 + h:02d}:{m:02d}:{s:02d} [{niveau}] "
                f"{ident} {etape} - {message}"
            )
    ecrire(racine / "journaux" / "pipeline.log", "\n".join(lignes) + "\n")


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------
def main() -> None:
    racine = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else Path(__file__).resolve().parent.parent / "data"
    )
    racine.mkdir(parents=True, exist_ok=True)

    genome = construire_genome()
    genes = construire_genes(genome)

    ecrire_fasta_genome(genome, racine)
    ecrire_gff3(genes, racine)
    ecrire_fastq(genome, racine)
    ecrire_vcf(genome, racine)
    ecrire_sam(genome, racine)
    ecrire_tables(genes, racine)
    ecrire_proteines(racine)
    ecrire_brut_penible(genome, racine)
    ecrire_journal(racine)

    # --- contrôles de cohérence -------------------------------------------
    for ident, *_ in ECHANTILLONS:
        for sens in (1, 2):
            chemin = racine / "reads" / f"{ident}_R{sens}.fastq.gz"
            with gzip.open(chemin, "rt") as f:
                n = sum(1 for _ in f)
            attendu = not (ident == "ech04" and sens == 2)
            assert (n % 4 == 0) == attendu, (
                f"{chemin.name} : {n} lignes, multiple de 4 attendu={attendu}"
            )
    for g in genes:
        assert 1 <= g["debut"] <= g["fin"] <= CONTIGS[g["contig"]], f"gène hors bornes : {g}"

    total = 0
    for chemin in sorted(racine.rglob("*")):
        if chemin.is_file():
            taille = chemin.stat().st_size
            total += taille
            print(f"{chemin.relative_to(racine)}\t{taille}")
    print(f"TOTAL\t{total / 1024:.0f} Kio")


if __name__ == "__main__":
    main()
