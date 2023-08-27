import re
from rovina_slabiky import segmentace_na_slabiky

#text = ['Že bych se,konečně,dostala k další rovině', 'Je  mi trochu zima,přestože se tady,u oráče,topí']
#text = ['Chci večeři,spánek', 'A pivo', 'Dobré,to znamená', 'radegast,dvanáctku', 'Že,Štěpáne', 'Ano,Káťo', 'Ale,možná,bys,třeba,mohla zkusit i jiné,lagunové', 'Lagunové pivo,svrchně kvašené,to mi připomíná společnou,první', 'noc', 'U tebe,Byla hezká,i já', 'Byla,i ty', 'Máš mě ráda', 'ptá se Štěpán', 'Mám tě ráda,Pusu na to', 'a moc', 'Veles se myje', 'Přišel', 'zeptal se Štěpán', 'Kdo ví', 'mrzutě', 'odpověděla Káťa']


def segmentace_na_zvukove_klauze(seznam_vypovedi):
    """Segmentuje vypovedi na zvukové klauze"""

    zvukove_klauze = []

    for vypoved in seznam_vypovedi:
        zvukova_klauze_hruba = re.split(r",+", vypoved)
        zvukova_klauze_hotova = list(filter(None, zvukova_klauze_hruba))
        zvukove_klauze.append(zvukova_klauze_hotova)

    return zvukove_klauze


def segmentace_klauze_na_slabiky(zvukove_klauze):
    vypoved_zvukove_klauze_na_slabiky = []

    for zvukove_klauze_vypoved in zvukove_klauze:
        zvukove_klauze_na_slabiky = []
        for zvukova_klauze in zvukove_klauze_vypoved:
            #print(zvukova_klauze)

            klauze_na_slabiky = segmentace_na_slabiky(" " + zvukova_klauze.lower() + " ") # tu musí být mezera na začátku bo pobočné slabiky (jsou na začátku slova) a na konci...buchsuť
            zvukove_klauze_na_slabiky.append(klauze_na_slabiky)
        
        vypoved_zvukove_klauze_na_slabiky.append(zvukove_klauze_na_slabiky)

    return vypoved_zvukove_klauze_na_slabiky
