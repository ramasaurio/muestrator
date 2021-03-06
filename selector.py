from drillhole.controller.composites import Composites


def run():
    # -- Ejercicio 2 -- #
    # archivos
    folder = 'ejercicio_3/'
    compositePath = 'potential_samples_10kg_13y.csv'
    outpath = 'seleccion_ejercicio_3.csv'

    # Variables
    holeid = 'holeid'
    midx, midy, midz = 'midx', 'midy', 'midz'
    from_, to_ = 'from', 'to'
    numericVars = ['cut', 'clay', 'co3']
    groupVars = ['clay', 'co3']
    categVars = ['mine2', 'alte', 'lito', 'fase', 'Estado_Sondaje', 'Campana', 'banco', 'fyear',
                 'cross_f18', 'cross_f19', 'diametro', 'tipo', 'STARTDATE']

    # Filtros
    f1 = '0.6 <= "cutprom" <= 1.6'
    f2 = 'int("STARTDATE".replace(\'"\',\'\')[-2:]) in [14, 15, 16]'
    f3 = 'int("cross_f18") + int("cross_f19") > 0'

    filters = f1, f2, f3

    # Prioridades
    p1 = 'cross_f18', ['1', '2', '0']
    p2 = 'cross_f19', ['1', '2', '0']
    p3 = 'Estado_Sondaje', ['Extraible', 'Modelable', 'Entregado', 'Perforado', 'En Perforacion', 'A Perforacion',
                            'Propuesto', 'Perdido']
    # p4 = 'diametro', ['PQ', 'HQ', 'HQ3', 'NQ']
    priorities = p1, p2, p3
    # -- Ejercicio 3 -- #

    categColumns = [(carvar, str) for carvar in categVars]
    numericColumns = []
    for numvar in numericVars:
        numericColumns.append((numvar + 'prom', float))
        numericColumns.append((numvar + 'var', float))
        numericColumns.append((numvar + 'min', float))
        numericColumns.append((numvar + 'max', float))
        if numvar in groupVars:
            categColumns.append((numvar + 'group', str))
    compositesColumns = categColumns + numericColumns

    composites = Composites(path=folder + compositePath, holeid=holeid, middlex=midx, middley=midy, middlez=midz,
                            from_=from_, to_=to_, columns=compositesColumns, readComposites=True)

    selectedSamples = selectSamples(composites, filters, priorities)
    exportSelectedSamples(folder + compositePath, folder + outpath, selectedSamples, (holeid, from_))


def exportSelectedSamples(compositePath, outpath, selectedSamples, idVars):

    infile = open(compositePath, 'r')
    fullHeader = infile.readline()
    header = fullHeader.replace('\n', '').split(',')

    holeid, from_ = idVars

    indHoleid = header.index(holeid)
    indfrom = header.index(from_)

    compsById = {}
    for fullLine in infile:
        line = fullLine.replace('\n', '').split(',')
        compsById[(line[indHoleid], float(line[indfrom]))] = fullLine
    infile.close()

    outfile = open(outpath, 'w')
    outfile.write(fullHeader)
    for comp in selectedSamples:

        line = compsById[(comp.holeid, comp.from_)]
        outfile.write(line)
        outfile.flush()
    outfile.close()


def selectSamples(composites, filters, priorities):

    selectedSamplesByDhid = {}
    selectedSamples = []

    print('Compositos totales:', len(composites))
    for filt in filters:
        composites.composites = composites.applyFilter(filt)
    print('Compositos filtrados:', len(composites))

    keys = []
    for code_i in priorities[0][1]:
        for code_j in priorities[1][1]:
            for code_k in priorities[2][1]:
                # for code_l in priorities[3][1]:
                #     keys.append((code_i, code_j, code_k, code_l))
                keys.append((code_i, code_j, code_k))

    compByPriorities = {}
    for key in keys:
        condition = ''
        for i in range(len(key)):
            condition += '"' + priorities[i][0] + '" == \'' + key[i] + '\' and '
        condition = condition[:-5]
        compByPriorities[key] = composites.applyFilter(condition)

    for key in keys:
        for comp in compByPriorities[key]:
            if comp.holeid in selectedSamplesByDhid:
                traslape = False
                compSameDhid = selectedSamplesByDhid[comp.holeid]
                for cVecino in compSameDhid:
                    if cVecino.from_ < comp.to_ and cVecino.to_ > comp.from_:
                        traslape = True
                if not traslape:
                    selectedSamplesByDhid[comp.holeid].append(comp)
                    selectedSamples.append(comp)
            else:
                selectedSamplesByDhid[comp.holeid] = [comp]
                selectedSamples.append(comp)

    return selectedSamples


if __name__ == '__main__':
    run()

# -- Ejercicio 0 -- #
# # archivos
# folder = 'ejercicio_0/'
# compositePath = 'potential_samples2.csv'
# outpath = 'seleccion2.csv'
#
# # Variables
# holeid = 'holeid'
# midx, midy, midz = 'midx', 'midy', 'midz'
# from_, to_ = 'from', 'to'
# numericVars = ['cut', 'clay', 'co3']
# groupVars = ['clay', 'co3']
# categVars = ['mine2', 'alte', 'lito', 'fase', 'Estado_Sondaje', 'Campana', 'banco', 'fyear', 'periodo_fy17',
#              'cross_q3q4', 'diametro', 'tipo']
#
# # Filtros
# f1 = '0.6 <= "cutprom" <= 1.3'
# filters = f1,
#
# # Prioridades
# p1 = 'cross_q3q4', ['1', '2']
# p2 = 'Estado_Sondaje', ['Extraible', 'Modelable', 'Entregado', 'Perforado', 'En Perforacion', 'A Perforacion',
#                         'Propuesto', 'Perdido']
# p3 = 'diametro', ['PQ', 'HQ', 'HQ3', 'NQ']
#
# priorities = p1, p2, p3
# # -- Ejercicio 0 -- #

# -- Ejercicio 1 -- #
# # archivos
# folder = 'ejercicio_1/'
# compositePath = 'potential_samples_group4.csv'
# outpath = 'seleccion_f1819_dogtest.csv'
# # outpath = 'seleccion_f18_dog.csv'
#
# # Variables
# holeid = 'holeid'
# midx, midy, midz = 'midx', 'midy', 'midz'
# from_, to_ = 'from', 'to'
# numericVars = ['cut', 'clay', 'co3']
# groupVars = ['clay', 'co3']
# categVars = ['mine2', 'alte', 'lito', 'fase', 'Estado_Sondaje', 'Campana', 'banco', 'fyear',
#              'cross_f18', 'cross_f19', 'diametro', 'tipo']
#
# # Filtros
# f1 = '0.6 <= "cutprom" <= 1.3'
# filters = f1,
#
# # Prioridades
# p1 = 'cross_f19', ['1', '2', '0']
# p2 = 'cross_f18', ['1', '2', '0']
# p3 = 'Estado_Sondaje', ['Extraible', 'Modelable', 'Entregado', 'Perforado', 'En Perforacion', 'A Perforacion',
#                         'Propuesto', 'Perdido']
# p4 = 'diametro', ['PQ', 'HQ', 'HQ3', 'NQ']
#
# priorities = p1, p2, p3, p4
# -- Ejercicio 1 -- #

# -- Ejercicio 2 -- #
# # archivos
# folder = 'ejercicio_2/'
# compositePath = 'potential_samples.csv'
# outpath = 'seleccion_ejercicio_2.csv'
#
# # Variables
# holeid = 'holeid'
# midx, midy, midz = 'midx', 'midy', 'midz'
# from_, to_ = 'from', 'to'
# numericVars = ['cut', 'clay', 'co3']
# groupVars = ['clay', 'co3']
# categVars = ['mine2', 'alte', 'lito', 'fase', 'Estado_Sondaje', 'Campana', 'banco', 'fyear', 'periodo_fy17',
#              'cross_q3q4', 'diametro', 'tipo', 'STARTDATE']
#
# # Filtros
# f1 = 'len("STARTDATE") > 2 and int("STARDATE"[-2:]) >= 15'
# filters = f1,
#
# # Prioridades
# p1 = 'cross_q3q4', ['1', '2']
# p2 = 'Estado_Sondaje', ['Extraible', 'Modelable', 'Entregado', 'Perforado', 'En Perforacion', 'A Perforacion',
#                         'Propuesto', 'Perdido']
# p3 = 'diametro', ['PQ', 'HQ', 'HQ3', 'NQ']
#
# priorities = p1, p2, p3
# # -- Ejercicio 2 -- #
