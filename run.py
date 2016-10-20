# -*- coding: utf-8 -*-

# from block_model.controller.block_model import BlockModel
from drillhole.controller.composites import Composites
from drillhole.controller.drillholes import Drillholes
from utilities import divideSamplesByLength, divideSamplesByUg, selectCompleteSamples, writeDiameterFile
from preprocess import *


def run():
    # -- EJERCICIO 1 -- #
    folder = 'ejercicio_1/'
    outpath = 'potential_samples_group.csv'
    compositePath = 'composites/original/composites_flag_cross2.csv'

    holeid = 'dhid'
    midx, midy, midz = 'midx', 'midy', 'midz'
    from_, to_ = 'from', 'to'

    categVars = ['mine', 'alte', 'lito', 'fase', 'Estado_Sondaje', 'Campana', 'banco', 'fyear', 'periodo_fy17']
    numericVars = ['cut', 'clay', 'co3']
    groups = {'clay': [(15, "Bajo"), (19, "Medio"), (100, "Alta")],
              'co3': [(0.3, "Bajo"), (0.5, "Medio"), (100, "Alto")]}
    crossVars = ['cross_f18', 'cross_f19']
    ugVar = 'mine'
    usoVars = ['uso_r', 'uso_t']
    typeVar = 'drill'
    diamVar = 'diam'

    validUg = ['SUCC', 'SUCV']
    masa = 92
    tMasa = 80
    pureza = 0.7
    # -- EJERCICIO 1 -- #

    categColumns = [(carvar, str) for carvar in categVars]
    numerColumns = [(numvar, float) for numvar in numericVars]
    usoColumns = [(usovar, str) for usovar in usoVars]
    auxColumns = [(typeVar, str), (diamVar, str), (ugVar, str)]
    crossColumns = [(cross, int) for cross in crossVars]

    compositesColumns = numerColumns + categColumns + auxColumns + crossColumns + usoColumns

    composites = Composites(path=compositePath, holeid=holeid,   middlex=midx, middley=midy, middlez=midz,
                            from_=from_, to_=to_, columns=compositesColumns, readComposites=True)

    drillholes = Drillholes.makeDrillholes(composites=composites)
    setDrilholeType(drillholes, typeVar, diamVar)

    print('comp totales', len(composites))
    print('sondajes', len(drillholes))
    samples = divideSamplesByLength(drillholes, masa, diamVar)
    print('divididos', len(samples))
    completeSamples = selectCompleteSamples(samples, useVars=usoVars, typeVar=typeVar, use=True, ddh=True)
    print('completados', len(completeSamples))
    samplesByUg = divideSamplesByUg(completeSamples, ugVar, pureza, validUg)
    print('ugeados', len(samplesByUg))
    writeDiameterFile(folder + outpath, samplesByUg, typeVar, diamVar, tMasa, categVars, numericVars, crossVars, groups)
    print('escritos')

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

# [origen: run]
# para flaguear los cruces anuales
# blockPath = 'modelo/modelo_anual_volator_dog.csv'
# blockColumns = [('buffer_fy18', int), ('buffer_fy19', int)]
# blockModel = BlockModel(path=blockPath, x='xcentre', y='ycentre', z='zcentre', density='densidad',
#                         columns=blockColumns, readBlocks=True)
# compPath = 'composites/original/composites_flagq3q4.csv'
# composites = Composites(path=compPath, holeid='dhid', middlex='midx', middley='midy', middlez='midz',
#                         readComposites=True)
# outPath = 'composites/original/composites_flag_q3q4_f18_f19.csv'
# newVars = ['cross_f18', 'cross_f19']
# crossVars = ['buffer_fy18', 'buffer_fy19']
# flagCross(blockModel, composites, compPath, outPath, newVars, crossVars)

# [origen: run]
# para flaguear clay y co3 del modelo cuando no existiera info
# blockPath = 'modelo/modelo_me_volator_dog.csv'
# blockColumns = [('co3', float), ('clay', float)]
# blockModel = BlockModel(path=blockPath, x='xcentre', y='ycentre', z='zcentre', density='densidad',
#                         columns=blockColumns, readBlocks=True)
# compPath = 'composites/original/composites_flag_q3q4_f18_f19.csv'
# composites = Composites(path=compPath, holeid='dhid', middlex='midx', middley='midy', middlez='midz',
#                         readComposites=True)
# outPath = 'composites/original/composites_flag_cross.csv'
# numVarToFlag = ['co3', 'clay']
# flagCompositesWithBlocks(blockModel, composites, compPath, outPath, numVarToFlag=numVarToFlag)

# [origen: run]
# para flaguear clay y co3 del modelo cuando no existiera info
# blockPath = 'modelo/modelo_me_volator_dog.csv'
# blockColumns = [('periodo_fy17', str)]
# blockModel = BlockModel(path=blockPath, x='xcentre', y='ycentre', z='zcentre', density='densidad',
#                         columns=blockColumns, readBlocks=True)
# compPath = 'composites/original/composites_flag_cross.csv'
# composites = Composites(path=compPath, holeid='dhid', middlex='midx', middley='midy', middlez='midz',
#                         readComposites=True)
# outPath = 'composites/original/composites_flag_cross2.csv'
# catVarToFlag = ['periodo_fy17']
# flagCompositesWithBlocks(blockModel, composites, compPath, outPath, catVarToFlag=catVarToFlag)

# -- EJERCICIO 0 -- #
# folder = 'ejercicio_0/'
# outpath = 'potential_samples3.csv'
# compositePath = 'composites/original/composites_flag_cross2.csv'
#
# holeid = 'dhid'
# midx, midy, midz = 'midx', 'midy', 'midz'
# from_, to_ = 'from', 'to'
#
# categVars = ['mine', 'alte', 'lito', 'fase', 'Estado_Sondaje', 'Campana', 'banco', 'fyear', 'periodo_fy17']
# numericVars = ['cut', 'clay', 'co3']
# groups = {'clay': [(15, "Bajo"), (19, "Medio"), (100, "Alta")],
#           'co3': [(0.3, "Bajo"), (0.5, "Medio"), (100, "Alto")]}
# crossVars = ['cross_q3q4']
# ugVar = 'mine'
# usoVars = ['uso_r', 'uso_t']
# typeVar = 'drill'
# diamVar = 'diam'
#
# validUg = ['SUCC', 'SUCV']
# masa = 46
# pureza = 0.7
# -- EJERCICIO 0 -- #

# -- EJERCICIO 1 -- #
# folder = 'ejercicio_1/'
# outpath = 'potential_samples1.csv'
# compositePath = 'composites/original/composites_flag_cross2.csv'
#
# holeid = 'dhid'
# midx, midy, midz = 'midx', 'midy', 'midz'
# from_, to_ = 'from', 'to'
#
# categVars = ['mine', 'alte', 'lito', 'fase', 'Estado_Sondaje', 'Campana', 'banco', 'fyear', 'periodo_fy17']
# numericVars = ['cut', 'clay', 'co3']
# crossVars = ['cross_f18', 'cross_f19']
# ugVar = 'mine'
# usoVars = ['uso_r', 'uso_t']
# typeVar = 'drill'
# diamVar = 'diam'
#
# validUg = ['SUCC', 'SUCV']
# masa = 92
# pureza = 0.7
# -- EJERCICIO 1 -- #
