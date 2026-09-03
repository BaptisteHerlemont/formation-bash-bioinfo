---
title: Fiche de faits sur le jeu de données
---

# Fiche de faits : contenu réel du jeu de données

### Arborescence complète

```output
$ find data -type f | sort
data/README.md
data/alignements/ech01.sam
data/brut_desordre/Ech04_final_VRAIMENT_final.fastq
data/brut_desordre/Echantillon 01 - Run mars.fastq
data/brut_desordre/RESUME Manip.txt
data/brut_desordre/ech 03 (copie).fastq
data/brut_desordre/ech05.resultats.fastq
data/brut_desordre/ech06 -- a refaire.fastq
data/brut_desordre/echantillon_02.FASTQ
data/brut_desordre/notes du 12 mars.txt
data/genome/annotation.gff3
data/genome/ref_toy.fa
data/genome/ref_toy.fa.fai
data/journaux/pipeline.log
data/proteines/proteines.fa
data/reads/ech01_R1.fastq.gz
data/reads/ech01_R2.fastq.gz
data/reads/ech02_R1.fastq.gz
data/reads/ech02_R2.fastq.gz
data/reads/ech03_R1.fastq.gz
data/reads/ech03_R2.fastq.gz
data/reads/ech04_R1.fastq.gz
data/reads/ech04_R2.fastq.gz
data/reads/ech05_R1.fastq.gz
data/reads/ech05_R2.fastq.gz
data/reads/ech06_R1.fastq.gz
data/reads/ech06_R2.fastq.gz
data/regions/cibles.bed
data/tables/comptages.tsv
data/tables/echantillons.tsv
data/variants/cohorte.vcf
```

### Tailles

```output
$ du -h data/* | sort -k2
4.0K	data/README.md
 88K	data/alignements
 56K	data/brut_desordre
164K	data/genome
4.0K	data/journaux
 16K	data/proteines
528K	data/reads
4.0K	data/regions
 12K	data/tables
 28K	data/variants
```

### Nombre de lignes de chaque fichier texte

```output
     61  data/README.md
    305  data/alignements/ech01.sam
    100  data/brut_desordre/Ech04_final_VRAIMENT_final.fastq
    100  data/brut_desordre/Echantillon 01 - Run mars.fastq
      4  data/brut_desordre/RESUME Manip.txt
    100  data/brut_desordre/ech 03 (copie).fastq
    100  data/brut_desordre/ech05.resultats.fastq
    100  data/brut_desordre/ech06 -- a refaire.fastq
    100  data/brut_desordre/echantillon_02.FASTQ
      4  data/brut_desordre/notes du 12 mars.txt
    556  data/genome/annotation.gff3
   1753  data/genome/ref_toy.fa
      2  data/genome/ref_toy.fa.fai
     24  data/journaux/pipeline.log
    208  data/proteines/proteines.fa
     25  data/regions/cibles.bed
    129  data/tables/comptages.tsv
      7  data/tables/echantillons.tsv
    216  data/variants/cohorte.vcf
```

### Lignes des FASTQ (décompressés)

```output
$ for f in data/reads/*.gz; do printf '%7d %s\n' $(gunzip -c "$f" | wc -l) "$f"; done
   2000 data/reads/ech01_R1.fastq.gz
   2000 data/reads/ech01_R2.fastq.gz
   2000 data/reads/ech02_R1.fastq.gz
   2000 data/reads/ech02_R2.fastq.gz
   2000 data/reads/ech03_R1.fastq.gz
   2000 data/reads/ech03_R2.fastq.gz
   2000 data/reads/ech04_R1.fastq.gz
   1998 data/reads/ech04_R2.fastq.gz
   2000 data/reads/ech05_R1.fastq.gz
   2000 data/reads/ech05_R2.fastq.gz
   2000 data/reads/ech06_R1.fastq.gz
   2000 data/reads/ech06_R2.fastq.gz
```

### data/genome/ref_toy.fa (10 premières lignes + en-têtes)

```output
$ head -4 data/genome/ref_toy.fa; echo '...'; grep '^>' data/genome/ref_toy.fa; echo '--- longueur des lignes de séquence ---'; awk '!/^>/{print length($0)}' data/genome/ref_toy.fa | sort -u | head
>chr1 chromosome 1, assemblage jouet v1.0 length=100000
ATTAAGGCATGCTGGTATATTTTTTAACACAGAAAAGCAAGATGACGACATTCGCGATGG
TTGACGACGTGACTTCTTTAAATTCGCGGGTTGCACCGTCCTTTGGTTCAATACAAATAT
GGACTTAACTAATTTATGCAAATTACAGTAGGTACTCTAAGCTCCGAGATGTAGGCTGGT
...
>chr1 chromosome 1, assemblage jouet v1.0 length=100000
>chrM genome mitochondrial, assemblage jouet v1.0 length=5000
```
--- longueur des lignes de séquence ---
```output
20
40
60
```

### data/genome/annotation.gff3 (12 premières lignes)

```output
$ head -12 data/genome/annotation.gff3
```
##gff-version 3
##sequence-region chr1 1 100000
##sequence-region chrM 1 5000
#!genome-build assemblage-jouet v1.0
#!genome-date 2024-09
```output
chr1	formation	gene	171	513	.	-	.	ID=gene:GENE00001;Name=arf4D;biotype=protein_coding
chr1	formation	mRNA	171	513	.	-	.	ID=transcript:GENE00001.1;Parent=gene:GENE00001;Name=arf4D-201
chr1	formation	exon	171	513	.	-	.	ID=exon:GENE00001.1;Parent=transcript:GENE00001.1
chr1	formation	gene	956	1509	.	+	.	ID=gene:GENE00002;Name=eef3B;biotype=protein_coding
chr1	formation	mRNA	956	1509	.	+	.	ID=transcript:GENE00002.1;Parent=gene:GENE00002;Name=eef3B-201
chr1	formation	exon	956	1008	.	+	.	ID=exon:GENE00002.1;Parent=transcript:GENE00002.1
chr1	formation	exon	1122	1145	.	+	.	ID=exon:GENE00002.2;Parent=transcript:GENE00002.1
```

### annotation.gff3 : types de la colonne 3

```output
$ grep -v '^#' data/genome/annotation.gff3 | cut -f3 | sort | uniq -c
 295 exon
 128 gene
 128 mRNA
```

### annotation.gff3 : premières lignes de type gene

```output
chr1	formation	gene	171	513	.	-	.	ID=gene:GENE00001;Name=arf4D;biotype=protein_coding
chr1	formation	gene	956	1509	.	+	.	ID=gene:GENE00002;Name=eef3B;biotype=protein_coding
chr1	formation	gene	1726	2307	.	-	.	ID=gene:GENE00003;Name=rho6B;biotype=pseudogene
```

### data/reads/ech01_R1.fastq.gz (8 premières lignes)

```output
$ gunzip -c data/reads/ech01_R1.fastq.gz | head -8
@ECH01:1:FLOWCELL1:1:1101:1000:2000 1:N:0:ATCACG
CAGTTTTTGTCTGTGATTTTGAAACTGCAATTCATTTAAACTAAGTCTACAGTAGCTACTTAAAATTGCAACTCCATTGAACGGCCTTATGCCTATCCAG
+
B?DCBCEDEGEFCGFGDEECDFFGCDDFEFDCEFCEDCEGEEEDGFDFFEFGFFEFEGGEGCCFCFFFFFDDFEFGDCGEEGFBCA@@C@@?><=>;<=;
@ECH01:1:FLOWCELL1:1:1101:1007:2003 1:N:0:ATCACG
CATAATAAAGCGTCTAAATGCTTTCTGGTATGTATTATAATGGAACTCACAACTAATACTCCGATTTATGTCTCCTGGCCATTTAGCTCCCGAGAAAGTT
+
A@CAEFGECFGCDDEDGGDDDGFEDCCGFFDFGDGGFCCGFGEEEGFGEFGFFGDFFGEFFFGDGDFEECGDCFEEEFGFGECFCA@BCAAA?<<:::9:
```

### data/reads/ech05_R1.fastq.gz (8 premières lignes, échantillon dégradé)

```output
$ gunzip -c data/reads/ech05_R1.fastq.gz | head -8
@ECH05:1:FLOWCELL1:3:1101:1000:2000 1:N:0:ACAGTG
TAAATGCGACTCAAGACAGTTATTTCCCATAGTTTGGGTGCATAGTTAATTGTTCGGCAAGCTGAAGTTGACGTCTACCCACGCTCGACCGTGTTCAAGA
+
42537889889675876868658567788999796985686688667787666568997888595857766586669867678446351023120/--,-
@ECH05:1:FLOWCELL1:3:1101:1007:2003 1:N:0:ACAGTG
ATATAGATGTCCCTGCCTATATATCATCCAAACTATATTTAACCTGAACACCTAGGCTTAAAATTTTGTATTATGATAATTGTTCTGTTGACGGTCTATG
+
345445599896997896775677956887687689857875896895956886686586695997589586579587768687745254100/.,--.*
```

### data/variants/cohorte.vcf (18 premières lignes)

```output
$ head -18 data/variants/cohorte.vcf
```
##fileformat=VCFv4.2
##fileDate=20240917
##source=formation-bash-bioinfo
##reference=ref_toy.fa
##contig=<ID=chr1,length=100000>
##contig=<ID=chrM,length=5000>
##FILTER=<ID=PASS,Description="Variant retenu">
##FILTER=<ID=LowQual,Description="Qualite insuffisante">
##FILTER=<ID=LowDepth,Description="Profondeur inferieure a 10">
##INFO=<ID=DP,Number=1,Type=Integer,Description="Profondeur totale">
##INFO=<ID=AF,Number=A,Type=Float,Description="Frequence allelique">
##INFO=<ID=TYPE,Number=1,Type=String,Description="snp ou indel">
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Profondeur par echantillon">
##FORMAT=<ID=GQ,Number=1,Type=Integer,Description="Qualite du genotype">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	ech01	ech02	ech03	ech04	ech05	ech06
```output
chr1	218	.	A	AGG	482.1	PASS	DP=35;AF=0.557;TYPE=indel	GT:DP:GQ	0/0:19:17	0/1:7:53	0/1:6:29	1/1:16:85	0/0:51:37	1/1:51:34
chr1	1435	var0002	T	C	427.9	PASS	DP=20;AF=0.82;TYPE=snp	GT:DP:GQ	1/1:57:36	0/1:14:33	1/1:46:75	./.:45:20	1/1:6:83	0/0:53:29
```

### cohorte.vcf : répartition par contig et nombre de variants

```output
$ grep -v '^#' data/variants/cohorte.vcf | cut -f1 | sort | uniq -c; echo '--- total ---'; grep -vc '^#' data/variants/cohorte.vcf
 180 chr1
  20 chrM
```
--- total ---
```output
200
```

### data/alignements/ech01.sam (12 premières lignes)

```output
$ head -12 data/alignements/ech01.sam
@HD	VN:1.6	SO:coordinate
@SQ	SN:chr1	LN:100000
@SQ	SN:chrM	LN:5000
@RG	ID:ech01	SM:ech01	LB:lib1	PL:ILLUMINA
@PG	ID:aligneur-jouet	PN:aligneur-jouet	VN:0.1
ECH01:1:FLOWCELL1:1:1101:2659:2711	0	chr1	69	60	60M3D40M	*	0	0	GTGACTTCTTTAAATTCGCGGGTTGCACCGTCCTTTGGTTCAATACAAATATGGACTTAACTAATTTATGCAAATTACAGTAGGTACTCTAAGCTCCGAG	?C==DG?E=?AFBCG>CAHIECGEC@FG?=ABEFGEHI=F=CHCA?D?E?EEI=?FFC>DDC=@CABCIFCBDGDHFGCGE?HB=GHEBBGH??FBHG=I	NM:i:1	RG:Z:ech01	AS:i:95
ECH01:1:FLOWCELL1:1:1101:2414:2606	16	chr1	91	60	100M	*	0	0	ATTGCATATGACCAGCCTACATCTCGGAGCTTAGAGTACCTACTGTAATTTGCATAAATTAGTTAAGTCCATATTTGTATTGAACCAAAGGACGGTGCAA	>I=ED?B=IGE>I?GD@EB=IBD@G=>>>B?HFFCHFAF>>GIDFI?GD?>FHBDA>FBF>AE>ADCGBB>?=AHAG=HD?@ACFII?=FFA@GFGHDGD	NM:i:2	RG:Z:ech01	AS:i:90
ECH01:1:FLOWCELL1:1:1101:1140:2060	16	chr1	355	42	100M	*	0	0	TAACTAATATTCGACCTCACCTGGTGGCATCCGCAACGGGTGGATGCTAACAGAAGACAATTTCGATGCTGAATAACCGTTTAACCGATTTGGATAACGA	FFDI=IB=>G@A?AI@IEFD=B>CDHDD@G>E@E=I=D>AF?H>IDBDEHDIB>AAAD>F@@>CFE@I=H?B?H@E?B?IB>CAAEFIIAFD>IG??EBG	NM:i:0	RG:Z:ech01	AS:i:100
ECH01:1:FLOWCELL1:1:1101:1532:2228	0	chr1	652	23	100M	*	0	0	GTCCGCATTACTCTAAGACCCTTATTTTTCCGAGTTTCGTATTACAGGTGTTTCATTAGAAAATAACGCGAGAGTAATATATCTATTTAACACCCCTTGA	D@IIE??GCE>D?GGA@@>EDH=G==?B@AB>CAGDIH@ACGGE=DCI=@FG@IDHE?G>HF>ACEBHHFH?F>B=HIBAAI@DHH@ABG@A@GFECHAF	NM:i:1	RG:Z:ech01	AS:i:95
ECH01:1:FLOWCELL1:1:1101:2106:2474	0	chr1	751	0	98M2S	*	0	0	AAATCATATTAGAGAGCCAGGTAAAAACAAGTGCTAACACTTAGGTGGATTAACAAAATTTTCAACACCTATGAATAAACATCTAGCCCCTACTTGATCT	AD@F=H?B@FCIAEDHBG=II>@G?AAHGG>E@G@CDFIBEDF?F@?G=C>@?H=IBBCF=?CIDFG@EAC=@IBDFICG@@H>D?D=GEHID@CC=BII	NM:i:4	RG:Z:ech01	AS:i:80
ECH01:1:FLOWCELL1:1:1101:1189:2081	0	chr1	819	60	100M	*	0	0	CTATGAATAAACATCTAGCCCCTACTTGATCTATTTGCGCTGTGTTATTAGTAAAGGCTAGCCAGGAGCTGCAGCTATTGAGCTCAAGATGAGACAAAGG	A=I=G?FIE>GCH@@E?>F=AHA@?ABGCACEG>BEF@I??ICBFI>FDBFFCEG@HB?@=IBCBG=BD@HB??GHI>CBE?C@GA=@F=?IA>GCDBBI	NM:i:1	RG:Z:ech01	AS:i:95
ECH01:1:FLOWCELL1:1:1101:2946:2834	16	chr1	963	3	45M2I53M	*	0	0	GTGGCTCCAATATCTGTGGGTGGTCTCGAAATATACCCTGTATTTAGTCAAATCTAGGGAGATACAATATTGTCTAAGTAATGTCCTCCGAGACCGTGTA	AG>CCADABCIC=?F>GG>EEFB@ECI>GFC>CHEIAB?=IIIEGDCC?A=GB>??D>>ADBEIC>?B@C@BF=CGHI?GE?>?DDCEG@G@AI?>CFH>	NM:i:3	RG:Z:ech01	AS:i:85
```

### data/regions/cibles.bed (intégral ou 15 lignes)

```output
$ head -15 data/regions/cibles.bed; echo '...'; wc -l < data/regions/cibles.bed
chr1	955	1509	eef3B	448	+
chr1	2633	3257	rho5B	244	-
chr1	6782	7339	fbx4D	605	+
chr1	16863	17354	orc4C	191	-
chr1	19288	19800	abc3C	332	-
chr1	23407	24109	srp6A	229	-
chr1	27652	28218	tub7D	376	+
chr1	32543	33000	orc5E	422	+
chr1	40030	40502	cbp5A	583	-
chr1	42619	43052	hsp2D	919	-
chr1	43420	43967	gst9D	866	-
chr1	45124	45488	ubq2D	911	+
chr1	45878	46318	dna8B	158	+
chr1	50148	50488	dna1A	124	-
chr1	53469	54068	eef8A	929	-
...
      25
```

### data/tables/comptages.tsv (6 premières lignes)

```output
$ head -6 data/tables/comptages.tsv
gene_id	gene_name	ech01	ech02	ech03	ech04	ech05	ech06
GENE00001	arf4D	518	478	269	513	369	411
GENE00002	eef3B	0	0	0	0	0	0
GENE00003	rho6B	316	637	483	539	386	237
GENE00004	rho5B	2	3	2	2	3	2
GENE00005	aco3A	118	93	56	89	129	104
```

### data/tables/echantillons.tsv (intégral)

```output
$ cat data/tables/echantillons.tsv
sample_id	condition	replicat	lane	fichier_R1	fichier_R2
ech01	temoin	1	L001	ech01_R1.fastq.gz	ech01_R2.fastq.gz
ech02	temoin	2	L001	ech02_R1.fastq.gz	ech02_R2.fastq.gz
ech03	temoin	3	L002	ech03_R1.fastq.gz	ech03_R2.fastq.gz
ech04	traite	1	L002	ech04_R1.fastq.gz	ech04_R2.fastq.gz
ech05	traite	2	L003	ech05_R1.fastq.gz	ech05_R2.fastq.gz
ech06	traite	3	L003	ech06_R1.fastq.gz	ech06_R2.fastq.gz
```

### data/proteines/proteines.fa (8 premières lignes + en-têtes)

```output
$ head -6 data/proteines/proteines.fa; echo '--- tous les en-têtes ---'; grep '^>' data/proteines/proteines.fa
>sp|P27322|PROT01_TOY ribosomal protein OS=Escherichia coli OX=69275 GN=prot1 PE=1 SV=1
MPKECMFGVFHFITSITNEEACAMVHPFYDTCTNLRKHHDNMTDDFNTKCGMAAVGAEIN
NAMAMLDAKMIWCCFGFHAVANLGWHLLAWSENLTCHLMCGPENKGVFRAWEPPYKFAHW
HSCFHYDIKCGKDIRIKNPWHCCGQSV
>sp|P11645|PROT02_TOY hypothetical protein OS=Homo sapiens OX=48404 GN=prot2 PE=1 SV=1
MGQLTFAQYKAHWVWVHKIVYWPLLMYNGIVYCLCIRHDANQKEGHSFCIRSRPVHKWQL
```
--- tous les en-têtes ---
```output
>sp|P27322|PROT01_TOY ribosomal protein OS=Escherichia coli OX=69275 GN=prot1 PE=1 SV=1
>sp|P11645|PROT02_TOY hypothetical protein OS=Homo sapiens OX=48404 GN=prot2 PE=1 SV=1
>sp|P98339|PROT03_TOY cytochrome c oxidase subunit OS=Mus musculus OX=3086 GN=prot3 PE=1 SV=1
>sp|P29543|PROT04_TOY DNA polymerase subunit OS=Saccharomyces cerevisiae OX=83228 GN=prot4 PE=1 SV=1
>sp|P13203|PROT05_TOY hypothetical protein OS=Drosophila melanogaster OX=87063 GN=prot5 PE=1 SV=1
>sp|P93530|PROT06_TOY ABC transporter permease OS=Arabidopsis thaliana OX=30163 GN=prot6 PE=1 SV=1
>sp|P81427|PROT07_TOY ribosomal protein OS=Homo sapiens OX=91303 GN=prot7 PE=1 SV=1
>sp|P33266|PROT08_TOY heat shock protein OS=Escherichia coli OX=75484 GN=prot8 PE=1 SV=1
>sp|P90265|PROT09_TOY transcription factor OS=Arabidopsis thaliana OX=60990 GN=prot9 PE=1 SV=1
>sp|P50199|PROT10_TOY ABC transporter permease OS=Arabidopsis thaliana OX=89013 GN=prot10 PE=1 SV=1
>sp|P24841|PROT11_TOY ATP synthase subunit OS=Escherichia coli OX=55060 GN=prot11 PE=1 SV=1
>sp|P33623|PROT12_TOY ABC transporter permease OS=Arabidopsis thaliana OX=73277 GN=prot12 PE=1 SV=1
>sp|P94801|PROT13_TOY heat shock protein OS=Mus musculus OX=63454 GN=prot13 PE=1 SV=1
>sp|P29921|PROT14_TOY heat shock protein OS=Escherichia coli OX=75411 GN=prot14 PE=1 SV=1
>sp|P43581|PROT15_TOY transcription factor OS=Mus musculus OX=94119 GN=prot15 PE=1 SV=1
>sp|P50983|PROT16_TOY ABC transporter permease OS=Mus musculus OX=24813 GN=prot16 PE=1 SV=1
>sp|P44281|PROT17_TOY glutathione S-transferase OS=Saccharomyces cerevisiae OX=88381 GN=prot17 PE=1 SV=1
>sp|P79728|PROT18_TOY superoxide dismutase OS=Homo sapiens OX=85289 GN=prot18 PE=1 SV=1
>sp|P94306|PROT19_TOY glutathione S-transferase OS=Drosophila melanogaster OX=8483 GN=prot19 PE=1 SV=1
>sp|P64819|PROT20_TOY cytochrome c oxidase subunit OS=Homo sapiens OX=64945 GN=prot20 PE=1 SV=1
>sp|P19467|PROT21_TOY superoxide dismutase OS=Mus musculus OX=59825 GN=prot21 PE=1 SV=1
>sp|P36081|PROT22_TOY ABC transporter permease OS=Escherichia coli OX=82171 GN=prot22 PE=1 SV=1
>sp|P99240|PROT23_TOY ribosomal protein OS=Drosophila melanogaster OX=89341 GN=prot23 PE=1 SV=1
>sp|P30323|PROT24_TOY ribosomal protein OS=Escherichia coli OX=85099 GN=prot24 PE=1 SV=1
>sp|P43224|PROT25_TOY ATP synthase subunit OS=Arabidopsis thaliana OX=77271 GN=prot25 PE=1 SV=1
>sp|P74741|PROT26_TOY superoxide dismutase OS=Escherichia coli OX=72501 GN=prot26 PE=1 SV=1
>sp|P30391|PROT27_TOY hypothetical protein OS=Saccharomyces cerevisiae OX=38416 GN=prot27 PE=1 SV=1
>sp|P80405|PROT28_TOY ATP synthase subunit OS=Drosophila melanogaster OX=75160 GN=prot28 PE=1 SV=1
>sp|P61030|PROT29_TOY ATP synthase subunit OS=Saccharomyces cerevisiae OX=89957 GN=prot29 PE=1 SV=1
>sp|P98844|PROT30_TOY heat shock protein OS=Escherichia coli OX=57262 GN=prot30 PE=1 SV=1
>sp|P21066|PROT31_TOY transcription factor OS=Homo sapiens OX=53143 GN=prot31 PE=1 SV=1
>sp|P39600|PROT32_TOY cytochrome c oxidase subunit OS=Homo sapiens OX=31029 GN=prot32 PE=1 SV=1
>sp|P94110|PROT33_TOY ABC transporter permease OS=Mus musculus OX=81984 GN=prot33 PE=1 SV=1
>sp|P15416|PROT34_TOY ribosomal protein OS=Arabidopsis thaliana OX=21233 GN=prot34 PE=1 SV=1
>sp|P41296|PROT35_TOY superoxide dismutase OS=Arabidopsis thaliana OX=82231 GN=prot35 PE=1 SV=1
>sp|P32042|PROT36_TOY DNA polymerase subunit OS=Arabidopsis thaliana OX=6698 GN=prot36 PE=1 SV=1
>sp|P24528|PROT37_TOY ABC transporter permease OS=Escherichia coli OX=66720 GN=prot37 PE=1 SV=1
>sp|P93525|PROT38_TOY transcription factor OS=Escherichia coli OX=63830 GN=prot38 PE=1 SV=1
>sp|P86959|PROT39_TOY heat shock protein OS=Escherichia coli OX=42991 GN=prot39 PE=1 SV=1
>sp|P11033|PROT40_TOY ATP synthase subunit OS=Drosophila melanogaster OX=34685 GN=prot40 PE=1 SV=1
```

### data/journaux/pipeline.log (12 premières lignes)

```output
$ head -12 data/journaux/pipeline.log
2024-09-17 08:00:39 [INFO] ech01 controle_qualite - etape controle_qualite terminee en 39s
2024-09-17 08:01:40 [INFO] ech01 nettoyage - etape nettoyage terminee en 61s
2024-09-17 08:11:10 [INFO] ech01 alignement - etape alignement terminee en 570s
2024-09-17 08:12:21 [INFO] ech01 comptage - etape comptage terminee en 71s
2024-09-17 08:12:47 [INFO] ech02 controle_qualite - etape controle_qualite terminee en 26s
2024-09-17 08:13:58 [INFO] ech02 nettoyage - etape nettoyage terminee en 71s
2024-09-17 08:28:33 [INFO] ech02 alignement - etape alignement terminee en 875s
2024-09-17 08:30:04 [INFO] ech02 comptage - etape comptage terminee en 91s
2024-09-17 08:30:56 [INFO] ech03 controle_qualite - etape controle_qualite terminee en 52s
2024-09-17 08:34:08 [INFO] ech03 nettoyage - etape nettoyage terminee en 192s
2024-09-17 08:48:55 [INFO] ech03 alignement - etape alignement terminee en 887s
2024-09-17 08:50:05 [INFO] ech03 comptage - etape comptage terminee en 70s
```

### pipeline.log : lignes ERROR et WARNING

```output
$ grep -n -E 'ERROR|WARNING' data/journaux/pipeline.log
13:2024-09-17 08:50:52 [ERROR] ech04 controle_qualite - fichier ech04_R2.fastq.gz tronque : bloc FASTQ incomplet
18:2024-09-17 09:03:42 [WARNING] ech05 nettoyage - qualite moyenne inferieure au seuil (Q22), poursuite forcee
```

### data/brut_desordre/ (noms exacts)

```output
$ ls -1 data/brut_desordre/
Ech04_final_VRAIMENT_final.fastq
Echantillon 01 - Run mars.fastq
RESUME Manip.txt
ech 03 (copie).fastq
ech05.resultats.fastq
ech06 -- a refaire.fastq
echantillon_02.FASTQ
notes du 12 mars.txt
```

### Autres fichiers de data/tables et data/alignements

```output
$ ls -1 data/tables data/alignements data/regions data/variants data/journaux data/proteines data/genome
data/alignements:
ech01.sam
```

```output
data/genome:
annotation.gff3
ref_toy.fa
ref_toy.fa.fai
```

```output
data/journaux:
pipeline.log
```

```output
data/proteines:
proteines.fa
```

```output
data/regions:
cibles.bed
```

```output
data/tables:
comptages.tsv
echantillons.tsv
```

```output
data/variants:
cohorte.vcf
```
