
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
