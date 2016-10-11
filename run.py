# -*- coding: utf-8 -*-
import numpy


def writeDiameterFile(path, samplesByUg, drillcode, drilltol, ugvar, categVars=None, numericVars=None):

    outfile = open('data/' + path, 'w')

    # Se escribe el encabezado y el prototipo de fila del archivo
    outheader = 'holeid,from,to,midx,midy,midz'
    lineskel = '%s,%f,%f,%f,%f,%f'
    if categVars is not None:
        for categ in categVars:
            outheader += ',' + categ
            lineskel += ',%s'
    if numericVars is not None:
        for numvar in numericVars:
            outheader += ',' + numvar + 'prom'
            outheader += ',' + numvar + 'var'
            outheader += ',' + numvar + 'min'
            outheader += ',' + numvar + 'max'
            lineskel += ',%f,%f,%f,%f'
    outheader += ',tipo,diametro\n'
    lineskel += ',%s,%s\n'
    outfile.write(outheader)

    for ug in samplesByUg:
        for samples, pureza in samplesByUg[ug]:

            drilltype = [composite['drilltype'] for composite in samples]
            lengths = [composite.to_ - composite.from_ for composite in samples]
            code = sum([length for cod, length in zip(drilltype, lengths) if cod == drillcode]) / sum(lengths)
            if code < drilltol:
                continue

            midx = numpy.mean([composite.middlex for composite in samples])
            midy = numpy.mean([composite.middley for composite in samples])
            midz = numpy.mean([composite.middlez for composite in samples])

            line = [samples[0].holeid, samples[0].from_, samples[-1].to_, midx, midy, midz, ug, pureza]

            for sample in samples:
                if sample[ugvar] == ug:
                    line.extend(
                        [int(sample['minty']), int(sample['alte']), int(sample['lito']), sample['dom'], sample['plan']])
                    break

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

            samptype = [composite['samptype'] for composite in samples]
            ddh = len([cod for cod in samptype if cod == 'DDH']) / len(samptype)
            rc = len([cod for cod in samptype if cod == 'RC']) / len(samptype)
            line.extend([ddh, rc])

            # pq = len([cod for cod in drilltype if cod == 'PQ']) / len(drilltype)
            # nq = len([cod for cod in drilltype if cod == 'NQ']) / len(drilltype)
            # hq = len([cod for cod in drilltype if cod == 'HQ']) / len(drilltype)
            # hq3 = len([cod for cod in drilltype if cod == 'HQ3']) / len(drilltype)
            # line.extend([pq, nq, hq, hq3, 1-pq-nq-hq-hq3])

            if drillcode == 'PQ':
                codes = [code, 0, 0, 0]
            elif drillcode == 'HQ':
                codes = [0, code, 0, 0]
            elif drillcode == 'HQ3':
                codes = [0, 0, code, 0]
            else:
                codes = [0, 0, 0, code]
            line.extend(codes)

            outfile.write(lineskel % tuple(line))
            outfile.flush()

    outfile.close()


def divideSamplesByUg(samples, ugvar, purity):
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
            if ugdict[ug] >= purity:
                if ug in samplesByUg:
                    samplesByUg[ug].append((sample, ugdict[ug]))
                else:
                    samplesByUg[ug] = [(sample, ugdict[ug])]

    return samplesByUg


def divideSamplesByLength(drillholes, length, support, tolerance):
    sections = round(length / support + tolerance)
    resultsamples = []

    for drillhole in drillholes:

        composites = drillhole.composites
        n = len(composites)

        if n >= sections:

            for i in range(n - sections + 1):
                auxsamples = composites[i:i + sections]
                samplelength = auxsamples[-1].to_ - auxsamples[0].from_

                if samplelength < length + support * tolerance:

                    if auxsamples[-1].to_ == composites[-1].to_ and samplelength >= length + support * tolerance / 2:
                        resultsamples.append(auxsamples)
                        continue

                    for nexti in range(i + sections, len(composites)):
                        auxsamples.append(composites[nexti])
                        if auxsamples[-1].to_ - auxsamples[0].from_ >= length + support * tolerance:
                            resultsamples.append(auxsamples)
                            break
                    else:
                        continue
                else:
                    resultsamples.append(auxsamples)

    return resultsamples


def selectCompleteSamples(samples, useVar='uso', typeVar='samptype', use=True, ddh=True):
    # Este método se puede saltar si es que te da lo mismo el uso y el tipo (DDH/RC)
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
