import csv
import re


# insert names (or path) of files for segmentation (row 15) and for output (row 16)
INPUT_FILE = "file_name.txt" #  name of the file for segmentation (or the path to this file); use only txt files and UTF-8 coding
OUTPUT_FILE = "segmented_text_file_name.txt" # name of the file for saving the results of segmentation


############################### body of the script #####################################################################################
DICTIONARY_FILE = "MorfoCzech_dictionary.csv" # the morphological dictionary

def uprava_textu(text):
    """ removal of punctuation marks and other non-alphabetic symbols"""

    znaky = [",", ".", "!", "?", "'", "\"", "<", ">", "-", "–", ":", ";", "„", "“", "=", "%", "&", "#", "@", "/", "\\", "+", "(", ")", "[", "]", "§"]

    for znak in znaky:
        text = text.replace(znak, "")

    # removal of digits
    text = re.sub(r"[0-9]+", "", text)

    # removal of spaces
    text = re.sub(r"\s{2,}", " ", text)

    # splitting text to words
    text_na_slova = text.split(sep=" ")

    # substitution of graphic to represent the sound realisation
    text_na_slova_foneticky = []
    for slovo in text_na_slova: 
        slovo = slovo.replace("pouč", "po@uč")  
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
        slovo = slovo.replace("muzeu", "muzE")  
        slovo = slovo.replace("neutrál", "nEtrál")
        slovo = slovo.replace("eucken", "Ecken")
        slovo = slovo.replace("kreuzmann", "krEzmann")
        slovo = slovo.replace("pilocereus", "pilocerEs")
        slovo = slovo.replace("cephalocereus", "cephalocerEs")
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
        # removal of "@"
        slovo = slovo.replace("@", "")
        text_na_slova_foneticky.append(slovo)

    text_na_slova_uniq_foneticky = set(text_na_slova_foneticky)

    return text_na_slova_foneticky, text_na_slova_uniq_foneticky


# loading of the morphological dictionary as pyhton dict
with open(DICTIONARY_FILE, encoding="UTF-8") as soubor:
    obsah_slovniku = csv.reader(soubor, delimiter=";")
    slovnik = {}
    for polozka in obsah_slovniku:
        slovnik[polozka[0]] = polozka[1]

# file adjustment
with open(INPUT_FILE, encoding="UTF-8") as soubor:
    #slova_k_segmentaci = soubor.read().strip().split(sep="\n")

    text = soubor.read().lower().replace("\n", " ").strip()
    soubor.close()

### here the fun begins

# "phonological" transcription
slova_k_segmentaci, uniq_slova_k_segmentaci = uprava_textu(text)

# autosegmentation
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

text_segmentovany_slouceny = " ".join(segmented_words)

# saving of the segmented text
with open(OUTPUT_FILE, mode="x", encoding="UTF-8") as soubor:
    print(text_segmentovany_slouceny, file=soubor)
