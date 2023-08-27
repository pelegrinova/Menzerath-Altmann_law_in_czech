import enum
from operator import ne
from pprint import pformat
from traceback import print_tb
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


########################################################## body of the script #####################################################################################################################

# načtení morfologického slovníku jako slovníku (haha)
with open("MorfoCzech_dictionary.csv", encoding="UTF-8") as soubor:
    obsah_slovniku = csv.reader(soubor, delimiter=";")
    slovnik = {}
    for polozka in obsah_slovniku:
        slovnik[polozka[0]] = polozka[1]


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

def hledani_frazi(poradi_vety, hlava, predikaty_vety):
    """najde hlavy frází (=přímé uzly) jednotlivých klauzí; uloží, aby zachováno info o struktuře věta-klauze-fráze"""

    hlavy_frazi_klauze_id = []
    hlavy_frazi_klauze_form = []

    aktualni_veta = parsovani[poradi_vety]
    aktualni_veta = bez_interpunkce(aktualni_veta)

    for token in aktualni_veta:
        if token["id"] != hlava and token["id"] not in predikaty_vety and token["head"] == hlava:
            hlavy_frazi_klauze_id.append(token["id"])
            hlavy_frazi_klauze_form.append(token["form"])

    return hlavy_frazi_klauze_id, hlavy_frazi_klauze_form


def hledani_slov_frazi(poradi_vety, hlavy, predikaty):
    """najde všechna slova frází (rekurzivní funkce); uloží, aby zachováno info o struktuře věta-fráze-slovo"""
    aktualni_veta = parsovani[poradi_vety]
    aktualni_veta = bez_interpunkce(aktualni_veta)
    nove_hlavy = []
    

    if len(hlavy) == 0:
        return

    else:
        for token in aktualni_veta:
            if token["id"] not in predikaty and token["id"] not in hlavy and token["head"] in hlavy:
                nove_hlavy.append(token["id"])
                slova_fraze_id.append(token["id"])
                slova_fraze_form.append(token["form"])
                
    
    hledani_slov_frazi(poradi_vety, nove_hlavy, predikaty)

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
    veta_info["délka v počtu klauzí"] = len(veta_info["predikáty id"])
    veta_info["klauze infa"] = []
    vety_infa.append(veta_info)

# ukládání zbylých informací o větách do seznamu; 
for poradi_vety, veta_info in enumerate(vety_infa):
    hlavy_frazi_veta_id = []
    hlavy_frazi_veta_form = []
    delky_klauzi = []

    hlavy_frazi_klauze_form = []

    slova_frazi_veta_form = []
    slova_frazi_veta_id = []

    for hlava_klauze in veta_info["predikáty id"]:
        fraze_klauze_id, fraze_klauze_form  = hledani_frazi(poradi_vety, hlava_klauze, veta_info["predikáty id"])
        hlavy_frazi_veta_id.append(fraze_klauze_id)
        hlavy_frazi_veta_form.append(fraze_klauze_form)

    veta_info["hlavy frází form"] = hlavy_frazi_veta_form
    veta_info["hlavy frází id"] = hlavy_frazi_veta_id
    
    for klauze in veta_info["hlavy frází id"]:
        delka_klauze = len(klauze)
        delky_klauzi.append(delka_klauze)
    veta_info["délky klauzí"] = delky_klauzi

    # přidávám pro hledání klauzí slov
    slova_veta_id = []
    slova_veta_form = []

    for hlava_klauze_form, hlava_klauze_id in enumerate(veta_info["predikáty id"]):
        slova_klauze_id = [hlava_klauze_id]
        slova_klauze_form = [veta_info["predikáty form"][hlava_klauze_form]]
        hledani_slov_klauzi(poradi_vety, [hlava_klauze_id], veta_info["predikáty id"])
        slova_veta_id.append(slova_klauze_id)
        slova_veta_form.append(slova_klauze_form)

    veta_info["slova klauzí form"] = slova_veta_form
    # končím svoje přidávání

    # vytváření slovníku pro každou klauzi (v seznamu klauze infa)
    for poradi, predikat in enumerate(veta_info["predikáty id"]):
        veta_info["klauze infa"].append({"klauze číslo": poradi})
        #veta_info["klauze infa"][poradi]["klauze hlavy frází"] = veta_info["hlavy frází form"][poradi]
        veta_info["klauze infa"][poradi]["délka klauze ve frázích"] = len(veta_info["hlavy frází form"][poradi])

        slova_frazi_klauze_form = []
        slova_frazi_klauze_id = []

        for hlava_fraze_form, hlava_fraze_id in enumerate(veta_info["hlavy frází id"][poradi]):
            slova_fraze_id = [hlava_fraze_id]
            slova_fraze_form = [veta_info["hlavy frází form"][poradi][hlava_fraze_form]]
            hledani_slov_frazi(poradi_vety, [hlava_fraze_id], veta_info["predikáty id"])
            slova_frazi_klauze_form.append(slova_fraze_form)
            slova_frazi_klauze_id.append(slova_fraze_id)
            

        slova_frazi_veta_form.append(slova_frazi_klauze_form)
        slova_frazi_veta_id.append(slova_frazi_klauze_id)
        #print(slova_frazi_veta_form)


        delka_frazi = []
        for klauze in slova_frazi_veta_form:
            delka_frazi_klauze = []
            for fraze in klauze:
                delka_frazi_klauze.append(len(fraze))
            delka_frazi.append(delka_frazi_klauze)
        

    for poradi, predikat in enumerate(veta_info["predikáty id"]):
        veta_info["klauze infa"][poradi]["slova frází form"] = slova_frazi_veta_form[poradi]
        veta_info["klauze infa"][poradi]["slova frází id"] = slova_frazi_veta_id[poradi]
        veta_info["klauze infa"][poradi]["délka frází ve slovech"] = delka_frazi[poradi]
        veta_info["klauze infa"][poradi]["hlavy fráze"] = veta_info["hlavy frází form"][poradi] # tohle možná smazat
        veta_info["klauze infa"][poradi]["fráze infa"] = []
        
    # vytváření slovníku pro každou frázi v seznamu "fráze infa"
    for poradi_klauze, klauze in enumerate(slova_frazi_veta_form):
        for poradi_fraze, fraze in enumerate(klauze):

            fono_fraze = []
            for slovo in fraze:
                fono_slovo = uprava_textu(slovo)
                fono_fraze.append(fono_slovo)

            morfo_fraze = morfo_segmentace(fono_fraze)

            morfo_fraze_delky = []
            for morfoslovo in morfo_fraze:
                morfoslovo_delka = morfoslovo.count("-") + 1
                morfo_fraze_delky.append(morfoslovo_delka)

            slovnik_fraze =\
                {
                    "fráze číslo": poradi_fraze, 
                    "slova fráze": fraze, 
                    "délka fráze ve slovech": len(fraze), 
                    "morfoslova fráze": morfo_fraze,
                    "délky slov v morfech": morfo_fraze_delky
                }
            veta_info["klauze infa"][poradi_klauze]["fráze infa"].append(slovnik_fraze)


# uložení do souboru
soubor_k_ulozeni_segmentace = open(OUTPUT_FILE, mode="w", encoding="UTF-8")

for veta in vety_infa:
    soubor_k_ulozeni_segmentace.write("senence id: " + str(veta["id věty"]) + "\n")
    soubor_k_ulozeni_segmentace.write("original sentence: " + veta["text"] + "\n")
    for poradi_klauze, klauze in enumerate(veta["slova klauzí form"]):
        soubor_k_ulozeni_segmentace.write("original clause: " + ",".join(klauze) + "\n")
        for fraze in veta["klauze infa"][poradi_klauze]["fráze infa"]:
            soubor_k_ulozeni_segmentace.write("\t" + "construct (phrase): " + ",".join(fraze["slova fráze"]) + "\n")
            soubor_k_ulozeni_segmentace.write("\t" + "\t" + "constituents (words) in subconstituents (morphemes): " + ",".join(fraze["morfoslova fráze"]) + "\n")
    soubor_k_ulozeni_segmentace.write("\n")
    
soubor_k_ulozeni_segmentace.close()