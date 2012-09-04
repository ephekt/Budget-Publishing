import numpy
import csv

#page size in inches, discounting margins
effectivepagesize = 5.5

class SpecialColumn:
    title = ''
    sum = False
    columns = None
    diff = 0 
    against = 0

class TableData:
    component = None
    table = None
    rowtitle = True
    coltitle = True
    rowdec = 0
    coldec = 0
    rowtitlecol = 0
    numspeccols = 0
    defaultrowmacro = ""
    defaultitemmacro = ""
    sumtable = False
    colsums = None
    #title is a misnomer. It's really what goes into the top left of the table
    title = ""
    colnums = None
    speccols = None
    subtables = None

def initializetabledata(component):
    tinfo = TableData()
    tinfo.component = component
    ##########THESE LINES MAY NEED TO CHANGE FOR MORE GENERALITY
    src = (component['src'])
    tinfo.table = list(csv.reader(open(src, 'rb'), delimiter=',', quotechar='|'))
    ############
    tinfo.rowtitle = not 'rowtitle' in component or component['rowtitle'] != 'false'
    tinfo.coltitle = not 'coltitle' in component or component['coltitle'] != 'false'
    tinfo.rowdec = 0 if tinfo.coltitle else 1
    tinfo.coldec = 0 if tinfo.rowtitle else 1
    tinfo.numspeccols = 0 if not 'speccols' in component else len(component['speccols'])
    #this is a really dumb field
    tinfo.rowtitlecol = 1-tinfo.rowdec

    tinfo.colnums = numpy.arange(1, len(tinfo.table[0])+tinfo.coldec, 1) if not 'columns' in component else component['columns']

    tinfo.sumtable = 'sum' in component and component['sum'] == 'true'

    if tinfo.sumtable:
        tinfo.colsums = [0]*(len(tinfo.colnums)+tinfo.numspeccols)

    tinfo.title = '' if not 'title' in component else component['title']
    
    tinfo.defaultrowmacro = "defaultrowstyle" if not 'defaultrowmacro' in component else component['defaultrowmacro']
    tinfo.defaultitemmacro = "defaultitemstyle" if not 'defaultitemmacro' in component else component['defaultitemmacro'] 

    return tinfo


def setuptable(info, outputfile):
    outputfile.write('\\begin{longtable}{') 
    if 'columnlayout' in info.component:
        outputfile.write(info.component['columnlayout'])
    else: #default
        extracols = info.rowtitlecol+info.numspeccols
        i = 0
        while i < extracols:
            outputfile.write(' p {' + str(1.0*effectivepagesize/(len(info.colnums)+extracols)) + 'in} ')
            i = i + 1
        for j in info.colnums:
            outputfile.write(' p {' + str(1.0*effectivepagesize/(len(info.colnums)+extracols)) + 'in} ')
        outputfile.write('}\n')

#speccol initiliazation 
def initspeccols(info):
    speccols = [None]*len(info.colnums)
    if 'speccols' in info.component:
        for speccol in info.component['speccols']:
            #by default we assume special columns go at the end
            #TODO: Make each of these lists so that we can have multiple in one position
            index = len(info.colnums)-1
            if 'after' in speccol:
                index = speccol['after']-1
            speccols[index] = SpecialColumn()
            speccols[index].title = speccol['title']
            if speccol['type'] == 'sum':
                speccols[index].sum = True
                # an empty list is assumed to be all columns
                if 'columns' in speccol:
                    speccols[index].columns = speccol['columns']
            else:
                speccols[index].diff = speccol['diff']
                speccols[index].against = speccol['against'] 
    return speccols

#from here on out styling matters  

def placecoltitles(info, outputfile):
    titlerowmacro = "defaultcoltitlerowstyle" if not 'coltitlerowmacro' in info.component else info.component['titlerowmacro']
    outputfile.write('\\' + titlerowmacro + '{\n')
    if info.rowtitle and info.coltitle:
        outputfile.write(info.title)

    itemstyle = "defaultcoltitleitemstyle" if not 'coltitleitemmacro' in info.component else info.component['coltitleitemmacro']
    count = 0
    for colindex in info.colnums:
        colindex = colindex - info.coldec
        if count != 0 or info.rowtitle:
            outputfile.write('&')

        outputfile.write('\\' + itemstyle + '{' + info.table[0][colindex] + '}')
        if info.speccols[count] != None:
            outputfile.write('&' + info.speccols[count].title)
        count = count+1
    #title only shows up if there's a coltitle in this iteration, so we don't need to (and shouldn't) check title, for now
        # } close title row macro
    outputfile.write('}\\\\\n')


def processspeccol(info, speccol, itemmacro, rowindex, outputfile): 
    outputfile.write('&')
    if speccol.sum:
        total = 0.0
        colstosum = numpy.arange(1, len(info.colnums)+1, 1) if speccol.columns == None else speccol.columns
        for colindex in colstosum:
            total = total + float(info.table[rowindex][localtoglobalcol(info, colindex)])
        outputfile.write('\\' + itemmacro + '{' + str(total) + '}')
        return total
    else:
        diff = info.table[rowindex][localtoglobalcol(info, speccol.diff)]
        against = info.table[rowindex][localtoglobalcol(info, speccol.against)]
        difference = float(diff)-float(against)
        outputfile.write('\\' + itemmacro + '{' + str(difference) + '}')      
        return difference

def localtoglobalcol(info, colindex):
    return info.colnums[colindex-1]-info.coldec

#This function is a little too monstrous
def processsubtable(info, subtable, outputfile):
    rownums = numpy.arange(1, len(info.table)+info.rowdec, 1) if not 'rows' in subtable else subtable['rows']
#This segment is all about macros        
    
    #this is somewhat inconsistent
    defaultrowmacro = info.defaultrowmacro if not 'defaultrowmacro' in subtable else subtable['defaultrowmacro']
    defaultitemmacro = info.defaultitemmacro if not 'defaultitemmacro' in subtable else subtable['defaultitemmacro']

    #will this just use tons of memory? I could optimize this if neccessary
    rowmacros = [defaultrowmacro]*len(rownums)
    itemmacros = [defaultitemmacro]*len(rownums)
    if 'rowmacros' in subtable:
        for macro in subtable['rowmacros']:
            rowmacros[macro['row']-1] = defaultrowmacro if not 'rowvalue' in macro else macro['rowvalue']
            itemmacros[macro['row']-1] = defaultitemmacro if not 'itemvalue' in macro else macro['itemvalue']
     
        #TODO: Macro whole subtable? I don't know how I feel about that
    if 'title' in subtable and subtable['title'] != "":
        titlestyling = "defaultsubtabletitlestyle" if not 'titlestyling' in subtable else subtable['titlestyling']
        outputfile.write('\\' + titlestyling + '{' + subtable['title'] + "}\\\\\n")
    rowtitlestyle = "defaultrowtitlestyle" if not 'rowtitlestyle' in info.component else info.component['rowtitlestyle']
    sumsubtable = 'sum' in subtable and subtable['sum'] == 'true'
    if sumsubtable or info.sumtable:
        colsums = [0]*(len(info.colnums)+info.numspeccols)

    for rowcount, rowindex in enumerate(rownums):
        rowindex = rowindex-info.rowdec
        count = 0
        auxcount = 0
        outputfile.write('\\' + rowmacros[rowcount] + '{\n')
        #row titles often have unique stylings. This needs to be incorporated. Probably first specific to a given row, then specific to row headers, than specific to the row
        if info.rowtitle:
            #TODO: default. Possibly customization options?
            outputfile.write('\\' + rowtitlestyle + '{' + info.table[rowindex][0] + '}')                       
        for colindex in info.colnums:
            colindex = colindex - info.coldec
            if count != 0 or info.rowtitle: 
                outputfile.write('&')
            #item macros should probably apply to the headers as well. However, 
            #one may want alternate styling for the header. I'll decide how to deal
            # with this later
            outputfile.write('\\' + itemmacros[rowcount] +'{' + info.table[rowindex][colindex] + '}')
            if sumsubtable or info.sumtable:
                colsums[count + auxcount] = colsums[count + auxcount] + float(info.table[rowindex][colindex])

            #Special column handling
                #TODO potentially make these lists
            if info.speccols[count] != None:
                auxcount = auxcount + 1
                speccolresult = processspeccol(info, info.speccols[count], itemmacros[rowcount], rowindex, outputfile)
                if sumsubtable or info.sumtable:
                    colsums[count + auxcount] = colsums[count + auxcount] + speccolresult  
            count = count+1

        outputfile.write('}\\\\\n')

    if info.sumtable:
        for i, colsum in enumerate(colsums):
            info.colsums[i] = info.colsums[i] + colsum

    if sumsubtable:
        processsumrow(subtable, info.rowtitle, colsums, outputfile, 'sub')

#Needs better modularity. Also, Summary rows generally have different styling than other rows, for obvious reasons
#I don't know how I'll deal with this
def processsumrow(component, rowtitle, colsums, outputfile, level):
    rowstyle = "default" + level + "sumrowstyle" if not 'sumrowstyle' in component else component['sumrowstyle']
    outputfile.write('\\' + rowstyle + '{\n')
    itemstyle = "default" + level + "sumitemstyle" if not 'sumitemstyle' in component else component['sumitemstyle']

    if rowtitle and 'sumtitle' in component:
        titlestyle = "default" + level + "sumtitlestyle" if not 'sumtitlestyle' in component else component['sumtitlestyle']
        outputfile.write('\\' + titlestyle + '{' + component['sumtitle'] + '}')
    count = 0

    for colindex in colsums:
        if count == 0 or rowtitle:
            outputfile.write('&')
        outputfile.write('\\' + itemstyle + '{' + str(colindex) + '}')
    outputfile.write('}\\\\\n')
