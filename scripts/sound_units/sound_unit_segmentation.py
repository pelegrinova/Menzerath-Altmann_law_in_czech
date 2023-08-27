from _rovina_výpovědi import segmentace_na_vypovedi 
from _rovina_clause_unit import segmentace_na_zvukove_klauze 
from _rovina_taktu import doplneni_metadat
from _rovina_taktu import pripojeni_neslabicnych_predlozek
from _rovina_taktu import pripojeni_jednoslabicnych_predlozek
from _rovina_clause_unit import segmentace_klauze_na_slabiky 
from _rovina_taktu import reseni_finalni_pozice
from _rovina_taktu import reseni_inicialni_pozice
from _rovina_taktu import reseni_medialni_pozice
from _rovina_taktu import TypSlova
from _rovina_taktu import Pozice
import re

# insert names (or path) of files for segmentation (row 15) and for output (row 16)
INPUT_FILE = "file_name.txt" # name of the file for segmentation (or the path to this file); use only txt files and UTF-8 coding
OUTPUT_FILE = "segmented_text_file_name.txt" # name of the file for saving the results of segmentation (or the path to this file)


############################### body of the script #####################################################################################
rovina = ["výpověď_klauze_takt", "klauze_takt_slabika", "takt_slabika_hláska"]


def segmentace_na_zvukove_jednotky(text):
    seznam_vypovedi = segmentace_na_vypovedi(text)
    vypovedi_na_klauze = segmentace_na_zvukove_klauze(seznam_vypovedi)
    vypovedi_na_slab_klauze = segmentace_klauze_na_slabiky(vypovedi_na_klauze)

    segmentovany_text = []
    for vypoved in vypovedi_na_slab_klauze:
        segmentovane_vypovedi = []
        for klauze in vypoved:
            klauze_na_slova = klauze.split()
            klauze_s_metadaty = doplneni_metadat(klauze_na_slova)
            klauze_mezitakty_neslab_prdl = pripojeni_neslabicnych_predlozek(klauze_s_metadaty)
            klauze_mezitakty_jednoslab_prdl = pripojeni_jednoslabicnych_predlozek(klauze_mezitakty_neslab_prdl)
            klauze_mezitakty_f_pozice = reseni_finalni_pozice(klauze_mezitakty_jednoslab_prdl)
            klauze_mezitakty_i_pozice = reseni_inicialni_pozice(klauze_mezitakty_f_pozice)
            klauze_mezitakty_m_pozice = reseni_medialni_pozice(klauze_mezitakty_i_pozice)
            segmentovane_vypovedi.append(klauze_mezitakty_m_pozice)
        segmentovany_text.append(segmentovane_vypovedi)
    
    return segmentovany_text


def ulozeni_ke_kontrole(segmentovany_text, puvodni_text, cesta_ulozeni): 
    seznam_vypovedi_chk_hrube = re.split(r"[.?!]+", puvodni_text) 
    seznam_vypovedi_ch = []
    for vypoved_hruba in seznam_vypovedi_chk_hrube:
        vypoved = vypoved_hruba.strip()
        if vypoved:
            seznam_vypovedi_ch.append(vypoved)

    ocekavany_pocet_vypovedi = len(seznam_vypovedi_ch)
    segmentovany_pocet_vypovedi = len(segmentovany_text)
    if ocekavany_pocet_vypovedi != segmentovany_pocet_vypovedi:
        print(f"Nesedí počet výpovědí.")
        print(f"Segmentovaný počet: {segmentovany_pocet_vypovedi}, očekávaný počet: {ocekavany_pocet_vypovedi}")
        

    TYPY_SLOV = \
        {
            TypSlova.klitikon: "K",
            TypSlova.predlozka_neslabicna: "PN",
            TypSlova.predlozka_jednoslabicna: "PJ",
            TypSlova.obycejne: "O"
        }

    with open(cesta_ulozeni, "w", encoding="UTF-8") as pytel:
    
        for chk_vypoved, metadata_vypoved in zip(seznam_vypovedi_ch, segmentovany_text):
            pytel.write(chk_vypoved + "\n")
            for metadata_klauze in metadata_vypoved:
                chk_takty = []

                for metadata_takt in metadata_klauze:
                    chk_slova = []

                    for metadata_slovo in metadata_takt:
                        tortellini =\
                            [
                                metadata_slovo.token
                                # TYPY_SLOV[metadata_slovo.typ],
                                # metadata_slovo.pozice.name,
                                # str(metadata_slovo.pocet_slabik)
                            ]
                        tortellini_spojene = " ".join(tortellini)
                        chk_slova.append(tortellini_spojene)

                    chk_slova_spojena = " ".join(chk_slova)
                    chk_takty.append(chk_slova_spojena)

                chk_takty_spojene = "; ".join(chk_takty)
                pytel.write(chk_takty_spojene + "\n")

                        #pytel.write(metadata_slovo.token + " ")
                

            pytel.write("\n")  # Výpovědi oddělujeme prázdným řádem.
           

# načtení souboru k segmentaci
soubor = open(INPUT_FILE, encoding="UTF-8")
puvodni_text = soubor.read().replace("\n", " ").strip()
soubor.close()

# spouštění skriptu
text_na_zvukove_jednotky = segmentace_na_zvukove_jednotky(puvodni_text)
ulozeni_ke_kontrole(text_na_zvukove_jednotky, puvodni_text, OUTPUT_FILE)    