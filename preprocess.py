import math


def setDrilholeType(drillholes, typeVar, diameterVar):

    indexdrill = drillholes.drillholes[0].composites[0].composites.positions[diameterVar]
    indexsamp = drillholes.drillholes[0].composites[0].composites.positions[typeVar]

    for drillhole in drillholes:

        composites = drillhole.composites

        auxcompositesdrill = []
        codedrill = ''
        for composite in composites:

            auxcodedrill = composite[typeVar]

            if auxcodedrill == '':
                if codedrill == '':
                    auxcompositesdrill.append(composite)
                else:
                    composite.values[indexdrill] = codedrill
            else:
                codedrill = auxcodedrill
                for comp in auxcompositesdrill:
                    comp.values[indexdrill] = codedrill
                auxcompositesdrill = []

        auxcompositessamp = []
        codesamp = ''
        for composite in composites:

            auxcodesamp = composite[diameterVar]

            if auxcodesamp == '':
                if codesamp == '':
                    auxcompositessamp.append(composite)
                else:
                    composite.values[indexsamp] = codesamp
            else:
                codesamp = auxcodesamp
                for comp in auxcompositessamp:
                    comp.values[indexsamp] = codesamp
                auxcompositessamp = []


def flagComposites(blockModel, composites, compPath, outPath, numVarToFlag=None, catVarToFlag=None):

    lenx, leny, lenz = 20, 20, 15
    for block in blockModel:
        xcenter = block.x - lenx / 2
        ycenter = block.y - leny / 2
        zcenter = block.z - lenz / 2
        resx = xcenter % lenx
        resy = ycenter % leny
        resz = zcenter % lenz
        break

    blocksByCoord = {}
    for block in blockModel:
        disx = math.floor((block.x - resx) / lenx) * lenx + resx
        disy = math.floor((block.y - resy) / leny) * leny + resy
        disz = math.floor((block.z - resz) / lenz) * lenz + resz

        blocksByCoord[(disx, disy, disz)] = block

    outfile = open(outPath, 'w')
    infile = open(compPath, 'r')
    header = infile.readline().replace('\n', '')

    if catVarToFlag is not None:
        for catVar in catVarToFlag:
            header += ',' + catVar
    if numVarToFlag is not None:
        for numVar in numVarToFlag:
            header += ',' + numVar
    outfile.write(header)

    for c in composites:

        line = infile.readline().replace('\n', '')
        block = None

        x, y, z = c.middlex, c.middley, c.middlez
        disx = math.floor((x - resx) / lenx) * lenx + resx
        disy = math.floor((y - resy) / leny) * leny + resy
        disz = math.floor((z - resz) / lenz) * lenz + resz
        if (disx, disy, disz) in blocksByCoord:

            block = blocksByCoord[(disx, disy, disz)]

            if numVarToFlag is not None:
                for numVar in numVarToFlag:
                    line += ',' + str(block[numVar])
            if catVarToFlag is not None:
                for catVar in catVarToFlag:
                    line += ',' + str(block[catVar])

        if block is None:
            for i in range(len(numVarToFlag + catVarToFlag)):
                line += ','

        line += '\n'
        outfile.write(line)
        outfile.flush()

    outfile.close()
    infile.close()
