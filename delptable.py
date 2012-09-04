import numpy
import csv
import re

# TODO: Check inputs. Indeces should be natural numbers, for example. Missing inputs will cause a crash, so those are fine

# Consider not subtracting from input indices and instead make 0 none in lists

# TODO: this should be global to all files in the project, which it isn't right now
# in inches
effectivePageSize = 5.5
tableType = 'longtable'

class TableData:
    component = None
    # rowTitles and colTitles:    These specify whether or not row and column
    # titles appear in the table. They are also used for determining where
    # to start when reading from a cvs table, skipping the first row and
    # column if true 
    
    # title:    title is a misnomer. It's really what goes into the top left of the table
       
    # srcTable:    cvs table used as the src when reading. SubTables and even
    # individual rows can specify seperate cvs files, but the higher level
    # tables will be used as default
       
    # department and fund:    when grabbing data from the Delphi database,
    # department and fund specify the obvious things. SubTables can specify
    # different departments and funds than their parent table (although
    # this is discouraged TODO: decide if should be dissallowed), but in
    # general should only specify additional information (specify a
    # department if only a fund was supplied in the parent table)
       
    # target and dataset:      potentially a row level thing, but these
    # specifies the defaults for the table/subTable. 
    rowTitles = True
    colTitles = True
    defaultRowMacro = "row"
    defaultItemMacro = "tableItem"
    defaultRowTitleMacro = "rowTitle"
    title = ""
    cols = None
    rows = None
    srcTable = None
    datafilter = ''
    department = ''
    fund = ''
    target = '' 
    dataset = ''
    year = ''

# TODO: allow more specification from the column side. For example, allow
# either a row OR column specify whether a table is custom or whatever
# else, and report an error on a conflict
# As of now, columns can specify datafilters and such, but rows take precedence
    # sumCol:       this is a column that is a sum of other columns
    # prodCol:      this is a column that is a product(multiple) of other columns
    # diffCol:      this is a column that is the difference of two other
    #               columns 
    # divCol:      this is a column that is the divsion  of two other
    #               columns 
    #  
    # diff:         If a diff is x-y and a division x/y, this is the column
    #               number of x
    # against:      and this is the column number of y
    # diffType:     This determines how data is represented in diff
    #               columns. For example, numeric or percentage
    #  
    # colSet:       The columns to sum or multiply if this is a
    #               sum/product column 
    #  
    # target:       Specifies which database items this row should fetch
    #               from the database (e.g. revenue_expense, department,
    #               etc.)
    # dataset:      Which dataset in the database to fetch data from (e.g
    #               financial, employees
    # datafilter:   Specifies, within a given returned dataset, which
    #               elements to sum across, e.g. the specific subfund or
    #               division
    # year:         Specifies which year the data should come from. Year
    #               is, effictively, the lowest level datafilter, and is
    #               common enough that it has it's own explicit field
    #  
    # title:        The column title written above the table if 'colTitles'
    #               is true 
    #  
    # colNum:       If the column is reading from a csv table, this is the
    #               specific column in the file it will read from. Starts
    #               from 0, skips the first column if 'rowTitles' is true
    #
    # numType:      This specifies what kind of numbers the elements that 
    #               Into this column are (e.g. monetary, FTE, etc). And
    #               simply add a macro tag matching the passed in string
    #               to be handled in LaTeX. The heuristic is that
    #               non-defaults take precendence over default, that
    #               rows take precendent over columns, and that
    #               percentages take precedent over all. TODO: As of now
    #               sums or multiples of percentages don't neccessarily
    #               inherit their traits. This maybe should be fixed in a
    #               future version
class Column:
    sumCol = False
    prodCol = False
    diffCol = False
    divCol = False
    diff = 0
    against = 0
    colSet = None
    target = '' 
    dataset = ''
    datafilter = ''
    year = ''
    title = ''
    colNum = 0
    numType = 'num'

# This is a lot of different fields, only a few of which get used at any
# given time. One should consider creating sub objects
    # rowData:      The items that go into the columns of a given row   
    #          
    # prodRow:      this is a row that is a product of other rows       
    # sumRow:       this is a row that is a sum of other rows 
    # diffRow:      this is a row that is the different of two other rows 
    # divRow:      this is a row that is the division of two other rows 
    #                
    # diff:         If a diff is x-y and a division x/y, this is the row 
    #               number (local within the given subTable) of x  
    # against:      and this is the row number (local within the given
    #               subTable) of y 
    # diffType:     This determines how data is represented in diff
    #               columns. For example, numeric or percentage
    #                
    # rowset:       The local row numbers to sum/multiply if this is a 
    #               sum/product row
    #                
    # target:       Specifies which database items this row should fetch
    #               from the database (e.g. revenue_expense, department,
    #               etc.)
    # dataset:      Which dataset in the database to fetch data from (e.g
    #               financial, employees
    # datafilter:   Specifies, within a given returned dataset, which
    #               elements to sum across, e.g. the specific subfund or
    #               division. TODO: It may be advantageous to make this a
    #               list in order to support deeper levels of displaying
    #               data
    # year:         Specifies which year the data should come from. Year
    #               is, effictively, the lowest level datafilter, and is
    #               common enough that it has it's own explicit field
    #                
    # title:        The row title written above the table if 'colTitles' is true
    #                
    # custom:       specifies if this row gets its data from a csv or other source file 
    #                
    # rowNum:       If the row is reading from a csv table, this is the specific row 
    #               in the file it will read from. Starts from 0, skips the first row if 
    #               'rowTitles' is true  
    #  
    # srcTable:     The cvs srcTable of a given custom row
    #
    # numType:      This specifies what kind of numbers the elements that 
    #               Into this row are (e.g. monetary, FTE, etc). And
    #               simply add a macro tag matching the passed in string
    #               to be handled in LaTeX. The heuristic is that
    #               non-defaults take precendence over default, that
    #               rows take precendent over columns, and that
    #               percentages take precedent over all. TODO: As of now
    #               sums or multiples of percentages don't neccessarily
    #               inherit their traits. This maybe should be fixed in a
    #               future version
class Row:
    rowTitleMacro = ""
    rowMacro = ""
    itemMacro = ""
    rowData = None
    sumRow  = False
    prodRow = False
    diffRow = False
    divRow = False
    diff = 0
    against = 0
    diffType = 'numeric'
    rowset = None
    target = '' 
    dataset = ''
    datafilter = ''
    year = ''
    title = ''
    custom = False
    rowNum = 0
    srcTable = None
    numType = 'num'

# Nothing really happens in this function. It just pieces together the 
# helpers that build the table
def writeTable(component, outputfile):
    tinfo = initTable(component)
    setupTable(tinfo, outputfile)
    placeColTitles(tinfo, outputfile)
    for rowcount, row in enumerate(tinfo.rows):
        constructRow(tinfo, row, rowcount)
    writeRows(tinfo, outputfile)
    outputfile.write('\\end{' + tableType + '}\n')

# Once the content of all rows in the table have been generated, this goes
# through and writes the contents of the rows, as well as recursively
# writing the contents of subTables
def writeRows(info, outputfile):
    
    for row in info.rows:

        # if it's a regular row, and not a subTable, we simply print the contents
        if isinstance(row, Row):
            outputfile.write('\\' + row.rowMacro + '{\n')
            if info.rowTitles:
                outputfile.write('\\' + row.rowTitleMacro + '{' + row.title + '}')
            for colcount, col in enumerate(info.cols):
                # We don't want to put an amprisand before the first element in a given row,
                # although this isn't a problem if we have rowTitles
                if colcount != 0 or info.rowTitles:
                    outputfile.write('&')
                #T ODO formatting of data (numbers, etc)
                outputfile.write('\\' + row.itemMacro + '{' + tostring(row.rowData[colcount], row, col) + '}')
            outputfile.write('}\\\\\n')

        
        elif isinstance(row, TableData):
            # We rename row to subTable to signify our original speculation
            # that it was a regular row is false
            subTable = row
            if subTable.title != '':
                # title macros can incorporate both row and item macros, since there is only one element
                titlestyling = "subTableTitle" if not 'titleMacro' in subTable.component else subTable.component['titleMacro']
                outputfile.write('\\' + titlestyling + '{' + subTable.title + "}\\\\\n")
            writeRows(subTable, outputfile)
        
        # Things should be of either class Row or TableData. If it's
        # neither, somewhere along the way something wasn't initialized,
        # and the code is broken
        else:
            exit('Fatal Error, rowtype not valid')
       
# Initializes all the elements in the top level table. Pretty straight 
# forward. Mostly just reads from the component
def initTable(component):
    tinfo = TableData()
    tinfo.component = component
    tinfo.root = "" if not 'root' in component else component['root']
    tinfo.rowTitles = not 'rowTitles' in component or strcasecmp(component['rowTitles'], 'false')
    tinfo.colTitles = not 'colTitles' in component or strcasecmp(component['colTitles'], 'false')
    tinfo.title = '' if not 'title' in component else component['title']
    if 'defaultRowMacro' in component: tinfo.defaultRowMacro = component['defaultRowMacro']
    if 'defaultItemMacro' in component: tinfo.defaultItemMacro = component['defaultItemMacro'] 
    if 'defaultrowTitleMacro' in component: tinfo.defaultRowTitleMacro = component['defaultRowTitleMacro'] 
    
    if 'src' in component:
        tinfo.srcTable = list(csv.reader(open(component['src'], 'rb'), delimiter=',', quotechar='|'))

    tinfo.cols = initCols(tinfo, component)
    tableRowInit(tinfo, component, '')

    return tinfo

# Similar initialization as for the top level table, except with a few
# minor tweaks. Notably, columns no longer need to be handled as columns
# are global to the entire table. Additionally, many attributes can be
# inherited form a parent table
def initSubTable(info, component):
    stinfo = TableData()
    stinfo.component = component
    stinfo.root = "" if not 'subroot' in component else component['subroot']
    stinfo.rowTitles = info.rowTitles
    # This is pretty stupid. Entirely for determining how custom tables
    # read from a csv. I don't really know what to do about this. 
    if not 'skipFirstRow' in component:
        stinfo.colTitles = info.rowTitles 
    elif strcasecmp(component['skipFirstRow'], 'false'):
        stinfo.colTitles = False

    stinfo.title = '' if not 'title' in component else component['title']
    stinfo.defaultRowMacro = info.defaultRowMacro if not 'defaultRowMacro' in component else component['defaultRowMacro']
    stinfo.defaultItemMacro = info.defaultItemMacro if not 'defaultItemMacro' in component else component['defaultItemMacro'] 
    stinfo.defaultRowTitleMacro = info.defaultRowTitleMacro if not 'defaultRowTitleMacro' in component else component['defaultRowTitleMacro']
    
    stinfo.srcTable = info.srcTable if not 'src' in component else list(csv.reader(open(component['src'], 'rb'), delimiter=',', quotechar='|'))
    
    stinfo.cols = info.cols
    tableRowInit(stinfo, component, 'sub')
    
    return stinfo


# Function for initializing the rows of a given subTable. It's a little
# different than how columns are handled, as rows are left in dict form
# for later processing. This is due to subTables being specified as a row 
def tableRowInit(tinfo, component, level):
    # autorows generates the rows of a subTable based on the database
    # return of a generic query.
    if 'autorows' in component and strcasecmp(component['autorows'],'true'):
        #TODO: SUPPORT FEATURE
        print('Feature not yet supported')

    elif 'src' in component and not 'rows' in component:
        rows = list()
        for i, row in enumerate(tinfo.srcTable):
            if tinfo.colTitles and i == 0:
                continue
            nrow = dict()
            nrow['type'] = 'custom'
            #This always starts off numbering from 1, as 0 is skipped if
            #colTitles is true
            nrow['rowNum'] = i + (not tinfo.colTitles)
            rows.append(nrow)
        tinfo.rows = rows     
    else: 
        #passing rows in as a dict is inconsistent, but it makes it much easier to deal with subTables. TODO: Find an alternate way of dealing with this
        tinfo.rows = component['rows']

    if 'sumRow' in component and strcasecmp(component['sumRow'],'true'):
        sumRow = dict()
        sumRow['rowMacro'] = uncapitalize((level + 'SumRow')) if not 'sumRowMacro' in component else component['sumRowMacro']
        sumRow['itemMacro'] = uncapitalize((level + 'SumItem')) if not 'sumItemMacro' in component else component['sumItemMacro']
        sumRow['titleMacro'] = uncapitalize((level + 'SumTitle')) if not 'sumTitleMacro' in component else component['sumTitleMacro']
        sumRow['type'] = 'sum'
        sumRow['title'] = (level + "total").capitalize() if not 'sumRowTitle' in component else component['sumRowTitle']
        tinfo.rows.append(sumRow)

# Initializes the columns in a table based on passed in information
# TODO: This function is broken up into several blocks, but maybe make that more explicit
def initCols(info, component):
    columns = None
    sumCol = 'sumCol' in component and strcasecmp(component['sumCol'],'true')

    # autocolumns generates the columns of a table based on the database
    # return of a generic query. autocolumns is a much less useful feature
    # than autorows, and may not be supported.
    if 'autocolumns' in component and strcasecmp(component['autocolumns'],'true'):
        #TODO: SUPPORT FEATURE
        print('Feature not yet supported')

    #it's a cvs/other type of table
    elif not 'columns' in component and 'src' in component:
        columns = [Column() for i in range(len(info.srcTable[0]) + sumCol - info.rowTitles)]
        for count, srccol in enumerate(info.srcTable[0]):
            if info.colTitles:
                if count == 0 and info.rowTitles:
                    continue
                columns[count-info.rowTitles].title = srccol
            columns[count-info.rowTitles].colNum = count
            
    else:
        columns = [Column() for i in range(len(component['columns']) + sumCol)]
        for i, col in enumerate(component['columns']):
            columns[i].colNum = i+1 if not 'colNum' in col else col['colNum']
            assert(columns[i].colNum > 0)
            columns[i].colNum = columns[i].colNum - (not info.rowTitles)

            if 'type' in col:
                coltype = col['type'].lower()
                if coltype == 'sum' or coltype == 'product':
                    #user input from 1 to number of column, this puts things in terms of array indices
                    colSet = sumColAutogen(columns, i) if not 'columns' in col else [x-1 for x in col['columns']]
                    assert(x >= 0 for x in colSet)   
                    columns[i].colSet = colSet

                    if coltype == 'sum':
                        columns[i].sumCol = True
                    #built in default, beware
                        columns[i].title = "Total" if not 'title' in col else col['title']
                    
                    elif coltype == 'product':
                        columns[i].prodCol = True
                        columns[i].title = "Product" if not 'title' in col else col['title']

                #TODO: Should one be able to diff arbitrary numbers of rows? 
                #TODO: Possibly combine diff and sum, and just allow sum to take a sign
                if coltype == 'diff' or coltype == 'divison':
                    columns[i].diff = i-1 if not 'diff' in col else col['diff'] - 1
                    columns[i].against = i-2 if not 'against' in col else col['against'] - 1
                    columns[i].diffType = 'numeric' if not 'diffType' in col else col['diffType']
                    assert(columns[i].diff >= 0)
                    assert(columns[i].against >=0)
                    if coltype == 'diff':
                        columns[i].diffCol = True
                        columns[i].title = "Change" if not 'title' in col else col['title']

                    elif coltype == 'division':
                        columns[i].divCol = True
                        columns[i].title = "Division" if not 'title' in col else col['title']

            elif info.colTitles and 'src' in component:
                columns[i].title = info.srcTable[0][columns[i].colNum] if not 'title' in col else col['title']

            elif 'datafilter' in col:
                #TODO: Support for single column tables
                columns[i].title = col['datafilter'] if not 'title' in col else col['title']
            
            elif 'year' in col:
                columns[i].title = col['year'] if not 'title' in col else col['title']

            columns[i].datafilter = '' if not 'datafilter' in col else col['datafilter']
            columns[i].year = '' if not 'year' in col else col['year']
            columns[i].target = '' if not 'target' in col else col['target']
            columns[i].dataset = '' if not 'dataset' in col else col['dateset']

    if sumCol:
        #-1 accesses the last element in a list
        lastcol = columns[-1]
        lastcol.sumCol = True
        lastcol.colSet = sumColAutogen(columns, len(columns)+1)
        lastcol.title = "Total" if not 'sumColTitle' in component else component['sumColTitle']
        columns[-1] = lastcol

    return columns

# does the semantic latex setup of a table. Components can give a 'columnLayout' 
# to specifically designate formatting, otherwise they can give a width for the 
# row titles, since that's a commonly different column 
def setupTable(info, outputfile):
    outputfile.write('\\begin{' + tableType + '}{') 
    if 'columnLayout' in info.component:
        outputfile.write(info.component['columnLayout'])
    else: #default
        rowTitleWidth = 0 
        if info.rowTitles and not 'rowTitleWidth' in info.component:
            rowTitleWidth = effectivePageSize/(len(info.cols) + 1)
        else:
            rowTitleWidth = info.component['rowTitleWidth']
        outputfile.write(' p {' + str(rowTitleWidth) + 'in} ')

        for j in info.cols:
            outputfile.write(' p {' + str(1.0*(effectivePageSize - rowTitleWidth)/(len(info.cols))) + 'in} ')
        outputfile.write('}\n')

# Places all the column titles for the table. Not too much here that can't
# be found in the code
def placeColTitles(info, outputfile):
    if not info.colTitles:
        return 
    colTitlerowMacro = "colTitleRow" if not 'colTitleRowMacro' in info.component else info.component['colTitleRowMacro']
    outputfile.write('\\' + colTitlerowMacro + '{\n') 
    #We only have the free space in the top left of the table if 
    #there are row titles
    if info.rowTitles:
        titleMacro = "tableTitle" if not 'titleMacro' in info.component else info.component['titleMacro']
        outputfile.write('\\' + titleMacro + '{' + info.title + '}')

    itemstyle = "colTitleItem" if not 'colTitleItemMacro' in info.component else info.component['colTitleItemMacro']
    for count, col in enumerate(info.cols):
        if count != 0 or info.rowTitles:
            outputfile.write('&')

        outputfile.write('\\' + itemstyle + '{' + col.title + '}')
        # } close title row macro
    outputfile.write('}\\\\\n\\endhead\n')


def parseSubTable(info, subTable):
    stinfo = initSubTable(info, subTable)
    for rowcount, row in enumerate(stinfo.rows):
        constructRow(stinfo, row, rowcount)
    return stinfo


def constructRow(info, row, rowcount):
    if isinstance(row, Row) or isinstance(row, TableData):
        return

    if 'subTable' in row:
        subTableinfo = parseSubTable(info, row['subTable'])
        info.rows[rowcount] = subTableinfo
    else: 
        trow = initRow(info, row, rowcount)
        info.rows[rowcount] = trow
            

def initRow(info, row, rowcount):
    trow = Row()
    trow.rowMacro = info.defaultRowMacro if not 'rowMacro' in row else row['rowMacro']
    trow.itemMacro = info.defaultItemMacro if not 'itemMacro' in row else row['itemMacro']
    trow.rowTitleMacro = info.defaultRowTitleMacro if not 'rowTitleMacro' in row else row['rowTitleMacro']

    if 'type' in row:

        if strcasecmp(row['type'],'sum') or strcasecmp(row['type'],'product'):
            #TODO: Seperate macros from products and divisions?
            trow.rowMacro = 'subSubSumRow' if not 'rowMacro' in row else row['rowMacro']
            trow.itemMacro = 'subSubSumItem' if not 'itemMacro' in row else row['itemMacro']
            trow.titleMacro = 'subSubSumTitle' if not 'titleMacro' in row else row['titleMacro']

            if 'rows' in row: 
                #user input from 1 to number of rows, this puts things in terms of array indices
                trow.rowset = [int(x)-1 for x in row['rows']]
            else:
                trow.rowset = sumRowAutogen(info.rows, rowcount)

            if strcasecmp(row['type'],'sum'):
                trow.sumRow = True
                if info.rowTitles:
                    trow.title = "Subtotal" if not 'title' in row else row['title']

            if strcasecmp(row['type'],'product'):
                trow.prodRow = True
                if info.rowTitles:
                    trow.title = "Product" if not 'title' in row else row['title']

        if strcasecmp(row['type'], 'diff') or strcasecmp(row['type'],'division'):
            trow.rowMacro = 'diffRow' if not 'rowMacro' in row else row['rowMacro']
            trow.itemMacro = 'diffItem' if not 'itemMacro' in row else row['itemMacro']
            trow.titleMacro = 'diffTitle' if not 'titleMacro' in row else row['titleMacro']

            trow.diff = rowcount-1 if not 'diff' in row else row['diff'] - 1
            trow.against = rowcount-2 if not 'against' in row else row['against'] - 1
            trow.diffType = 'numeric' if not 'diffType' in row else row['diffType']

            if strcasecmp(row['type'], 'diff'):
                trow.diffRow = True
                if info.rowTitles:
                    trow.title = "Change" if not 'title' in row else row['title']

            if strcasecmp(row['type'], 'division'):
                trow.divRow = True
                if info.rowTitles:
                    trow.title = "Division" if not 'title' in row else row['title']

        if strcasecmp(row['type'], 'custom'):
            trow.custom = True
            trow.rowNum = row['rowNum'] - (not info.colTitles)
            trow.srcTable = info.srcTable if not 'src' in row else list(csv.reader(open(row['src'], 'rb'), delimiter=',', quotechar='|'))
            if info.rowTitles:
                #possibly add colTitles, but probably not
                trow.title = trow.srcTable[trow.rowNum][0]         
            
    elif 'datafilter' in row:
        #TODO: Support for single row tables <- can't remember why I wrote this
        trow.title = row['datafilter'] if not 'title' in row else row['title']

    elif 'year' in row:
        trow.title = row['year'] if not 'title' in row else row['title']

    trow.datafilter = '' if not 'datafilter' in row else row['datafilter']
    trow.year = '' if not 'year' in row else row['year']
    trow.target = '' if not 'target' in row else row['target']
    trow.dataset = '' if not 'dataset' in row else row['dateset']

    produceRowData(info, trow, rowcount)
    trow.processed = True
    return trow


def produceRowData(info, row, rowcount):
    row.rowData = [None]*(len(info.cols))
    for colcount, col in enumerate(info.cols):
        #Skip rows already recursively processed
        if (row.rowData[colcount] != None):
            continue
        row.rowData[colcount] = produceData(info, row, rowcount, col, colcount)


#TODO: Currently the default is for a sum to sum all rows/columns up to that point. Maybe it makes more sense 
# for the default to be all rows/columns up to the last sum. This is also a problem because a rowtotal will also
# sum other sums. 
def produceData(info, row, rowcount, col, colcount):
    assert(rowcount >= 0 and colcount >=0)

    #This is the bad interaction list. Essentially if you have conflicting rows and columns,
    # Nothing happens, and you get a /noInfo
    if col.sumCol and ((row.diffRow and strcasecmp(row.diffType, 'percent')) or row.divRow):
        data = '\\noInfo{}'
    #elif row.sumRow and ((col.diffCol and strcasecmp(col.diffType, 'percent')) or col.divCol):
    #    data = '\\noInfo{}'

    elif col.sumCol or col.prodCol:
        data = 1 if col.prodCol else 0
        for colindex in col.colSet:
            if row.rowData[colindex] == None:
                row.rowData[colindex] = produceData(info, row, rowcount, info.cols[colindex], colindex)
            if col.sumCol: 
                data = data + tofloat(row.rowData[colindex])
            elif col.prodCol:
                data = data * tofloat(row.rowData[colindex])
    
    
    elif col.diffCol or col.divCol:
        try:
            diff = col.diff
            against = col.against
            if row.rowData[diff] == None:
                row.rowData[diff] = produceData(info, row, rowcount, info.cols[diff], diff)
            if row.rowData[against] == None:
                row.rowData[against] = produceData(info, row, rowcount, info.cols[against], against)
            diffvalue = tofloat(row.rowData[diff])
            againstvalue = tofloat(row.rowData[against])

            if col.diffCol:
                if strcasecmp(col.diffType, 'percent'):
                    value = 100.0*((diffvalue/againstvalue)-1)
                    data = '\\percentage{' + str(value) + '}'  
        #default is numeric difference
                else:
                    data = diff-against

            elif col.divCol:
                if strcasecmp(col.diffType, 'percent'):
                    value = 100.0*((diffvalue/againstvalue))
                    data = '\\percentage{' + str(value) + '}'  
        #default is numeric difference
                else:
                    data = diff/against
        except ZeroDivisionError:
            data = '\\noInfo{}'
        
    elif row.sumRow or row.prodRow: 
        coltotal = 1 if row.prodRow else 0
        #Aggregate what are potentially lists of data
        for rowindex in row.rowset:
            if not isinstance(info.rows[rowindex], Row) and not isinstance(info.rows[rowindex], TableData):
                constructRow(info, info.rows[rowindex], rowindex)
            #TODO: get rid of $ and make positive, whatever else
            cell = getCell(info.rows[rowindex], colcount)
            if row.sumRow: coltotal = coltotal + cell
            elif row.prodRow: coltotal = coltotal*cell
        data = coltotal

    elif row.diffRow or row.divRow:
        try:
            diff = row.diff
            against = row.against
            if not isinstance(info.rows[diff], Row) and not isinstance(info.rows[diff], TableData):
                constructRow(info, info.rows[diff], diff)
            if not isinstance(info.rows[against], Row) and not isinstance(info.rows[against], TableData):
                constructRow(info, info.rows[against], against)

            diffvalue = getCell(info.rows[diff], colcount)
            againstvalue = getCell(info.rows[against], colcount)

            if row.diffRow:
                if strcasecmp(row.diffType, 'percent'):
                   value = 100*((diffvalue/againstvalue)-1)
                   data = '\\percentage{' + str(value) + '}'  

            #default is numeric difference
                else:
                    data = diff-against

            elif row.divRow:
                if strcasecmp(row.diffType, 'percent'):
                    value = 100.0*((diffvalue/againstvalue))
                    data = '\\percentage{' + str(value) + '}'  
            #default is numeric difference
                else:
                    data = diff/against
        except ZeroDivisionError:
            return '\\noInfo{}'

    elif row.custom:
        data = row.srcTable[row.rowNum][col.colNum]

    else:
        data = '\\noInfo{}' 
    '''
    else: 
        fund = info.fund
        department = info.department
        #not, row takes priority over column for these specifiers
        dataset = row.dataset if row.dataset != '' else col.dataset if col.dataset != '' else info.dataset
        target = row.target if row.target != '' else col.target if col.target != '' else info.target
        datafilter = row.datafilter if row.datafilter != '' else col.datafilter if col.datafilter != '' else info.datafilter
        year = row.year if row.year != '' else col.year if col.year != '' else info.year
        #TODO: Make query


        #TODO, support feature
        print('feature unsupported!')
    '''
    return data

def strcasecmp(str1, str2): 
    return str1.lower() == str2.lower()

# This function is used for summing and diffing, and expands subTables into their sums
# getCell is an outer wrapper version which allows for explicit adding of sum and diff
# rows, which one doesn't want to include when recursively entering a subTable. Gcell
# is the exact same function except it does ignore those rows
def getCell(row, colindex):
    if isinstance(row, Row):
        return tofloat(row.rowData[colindex])
    else:
        #purely an optimization. Simply grabs the last row in a summed subTable
        if strcasecmp(row.component['sumRow'], 'true'):
            return tofloat(row.rows[-1].rowData[colindex])
        total = 0
        for subrow in row.rows:
            total = total + gcell(subrow, colindex)
            
def gcell(row, colindex):
    if isinstance(row, Row):
        if row.sumRow or row.diffRow:
            return 0
        else:
            return tofloat(row.rowData[colindex])
    else:
        #purely an optimization. Simply grabs the last row in a summed subTable
        if strcasecmp(row.component['sumRow'], 'true'):
            return tofloat(row.rows[-1].rowData[colindex])
        total = 0
        for subrow in row.rows:
            total = total + getc(subrow, colindex)


# automatically generates the rows to sum for a summing row which has
# no specification for which rows to sum. By default, all rows up to 
# that row, excluding sum and difference rows, are included in the same
def sumRowAutogen(rows, rowcount):
    rowset = []
    for rowindex, row in enumerate(rows):
        if rowindex == rowcount:
            break
        if isinstance(row, Row) and (row.sumRow or row.diffRow):
            continue
        if isinstance(row, dict) and 'type' in row and (strcasecmp(row['type'],'sum') or strcasecmp(row['type'],'diff')):
            continue
        rowset.append(rowindex)
    return rowset

# Same as sumRow autogen except with columns
def sumColAutogen(columns, colcount):
    colSet = []
    for colindex, col in enumerate(columns):
        if colindex == colcount:
            break
        if not col.sumCol and not col.diffCol:
            colSet.append(colindex)
    return colSet
    
# Converts objects to strings. In general this function is specifically 
# for special handling of cases like numbers where things need to be 
# represented in a specific way
# TODO: This probably isn't satisfactory. The way one wants to represent 
# currency will be very different than how one wants to represent FTE
def tostring(o, row, col): 
    if isnum(o):
        if not strcasecmp(row.numType, 'num'):
            #CONSIDER: replace .strip with str(float(o))
            return '\\' + row.numType + '{' + str(o).strip() + '}'
        else:
            return '\\' + col.numType + '{' + str(o).strip() + '}'
    else:
        return str(o)

# Determines if a given string can be represented as a number. 
# This is primarily for data representation purposes
def isnum(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

#Right now this can't deal with () around numbers
#convets a string to a workable number, eliding anything that isn't a -, ., or digit
def tofloat(s):
    try:
        return float(s)
    except ValueError:
        tempstr = re.sub(r'[^\d()+-.]+', '', s)
        if tempstr[0] == '(' and tempstr[-1] == ')':
            tempstr = '-' + tempstr
        try:
            return float(re.sub(r'[^\d+-.]+', '', tempstr))
        except ValueError:
            return 0.0
        #consider just doing: 
        #return float(re.sub(r'[^\d+-.]+', '', s))

def uncapitalize(s):
   if len(s) == 0:
      return s
   else:
      return s[0].lower() + s[1:]
