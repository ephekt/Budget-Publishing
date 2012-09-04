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

#page size in inches, discounting margins
effectivepagesize = 5.5

#These two functions probably have no place in the final version
def titlepage(report, outputfile):
    outputfile.write('\\thispagestyle{empty}\n')
    outputfile.write('\\hbox{\XeTeXpicfile ' + report['coverimage'] + '\n}\n')
    outputfile.write('\\newpage\n')


def mainpage(report, outputfile):
    outputfile.write('\\begin{center}\n')
    outputfile.write('{\\large \\textbf{Fiscal Year ' + report['year'] + '\\\\\n\
    ' + report['title'] + '}}\n\n')
    authors = report['authors']
    outputfile.write('\\textbf{City Council}\\\\\n')
    outputfile.write(authors['mayor'] + ', Mayor\\\\\n')
    outputfile.write(authors['vice-mayor'] + ', Vice Mayor\n')
    for councilmen in authors['council']:
        #todo, multiple columns?
        outputfile.write('\\\\' + councilmen + '\n')


    for others in authors['others']:
        outputfile.write('\n{\small ' + others['name'] + '\\\\\n')
        outputfile.write('\\textbf{' + others['title'] + '}}\n')
    outputfile.write('\\end{center}\n\\newpage\n')


# Iteratively examines the components of the report and publishes their contents
def publish(report, outputfile):
    for part in report['parts']:
       parsepart(part, outputfile)

# Parses out the subcontent within a given part of the report, and also titles the
# section. One thing to note is that a given part can have both sections and content.
# When this occurs, the content is a preface to the content, and has no section header
def parsepart(part, outputfile):
    if 'classname' in part:
        writeclass(part, outputfile)
        return
    titlemacro = "" if not 'titlemacro' in part else '\\' + part['titlemacro'] + '{'
    close = "" if not 'titlemacro' in part else '}'
    outputfile.write('\\part{' + titlemacro + part['title'] + close + '}\n')
    if 'content' in part:
        parse(part['content'], outputfile)
    if 'sections' in part:
        for section in part['sections']:
            parsesection(section, outputfile, '')         

# Very similar to parse part, with the exception of the 'level' argument, which specifies
# what heirarchical level the section is (in terms of number of 'subs'. By default only 
# up to subsubsection is defined, but in the header file lower levels can be defined
def parsesection(section, outputfile, level):
    if 'classname' in section:
        writeclass(section, outputfile)
        return
    titlemacro = "" if not 'titlemacro' in section else '\\' + section['titlemacro'] + '{'
    close = "" if not 'titlemacro' in section else '}'
    outputfile.write('\\' + level + 'section{' + titlemacro + section['title'] + close + '}\n')
            #used for preheading and such
    if 'content' in section:
        parse(section['content'], outputfile)
    if level + 'subsections' in section:
        for subsection in section[level + 'subsections']:
            parsesection(subsection, outputfile, 'sub' + level)

# Parses the content section of given part/section, and proceeds to specially handle
# the various content types. Essentially a glorified switch statement
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
            delptable.writetable(component, outputfile)
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
    if 'listtype' in component:
        outputfile.write('\\' + component['listtype'] + '\n')
    
    # Value here should be a list, which makes sense given the type
    for point in component['value']:
        outputfile.write('\\item ' + point + '\n')
    outputfile.write('\\end{itemize}\n')
    

# This function is probably pretty underdeveloped right now.
# I don't really know what features people want for these. One
# probably useful feature is a * which spreads the picture across
# the entire page
def writeimg(component, outputfile):
    outputfile.write('{\XeTeXpicfile "' + component['value'] +'" ')
    if 'height' in component:
        outputfile.write(' height ' + component['height'])
    if 'width' in component:
        outputfile.write(' width ' + component['width'])
    outputfile.write('}\n')


# Classes aren't content types, per se, but rather predefined collections
# of content types defined in the json. These can replace sections or 
# individual components, and take classvalues which specify the dynamic
# parts of the class
def writeclass(component, outputfile):
    classlist = (report['classes'])
    index = 0
    for i, classdef in enumerate(classlist):
        if classdef['name'] == component['classname']:
            index = i
            break
    classdef = classlist[index]
    if 'amount' in component:
        i = 0
        while i < int(component['amount']):
            if 'classvalues' in component:
                parseclass(classdef, component['classvalues'][i])
            else:
                parseclass(classdef, None)
            i = i + 1
    else: 
        if 'classvalues' in component:
            parseclass(classdef, component['classvalues'])
        else:
            parseclass(classdef, None)

def parseclass(classdef, classvalues):
    classinst = None
    if classvalues != None:
        classinst = classreplace(classdef, classvalues)
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


# Replaces all instances of *classvalue*[x] with the appropriate given 
# classvalue
def classreplace(classdef, classvalues):
    componentstr = json.dumps(classdef)
    for i, cvalue in enumerate(classvalues):
        #THIS IS A HARDCORE HACK, AND IT ISN'T THE RIGHT THING TO DO, SO
        #FIX IT WHEN ABLE. This hack addresses the problem of replacing a
        #classvalue marker with a list, as "value":*classvalue*[x] is not
        #valid json
        if isinstance(cvalue, list):
            cvalue = json.dumps(cvalue)
            replacestring = '"*classvalue*[' + str(i) + ']"'
        else:    
            replacestring = '*classvalue*[' + str(i) + ']'
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
outputfilename = "temp" + str(time.time()) + ".tex"
outputfile = open(outputfilename, 'w')
outputfile.write('\\nonstopmode\n')
outputfile.write('\\input{documentheader.tex}\n')
outputfile.write('\\begin{document}\n')
outputfile.write('\\frontmatter\n')

reportdoc = json.load(f)
report = reportdoc['report']
if 'coverimage' in report:
    titlepage(report, outputfile)

mainpage(report, outputfile)
outputfile.write('\\tableofcontents\n')
outputfile.write('\\mainmatter\n')
publish(report, outputfile)

outputfile.write('\end{document}')
outputfile.close()

os.system("xelatex -halt-on-error " + outputfilename)
os.system("xelatex -halt-on-error " + outputfilename)
os.system("evince " + string.replace(outputfilename, '.tex', '.pdf') + " &")

#os.remove(outputfilename)

def strcasecmp(str1, str2):
    return str1.lower() == str2.lower()
