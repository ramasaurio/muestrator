# -*- coding: utf-8 -*-

from block_model.controller.block_model import BlockModel
from drillhole.controller.composites import Composites
from drillhole.controller.drillholes import Drillholes
from utilities import divideSamplesByLength, divideSamplesByUg, selectCompleteSamples, writeDiameterFile
from preprocess import *


def run():

    folder = 'ejercicio_0/'
    outpath = 'potential_samples.csv'
    compositePath = 'composites/original/cy16_spc_seleccion_all.csv'

    categVars = ['minty', 'fase', 'claygroup']
    numericVars = ['cut', 'clay']
    ugVar = 'fase'
    usoVar = 'uso'
    typeVar = 'samptype'
    diamVar = 'diametro'

    masa = 80
    pureza = 0.8

    categColumns = [(carvar, str) for carvar in categVars]
    numerColumns = [(numvar, float) for numvar in numericVars]
    compositesColumns = numerColumns + categColumns + [(typeVar, str), (diamVar, str)]

    composites = Composites(path=compositePath, holeid='holeid', middlex='midx', middley='midy', middlez='midz',
                            from_='from', to_='to', columns=compositesColumns, readComposites=True)

    drillholes = Drillholes.makeDrillholes(composites=composites)
    setDrilholeType(drillholes, typeVar, diamVar)

    samples = divideSamplesByLength(drillholes, masa, diamVar)
    completeSamples = selectCompleteSamples(samples, useVar=usoVar, typeVar=typeVar, use=True, ddh=True)
    samplesByUg = divideSamplesByUg(completeSamples, ugVar, pureza)
    writeDiameterFile(folder + outpath, samplesByUg, typeVar, diamVar, categVars, numericVars)


if __name__ == '__main__':

    compositePath = 'composites/original/cy16_spc_seleccion_all.csv'
    collarPath = 'composites/original/collar.csv'
    outPath = 'composites/original/composites.csv'
    composites = Composites(path=compositePath, holeid='dhid', readComposites=True)
    drillholes = Composites(path=collarPath, holeid='HOLEID', columns=[('Estado_Sondaje', str), ('Campana', str)],
                            readComposites=True)

    flagCompositesWithDrillholes(drillholes, composites, compositePath, outPath,
                                 catVarToFlag=['Estado_Sondaje', 'Campana'])
    # run()
