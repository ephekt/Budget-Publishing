# Budget-Publishing
This repo contains tools for publishing a pdf budget report based on a
json input

## Description
The main tool in this repo is a publishing program. This program heavily
leverages LaTeX to provide a strictly formatted yet highly customizable
environment for producing a budget PDF. 

The budget publishing program takes in a JSON and requires that there be a
.tex file called documentheader.tex (this is subject to change if
desired). This .tex file defines the macros used in the JSON file, as well
as many default macros for table environment. It also sets rules and
imports neccessary packages. 

## Usage
### Invocation
The tool is invoked from the command line, and takes just one argument
(the JSON file containing the data for the report)
     
     python budgetPublishing.py example.json

## Configuration
### Document Header
The tool requires a documentheader to be present in the repository that
the tool is running in. This header is responsible for a few things

#### Document Specification
The documentheader should specify the document type, e.g.  

    \documentclass{book}

As well as make any neccessary modifications to the various document
attributes, e.g.
    
    \marginsize{2cm}{2cm}{1cm}{1cm}
    \pagestyle{fancy}

#### Package Imports
The documentheader should import required packages, using the
\usepackage{package} syntax

#### Macro definition
The python program attempts to heavily leverage the builtin capabilities
of LaTeX. Various fields are wrapped in macros to allow for modification
of their style.

So far, the default macros that need to be defined (all for tables) are as
follows. All should take 1 argument unless otherwise indicated

Not so much a macro but something to display in a table when no information is
found for a particular row. Should take 0 arguments. For example
\newcommand{\noinfo}[0]{-} 

    \noinfo

Macro for formatting normal numbers, applied to any numerical rows in a
 table or column unless specifically overridden.
    
    \num

Macro for fromatting and displaying percentages, applied by default to any
 diff row that outputs a percentage. For example

    \newcommand{\percentage}[1]{\numprint{#1}\%} 
    \percentage

Macro applied to the text in the top left corner of a table (that has both a
title column and row

    \tableTitleMacro

Macro applied to the entire column title row

    \colTitleRow

Macro applied to each item in the column title row

    \colTitleItem

Default macro applied to each row in every table

    \row

Default macro applied to every regular item in a table

    \tableItem

Default macro applied to every row title

    \rowTitle

Default macro applied to a sum of an entire table

    \sumRow

Default macro applied to a sum of an entire subtable

    \subSumRow

Default macro applied to any other sum row

    \subSubSumRow

Default macro applied to the items of a sum of an entire table

    \sumItem

Default macro applied to the items of a sum of an entire subtable

    \subSumItem

Default macro applied to the items of any other sum

    \subSubSumItem

Similar to the above, except apply to the row titles of sums

    \sumTitle
    \subSumTitle
    \subSubSumTitle

Same as sum macros, except for diff rows. Doesn't differentiate between levels
 like sums do.
     
    \diffRow
    \diffItem
    \diffTitle

Default macro applied to the title of a subtable (which is a floating title
above the actual table.

    \subTableTitle


It is may prove useful to define a none macro. This would simply be an
identity function, such as 

    \newcommand{\none}[1]{#1}

So that defaults can be defined as 

    \sumtitle[1]{\none{#1}}

To explicitly state that the default is plaintext. Most defaults will
likely just be plaintext

### JSON

The JSON has a very particular format, below is a heirarchical breakdown
Every JSON is wrapped with an outer object called "report". If this is not
the outermost object, the program will not work. Within report, there is
likely going to be some metadata information. Currently this is in flux.

Likely the largest object within report will be the 'parts' section. In
here, the report body will be constructed. A 'part' corresponds to a
section in the document initialized with LaTeX \part. It can have 3
sub-attributes: 

* title:
Defines the title of the section fed to the
LaTeX \part command 
* section:
Defines sections within parts. Sections are exactly like parts
in content, except they use the LaTeX /section command. Within sections
there can be subsections (which can in turn contain subsubsections,
etc.). By default LaTeX only supports down to /subsubsection, so any
further divisions will have to be defined in the header
* content:
Defines content that goes at the beginning of a part that does
not belong to a subsection (or, in the event of a leaf
part/section/subsection/etc., defines the content of that
section). Content contains a list of various components. Components always
have a "type" attribute and a "macro" attribute, and then from there other
attributes are specific to type. "macro" defines a LaTeX command that
wraps the entire component. These macros are, as previously mentioned,
included in the header file and can exercise any of the functionality of
TeX. 

Components make up the meat of the document. The currently implemented
components are: 

#### text
Contains only a "value" attribute. Simply outputs text. What we
may want to do in the future is come up with some sort of markup language
in order to support formatting specific words. Right now that kind of
formatting can be accomplished my manually putting LaTeX commands (with
the \ escaped to be \\\\) in the text.

#### list
contains two attributes, a "value" which is a list of text string
that will be put into the list, and an optional "listType". List time is
the name of a defined macro used for the list bulleting. For example, one
may have 

    "listType":"checkl"
    
where checkl has been defined as follows:

    \newcommand{\checkl}[0]{\renewcommand{\labelitemi}{$\checkmark$}}

and produces a list with checkmark bullets

#### img 
Outputs an image

##### Mandatory Attributes
* src: The name of the image file to be loaded. Should be in the
          current working directory

##### Optional Attributes:
* height: The height of the image, with LaTeX units (in for
inches, etc.)
* width: The Width of the image

By default, if only one of the above two parameters is specified,
LaTeX keeps the original ratio of the image, which is often
desirable


#### function
Performs an arbitrary latex function, in the from of

    \function[optarg1]{mandarg1}
    
This allows for more control over the document styling

##### Mandatory Attributes:
* value: The name of the function
          
##### Optional (?) Attributes:
* optargs: A list of the functions optional arguments
* args: A list of the functions mandatory args

The optional nature of args depends on how the function is
defined. Obviously a function with no mandatory arguments doesn't
need that attribute and shouldn't have it

Functions are best used for things that are only done once or a very small
number of time in the document, such as invoking the table of contents,
for that it may be useful to invoke tableofcontents function in the JSON

#### Table
Produces a table given certain parameters. Tables are a bit confusing, as
no single parameter is mandatory. Rather, sometimes one attribute assumes
others are given. I'll do my best to indicate those as clearly as possible

##### Optional Attributes:
* src: If the table is at least partially custom, this determines
the src cvs file that data is read from. This default can be
overridden in lower levels (subtables, rows) by redeclaring the
src field, as will be described later

* colTitles: Determines whether the table has titles over the
         columns. By default this is true, but if one wants to disable
         this, they can write "coltitles":"false". An important note about
         coltitles is that they also determine whether or not to skip the
         first row when reading from cvs files for custom tables (as in,
         if the user inputs 1 that refers to the second row, assuming the
         first row is all titles). If an override for this is desired, I
         will add one.  

* rowTitles: Similar to coltitles, except for rows. Same
         interaction with reading from cvs.

* title: Title is a slight misnomer. If both rowtitles and
         coltitles are true, this defines what goes into the top right of
         the document. This has a slightly different meaning for
         subtables. If given for a subtable, this is what goes above the
         rows of that subtable

* titleMacro: defines the styling for the above 'title'. For
         subtables, defines the styling for its title, which can include
         the rowmacro since it's on it's own row. I reccommend using
         multicolumns in order to allow a long subtable title to span more
         than the title row (so that it doesn't unneccessarily widen the
         title row.

* defaultRowMacro: This overrides the document wide default row
         macro for nonspecial rows. This Functionality is mostly useful
         for subtables, as with the outer table the functionality can be
         performed using a macro over the entire table and the
         \renewcommand LaTeX functionality

* defaultItemMacro: Similar to rowmacro, except for the individual
         items in a row

* defaultRowTitleMacro: Similar to rowmacro, except for the title
         of each row
 
* columnLayout: This is used to manually specify the exact layout
         of the columns of a table, e.g. c|p{2in} r | l {@} c, or some
         other random layout like that. This is pretty cumbersome, but I
         feel like 'column' oriented layouts are much less common than row
         oriented layouts. However, much of the framework neccessary to
         make this a little less cumbersome is already there, I just don't
         want to bloat the interface more if it isn't seen as useful. 
         
* rowTitleWidth: In the event columnlayout is not specified, this
         allows specififying the width of the first column, in inches, as
         often the first colun is different from the rest. 
         By default, all columns are the same width, and tables are
         designed to take up the entire page.

* sumRow: A boolean, default false, which determines if the last
          row in a given row or subtable should be the sum of all other
          nonspecial rows.
          
* sumRowMacro, sumItemMacro, sumTitleMacro: As with the
          similar functionality for the other macros, these override the
          default macros for the automatically generated sum row (these do
          not effect other, manually specified sum rows)

* sumRowTitle: determines the title of the automatically
          generated sum row. By default the title is Total (for the top
          level table) or Subtotal for any subtables

* rows: rows contains a list of 'rows' for a given
table/subtable, although subtables are also defined here. rows
have several possible attributes:
    * subTable: this is used for definining a subtable, and
      should be the only attribute in a given row. subtable
      itself is an object that defines many subattributes. I will
      not list these, as a subtable is very similar to a table,
      except that it cannot specify things that pertain to
      columns
    * rowMacro, itemMacro, titleMacro: as before, define
    the specific macroes for this row, overriding the defaults   
    * type: type can take a few different values, and is used
      to specify special rows. The valid values are listed:
          * sum, product: Sum and product are fairly self
            explanatory, and are rows that are sums (or
            multiples) of other rows. When these are specified
            an optional argument to specified the rows to sum
            can also be given as:
                * rows: Specifies the rows to sum or
                  multiply. By default, if this is not
                      specified, all nonspecial rows leading up
                          to the current row (this can be
                              changed). It's important to note that rows
                                  are referenced from 1, not 0 as in
                                      computer Science, and that if coltitles
                  are enabled the first column does not count.
                * diff, division: Difference and Division rows
                         are rows that are differences (or divisions) of
                         two other rows. The rows can be manually
                         specified as shown
                     * diff: If a diff is x-y and a division
                                 x/y, this is the column number of x
                                against: And this would be y
                     * diffType: Right now, there are only two
                                 types. 'numeric', which is the default and
                                 is exaclty what shown with the x y thing,
                                 and 'percent'. Percent for diff shows the
                                 change going from y to x. Percent for
                                 division shows the percent that x is of
                                 y.                           
    * custom: States that this row should read from a
                          cvs file. Takes the following optional arguments
        * rowNum: specifies which row in the cvs
                                 file to read from. By default this is the
                                 number of the current row in the given
                                 subtable. As per usual, numbering starts
                                 from one and the column title is ignored.
        * src: specifies a cvs file to read
                                  from. This only needs to be specified if
                                  no src was specified in the parent
                                  table or some ancestor table, however it
                                  can also be used to specify a file
                                  unique to that row
    * title: determines the rowtitle of the given row
    * numType: This specifies what kind of numbers the elements
               in this row are (e.g. monetary, FTE, etc). And
               simply add a macro tag matching the passed in string
               to be handled in LaTeX. The heuristic is that
               non-defaults take precendence over default, that
               rows take precendent over columns, and that
               percentages take precedent over all. TODO: As of now
               sums or multiples of percentages don't neccessarily
               inherit their traits. This maybe should be fixed in a
               future version
                         
                         
* sumCol: Specifies whether the last column should be a sum of all
       other columns.
    * sumColTitle: Self explanatory. Total by default
      
      
* columns: Much like rows, this allows manual specification of
       columns in the table. Many of the arguments are the same, with row
       replace by column where neccessary, so I will not go into all of
       them. Notably, macros cannot be declared for columns, as these are
       put into the header of the column in columnlayout. If this is not
       specified by src is, by default the columns will simply be the
       columns in the src table. Rows behave similarly. 


#### Class
 Classes are special, in that they are not objects in and of them selves,
 but rather expansions of predefined definitions. I'll go into both the
 definition and the use here.

 In order to define a class, the top level report should contain a
 classes attribute, which has a value which is a list of objects, which
 contain the following fields:
 
* name: The name of the class, so that it can be instanciated
        
* level: the heirarchcial 'report' level the class fits into,
        e.g. 'part', 'section', 'subsection', subsubsection',
        'component'. This states what level the component should be
        instantiated in. 

* definition: This is the meat of the class. What you do here is
         write the objects within the class as though it were the contents
         of the level given in "level". The only difference is, any  
         place where the content of the class should be specifiable, you
         write \*classValue\*[x], where x is a list index starting from
         0. If you want the classvalue to be a list, write
         "\*classValue\*[x]", and the outer quotation marks will be removed
         if the classvalue is a list. 

Instanciating: Classes can be instanciated in two main ways, as a
component and as a 'section' (part, whatever). To instanciate it as a
component, simply write "type":"class" then given the two be stated
attributes. To instanciate it as a section, when giving a section object,
instead of 'title' 'content' and all that, just give the class attributes,
which will be detected and take precedence. The attributes are as follows:
      
* className: The name of the class to instanciate

* classValues: a list of values to replace the *classvalue*s in
         the declaration with. Each element can be a list or a list of
         lists as neccessary, if it's supported in the definition

* Optionally, amount: "amount" specifies the number of
        replications of a class object, each with it's own classvalues
        (the passed in classvalues must be a list of lists, which each
        element being the classvalues for the corresponding
        instanciation). The primary use of this functionality is for
        declaring classes that have variable numbers of a subclass.

Classes are a little cumbersome right now, and a lot of that's tied to it
having to be in the JSON format. This may be redesignable to great benifit.

## Development Notes
A lot of the first round of this tool was written in a fairly unstructured
way. Things make sense but they don't neccessarily flow, and there are
lots of fairly large code blocks that do similar things in slightly
different ways. For that reason among others, rewriting the core of this
code for new development may not be such a bad idea, but I wanted to share
some of the thought process which went into the current structure, which
may not be neccessary to change.

### Basic Structure
The basic thoughts I had regarding the basic structuring of the documents
was that it should leverage LaTeX as much as possible. Almost nothing
should be built in, except basic structural components (text blocks,
images, tables, etc). Rather, things should be macro based. The user is
able to macro any basic component using built-in LaTeX functions to alter
##the style. This leaves the system highly configurable, and uses the
##Python more for glue that anything else

### Functions
There are lots of little structural things a user may want to have control
over in the document. They may want to force a new page, switch from
frontmatter to mainmatter, place the table of contents, or do various
other things. Rather that hardcoding these functions as 'components', or
some hardcoded subset of 'function', it made sense to put in a 'function'
component that just literally calls a LaTeX function. 

In some ways this leverages the front-end. It's not like the user is going
to write {type:"function", value:"tableofcontents"}, theoretically they're
going to go through a front-end tool, where the high level function 'Table
of Contents' will be presented to them. This creates flexibility to alter
what these presented functions are without changing the backend, and even
have them differ between multiple tools using the same backend.

### Classes
One thing about city budgets is that for all the mess and clutter that
occurs in large parts of them, about 70-80% is in a very structured (or at
the very least repetitive) form. A good tool should allow for
specification of certain budget elements such as a Department Ledger, and
then allow the user to only enter the elements that change within that
(department name, goals, etc.). The current method of doing it may be a
little clumsy. It requires handwritten JSON and has a few hacks. A
different abstraction for this would be befificial

### Tables
Tables are really the core of this project, and they aren't really
finished, which is a problem. 

#### What I did
The problem with tables is that governments often want to do really random
stuff and have stupid organization in tables. The idea of a good
abstraction for how to specify tables is that we make doing well organized
things as easy as possible, and allow for poorly specified things through
heavy customizability but make that significantly more difficult. The way
to do this is through healthy defaults.

For example, if a user simply wants to place a table loaded in from a csv,
they simply specify the table src and the table is automatically generated
and placed for them. If they want to modify an individual row in the
middle, have another row have different styling, do a percentage
difference between two rows, or whatever other random thing, they can do
that, but they have to put work into it.

Another insight is the general organization of tables into
subtables. Tables can be composed of arbitrarily nested subtables, and we
have to allow for this. One nice thing about subtables is that they exist
as a unit of summing within a larger subtable. For example, you can sum
two subtables, but you will never sum one row within a given subtable with
another row in another subtable. This allowed me to treat subtables in the
same way that I treat rows, and just have a subtable be a different 'type'
of row.

#### Missing features and considerations
Arguably the most important feature of this tool, and one that is missing
at the time of writing this due to missing infrastructure, is the ability
to generate a table from the database data. Using a combination of row and
column specifiers, the user should be able to specify data cells that read
in from the database. For example, the row specifier could be 'salary line
items from the Administration Division of the Fire department' and the
column specifier could be year 2012, and this would automatically fill in
a cell with data. 

Now, there may be situations where specifiers do not resolve to a single
line item, but perhaps many. In these cases, they should probably be
aggregated by a simple sum.

I think an important feature will be the autogeneration of rows within a
table or subtable (and potentially even the automatic generation of
subtables). Here's what I mean by this: Say the user wants to lay out the
total expenses of each department across the last 5 years. A user should
be able to specify the years as columns, but for the rows, rather than
specifying all of the departments, they should be able to only specify
they want the total expensenses of each department, and have the table
be created for them. 

As for subtable autogenerating, that would be something along the lines of
specifying "each expense line item matching 'taxes' for each department,
where each department name becomes the title of a subtable listing the
line items within it.

It may be beneficial in a future edition to separate out the data side of
the table and the format side. I saw them as pretty entertwined, which is
why I didn't do this, but it may be possible with the right abstraction to
have the main program only load from CSVs, and have another program be
responsible for creating that csv (Frankenstein style, reading from the
database, or otherwise).

Another potentially missing feature of the current implementation is the
ability to edit a cell after the fact. This feature is cumbersome and
requires better front-end integration to understand how it'll work.

### TODO
case-insensitivity for reading in the JSON. Not neccessary but more robust
