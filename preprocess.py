import math


# Rellena con el valor de la variable del compósito más cercano cuando no exista
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


# Flagea desde el modelo de bloque las variables seleccionadas en los compósitos
def flagCompositesWithBlocks(blockModel, composites, compPath, outPath, numVarToFlag=None, catVarToFlag=None):

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
    header += '\n'
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
            if numVarToFlag is not None:
                for i in range(len(numVarToFlag)):
                    line += ',-99'
            if catVarToFlag is not None:
                for i in range(len(catVarToFlag)):
                    line += ',-99'

        line += '\n'
        outfile.write(line)
        outfile.flush()

    outfile.close()
    infile.close()


# Flagea desde una base de datos de sondaje las variables seleccionadas en los compósitos
def flagCompositesWithDrillholes(drillholes, composites, compPath, outPath, numVarToFlag=None, catVarToFlag=None):

    dhid = dict([(drillhole.holeid, drillhole) for drillhole in drillholes])

    outfile = open(outPath, 'w')
    infile = open(compPath, 'r')
    header = infile.readline().replace('\n', '')

    if catVarToFlag is not None:
        for catVar in catVarToFlag:
            header += ',' + catVar
    if numVarToFlag is not None:
        for numVar in numVarToFlag:
            header += ',' + numVar
    header += '\n'
    outfile.write(header)

    for c in composites:

        line = infile.readline().replace('\n', '')
        dh = dhid[c.holeid]

        if numVarToFlag is not None:
            for numVar in numVarToFlag:
                line += ',' + str(dh[numVar])
        if catVarToFlag is not None:
            for catVar in catVarToFlag:
                line += ',' + str(dh[catVar])

        line += '\n'
        outfile.write(line)
        outfile.flush()

    outfile.close()
    infile.close()


# flagea la cruza entre el modelo de bloques y las muestras
def flagCross(blockModel, composites, compPath, outPath, newVars, crossVars):

    lenx, leny, lenz = 20, 20, 15
    for block in blockModel:
        xcenter = block.x - lenx / 2
        ycenter = block.y - leny / 2
        zcenter = block.z - lenz / 2
        resx = xcenter % lenx
        resy = ycenter % leny
        resz = zcenter % lenz
        break

    # blocksByCoord = {}
    # for block in blockModel:
    #     disx = math.floor((block.x - resx) / lenx) * lenx + resx
    #     disy = math.floor((block.y - resy) / leny) * leny + resy
    #     disz = math.floor((block.z - resz) / lenz) * lenz + resz
    #     blocksByCoord[(disx, disy, disz)] = block

    blocksByCrossVar = {}
    for crossVar in crossVars:
        daux1 = {}
        daux2 = {}
        for block in blockModel.applyFilter('"' + crossVar + '" in [1, 2]'):
            disx = math.floor((block.x - resx) / lenx) * lenx + resx
            disy = math.floor((block.y - resy) / leny) * leny + resy
            disz = math.floor((block.z - resz) / lenz) * lenz + resz
            if block[crossVar] == 1:
                daux1[(disx, disy, disz)] = block
            else:
                daux2[(disx, disy, disz)] = block
        blocksByCrossVar[crossVar] = [daux1, daux2]

    # se abren los archivos de lectura y escritura y se escribe el header
    outfile = open(outPath, 'w')
    infile = open(compPath, 'r')
    header = infile.readline().replace('\n', '')
    for newVar in newVars:
        header += ',' + newVar
    header += '\n'
    outfile.write(header)

    for c in composites:
        line = infile.readline().replace('\n', '')

        x, y, z = c.middlex, c.middley, c.middlez
        disx = math.floor((x - resx) / lenx) * lenx + resx
        disy = math.floor((y - resy) / leny) * leny + resy
        disz = math.floor((z - resz) / lenz) * lenz + resz

        for crossVar in crossVars:
            if (disx, disy, disz) in blocksByCrossVar[crossVar][0]:
                cross = '1'
            elif (disx, disy, disz) in blocksByCrossVar[crossVar][1]:
                cross = '2'
            else:
                cross = '0'

            line += ',' + cross

        line += '\n'
        outfile.write(line)
        outfile.flush()

    outfile.close()
    infile.close()
