# -*- coding: utf-8 -*-
from block_model.controller.block_model import BlockModel
from drillhole.controller.composites import Composites
from drillhole.controller.drillholes import Drillholes
from utilities import divideSamplesByLength, divideSamplesByUg, selectCompleteSamples, writeDiameterFile
import math


def run:


    auxsamples = divideSamplesByLength(drillholes, largo, soporte, tolerancia)
    completeSamples = selectCompleteSamples(auxsamples)
    samplesByUg = divideSamplesByUg(completeSamples, ugvar, pureza)
    writeFile(folder + 'complete_samples_PQ.csv', samplesByUg, 'PQ', 0.8, ugvar)