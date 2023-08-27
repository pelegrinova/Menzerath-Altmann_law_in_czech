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


########################################################### body of the script #####################################################################################################################

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

    # print(root_form)
    # print(root_id)


    return root_id, root_form


def hledani_hlav_frazi(poradi_vety, root):
    """najde hlavy frází (=přímých uzlů) pro danou větu"""
    #print(root)
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
    vety_infa.append(veta_info)

# ukládání zbylých informací o větách: hledání a ukládání slov klauzí; délky vět, klauzí
for poradi_vety, veta_info in enumerate(vety_infa):

    slova_veta_id = []
    slova_veta_form = []
    delky_frazi = []

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


# uložení do souboru
soubor_k_ulozeni_segmentace = open(OUTPUT_FILE, mode="w", encoding="UTF-8")

for veta in vety_infa:
    soubor_k_ulozeni_segmentace.write("senence id: " + str(veta["id věty"]) + "\n")
    soubor_k_ulozeni_segmentace.write("construct (sentence): " + veta["text"] + "\n")
    if veta["root form"] is not None:
        soubor_k_ulozeni_segmentace.write("verbal root: " + veta["root form"] + "\n")
        for fraze in veta["slova frází form"]:
            soubor_k_ulozeni_segmentace.write("constituent (sentential phrase) in subconstituents (words): " + ",".join(fraze) + "\n")
    else:
        soubor_k_ulozeni_segmentace.write("verbal root: " "NONE" + "\n")
    soubor_k_ulozeni_segmentace.write("\n")
    
soubor_k_ulozeni_segmentace.close()
