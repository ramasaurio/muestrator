# -*- coding: utf-8 -*-
import numpy

massByDiameter = {'PQ': 6, 'HQ': 3, 'HQ3': 3, 'NQ': 1.8}


def writeDiameterFile(path, samplesByUg, typeVar, diameterVar, categVars=None, numericVars=None, crossVars=None):
    outfile = open('data/' + path, 'w')

    # Se escribe el encabezado y el prototipo de fila del archivo
    outheader = 'holeid,from,to,midx,midy,midz,ug,pureza'
    lineskel = '%s,%f,%f,%f,%f,%f,%s,%f'
    if numericVars is not None:
        for numvar in numericVars:
            outheader += ',' + numvar + 'prom'
            outheader += ',' + numvar + 'var'
            outheader += ',' + numvar + 'min'
            outheader += ',' + numvar + 'max'
            lineskel += ',%f,%f,%f,%f'
    if categVars is not None:
        for categ in categVars:
            outheader += ',' + categ + ',ratio'
            lineskel += ',%s,%f'
    outheader += ',tipo,ratio,diametro,ratio'
    lineskel += ',%s,%f,%s,%f'
    if crossVars is not None:
        for crossVar in crossVars:
            outheader += ',' + crossVar
            lineskel += ',%d'
    outheader += '\n'
    lineskel += '\n'
    outfile.write(outheader)

    for ug in samplesByUg:
        for samples, pureza in samplesByUg[ug]:

            lengths = [composite.to_ - composite.from_ for composite in samples]
            totalLen = sum(lengths)

            midx = numpy.mean([composite.middlex for composite in samples])
            midy = numpy.mean([composite.middley for composite in samples])
            midz = numpy.mean([composite.middlez for composite in samples])

            line = [samples[0].holeid, samples[0].from_, samples[-1].to_, midx, midy, midz, str(ug), pureza]

            # Se calculan los valores medio, varianza, mínimo y máximo de las variables numéricas
            if numericVars is not None:
                for var in numericVars:
                    values = [composite[var] for composite in samples if composite[var] >= 0]
                    if len(values) != 0:
                        mean = numpy.mean(values)
                        variance = numpy.var(values)
                        minv = min(values)
                        maxv = max(values)
                        line.extend([mean, variance, minv, maxv])
                    else:
                        line.extend([0, 0, 0, 0])

            # Se calcula el código de la variable categórica mayoritaria
            if categVars is not None:
                for categVar in categVars:
                    codes = {}
                    catVarInSamp = [composite[categVar] for composite in samples]
                    for code, length in zip(catVarInSamp, lengths):
                        if code in codes:
                            codes[code] += length
                        else:
                            codes[code] = length
                    maxCode = ''
                    maxValue = 0
                    for code in codes:
                        if codes[code] > maxValue:
                            maxCode = code
                            maxValue = codes[code]
                    line.append(maxCode)
                    line.append(codes[maxCode] / totalLen)

            # Se determina el contacto de la muestra con el volumen requerido
            if crossVars is not None:
                for crossVar in crossVars:
                    crosses = [sample[crossVar] for sample in samples]
                    if 1 in crosses:
                        line.append(1)
                    elif 2 in crosses:
                        line.append(2)
                    else:
                        line.append(0)

            # Se calcula la proporción de la variable diámetro y tipo
            for categVar in [typeVar, diameterVar]:
                codes = {}
                catVarInSamp = [composite[categVar] for composite in samples]
                for code, length in zip(catVarInSamp, lengths):
                    if code in codes:
                        codes[code] += length
                    else:
                        codes[code] = length
                maxCode = ''
                maxValue = 0
                for code in codes:
                    if codes[code] > maxValue:
                        maxCode = code
                        maxValue = codes[code]
                line.append(maxCode)
                line.append(codes[maxCode] / totalLen)

            outfile.write(lineskel % tuple(line))
            outfile.flush()

    outfile.close()


def divideSamplesByUg(samples, ugvar, purity, validUg):
    samplesByUg = {}
    for sample in samples:

        ugdict = {}
        ugs = [composite[ugvar] for composite in sample]
        lens = [composite.to_ - composite.from_ for composite in sample]
        totalLength = sum(lens)

        for ug, length in zip(ugs, lens):
            if ug in ugdict:
                ugdict[ug] += length
            else:
                ugdict[ug] = length
        for ug in ugdict:
            ugdict[ug] /= totalLength
            if ug in validUg and ugdict[ug] >= purity:
                if ug in samplesByUg:
                    samplesByUg[ug].append((sample, ugdict[ug]))
                else:
                    samplesByUg[ug] = [(sample, ugdict[ug])]

    return samplesByUg


def divideSamplesByLength(drillholes, targetMass, diameterVar):
    resultSamples = []

    for drillhole in drillholes:

        composites = drillhole.composites
        composites = [c for c in composites if c[diameterVar] in massByDiameter]

        compsInDh = len(composites)

        for i in range(compsInDh - 1):
            counter = i + 1
            actualSample = [composites[counter - 1]]
            actualMasses = [
                massByDiameter[actualSample[counter - 1][diameterVar]] * (
                    actualSample[counter - 1].to_ - actualSample[counter - 1].from_)]

            while sum(actualMasses) < targetMass and counter < compsInDh \
                    and composites[counter].from_ == actualSample[-1].to_:

                masa = massByDiameter[composites[i][diameterVar]] * (composites[1].to_ - composites[1].from_)
                actualMasses.append(masa)
                actualSample.append(composites[i])
                counter += 1

                if sum(actualMasses) >= targetMass:
                    resultSamples.append(composites[i])
                    actualSample.pop(0)
                    actualMasses.pop(0)

    return resultSamples


def selectCompleteSamples(samples, useVar='uso', typeVar='samptype', use=True, ddh=True):
    completeSampleIndices = []
    for sample in samples:

        if sample[0][useVar] == 1 or not use:
            continue

        to_ = sample[0].to_
        for i in range(1, len(sample)):

            if sample[i][useVar] == 1 or not use:
                continue
            if sample[i][typeVar] != 'DDH' or not ddh:
                continue
            if sample[i].from_ != to_:
                break
            to_ = sample[i].to_
        else:
            completeSampleIndices.append(samples.index(sample))

    completeSamples = []
    for index in completeSampleIndices:
        completeSamples.append(samples[index])

    return completeSamples
