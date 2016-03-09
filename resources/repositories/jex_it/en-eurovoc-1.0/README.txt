###################
# EUROVOC-INDEXER #
###################

EuroVoc Indexer is an automatic indexing system developed at the JRC.
It learns from previously manually Eurovoc-indexed documents. 
JRC provides a trained version, but advanced users can re-train it on their own data. 

The purpose of this file is to give  users a quick explanation on how to use the software. 
For background information on the methods used, please refer to the web page http://langtech.jrc.ec.europa.eu/Eurovoc.html and to the scientific publication
http://langtech.jrc.ec.europa.eu/Documents/EuroLan-03_Pouliquen-Steinberger-et-al.pdf .



System Requirements:
#####################

The software is implemented in Java and is in principle platform-independent.
For the processing steps described below, please use the executables ending on .bat. 
For Un*x, please use the executables with the suffix .sh.

In order to run the EuroVoc Indexer, Java 5 or higher should be installed.

The machine on which the indexer runs should have a minimum of 2 GB of memory.


Directory Structure:
#####################

bin: 		includes the different executables  provided by the system.
config: 	includes different configuration files to control the behaviour of the software.
documents: 	in the standard configuration, any documents to be indexed should be put here.
lib: 		includes the different libraries used by the system.
resources: 	includes the different resources used by our system, including stop words, 
			thesaurus definitions, and so on.
workspace: 	programs and resources to retrain the software on new documents 
			(only needed when re-training the system).

Gaphical User Interface
###############
To start the graphical interface please execute start_gui.{bat|sh} or start.vbs. 

This interface well allow you to load one document or write some text and then assign some categories to  your 
input. For each category, a list of terms which led to the choice of that category well be shown if the user
selects that category.


Command Line Interface:
#######

The assignment process consists of three steps: 'pre-processing', 'indexing'  and 'post-processing'. Optionally, advanced users can re-train the system on their own data in the 'training' step. All input file to the system must be encoded in utf-8, also any output is written in utf-8. 

Pre-processing:
--------------
Pre-processing means converting the documents that should be indexed into the format used by the software.

For that purpose, please use the executable bin/PreProcess.{bat|sh}.

Please check the file config/PreProcess.properties to change the default settings and to adapt the tool to your needs. This file contains a detailed description of the pre-processing functionality and explains the options you have.


Indexing: 
---------
Indexing is the main process where the assignment of Eurovoc descriptors happens.

Use bin/Index.{bat|sh} for that purpose. This process takes as input the output of the pre-processing module. 

Please consult config/Index.properties for a detailed description of the possible options to adapt the system to your needs.

Post-processing:
----------------
Indexing produces minimal output, i.e. only the ranked list of Eurovoc descriptors assigned. In the post-processing step, additional useful information can be added to the output.
Please look at config/PostProcess.propeties for the available options.

To make use of the post-processing functionality, please use the executable bin/PostProcess.{bat|sh}. 

If you want to execute all three steps at once, you can use the script AllInOneStep.{bat|sh} .

Training:
---------

If you are interested in evaluating the system and in training the system on your own data, please consult the manual. 

------------------------------------------------------------------

This software has been developed at, and is owned by:

	European Commission - Joint Research Centre (JRC)
	IPSC-GlobeSec-OPTIMA
	21027 Ispra (VA), Italy
	Contact: mohamed.ebrahim@jrc.ec.europa.eu 

Contributors: Mohamed Ebrahim, Marco Turchi, Mladen Kolar, Bruno Pouliquen & Ralf Steinberger.	
	
(c) All rights reserved.

