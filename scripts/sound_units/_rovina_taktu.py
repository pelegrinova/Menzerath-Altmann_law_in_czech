from collections import namedtuple
from enum import Enum
from itertools import chain
from math import ceil
from math import floor


# ty výčty slov by měly být asi už nasekané na slabiky a foneticky přepsané bo dělení na slabiky se děje už dříve
TypSlova = Enum("TypSlova", ["klitikon", "predlozka_neslabicna", "predlozka_jednoslabicna", "obycejne"])
typy_slov_vycty = \
    {
        TypSlova.klitikon: ["jsem", "jsi", "je", "jsme", "jste", "jsO", "byX", "bys", "by", "mi", "mňe", "ti", "ťe", "ho", "mu", "ji", "se", "si"],
        TypSlova.predlozka_neslabicna: ["k", "s", "v", "z"], 
        TypSlova.predlozka_jednoslabicna: ["na", "do", "o", "za", "pro", "po", "od", "u", "při", "před", "bez", "pod", "nad", "přes", "dle", "skrz", "vstříc", "zpod", "dík", "vňe", "vzdor", "ob", "stran", "ke", "ve", "ze", "sé"] # předložka se je ručně přepsané na sé, aby se odližila od zájmena 
    }

Pozice = Enum("Pozice", ["I", "M", "F"])
SlovoMetadata = namedtuple("SlovoMetadata", ["token", "typ", "pozice", "pocet_slabik", "pocet_hlasek"])


def _urceni_typu_slova(slovo):
    for typ_vycet in typy_slov_vycty:
        if slovo.lower() in typy_slov_vycty[typ_vycet]:
            typ_slovo = typ_vycet
            break
    else:
        typ_slovo = TypSlova.obycejne

    return typ_slovo


def _urceni_pozice_slova(poradi_slova, delka_klauze):
    if poradi_slova == 0:
        pozice_slova = Pozice.I
    elif poradi_slova == (delka_klauze-1):
        pozice_slova = Pozice.F
    else:
        pozice_slova = Pozice.M

    return pozice_slova


def _pocitani_slabik_slova(slovo_na_slabiky):
    if slovo_na_slabiky.lower() not in typy_slov_vycty[TypSlova.predlozka_neslabicna]:
        pocet_slabik = slovo_na_slabiky.count("-") + 1  # alternativní možnost: pocet_slabik = len(slovo_na_slabiky.split("-"))
    else:
        pocet_slabik = 0

    return pocet_slabik


def _pocitani_hlasek_slova(slovo_na_slabiky):
    slovo = slovo_na_slabiky.replace("-", "")
    pocet_hlasek = len(slovo)

    return pocet_hlasek


def doplneni_metadat(zvukova_klauze_slova):
    matedata_klauze = []
    for poradi, slovo in enumerate(zvukova_klauze_slova):
        typ_slovo = _urceni_typu_slova(slovo)
        pozice = _urceni_pozice_slova(poradi, len(zvukova_klauze_slova))
        pocet_slabik = _pocitani_slabik_slova(slovo)
        pocet_hlasek = _pocitani_hlasek_slova(slovo)
        
        metadata_aktualni_slovo = SlovoMetadata(slovo, typ_slovo, pozice, pocet_slabik, pocet_hlasek)
        matedata_klauze.append(metadata_aktualni_slovo)

    return matedata_klauze


def pripojeni_neslabicnych_predlozek(metadata_klauze):
    klauze_neslabicne = []
    mezitakt = []
    for metadata_slovo in metadata_klauze: 
 
        if metadata_slovo.typ is TypSlova.predlozka_neslabicna:
            mezitakt.append(metadata_slovo)
            if metadata_slovo.pozice == Pozice.F:
                klauze_neslabicne[-1].extend(mezitakt)  # i kdyby klauze složená pouze z neslabičné prdl, nevadí bo bude mít I pozici a toto se nepustí
        else:
            mezitakt.append(metadata_slovo)
            klauze_neslabicne.append(mezitakt)
            mezitakt = []

    return klauze_neslabicne


def pripojeni_jednoslabicnych_predlozek(mezitakty):
    klauze_jednoslabice = []
    po_jednoslabicne = False
    for mezitakt in mezitakty:

        if po_jednoslabicne == True: 
            klauze_jednoslabice[-1].extend(mezitakt)
            po_jednoslabicne = False
        else:
            if mezitakt[-1].typ is TypSlova.predlozka_jednoslabicna:  # přepsala jsem, aby se to dívalo na poslední položku v mezitaktu bo před ní můžou být ještě neslabičné předložky
                po_jednoslabicne = True
            klauze_jednoslabice.append(mezitakt)

    return klauze_jednoslabice


def _pocitani_finalnich_klitik_klauze(klauze_s_mezitakty):
    pocet_F_klitik = 0
    for hovni_mezitakt in reversed(klauze_s_mezitakty):
        if len(hovni_mezitakt) == 1 and hovni_mezitakt[0].typ == TypSlova.klitikon: # kdyby byl mezitakt neslabičná + klitikon na konci, nerozpozná to jako klitikon, ale obyč jednoslabičné slovo na konci - podle mě nevadí bo by se to stejně nemělo stát, popř. jen velmi okrajově
            pocet_F_klitik += 1
        else:
            break
   
    return pocet_F_klitik
        

def _urcovani_inicialnich_jednoslabicnych(klauze_s_mezitakty):
    seznam_i_jednoslabicnych = []

    for mezitakt in klauze_s_mezitakty:
        pocet_slabik_mezitaktu = _pocitani_slabik_mezitaktu(mezitakt)
        if pocet_slabik_mezitaktu == 1:
            seznam_i_jednoslabicnych = seznam_i_jednoslabicnych + mezitakt
        else:
            break

    return seznam_i_jednoslabicnych


def _pocitani_slabik_mezitaktu(mezitakt):
    pocet_slabik = 0

    for slovo in mezitakt:
        pocet_slabik += slovo.pocet_slabik

    return pocet_slabik


def _skladani_casti_klauze(seznam_casti):
    nova_klauze = []
    for cast in seznam_casti:
        nova_klauze += cast

    return nova_klauze


def reseni_finalni_pozice(klauze_s_mezitakty):
    pocet_f_klitik = _pocitani_finalnich_klitik_klauze(klauze_s_mezitakty) 

    if pocet_f_klitik == len(klauze_s_mezitakty) or pocet_f_klitik == 0: # pokud je klauze složena jen z klitik, neděje se v téhle fázi nic
        return klauze_s_mezitakty
    
    seznam_f_klitik = []
    for klitikon in klauze_s_mezitakty[-pocet_f_klitik:]:
        seznam_f_klitik.extend(klitikon)

    sekvence_pred_f_klitiky = klauze_s_mezitakty[:-pocet_f_klitik]
    pocet_slabik_mezitaktu_pred_f = _pocitani_slabik_mezitaktu(sekvence_pred_f_klitiky[-1])

    nova_klauze_s_mezitakty = []

    if pocet_f_klitik == 1:
        zacatek = sekvence_pred_f_klitiky[:-1]
        konec = [sekvence_pred_f_klitiky[-1] + seznam_f_klitik]
        casti_ke_spojeni = [zacatek, konec]
    elif pocet_f_klitik == 2:
        if pocet_slabik_mezitaktu_pred_f < 5:
            zacatek = sekvence_pred_f_klitiky[:-1]
            konec = [sekvence_pred_f_klitiky[-1] + seznam_f_klitik]
            casti_ke_spojeni = [zacatek, konec]
        else:
            zacatek = sekvence_pred_f_klitiky
            konec = [seznam_f_klitik]
            casti_ke_spojeni = [zacatek, konec]
    elif pocet_f_klitik == 3:
        if pocet_slabik_mezitaktu_pred_f < 4:
            zacatek = sekvence_pred_f_klitiky[:-1]
            konec = [sekvence_pred_f_klitiky[-1] + seznam_f_klitik]
            casti_ke_spojeni = [zacatek, konec]
        else:
            zacatek = sekvence_pred_f_klitiky
            konec = [seznam_f_klitik]
            casti_ke_spojeni = [zacatek, konec]
    elif pocet_f_klitik ==  4:
        if pocet_slabik_mezitaktu_pred_f < 3:
            zacatek = sekvence_pred_f_klitiky[:-1]
            konec = [sekvence_pred_f_klitiky[-1] + seznam_f_klitik]
            casti_ke_spojeni = [zacatek, konec] 
        elif pocet_slabik_mezitaktu_pred_f in [3, 4]:
            zacatek = sekvence_pred_f_klitiky[:-1]
            prostredek = [sekvence_pred_f_klitiky[-1] + seznam_f_klitik[:2]]
            konec = [seznam_f_klitik[2:]]
            casti_ke_spojeni = [zacatek, prostredek, konec] 
        else:
            zacatek = sekvence_pred_f_klitiky
            konec = [seznam_f_klitik]
            casti_ke_spojeni = [zacatek, konec]
    elif pocet_f_klitik == 5:
        if pocet_slabik_mezitaktu_pred_f < 4:
            zacatek = sekvence_pred_f_klitiky[:-1]
            prostredek = [sekvence_pred_f_klitiky[-1] + seznam_f_klitik[:2]]
            konec = [seznam_f_klitik[2:]]
            casti_ke_spojeni = [zacatek, prostredek, konec] 
        elif pocet_slabik_mezitaktu_pred_f == 4:
            zacatek = sekvence_pred_f_klitiky
            prostredek = [seznam_f_klitik[:2]]
            konec = [seznam_f_klitik[2:]]
            casti_ke_spojeni = [zacatek, prostredek, konec]
        else:
            zacatek = sekvence_pred_f_klitiky
            prostredek = [seznam_f_klitik[:3]]
            konec = [seznam_f_klitik[3:]]
            casti_ke_spojeni = [zacatek, prostredek, konec]
    elif pocet_f_klitik == 6:
        if pocet_slabik_mezitaktu_pred_f < 4:
            zacatek = sekvence_pred_f_klitiky[:-1]
            prostredek = [sekvence_pred_f_klitiky[-1] + seznam_f_klitik[:2]]
            konec = [seznam_f_klitik[2:]]
            casti_ke_spojeni = [zacatek, prostredek, konec]
        else:
            zacatek = sekvence_pred_f_klitiky
            prostredek = [seznam_f_klitik[:3]]
            konec = [seznam_f_klitik[3:]]
            casti_ke_spojeni = [zacatek, prostredek, konec]
    elif pocet_f_klitik > 6:
        if pocet_f_klitik % 2 == 0:
            delici_cast = pocet_f_klitik // 2
            zacatek = sekvence_pred_f_klitiky
            prostredek = [seznam_f_klitik[:delici_cast]]
            konec = [seznam_f_klitik[delici_cast:]]
            casti_ke_spojeni = [zacatek, prostredek, konec]
        else:
            if pocet_slabik_mezitaktu_pred_f < 4:
                delici_cast = floor(pocet_f_klitik/2) # zaokrouhlí vždy dolů
                zacatek = sekvence_pred_f_klitiky
                prostredek = [seznam_f_klitik[:delici_cast]]
                konec = [seznam_f_klitik[delici_cast:]]
                casti_ke_spojeni = [zacatek, prostredek, konec]
            else:
                delici_cast = ceil(pocet_f_klitik/2) # zaokrouhlí vždy nahoru
                zacatek = sekvence_pred_f_klitiky
                prostredek = [seznam_f_klitik[:delici_cast]]
                konec = [seznam_f_klitik[delici_cast:]]
                casti_ke_spojeni = [zacatek, prostredek, konec]
    nova_klauze_s_mezitakty = _skladani_casti_klauze(casti_ke_spojeni)

    return nova_klauze_s_mezitakty


def reseni_inicialni_pozice(klauze_s_mezitakty):
    seznam_i_jednoslabicnych = _urcovani_inicialnich_jednoslabicnych(klauze_s_mezitakty)
    pocet_slabik_I_jednoslabicnych = _pocitani_slabik_mezitaktu(seznam_i_jednoslabicnych) # musím počítat slabiky, protože tam může být i neslabičná předložka
    sekvence_po_i_jednoslabicnych = klauze_s_mezitakty[pocet_slabik_I_jednoslabicnych:]
    
    if seznam_i_jednoslabicnych and len(klauze_s_mezitakty) > 1:
        if pocet_slabik_I_jednoslabicnych == 1:
            inicialni_mezitakt = seznam_i_jednoslabicnych + sekvence_po_i_jednoslabicnych[0]
            klauze_s_novymi_mezitakty = [inicialni_mezitakt] + sekvence_po_i_jednoslabicnych[1:]
        elif pocet_slabik_I_jednoslabicnych in [2, 3, 4]:
            klauze_s_novymi_mezitakty = [seznam_i_jednoslabicnych] + sekvence_po_i_jednoslabicnych  
        elif pocet_slabik_I_jednoslabicnych == 5:
            inicialni_mezitakt_prvni = seznam_i_jednoslabicnych[:3]
            inicialni_mezitakt_druhy = seznam_i_jednoslabicnych[3:]
            klauze_s_novymi_mezitakty = [inicialni_mezitakt_prvni] + [inicialni_mezitakt_druhy] + sekvence_po_i_jednoslabicnych
        elif pocet_slabik_I_jednoslabicnych == 6:
            inicialni_mezitakt_prvni = seznam_i_jednoslabicnych[:3]
            inicialni_mezitakt_druhy = seznam_i_jednoslabicnych[3:]
            klauze_s_novymi_mezitakty = [inicialni_mezitakt_prvni] + [inicialni_mezitakt_druhy] + sekvence_po_i_jednoslabicnych
        elif pocet_slabik_I_jednoslabicnych == 7:
            inicialni_mezitakt_prvni = seznam_i_jednoslabicnych[:4]
            inicialni_mezitakt_druhy = seznam_i_jednoslabicnych[4:]
            klauze_s_novymi_mezitakty = [inicialni_mezitakt_prvni] + [inicialni_mezitakt_druhy] + sekvence_po_i_jednoslabicnych
        # tohle přidávám nad rámec palkové, snaha o extrapolaci, abych zachytila i atypické stavy aspoň nějak rozumně
        elif pocet_slabik_I_jednoslabicnych > 7:   
            if pocet_slabik_I_jednoslabicnych % 2 == 0:
                cast = pocet_slabik_I_jednoslabicnych//2
                inicialni_mezitakt_prvni = seznam_i_jednoslabicnych[:cast]
                inicialni_mezitakt_druhy = seznam_i_jednoslabicnych[cast:]
                klauze_s_novymi_mezitakty = [inicialni_mezitakt_prvni] + [inicialni_mezitakt_druhy] + sekvence_po_i_jednoslabicnych
            else:
                cast = ceil(pocet_slabik_I_jednoslabicnych/2)
                inicialni_mezitakt_prvni = seznam_i_jednoslabicnych[:cast]
                inicialni_mezitakt_druhy = seznam_i_jednoslabicnych[cast:]
                klauze_s_novymi_mezitakty = [inicialni_mezitakt_prvni] + [inicialni_mezitakt_druhy] + sekvence_po_i_jednoslabicnych
    else:
        klauze_s_novymi_mezitakty = klauze_s_mezitakty
        
    return klauze_s_novymi_mezitakty


def reseni_medialni_pozice(klauze_s_mezitakty):
    nova_klauze_s_mezitakty = [] 
    seznam_m_jednoslabicnych = []

    if len(klauze_s_mezitakty) == 1:
        return klauze_s_mezitakty
  
    for mezitakt in klauze_s_mezitakty:
        je_m_jednoslabicne = _pocitani_slabik_mezitaktu(mezitakt) == 1 and mezitakt[-1].pozice is not Pozice.F
 
        if je_m_jednoslabicne:
            seznam_m_jednoslabicnych = seznam_m_jednoslabicnych + mezitakt 
        elif seznam_m_jednoslabicnych:
            pocet_slabik_predmedialniho = _pocitani_slabik_mezitaktu(nova_klauze_s_mezitakty[-1])
            pocet_slabik_seznamu_m_jednoslabicnych = _pocitani_slabik_mezitaktu(seznam_m_jednoslabicnych)

            if pocet_slabik_seznamu_m_jednoslabicnych == 1:
                zacatek = nova_klauze_s_mezitakty[:-1]
                konec = [nova_klauze_s_mezitakty[-1] + seznam_m_jednoslabicnych]
                casti_ke_spojeni = [zacatek, konec]
            elif pocet_slabik_seznamu_m_jednoslabicnych == 2:
                if pocet_slabik_predmedialniho < 5:
                    zacatek = nova_klauze_s_mezitakty[:-1]
                    konec = [nova_klauze_s_mezitakty[-1] + seznam_m_jednoslabicnych]
                    casti_ke_spojeni = [zacatek, konec]
                else:
                    zacatek = nova_klauze_s_mezitakty
                    konec = [seznam_m_jednoslabicnych]
                    casti_ke_spojeni = [zacatek, konec]
            elif pocet_slabik_seznamu_m_jednoslabicnych == 3:
                if pocet_slabik_predmedialniho < 4:
                    zacatek = nova_klauze_s_mezitakty[:-1]
                    konec = [nova_klauze_s_mezitakty[-1] + seznam_m_jednoslabicnych]
                    casti_ke_spojeni = [zacatek, konec]
                else:
                    zacatek = nova_klauze_s_mezitakty
                    konec = [seznam_m_jednoslabicnych]
                    casti_ke_spojeni = [zacatek, konec]
            elif pocet_slabik_seznamu_m_jednoslabicnych == 4:
                if pocet_slabik_predmedialniho < 3:
                    zacatek = nova_klauze_s_mezitakty[:-1]
                    konec = [nova_klauze_s_mezitakty[-1] + seznam_m_jednoslabicnych]
                    casti_ke_spojeni = [zacatek, konec]
                elif pocet_slabik_predmedialniho in [3, 4]:
                    zacatek = nova_klauze_s_mezitakty[:-1]
                    prostredek = [nova_klauze_s_mezitakty[-1] + seznam_m_jednoslabicnych[:2]]
                    konec = [seznam_m_jednoslabicnych[2:]]
                    casti_ke_spojeni = [zacatek, prostredek, konec]
                else:
                    zacatek = nova_klauze_s_mezitakty
                    konec = [seznam_m_jednoslabicnych]
                    casti_ke_spojeni = [zacatek, konec]
            elif pocet_slabik_seznamu_m_jednoslabicnych == 5:
                if pocet_slabik_predmedialniho < 4:
                    zacatek = nova_klauze_s_mezitakty[:-1]
                    prostredek = [nova_klauze_s_mezitakty[-1] + seznam_m_jednoslabicnych[:2]]
                    konec = [seznam_m_jednoslabicnych[2:]]
                    casti_ke_spojeni = [zacatek, prostredek, konec]
                elif pocet_slabik_predmedialniho == 4:
                    zacatek = nova_klauze_s_mezitakty
                    prostredek = [seznam_m_jednoslabicnych[:2]]
                    konec = [seznam_m_jednoslabicnych[2:]]
                    casti_ke_spojeni = [zacatek, prostredek, konec]
                else:
                    zacatek = nova_klauze_s_mezitakty
                    prostredek = [seznam_m_jednoslabicnych[:3]]
                    konec = [seznam_m_jednoslabicnych[3:]]
                    casti_ke_spojeni = [zacatek, prostredek, konec]
            elif pocet_slabik_seznamu_m_jednoslabicnych == 6:
                if pocet_slabik_predmedialniho < 4:
                    zacatek = nova_klauze_s_mezitakty[:-1]
                    prostredek = [nova_klauze_s_mezitakty[-1] + seznam_m_jednoslabicnych[:2]]
                    konec = [seznam_m_jednoslabicnych[2:]]
                    casti_ke_spojeni = [zacatek, prostredek, konec]
                else:
                    zacatek = nova_klauze_s_mezitakty
                    prostredek = [seznam_m_jednoslabicnych[:3]]
                    konec = [seznam_m_jednoslabicnych[3:]]
                    casti_ke_spojeni = [zacatek, prostredek, konec]
            elif pocet_slabik_seznamu_m_jednoslabicnych > 6:  # vkládám nad rámec palkové, viz předešlé fce, probrat s R
                if pocet_slabik_seznamu_m_jednoslabicnych % 2 == 0:
                    zacatek = nova_klauze_s_mezitakty
                    prostredek = [seznam_m_jednoslabicnych[:pocet_slabik_seznamu_m_jednoslabicnych//2]]
                    konec = [seznam_m_jednoslabicnych[pocet_slabik_seznamu_m_jednoslabicnych//2:]]
                    casti_ke_spojeni = [zacatek, prostredek, konec]
                else:
                    if pocet_slabik_predmedialniho < 4:
                        delici_cast = floor(pocet_slabik_seznamu_m_jednoslabicnych/2) # zaokrouhlí vždy dolů
                        zacatek = nova_klauze_s_mezitakty
                        prostredek = [seznam_m_jednoslabicnych[:delici_cast]]
                        konec = [seznam_m_jednoslabicnych[delici_cast:]]
                        casti_ke_spojeni = [zacatek, prostredek, konec]
                    else:
                        cast = ceil(len(seznam_m_jednoslabicnych)/2)
                        zacatek = nova_klauze_s_mezitakty
                        prostredek = [seznam_m_jednoslabicnych[:cast]]
                        konec = [seznam_m_jednoslabicnych[cast:]]
                        casti_ke_spojeni = [zacatek, prostredek, konec]
            seznam_m_jednoslabicnych = []
            spojene_casti = _skladani_casti_klauze(casti_ke_spojeni)
            casti_nove_klauze = [spojene_casti, [mezitakt]]
            nova_klauze_s_mezitakty = _skladani_casti_klauze(casti_nove_klauze)
        else:
            casti_nove_klauze = [nova_klauze_s_mezitakty, [mezitakt]]
            nova_klauze_s_mezitakty = _skladani_casti_klauze(casti_nove_klauze)

    return nova_klauze_s_mezitakty
