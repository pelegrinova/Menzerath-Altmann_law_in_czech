from collections import OrderedDict
import os
from pathlib import Path
import csv
import re


# funkce pro nahrazení řetězce
def nahrazeni(slovo, co_nahrazuju, cim_to_nahrazuju):
    slovo_nahrazene = slovo.replace(co_nahrazuju, cim_to_nahrazuju)
    return slovo_nahrazene

# funkce pro nahrazení řetězce pomocí regulárního výrazu
def nahrazeni_regular(slovo, co_nahrazuju, cim_to_nahrazuju):
    slovo_nahrazene = re.sub(co_nahrazuju, cim_to_nahrazuju, slovo)
    return slovo_nahrazene

def segmentace_na_slabiky(text):
    substituce = [("pouč", "po@uč"),            # nediftongická spojení "ou", "au"
                        ("nauč", "na@uč"),
                        ("douč", "do@uč"),
                        ("přeuč", "pře@uč"),
                        ("přiuč", "při@uč"),
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

    # všem slabikám dám hranici za vokálem, tj. udělám otevřené slabiky
    text_substituce = nahrazeni(text_substituce, "V", "V_")


    # princip sonority: viz Skarnitzl et al. (2016, s. 112) - sonorita nesmí stoupat (NE SPÍŠ ŽE NESMÍ KLESAT NA INICIÁLE?), je to "lehči" verze oproti Zikové (tam nesmí být na inciále ani stejná)
    # princip sonority se realizuje na iniciále 
    # pokud na iniciale sonorita stoupa, rozdelim S a V - klesa, ne?
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
    text_na_slabiky_CVCV = nahrazeni(text_na_slabiky_CVCV + " ", ". ", " ") 
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
        for x, pozice_slovo in enumerate(slovo):
            if pozice_slovo == ".":
                pozice_tecek_slovo.append(x)

        pozice_tecek_vsechny_slova.append(pozice_tecek_slovo)

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
    text_souvisly_hranice_slabik = " ".join(text_foneticky_hranice_slabik).strip()

    #print(text_souvisly_hranice_slabik)
    return text_souvisly_hranice_slabik