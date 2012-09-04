import argparse
import time
import os
import sys
import json
import csv
import array
import numpy
import string
import delptable

'''
Iteratively examines the components of the report and publishes their contents
'''
def publish(report, outputfile):
    for part in report['parts']:
       parsepart(part, outputfile)

''' 
Parses out the subcontent within a given part of the report, and also titles the
section. One thing to note is that a given part can have both sections and content.
When this occurs, the content is a preface to the content, and has no section header
'''
def parsepart(part, outputfile):
    if 'className' in part:
        writeclass(part, outputfile)
        return
    titleMacro = "" if not 'titleMacro' in part else '\\' + part['titleMacro'] + '{'
    close = "" if not 'titleMacro' in part else '}'
    outputfile.write('\\part{' + titleMacro + part['title'] + close + '}\n')
    if 'content' in part:
        parse(part['content'], outputfile)
    if 'sections' in part:
        for section in part['sections']:
            parsesection(section, outputfile, '')         

'''
Very similar to parse part, with the exception of the 'level' argument, which specifies
what heirarchical level the section is (in terms of number of 'subs'. By default only 
up to subsubsection is defined, but in the header file lower levels can be defined
'''
def parsesection(section, outputfile, level):
    if 'className' in section:
        writeclass(section, outputfile)
        return
    if 'title' in section:
        titleMacro = "" if not 'titleMacro' in section else '\\' + section['titleMacro'] + '{'
        close = "" if not 'titleMacro' in section else '}'
        outputfile.write('\\' + level + 'section{' + titleMacro + section['title'] + close + '}\n')
    else:
        outputfile.write('\\' + level + 'section*{}\n')
            #used for preheading and such
    if 'content' in section:
        parse(section['content'], outputfile)
    if level + 'subsections' in section:
        for subsection in section[level + 'subsections']:
            parsesection(subsection, outputfile, 'sub' + level)

'''
Parses the content section of given part/section, and proceeds to specially handle
the various content types. Essentially a glorified switch statement
'''
def parse(content, outputfile):
    for component in content:
        if 'macro' in component:
            outputfile.write('{\\' + component['macro'] + '{\n')
        if component['type'] == 'text':
            writetext(component, outputfile)
        elif component['type'] == 'list':
            writelist(component, outputfile)
        elif component['type'] == 'img':
            writeimg(component, outputfile)
        elif component['type'] == 'table':
            delptable.writeTable(component, outputfile)
        elif component['type'] == 'class':
            writeclass(component, outputfile)
        elif component['type'] == 'function':
            writefunction(component, outputfile)
        if 'macro' in component:
            outputfile.write('}}\n')

def writetext(component, outputfile):
    outputfile.write(component['value'] + '\n')


def writelist(component, outputfile):
    outputfile.write('\\begin{itemize}\n')
    # enables the user to choose a specific type of bulleting
    # for the list
    if 'listType' in component:
        outputfile.write('\\' + component['listType'] + '\n')
    
    # Value here should be a list, which makes sense given the type
    for point in component['value']:
        outputfile.write('\\item ' + point + '\n')
    outputfile.write('\\end{itemize}\n')
    

# This function is probably pretty underdeveloped right now.
# I don't really know what features people want for these. One
# probably useful feature is a * which spreads the picture across
# the entire page
def writeimg(component, outputfile):
    outputfile.write('{\includeimg')
    flag = False;
    if 'height' in component:
        outputfile.write('[height=' + component['height'])
        flag = True
    if 'width' in component:
        if not flag:
            outputfile.write('[')
        else:
            outputfile.write(', ')
        outputfile.write('width=' + component['width'])
        flag = True
    if flag:
        outputfile.write(']')
    outputfile.write('{' + component['value'] + '}');
    
    outputfile.write('}\n')

'''
 Classes aren't content types, per se, but rather predefined collections
 of content types defined in the json. These can replace sections or 
 individual components, and take classValues which specify the dynamic
 parts of the class
'''
def writeclass(component, outputfile):
    classlist = (report['classes'])
    index = 0
    for i, classdef in enumerate(classlist):
        if classdef['name'] == component['className']:
            index = i
            break
    classdef = classlist[index]
    if 'amount' in component:
        i = 0
        while i < int(component['amount']):
            if 'classValues' in component:
                parseclass(classdef, component['classValues'][i])
            else:
                parseclass(classdef, None)
            i += 1
    else: 
        if 'classValues' in component:
            parseclass(classdef, component['classValues'])
        else:
            parseclass(classdef, None)

def parseclass(classdef, classValues):
    classinst = None
    if classValues != None:
        classinst = classreplace(classdef, classValues)
    else:
        classinst = classdef
    level = classinst['level']
    if level == "part":
        parsepart(classinst['definition'], outputfile)
    if level == "section":
        parsesection(classinst['definition'], outputfile, '')
    if level == "subsection":
        parsesection(classinst['definition'], outputfile, 'sub')
    if level == "subsubsection":
        parsesection(classinst['definition'], outputfile, 'subsub')
    if level == "content":
        parse(classinst['definition'], outputfile)


'''
Replaces all instances of *classValue*[x] with the appropriate given 
classvalue
'''
def classreplace(classdef, classValues):
    componentstr = json.dumps(classdef)
    for i, cvalue in enumerate(classValues):
        #THIS IS A HARDCORE HACK, AND IT ISN'T THE RIGHT THING TO DO, SO
        #FIX IT WHEN ABLE. This hack addresses the problem of replacing a
        #classvalue marker with a list, as "value":*classValue*[x] is not
        #valid json
        if isinstance(cvalue, list):
            cvalue = json.dumps(cvalue)
            replacestring = '"*classValue*[' + str(i) + ']"'
        else:    
            replacestring = '*classValue*[' + str(i) + ']'
        componentstr = string.replace(componentstr, replacestring, str(cvalue))
    return json.loads(componentstr)

#this is the ioctl of this project. Basically you can just write arbitrary TeX
def writefunction(component, outputfile):
    outputfile.write("\\" + component['value'])
    if 'optargs' in component:
        for optarg in component['optargs']:
            outputfile.write('[' + optarg + ']') 
    if 'args' in component:
        for arg in component['args']:
            outputfile.write('{' + arg + '}')



f = open(sys.argv[1], 'r')
outputfilename = "temp.tex"
outputfile = open(outputfilename, 'w')
outputfile.write('''
\\nonstopmode
\\input{documentheader.tex}
\\usepackage{graphicx}
\\usepackage[space]{grffile}
\\usepackage{adjustbox}
\\newcommand*{\\includeimg}[2][]{%
    \\begin{adjustbox}{max size={\\textwidth}{\\textheight}}
        \\includegraphics[#1]{#2}%
    \\end{adjustbox}
}
\\begin{document}
''')

reportdoc = json.load(f)
report = reportdoc['report']
publish(report, outputfile)

outputfile.write('\end{document}')
outputfile.close()

os.system("xelatex -halt-on-error " + outputfilename)
os.system("xelatex -halt-on-error " + outputfilename)
os.system("evince " + string.replace(outputfilename, '.tex', '.pdf') + " &")


def strcasecmp(str1, str2):
    return str1.lower() == str2.lower()
