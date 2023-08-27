from typing import Counter as tpcounter   # nahradit dole u frcí slabik
from collections import OrderedDict
import os
from pathlib import Path
import csv
import re
from collections import Counter

INPUT_FILE = "file_name.txt" # the name of the file for segmentation (or the path to this file); use only the txt files and UTF-8 coding
OUTPUT_FILE = "segmented_text_file_name.txt" # name of the file for saving the results of segmentation


# převod textu v tokens na text v types
def token_to_types(text):
    text_types = []

    for slovo in text:
        if slovo not in text_types:
            text_types.append(slovo)

    return text_types

# počítadlo frekvencí
def pocitadlo(soubor):
    frekvence = Counter(soubor)
    return frekvence


# file adjustment
with open(INPUT_FILE, encoding="UTF-8") as soubor:
    text = soubor.read().lower().replace("\n", " ")
    soubor.close()

# znaky, které chci odstranit z textu + jejich odstranění
znaky = [",", ".", "!", "?", "'", "\"", "<", ">", "-", "–", ":", ";", "„", "“", "=", "%", "&", "#", "@", "/", "\\", "+", "(", ")", "[", "]", "§"]
# dát mu seznam povolených znaků a slova, co by obsahovaly ostatní vyhodit
for znak in znaky:
    text = text.replace(znak, "")

# místo znaků jen interpunkci + aby to bralo jen slova, která českou abecedu
ceska_abeceda = []


# odstranění číslic
text = re.sub(r"[0-9]+", "", text)

# odstranění x-titých mezer (2 a více)
text = re.sub(r"\s{2,}", " ", text)

# funkce pro nahrazení řetězce
def nahrazeni(slovo, co_nahrazuju, cim_to_nahrazuju):
    slovo_nahrazene = slovo.replace(co_nahrazuju, cim_to_nahrazuju)
    return slovo_nahrazene

# funkce pro nahrazení řetězce pomocí regulárního výrazu
def nahrazeni_regular(slovo, co_nahrazuju, cim_to_nahrazuju):
    slovo_nahrazene = re.sub(co_nahrazuju, cim_to_nahrazuju, slovo)
    return slovo_nahrazene

substituce = [("pouč", "po@uč"),            # nediftongická spojení "ou", "au"
            ("nauč", "na@uč"),
            ("douč", "do@uč"),
            ("přeuč", "pře@uč"),
            ("přič", "při@uč"),
            ("vyuč", "vy@uč"),
            ("pouka", "po@uka"), 
            ("pouká", "po@uká"), 
            ("poukl", "po@ukl"), 
            ("poulič", "po@ulič"), 
            ("poum", "po@um"), 
            ("poupr", "po@upr"), 
            ("pouráž", "po@uráž"), 
            ("pousm", "po@usm"),
            ("poust", "po@ust"),
            ("poute", "po@ute"),
            ("pouvaž", "po@uvaž"),
            ("pouzen", "po@uzen"),
            ("douč", "do@uč"),
            ("douprav", "do@uprav"),
            ("doužív", "do@užív"),
            ("douzov", "do@uzov"),
            ("doupřesn", "do@upřesn"),
            ("doudit", "do@udit"),
            ("doudí", "do@udí"),
            ("muzeu", "muzE"),             # diftongické EU (jen ty z mých textů)
            ("neutrál", "nEtrál"),
            ("eucken", "Ecken"),
            ("kreuzmann", "krEzmann"),
            ("pilocereus", "pilocerEs"),
            ("cephalocereus", "cephalocerEs"),
            ("ie", "ije"),                 # substituce grafiky tak, aby odpovídala realizaci hlásek
            ("ii", "iji"),
            ("ií", "ijí"),
            ("dě", "ďe"),
            ("tě", "ťe"),
            ("ně", "ňe"),
            ("mě", "MŇE"),
            ("ě", "JE"),
            ("x", "KS"),
            ("ch", "X"),
            ("q", "KW"),
            ("ou", "O"),
            ("au", "A"),
            ("dž", "G")                     # přidané pravidlo, pozor! mohlo by lehoučce změnit výsledky 
            ]

# provedu substituci hlásek
text_substituce = text

for polozka in substituce:
    text_substituce = nahrazeni(text_substituce, polozka[0], polozka[1])

# ukládám na později text jen s tímto nahrazením
text_substituce_foneticka = text_substituce
text_substituce_foneticka = nahrazeni(text_substituce_foneticka, "@", "")


# klasifikace konsonantů podle sonority (viz Skarnitzel et al. (2016)
# sonory: r,l,m,n,j,ň, = S; obstruenty: to ostatni = C; vokály + diftongy = V

klasifikace_dle_sonority = [("a|á|e|é|ě|i|í|y|ý|o|ó|u|ú|ů|E|A|O",  "V"),  
                            ("b|c|č|d|ď|f|g|h|k|p|ř|s|š|t|ť|v|w|z|ž|K|S|W|X", "C"),  
                            ("CrC|ClC|CmC", "CVC"),  
                            ("Cr |Cl |Cm ", "CV "),
                            ("m|n|j|ň|Ň|J|M", "S"),
                            ("SrS|SlS|SrC|SlC|CrS|ClS", "CVC"),
                            ("Sr |Sl ", "CV "),
                            ("r|l", "S")
                            ]

for polozka in klasifikace_dle_sonority:
    text_substituce = nahrazeni_regular(text_substituce, polozka[0], polozka[1])

# na závěr mažu zavináče
text_substituce = nahrazeni(text_substituce, "@", "")

## vymezení slabičných hranic

# neslabičné předložky připojím k následující slabice
text_substituce = nahrazeni(text_substituce, " C ", " C")

# všem slabikám dám hranici za vokálem, tj. udělám otevřené slabiky
text_substituce = nahrazeni(text_substituce, "V", "V_")


# princip sonority: viz Skarnitzl et al. (2016, s. 112) - sonorita nesmí stoupat (NE SPÍŠ ŽE NESMÍ KLESAT NA INICIÁLE?), je to "lehči" verze oproti Zikové (tam nesmí být na inciále ani stejná)
# princip sonority se realizuje na iniciále 
# pokud na iniciale sonorita stoupa, rozdelim S a V
sonorita = [("SCV", "S_CV"), ("SCCV", "S_CCV"), ("SCSV", "S_CSV"), ("SCCCV", "S_CCCV"), ("SCCSV", "S_CCSV"), ("SCSSV", "S_CSSV")]
for polozka in sonorita:
    text_substituce = nahrazeni(text_substituce, polozka[0], polozka[1])

# pripojim S k predchozi slabice
text_substituce = nahrazeni(text_substituce, "_S_", "S_")

#zjistit, jak je to s pripadnym narustem sonority u kody, potrebuju priklad

#konsonanty, ktere stoji samostatne, pridam k vokalu - napr. sra_z
osamele_kons = [("_C ", "C "), ("_CC ", "CC "), ("_CCC ", "CCC "), ("_S ", "S "), ("_SS ", "SS "), ("_SSS ", "SSS "), ("_SC ", "SC "), ("_SSC ", "SSC "), ("_SCC ", "SCC ")]
for polozka in osamele_kons:
    text_substituce = nahrazeni(text_substituce, polozka[0], polozka[1])

# tzv. pobocne slabiky opravuju tak, aby tvorily jednu slabiku "j_sem", musi to byt ale jen na zacatku slova
text_substituce = nahrazeni(text_substituce, " S_C", " SC")

# pokud chci "videt" slova (CVCV) a jejich slabicnou strukturu (hranice slabiky = tečka)
text_na_slabiky_CVCV = nahrazeni(text_substituce, "_", ".")
text_na_slabiky_CVCV = nahrazeni(text_na_slabiky_CVCV + " ", ". ", " ") # + " " = OČIVIDNĚ TO NEPOMÁHÁ připojuju za svůj text další text sestávající se jen z mezery :D mě poser :D
text_na_slabiky_CVCV = nahrazeni(text_na_slabiky_CVCV, "S", "C")
# pokud chci sekvence slabik CVCV (hranice slabik = mezera)
text_sekvence_slabik_CVCV = nahrazeni(text_substituce, "_", " ")
text_sekvence_slabik_CVCV = nahrazeni(text_sekvence_slabik_CVCV, "S", "C")

## hranice slabik v textu
# ukládám si informaci pro každé slovo o pozici hranic (teček) (POZOR: python počítá od 0)
text_na_slabiky_CVCV_list = text_na_slabiky_CVCV.split(sep=" ")

pozice_tecek_vsechny_slova = []
for slovo in text_na_slabiky_CVCV_list:
    pozice_tecek_slovo = []
    #print(slovo)
    for x, pozice_slovo in enumerate(slovo):
        if pozice_slovo == ".":
            pozice_tecek_slovo.append(x)

    pozice_tecek_vsechny_slova.append(pozice_tecek_slovo)

# připojení neslabičných předložek k následující slabice ve "foneticky" upraveném textu
neslabicne_prep = [(" k ", " k"), (" s ", " s"), (" v ", " v"), (" z ", " z")]
for polozka in neslabicne_prep:
    text_substituce_foneticka = nahrazeni(text_substituce_foneticka, polozka[0], polozka[1])

# vložení slabičných hranic do "foneticky" upraveného textu
text_substituce_foneticka_list = text_substituce_foneticka.split(sep=" ")
if text_substituce_foneticka_list[-1] == "": # odstranění mezery na konci
    del text_substituce_foneticka_list[-1]
text_foneticky_hranice_slabik = []
for x, slovo in enumerate(text_substituce_foneticka_list):
    slovo = list(slovo)
    for y, pozice in enumerate(pozice_tecek_vsechny_slova[x]):
        slovo.insert(pozice, "-")
    slovo_s_hranici = "".join(slovo)
    text_foneticky_hranice_slabik.append(slovo_s_hranici)

# text souvislý se slabičnými hranicemi
text_souvisly_hranice_slabik = " ".join(text_foneticky_hranice_slabik)
text_segmentovany_slouceny = text_souvisly_hranice_slabik

# saving of the segmented text
with open(OUTPUT_FILE, mode="x", encoding="UTF-8") as soubor:
    print(text_segmentovany_slouceny, file=soubor)
