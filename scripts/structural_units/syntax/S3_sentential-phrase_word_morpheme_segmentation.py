from pprint import pformat
from traceback import print_tb
import os
from conllu import parse 
import requests
from collections import Counter, OrderedDict
from decimal import Decimal
import csv
from locale import LC_NUMERIC
from locale import setlocale

# fill in
INPUT_FILE = "file_name.txt" # name of the file for segmentation (or the path to this file); use only txt files and UTF-8 coding
OUTPUT_FILE = "segmented_text_file_name.txt" # name of the file for saving the results of segmentation (or the path to this file)


######################################################### body of the script #####################################################################################################################

# načtení morfologického slovníku jako slovníku (haha)
with open("MorfoCzech_dictionary.csv", encoding="UTF-8") as soubor:
    obsah_slovniku = csv.reader(soubor, delimiter=";")
    slovnik = {}
    for polozka in obsah_slovniku:
        slovnik[polozka[0]] = polozka[1]


def bez_interpunkce(veta):
    """vyhodí z věty interpunkční znaménka bo v UD tvoří samostatné tokeny"""

    return veta.filter(xpos=lambda x: x != "Z:-------------") 


def hledani_rootu(poradi_vety):
    """najde root v dané větě a uloží jeho id a form"""

    aktualni_veta = parsovani[poradi_vety]
    aktualni_veta = bez_interpunkce(aktualni_veta)
    morfo_kategorie_predikatu = ("VB", "Vp", "Vi", "Vs")
    root_id_hledani = []
    root_form_hledani = []

    
    for token in aktualni_veta:
        if token["deprel"] == "root" and token["upos"] == "VERB" and token["xpos"][0:2] in morfo_kategorie_predikatu:
            root_id_hledani.append(token["id"])
            root_form_hledani.append(token["form"])

        elif token["upos"] == "AUX" and token["xpos"][0:2] in morfo_kategorie_predikatu:
            nominalni_cast_id = int(token["head"])  
            for token_pomocny in aktualni_veta:   
                if token_pomocny["id"] == nominalni_cast_id and token_pomocny["deprel"] == "root":
                    root_id_hledani.append(token_pomocny["id"])
                    root_form_hledani.append(token_pomocny["form"])
            if nominalni_cast_id == 0:   # tuhle podmínku jsem přidala
                root_id_hledani.append(token["id"])
                root_form_hledani.append(token["form"])

    if len(root_id_hledani) == 0:
        root_id = "není"
        root_form = None

    if len(root_id_hledani) > 0:
        root_id = root_id_hledani[0]
        root_form = root_form_hledani[0]

    return root_id, root_form


def hledani_hlav_frazi(poradi_vety, root):
    """najde hlavy frází (=přímých uzlů) pro danou větu"""

    hlavy_frazi_id = []
    hlavy_frazi_form = []
    aktualni_veta = parsovani[poradi_vety]
    aktualni_veta = bez_interpunkce(aktualni_veta)


    for token in aktualni_veta:
        if token["head"] == root:
            hlavy_frazi_id.append(token["id"])
            hlavy_frazi_form.append(token["form"])
    
    return hlavy_frazi_id, hlavy_frazi_form


def hledani_slov_frazi(poradi_vety, hlavy, root):
    """najde všechna slova frází (rekurzivní funkce); uloží, aby zachováno info o struktuře věta-fráze-slovo"""

    aktualni_veta = parsovani[poradi_vety]
    aktualni_veta = bez_interpunkce(aktualni_veta)
    nove_hlavy = []

    if len(hlavy) == 0:
        return

    else:
        for token in aktualni_veta:
            if token["id"] != root and token["id"] not in hlavy and token["head"] in hlavy:
                nove_hlavy.append(token["id"])
                slova_fraze_id.append(token["id"])
                slova_fraze_form.append(token["form"])

    hledani_slov_frazi(poradi_vety, nove_hlavy, root)

    return 


def uprava_textu(slovo):
    # substituce grafiky tak, aby odpovídala realizaci hlásek
    slovo = slovo.lower()
    slovo = slovo.replace("pouč", "po@uč")  # joojoo, tohle je prasárna a vím o tom; třeba vyřešit
    slovo = slovo.replace("nauč", "na@uč")
    slovo = slovo.replace("douč", "do@uč")
    slovo = slovo.replace("přeuč", "pře@uč")
    slovo = slovo.replace("přiuč", "při@uč")
    slovo = slovo.replace("vyuč", "vy@uč")
    slovo = slovo.replace("pouka", "po@uka")
    slovo = slovo.replace("pouká", "po@uká")
    slovo = slovo.replace("poukl", "po@ukl")
    slovo = slovo.replace("poulič", "po@ulič")
    slovo = slovo.replace("poum", "po@um")
    slovo = slovo.replace("poupr", "po@upr")
    slovo = slovo.replace("pouráž", "po@uráž")
    slovo = slovo.replace("pousm", "po@usm")
    slovo = slovo.replace("poust", "po@ust")
    slovo = slovo.replace("poute", "po@ute")
    slovo = slovo.replace("pouvaž", "po@uvaž")
    slovo = slovo.replace("pouzen", "po@uzen")
    slovo = slovo.replace("douč", "do@uč")
    slovo = slovo.replace("douprav", "do@uprav")
    slovo = slovo.replace("doužív", "do@užív")
    slovo = slovo.replace("douzov", "do@uzov")
    slovo = slovo.replace("doupřesn", "do@upřesn")
    slovo = slovo.replace("doudit", "do@udit")
    slovo = slovo.replace("doudí", "do@udí")
    slovo = slovo.replace("muzeu", "muzE")  # diftongické "eu"
    slovo = slovo.replace("neutrál", "nEtrál")
    slovo = slovo.replace("eucken", "Ecken")
    slovo = slovo.replace("kreuzmann", "krEzmann")
    slovo = slovo.replace("pilocereus", "pilocerEs")
    slovo = slovo.replace("cephalocereus", "cephalocerEs")
    # části
    slovo = slovo.replace("ie", "ije")
    slovo = slovo.replace("ii", "iji")
    slovo = slovo.replace("ií", "ijí")
    slovo = slovo.replace("dě", "ďe")
    slovo = slovo.replace("tě", "ťe")
    slovo = slovo.replace("ně", "ňe")
    slovo = slovo.replace("mě", "MŇE")
    slovo = slovo.replace("ě", "JE")
    slovo = slovo.replace("x", "KS")
    slovo = slovo.replace("ch", "X")
    slovo = slovo.replace("q", "KW")
    slovo = slovo.replace("ou", "O")
    slovo = slovo.replace("au", "A")
    slovo = slovo.replace("dž", "G")
    # odstranění "@"
    slovo = slovo.replace("@", "")

    return slovo

def morfo_segmentace(slova_k_segmentaci):
    segmented_words = []
    for original_word in slova_k_segmentaci:
        try:
            segmented_word = slovnik[original_word]
        except KeyError:
            print(
                f"POZOR! SLOVO {original_word} CHYBÍ VE SLOVNÍKU A TUDÍŽ"
                "NEBUDE SEGMENTOVÁNO!"
            )
            segmented_word = original_word
        segmented_words.append(segmented_word)
        
    return segmented_words


soubor = open(INPUT_FILE, encoding="UTF-8")

# načítání dat: do prvního řádku (za open, má příponu .txt) vepisuju název souboru, kde je text ke zpracování (UTF 8 bez BOM :D)
data_z_webu = requests.post('http://lindat.mff.cuni.cz/services/udpipe/api/process', data={'tokenizer': "", 'tagger': "", 'parser': "", 'model': "czech-pdt-ud-2.10-220711"}, files={"data": soubor}) # odešle požadavek na web
soubor.close()
data = data_z_webu.json()['result'] 

parsovani = parse(data)

# řešení "aby", "kdyby" & spol. # zamyslet se, jestli by nešlo líp?
for veta in parsovani:
    for token_pomocny in veta: 
        if type(token_pomocny["id"]) is not int: 
            id_pomocne = token_pomocny["id"][0] # [-1] kdybych chtěla počítat tu spojku místo slovesa
            form_pomocne = token_pomocny["form"] # pro kontrolu
            for token_pomocny_dva in veta:
                if token_pomocny_dva["id"] == id_pomocne:
                    token_pomocny_dva["head"] = None 


# uloží prvotní informace o větách do seznamu; každá položka = slovník s infem jedné věty 
vety_infa = []
for poradi_vety, veta in enumerate(parsovani):

    veta_info = {}
    veta_info["id věty"] = int(veta.metadata["sent_id"])
    veta_info["text"] = veta.metadata["text"] # uložení textu věty
    veta_info["root id"], veta_info["root form"] = hledani_rootu(poradi_vety)
    veta_info["hlavy frází id"], veta_info["hlavy frází form"] = hledani_hlav_frazi(poradi_vety, veta_info["root id"])
    veta_info["délka v počtu frází"] = len(veta_info["hlavy frází id"])
    veta_info["fráze infa"] = []
    vety_infa.append(veta_info)

# ukládání zbylých informací o větách: hledání a ukládání slov klauzí; délky vět, klauzí
for poradi_vety, veta_info in enumerate(vety_infa):

    slova_veta_id = []
    slova_veta_form = []
    delky_frazi = []

    slova_frazi_form = []

    for hlava_fraze_form, hlava_fraze_id in enumerate(veta_info["hlavy frází id"]):
        slova_fraze_id = [hlava_fraze_id]
        slova_fraze_form = [veta_info["hlavy frází form"][hlava_fraze_form]]
        hledani_slov_frazi(poradi_vety, [hlava_fraze_id], veta_info["root id"])
        slova_veta_id.append(slova_fraze_id)
        slova_veta_form.append(slova_fraze_form)

    veta_info["slova frází form"] = slova_veta_form
    veta_info["slova frází id"] = slova_veta_id

    for fraze in veta_info["slova frází id"]:
        delka_fraze = len(fraze)
        delky_frazi.append(delka_fraze)

    veta_info["délky frází"] = delky_frazi

    # vytváření slovníku pro každou frázi (v seznamu fráze infa)
    slova_frazi_form.append(slova_fraze_form)
    for poradi, hlava_fraze in enumerate(veta_info["hlavy frází id"]):  # tady jsem na úrovni fráze
        veta_info["fráze infa"].append({"fráze číslo": poradi})
        veta_info["fráze infa"][poradi]["fráze slova"] = veta_info["slova frází form"][poradi]
        veta_info["fráze infa"][poradi]["délka fráze ve slovech"] = len(veta_info["fráze infa"][poradi]["fráze slova"])

        # uložení morfologicky segmentovaných slov do infa o klauzi
        fraze_fono_slova = []
        for slovo in veta_info["fráze infa"][poradi]["fráze slova"]:
            fono_slovo = uprava_textu(slovo)
            fraze_fono_slova.append(fono_slovo)

        fraze_morfo_slova = morfo_segmentace(fraze_fono_slova)
        veta_info["fráze infa"][poradi]["fráze morfoslova"] = fraze_morfo_slova

        # uložení infa o délkách slov v morfémech
        fraze_delky_slov = []
        for morfoslovo in veta_info["fráze infa"][poradi]["fráze morfoslova"]:
            delka_morfoslova = morfoslovo.count("-") + 1
            fraze_delky_slov.append(delka_morfoslova)

        veta_info["fráze infa"][poradi]["délky slov v morfech"] = fraze_delky_slov


print(vety_infa)
# uložení segmanteace do souboru
soubor_k_ulozeni_segmentace = open(OUTPUT_FILE, mode="w", encoding="UTF-8")

for veta in vety_infa:
    soubor_k_ulozeni_segmentace.write("senence id: " + str(veta["id věty"]) + "\n")
    soubor_k_ulozeni_segmentace.write("original sentence: " + veta["text"] + "\n")
    if veta["root form"] is not None:
        soubor_k_ulozeni_segmentace.write("verbal root: " + veta["root form"] + "\n")
        for fraze in veta["fráze infa"]:
            soubor_k_ulozeni_segmentace.write("construct (s.phrase) in constituents (words) in subconstituents (morphemes): " + ",".join(fraze["fráze morfoslova"]) + "\n")
    else:
        soubor_k_ulozeni_segmentace.write("verbal root: " "NONE" + "\n")
    soubor_k_ulozeni_segmentace.write("\n")
    
soubor_k_ulozeni_segmentace.close()