# -*- coding: utf-8 -*-
from block_model.controller.block_model import BlockModel
from drillhole.controller.composites import Composites
from drillhole.controller.drillholes import Drillholes
from utilities import divideSamplesByLength, divideSamplesByUg, selectCompleteSamples, writeDiameterFile
from preprocess import setDrilholeType
import math


def run():

    compositePath = 'data/muestras_disponibles_variabilidad.csv'

    compositesColumns = [('cut', float), ('minty', str), ('alte', str), ('lito', str), ('drilltype', str),
                         ('clay', float), ('mo', float), ('uso', int), ('csr', float), ('plan', int), ('ugvar', int),
                         ('samptype', str), ('spi', float), ('dom', int)]
    composites = Composites(path=compositePath, holeid='holeid', middlex='midx', middley='midy', middlez='midz',
                            from_='from', to_='to', columns=compositesColumns, readComposites=True)

    drillholes = Drillholes.makeDrillholes(composites=composites)
    setDrilholeType(drillholes)

    soporte = 3  # largo en metros del soporte
    tolerancia = 2  # soportes adicionales
    pureza = 0.8  # mínimo de pureza en ug para considerar muestra
    ugvar = 'ugvar'  # variable con la info de la ug

    samples = divideSamplesByLength(drillholes, 12, soporte, tolerancia)
    completeSamples = selectCompleteSamples(samples)
    samplesByUg = divideSamplesByUg(completeSamples, ugvar, pureza)
    writeDiameterFile(folder + 'complete_samples_PQ.csv', samplesByUg, 'PQ', 0.8, ugvar)

# (path, samplesByUg, typeVar, diameterVar, categVars=None, numericVars=None)

if __name__ == '__main__':
    run()
