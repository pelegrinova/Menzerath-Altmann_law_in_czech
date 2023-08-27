# Menzerath-Altmann Law in Czech

This repository contains data and scripts from the dissertation titled "Menzerath-Altmann Law in Czech". The research was carried out at Ostrava University in 2023 under the supervision of Radek Čech. The author of this work is Kateřina Pelegrinová.

## Abstract

This dissertation investigates the application of the Menzerath–Altmann Law to Czech. The aim of this thesis is to examine the relationship between lengths of adjacent units ranging from syntactical to phonological levels. Various types of operationalisations are explored for several units, including sentence, clause, and orthographic word. In addition, this research delves into the segmentation of the same text into sound units, providing a comparison of results and offering insights into the applicability of the law to sound units, taking into consideration the approximations involved. The thesis investigates data across four different genres, namely letters, fairy tales, short stories, and essays. Results of the analyses indicate a good fit for lower language levels, but they generally do not follow the investigated law on syntactical levels. Another aspect of this study focuses on examining the parameters of the truncated mathematical formula used in the analysis.

## Repository Structure

- **nlreg outcomes**: Contains fitting results for both Altmann formulas (truncated and complete).
- **raw data**: Contains lengths of constructs with corresponding average length of constituents and frequency for all studied levels.
- **weighted data**: Contains the same data recalculated to weighted averages.
- **segmented texts**: Contains texts in their segmented form for each level.
- **scripts**: Contains scripts for segmentation for each studied triplet.

Within each folder, there are subfolders for structural and sound levels, further divided by genres or individual levels.

## Guidelines for Using the Scripts

- The scripts are as provided and were originally written in Czech.
- In each script, at the top, there are two constants: `INPUT_FILE` and `OUTPUT_FILE`. These need to be set to the path of the file to be segmented and where the segmented output should be saved respectively.
- The scripts are divided by levels, with an exception for sound levels where one script segments for all levels (utterance - clause-unit - phonological word - syllable - sound) simultaneously.
- The scripts for syntactic segmentation of structural units work with the UDPipe tool using the model `czech-pdt-ud-2.10-220711`. (Note: A newer version of the model has since been released, which processes some aspects differently. Therefore, these scripts might not function optimally with the latest model.)
- The script for morphological segmentation requires an additional morphological dictionary (included) for segmentation. Words not found in this dictionary will remain unsegmented. For morphological segmentation, you can utilize the beta version of the tool [MorphoCzech](https://morphoczech.korpus.cz/index.php).

---

Please make sure to cite the work if you use any data or scripts from this repository for your research or projects.
