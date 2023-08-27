import re
# funkce s podtržítkem na začátku znamenají interní funkce daného modulu, neměly by se z něj importovat ven

neterminalni_interpunkce = r"[,;:()…—–-]+"
terminalni_interpunkce = r"[.?!]+"


def _zjednoduseni_interpunkci(vypovedi_hrube):
    """Nahradí neterminální interpunkci za čárku, očistí od přebytečných znamínek a mezer"""

    vypovedi_ciste = []

    for vypoved_hruba in vypovedi_hrube:

        vypoved_hruba_carky = re.sub(neterminalni_interpunkce, ",", vypoved_hruba)
        vypoved_hruba_bez_mezer = re.sub(r" *, *", ",", vypoved_hruba_carky).strip(" ,\n\r\t") # (" ,") u stripu znamená, že bude odstraňovat jak mezery, jak čárky 
        vypoved_cista = re.sub(r",{2,}", ",", vypoved_hruba_bez_mezer)

        if vypoved_cista != "":
            vypovedi_ciste.append(vypoved_cista)

    return vypovedi_ciste


def _segmentace_na_vypovedi(text):
    # obsahuje ale i prázdné "výpovědi", artefakty po splitu
    
    text = text.replace(" a ", ", a ")
    vypovedi_hruba_segmentace = re.split(terminalni_interpunkce, text)
    
    return vypovedi_hruba_segmentace


def segmentace_na_vypovedi(text):
     segmenovane = _segmentace_na_vypovedi(text)
     vypovedi_hotove = _zjednoduseni_interpunkci(segmenovane)
     
     return vypovedi_hotove
