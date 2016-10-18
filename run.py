# -*- coding: utf-8 -*-

from block_model.controller.block_model import BlockModel
from drillhole.controller.composites import Composites
from drillhole.controller.drillholes import Drillholes
from utilities import divideSamplesByLength, divideSamplesByUg, selectCompleteSamples, writeDiameterFile
from preprocess import *


def run():

    folder = 'ejercicio_0/'
    outpath = 'potential_samples.csv'
    compositePath = 'composites/original/composites.csv'

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

    run()


# OLD CODE:
# [origen: run]
# para flaguear las variables 'Estado_Sondaje', 'Campana' en los compóstos
# compositePath = 'composites/original/cy16_spc_seleccion_all.csv'
# collarPath = 'composites/original/collar.csv'
# outPath = 'composites/original/composites.csv'
# composites = Composites(path=compositePath, holeid='dhid', readComposites=True)
# drillholes = Composites(path=collarPath, holeid='HOLEID', columns=[('Estado_Sondaje', str), ('Campana', str)],
#                         readComposites=True)
# flagCompositesWithDrillholes(drillholes, composites, compositePath, outPath,
#                              catVarToFlag=['Estado_Sondaje', 'Campana'])

# [origen: run]
# para flaguear el cruze en el semestre
# blockPath = 'modelo/modelo_me_volator_dog.csv'
# blockColumns = [('buffer_q3q4', int)]
# blockModel = BlockModel(path=blockPath, x='xcentre', y='ycentre', z='zcentre', density='densidad',
#                         columns=blockColumns, readBlocks=True)
# compPath = 'composites/original/composites.csv'
# composites = Composites(path=compPath, holeid='dhid', middlex='midx', middley='midy', middlez='midz',
#                         readComposites=True)
# outPath = 'composites/original/composites_flagq3q4.csv'
# newVars = ['cross_q3q4']
# crossVars = ['buffer_q3q4']
# flagCross(blockModel, composites, compPath, outPath, newVars, crossVars)