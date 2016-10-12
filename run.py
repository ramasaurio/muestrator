# -*- coding: utf-8 -*-
from block_model.controller.block_model import BlockModel
from drillhole.controller.composites import Composites
from drillhole.controller.drillholes import Drillholes
from utilities import divideSamplesByLength, divideSamplesByUg, selectCompleteSamples, writeDiameterFile
from preprocess import setDrilholeType
import math


def run():

    folder = 'ejercicio_0/'
    outpath = 'potential_samples.csv'

    compositePath = 'data/muestras_disponibles_variabilidad.csv'
    categVars = ['minty', 'fase']
    numericVars = ['cut', 'clay']
    ugVar = 'fase'
    typeVar = 'samptype'
    diamVar = 'diametro'
    categColumns = [(carvar, str) for carvar in categVars]
    numerColumns = [(numvar, float) for numvar in numericVars]
    compositesColumns = numerColumns + categColumns + [(typeVar, str), (diamVar, str)]

    composites = Composites(path=compositePath, holeid='holeid', middlex='midx', middley='midy', middlez='midz',
                            from_='from', to_='to', columns=compositesColumns, readComposites=True)

    drillholes = Drillholes.makeDrillholes(composites=composites)
    setDrilholeType(drillholes, typeVar, diamVar)

    masa = 80
    pureza = 0.8

    samples = divideSamplesByLength(drillholes, masa)
    completeSamples = selectCompleteSamples(samples, useVar='uso', typeVar=typeVar, use=True, ddh=True)
    samplesByUg = divideSamplesByUg(completeSamples, ugVar, pureza)
    writeDiameterFile(folder + outpath, samplesByUg, typeVar, diamVar, categVars, numericVars)

# (path, samplesByUg, typeVar, diameterVar, categVars=None, numericVars=None)

if __name__ == '__main__':
    run()
