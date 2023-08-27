from pprint import pformat
from conllu import parse 
import os
import requests
from collections import Counter, OrderedDict
from decimal import Decimal
import csv
from locale import LC_NUMERIC
from locale import setlocale


# fill in
INPUT_FILE = "file_name.txt" # name of the file for segmentation (or the path to this file); use only txt files and UTF-8 coding
OUTPUT_FILE = "segmented_text_file_name.txt" # name of the file for saving the results of segmentation (or the path to this file)


########################################################## body of the script #######################################################################################################################

def bez_interpunkce(veta):
    """vyhodí z věty interpunkční znaménka bo v UD tvoří samostatné tokeny"""

    return veta.filter(xpos=lambda x: x != "Z:-------------") 


def hledani_predikatu(poradi_vety):
    """najde predikáty v dané větě a uloží jejich id a form"""

    predikaty_id = []
    predikaty_form = []
    morfo_kategorie_predikatu = ("VB", "Vp", "Vi", "Vs")
    aktualni_veta = parsovani[poradi_vety]
    aktualni_veta = bez_interpunkce(aktualni_veta)

    for token in aktualni_veta:

        if token["upos"] == "VERB" and token["xpos"][0:2] in morfo_kategorie_predikatu:
            if token["id"] not in predikaty_id:
                predikaty_id.append(token["id"])
                predikaty_form.append(token["form"])

        if token["upos"] == "AUX" and token["xpos"][0:2] in morfo_kategorie_predikatu:
            nominalni_cast_id = int(token["head"])  
            for token_pomocny in aktualni_veta:   
                if token_pomocny["id"] == nominalni_cast_id:
                    if token_pomocny["id"] not in predikaty_id: 
                        predikaty_id.append(token_pomocny["id"])
                        predikaty_form.append(token_pomocny["form"])
            if nominalni_cast_id == 0:   # tuhle podmínku jsem přidala
                predikaty_id.append(token["id"])
                predikaty_form.append(token["form"])

    return predikaty_id, predikaty_form


def hledani_slov_klauzi(poradi_vety, hlavy, predikaty_vety):
    """najde všechna slova klauzí dané věty (rekurzivní funkce); uloží, aby zachováno info o struktuře věta-klauze-slovo"""

    aktualni_veta = parsovani[poradi_vety]
    aktualni_veta = bez_interpunkce(aktualni_veta)
    nove_hlavy = []

    if len(hlavy) == 0:
        return

    else:
        for token in aktualni_veta:
            if token["id"] not in hlavy and token["id"] not in predikaty_vety and token["head"] in hlavy:
                nove_hlavy.append(token["id"])
                slova_klauze_id.append(token["id"])
                slova_klauze_form.append(token["form"])

    hledani_slov_klauzi(poradi_vety, nove_hlavy, predikaty_vety)

    return 
     

soubor = open(INPUT_FILE, encoding="UTF-8")

# načítání dat: do prvního řádku (za open, má příponu .txt) vepisuju název souboru, kde je text ke zpracování (UTF 8 bez BOM :D)
data_z_webu = requests.post('http://lindat.mff.cuni.cz/services/udpipe/api/process', data={'tokenizer': "", 'tagger': "", 'parser': "", 'model': "czech-pdt-ud-2.10-220711"}, files={"data": soubor}) # odešle požadavek na web
soubor.close()
data = data_z_webu.json()['result'] 

# zpracování dat knihovnou na conllu formát
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
    veta_info["predikáty id"], veta_info["predikáty form"] = hledani_predikatu(poradi_vety)
    #veta_info["délka v počtu klauzí"] = len(veta_info["predikáty id"])
    vety_infa.append(veta_info)

# ukládání zbylých informací o větách: hledání a ukládání slov klauzí; délky vět, klauzí
for poradi_vety, veta_info in enumerate(vety_infa):

    slova_veta_id = []
    slova_veta_form = []
    delky_klauzi = []

    for hlava_klauze_form, hlava_klauze_id in enumerate(veta_info["predikáty id"]):
        slova_klauze_id = [hlava_klauze_id]
        slova_klauze_form = [veta_info["predikáty form"][hlava_klauze_form]]
        hledani_slov_klauzi(poradi_vety, [hlava_klauze_id], veta_info["predikáty id"])
        slova_veta_id.append(slova_klauze_id)
        slova_veta_form.append(slova_klauze_form)

    veta_info["slova klauzí form"] = slova_veta_form
    #veta_info["slova klauzí id"] = slova_veta_id

    # for klauze in veta_info["slova klauzí id"]:
    #     delka_klauze = len(klauze)
    #     delky_klauzi.append(delka_klauze)

    # veta_info["délky klauzí"] = delky_klauzi


# uložení segmentace do souboru
soubor_k_ulozeni_segmentace = open(OUTPUT_FILE, mode="w", encoding="UTF-8")

for veta in vety_infa:
    soubor_k_ulozeni_segmentace.write("senence id: " + str(veta["id věty"]) + "\n")
    soubor_k_ulozeni_segmentace.write("construct (sentence): " + veta["text"] + "\n")
    soubor_k_ulozeni_segmentace.write("predicates: " + ",".join(veta["predikáty form"]) + "\n")
    for klauze in veta["slova klauzí form"]:
        soubor_k_ulozeni_segmentace.write("constituent (clause) in subconstituents (words): " + ",".join(klauze) + "\n")
    soubor_k_ulozeni_segmentace.write("\n")
    
soubor_k_ulozeni_segmentace.close()



