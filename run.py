# -*- coding: utf-8 -*-


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


def selectCompleteSamples(samples):
    completeSampleIndices = []
    for sample in samples:

        to_ = sample[0].to_
        for i in range(1, len(sample)):

            if sample[i].from_ != to_ or sample[i]['samptype'] != 'DDH':
                break
            to_ = sample[i].to_
        else:
            completeSampleIndices.append(samples.index(sample))

    completeSamples = []
    for index in completeSampleIndices:
        completeSamples.append(samples[index])

    return completeSamples
