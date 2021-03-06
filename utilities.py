# -*- coding: utf-8 -*-
import numpy
from drillhole.controller.drillholes import Drillholes

massByDiameter = {'PQ': 6, 'HQ': 3, 'HQ3': 3, 'NQ': 1.8, 'rechazo': 10}


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

            line = [samples[0].holeid, samples[0].from_, samples[-1].to_, samples[-1].to_ - samples[0].from_,
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
                    totalLength = 0
                    for code, length in zip(catVarInSamp, lengths):
                        if code != '-99':
                            if code in codes:
                                codes[code] += length
                            else:
                                codes[code] = length
                            totalLength += length
                    maxCode = '-99'
                    maxValue = 0
                    for code in codes:
                        if codes[code] > maxValue:
                            maxCode = code
                            maxValue = codes[code]
                    line.append(maxCode)
                    if maxCode != '-99':
                        line.append(codes[maxCode] / totalLength)
                    else:
                        line.append(1)
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
                            if code == 'rechazo':
                                total_mass += massByDiameter['rechazo']
                            else:
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

            actualSample = []
            actualMasses = []
            ind = 0

            while ind < compsInDh:
                code = composites[ind][diameterVar]
                if code == 'rechazo':
                    masa = massByDiameter[code]
                else:
                    masa = massByDiameter[code] * (composites[ind].to_ - composites[ind].from_)
                actualMasses.append(masa)
                actualSample.append(composites[ind])
                ind += 1

                if sum(actualMasses) >= targetMass:
                    resultSamples.append(actualSample)
                    actualSample = actualSample[1:] if len(actualSample) > 1 else []
                    actualMasses = actualMasses[1:] if len(actualMasses) > 1 else []

    samplesToRemove = set()
    for sample in resultSamples:
        if len(sample) > 1:
            for i in range(1, len(sample)):
                if sample[i - 1].to_ != sample[i].from_:
                    samplesToRemove.union(i)
                    break

    resultSamples = [resultSamples[i] for i in range(len(resultSamples)) if i not in samplesToRemove]

            # actualSample = [composites[0]]
            # code = composites[0][diameterVar]
            # if code == 'rechazo':
            #     initialMass = massByDiameter[code]
            # else:
            #     initialMass = massByDiameter[code] * (composites[0].to_ - composites[0].from_)
            # actualMasses = [initialMass]
            # ind = 1
            #
            # while sum(actualMasses) < targetMass and ind < compsInDh and composites[ind].from_ == actualSample[-1].to_:
            #
            #     code = composites[ind][diameterVar]
            #     if code == 'rechazo':
            #         masa = massByDiameter[code]
            #     else:
            #         masa = massByDiameter[code] * (composites[ind].to_ - composites[ind].from_)
            #     actualMasses.append(masa)
            #     actualSample.append(composites[ind])
            #     ind += 1
            #
            #     if sum(actualMasses) >= targetMass:
            #         resultSamples.append(actualSample)
            #         actualSample = actualSample[1:] if len(actualSample) > 1 else []
            #         actualMasses = actualMasses[1:] if len(actualMasses) > 1 else []

    return resultSamples


def selectCompleteSamples(samples, useVars=None, typeVar='samptype', use=True, ddh=True):
    completeSampleIndices = []

    for sample in samples:

        used = False

        if use and useVars is not None:
            for useVar in useVars:
                if sample[0][useVar] != '' and sample[0][useVar] != 'NONE':
                    used = True
        fecha = sample[0]['STARTDATE'].replace('"', '')
        if len(fecha) == 0 or (len(fecha) > 2 and int(fecha[-2:]) < 13):
            used = True

        if used:
            continue

        to_ = sample[0].to_
        for i in range(1, len(sample)):

            if use and useVars is not None:
                for useVar in useVars:
                    if sample[i][useVar] != '' and sample[i][useVar] != 'NONE':
                        used = True

            fecha = sample[i]['STARTDATE'].replace('"', '')
            if len(fecha) == 0 or (len(fecha) > 2 and int(fecha[-2:]) < 13):
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


# EN CONSTRUCCIÓN #
def eliminarTraslape(samples1, samples2):

    drills1 = Drillholes.makeDrillholes(composites=samples1)
    drills2 = Drillholes.makeDrillholes(composites=samples2)

    dhByHoleid1 = dict([(dh.holeid, dh.composites) for dh in drills1])
    dhByHoleid2 = dict([(dh.holeid, dh.composites) for dh in drills2])

    traslape = {}

    if len(dhByHoleid1) < len(dhByHoleid2):
        minDict = dhByHoleid1
        maxDict = dhByHoleid2
    else:
        minDict = dhByHoleid2
        maxDict = dhByHoleid1

    for dhid in minDict:
        if dhid in maxDict:
            for c1 in dhByHoleid1[dhid]:
                for c2 in dhByHoleid2[dhid]:
                    if c1.from_< c2.to_ and c1.to_> c2.from_:
                        if (c1.holeid, c1.from_) in traslape:
                            traslape[(c1.holeid, c1.from_)].append(c2)
                        else:
                            traslape[(c1.holeid, c1.from_)] = [c2]
                        if (c2.holeid, c2.from_) in traslape:
                            traslape[(c2.holeid, c2.from_)].append(c1)
                        else:
                            traslape[(c2.holeid, c2.from_)] = [c1]
