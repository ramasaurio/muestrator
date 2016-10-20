# -*- coding: utf-8 -*-
import numpy

massByDiameter = {'PQ': 6, 'HQ': 3, 'HQ3': 3, 'NQ': 1.8}


def writeDiameterFile(path, samplesByUg, typeVar, diameterVar, mass,
                      categVars=None, numericVars=None, crossVars=None, groupVars=None):
    outfile = open(path, 'w')

    # Se escribe el encabezado y el prototipo de fila del archivo
    outheader = 'holeid,from,to,length,target_length,masa,midx,midy,midz,ug,pureza'
    lineskel = '%s,%f,%f,%f,%f,%f,%f,%f,%f,%s,%f'
    if numericVars is not None:
        for numvar in numericVars:
            outheader += ',' + numvar + 'prom'
            outheader += ',' + numvar + 'var'
            outheader += ',' + numvar + 'min'
            outheader += ',' + numvar + 'max'
            lineskel += ',%f,%f,%f,%f'
            if groupVars is not None:
                if numvar in groupVars:
                    outheader += ',' + numvar + 'group'
                    lineskel += ',%s'
    if categVars is not None:
        for categ in categVars:
            outheader += ',' + categ + ',ratio'
            lineskel += ',%s,%f'
    if crossVars is not None:
        for crossVar in crossVars:
            outheader += ',' + crossVar
            lineskel += ',%d'
    outheader += ',tipo,ratio,diametro,ratio'
    lineskel += ',%s,%f,%s,%f'

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

            line = [samples[0].holeid, samples[0].from_, samples[-1].to_, samples[-1].to_- samples[0].from_,
                    midx, midy, midz, str(ug), pureza]

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
                        if groupVars is not None:
                            if var in groupVars:
                                for limit, value in groupVars[var]:
                                    if mean < limit:
                                        line.append(value)
                                        break
                                else:
                                    line.append('No Group')
                    else:
                        line.extend([0, 0, 0, 0])
                        if groupVars is not None and var in groupVars:
                            line.append('No Group')

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
            target_length = 0
            total_mass = 0
            for categVar in [typeVar, diameterVar]:
                codes = {}
                catVarInSamp = [composite[categVar] for composite in samples]
                for code, length in zip(catVarInSamp, lengths):
                    if code in codes:
                        codes[code] += length
                    else:
                        codes[code] = length
                    if categVar == diameterVar:
                        if code in massByDiameter:
                            total_mass += massByDiameter[code] * length

                maxCode = ''
                maxValue = 0
                for code in codes:
                    if codes[code] > maxValue:
                        maxCode = code
                        maxValue = codes[code]

                line.append(maxCode)
                if maxCode in massByDiameter:
                    target_length = mass / massByDiameter[maxCode]
                line.append(codes[maxCode] / totalLen)

            line.insert(4, target_length)
            line.insert(5, total_mass)

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
        if compsInDh > 0:
            actualSample = [composites[0]]
            initialMass = massByDiameter[composites[0][diameterVar]] * (composites[0].to_ - composites[0].from_)
            actualMasses = [initialMass]
            ind = 1

            while sum(actualMasses) < targetMass and ind < compsInDh and composites[ind].from_ == actualSample[-1].to_:

                masa = massByDiameter[composites[ind][diameterVar]] * (composites[ind].to_ - composites[ind].from_)
                actualMasses.append(masa)
                actualSample.append(composites[ind])
                ind += 1

                if sum(actualMasses) >= targetMass:
                    resultSamples.append(actualSample)
                    actualSample = actualSample[1:] if len(actualSample) > 1 else []
                    actualMasses = actualMasses[1:] if len(actualSample) > 1 else []

    return resultSamples


def selectCompleteSamples(samples, useVars=None, typeVar='samptype', use=True, ddh=True):
    completeSampleIndices = []

    for sample in samples:

        used = False

        if useVars is not None:
            for useVar in useVars:
                if use and sample[0][useVar] != '':
                    used = True
        if used:
            continue

        to_ = sample[0].to_
        for i in range(1, len(sample)):

            if useVars is not None:
                for useVar in useVars:
                    if use and sample[i][useVar] != '':
                        used = True
            if used:
                break

            if ddh and sample[i][typeVar] != 'DDH':
                break
            if sample[i].from_ != to_:
                break
            to_ = sample[i].to_
        else:
            completeSampleIndices.append(samples.index(sample))

    completeSamples = []
    for index in completeSampleIndices:
        completeSamples.append(samples[index])

    return completeSamples
