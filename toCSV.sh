#!/bin/bash

pathWorks='/home/wrfchem/test/experiment/other/GFS'
source /home/wrfchem/anaconda3/bin/activate GIS
	python $pathWorks/toCSV.py
conda deactivate

