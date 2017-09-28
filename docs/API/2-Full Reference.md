# API Full Reference

## Package `base`
 
FILE: ...\Parser\src\parsertools\base.py
	
### CLASSES

#### class ParseStruct(builtins.object)
Parent class for all ParseStruct subclasses. These subclasses will typically correspond to productions in a given grammar, e.g. an EBNF grammar.

     |  
     |  __eq__(self, other)
     |      Compares the instances for equality of:
     |      - class
     |      - string representation.
     |      This means that the labels, parent pointers etc. are not taken into account. This is because
     |      these are a form of annotation and/or context, separate from the parse tree in terms of resolved production rules.
     |  
     |  __getattr__(self, att)
     |      Retrieves the unique, direct subelement having a label equal to the argument, if it exists.
     |      Raises an exception if zero, or more than one values exist for that label.
     |  
     |  __init__(self, expr)
     |      A ParseStruct object contains a _pattern attribute, that corresponds to a pyparsing _pattern.
     |      It can be initialized wih either a valid string for the subclass concerned,
     |      using its own _pattern attribute to parse it, or it can be initialized with an explicit "None" as argument. This latter option is only
     |      meant to be used by internal parser processes. The normal use case is to feed it with a string.
     |      This will build the _items attribute. This is a list. Each element is either
     |      
     |      - a string, or
     |      - another ParseStruct object.
     |      
     |      This nested list is the basic internal structure for the class.
     |      The other attibutes: _label and _parent_, are context dependent and will be set by a containing higher level ParseStruct, if that exists.
     |  
     |  __ne__(self, other)
     |      Return self!=value.
     |  
     |  __repr__(self)
     |      Return repr(self).
     |  
     |  __setattr__(self, label, value)
     |      Raises exception when trying to set attributes directly.Elements are to be changed using "updateWith()".
     |  
     |  __str__(self)
     |      Generates a string corresponding to the object. Except for possible whitespace variation, 
     |      this is identical to the string that was used to create the object.
     |  
     |  check(self, *, report=False, render=False, dump=False)
     |      Runs various checks. Returns True if all checks pass, else False. Optionally prints a report with the check results, renders, and/or dumps itself.
     |  
     |  copy(self)
     |      Returns a deep copy of itself.
     |  
     |  createParentPointers(self, recursive=True)
     |  
     |  descend(self)
     |      Descends until either an atom or a branch node is encountered; returns that node.
     |  
     |  dump(self, indent='', step='|  ')
     |      Returns a dump of the object, with rich information
     |  
     |  getAncestors(self)
     |      Returns the list of parent nodes, starting with the direct parent and ending with the top element.
     |  
     |  getChildren(self)
     |      Returns a list of all its non-string child elements.
     |  
     |  getItems(self)
     |      Returns items attribute.
     |  
     |  getLabel(self)
     |      Returns name attribute.
     |  
     |  getLabels(self)
     |      Returns list of all labels from direct descendants.
     |  
     |  getParent(self)
     |      Returns its parent element, which is the first element encountered when going up in the parse tree.
     |      For the top element, the method returns None
     |  
     |  getValuesForLabel(self, k)
     |      Returns list of all direct descendants with k as label.
     |  
     |  hasLabel(self, k)
     |      True if k present as label of a direct descendant.
     |  
     |  hasParentPointers(self)
     |  
     |  isAtom(self)
     |      Test whether the node has a string as its single descendant.
     |  
     |  isBranch(self)
     |      Checks whether the node branches.
     |  
     |  isValid(self)
     |      Returns True if the object is equal to the result of re-parsing its own rendering.
     |      This should normally be the case.
     |  
     |  render(self)
     |  
     |  searchElements(self, *, label=None, element_type=None, value=None, labeledOnly=False)
     |      Returns a list of all elements with the specified search _pattern. If labeledOnly is True,
     |      only elements with label not None are considered for inclusion. Otherwise (the default case) all elements are considered.
     |      Keyword arguments label, element_type, value are used as a wildcard if None. All must be matched for an element to be included in the result.
     |  
     |  setItems(self, items)
     |  
     |  updateWith(self, new_content)
     |      Replaces the items attribute with the items attribute of a freshly parsed new_content, which must be a string.
     |      The parsing is done with the _pattern of the element being updated.
     |      This is the core function to change elements in place.
     |  
     |  yieldsValidExpression(self)
     |      Returns True if the rendered expression can be parsed again to an element of the same class.
     |      This should normally be the case.
     |  
     |  ----------------------------------------------------------------------
     |  Class methods defined here:
     |  
     |  getPattern() from builtins.type
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
     |  
     |  ----------------------------------------------------------------------
     |  Data and other attributes defined here:
     |  
     |  __hash__ = None

## FUNCTIONS
### parseStructFunc(class_)
Returns the function that converts a ParseResults object to a ParseStruct object of class "class_", with label set to None, and items set to a recursive list of objects, each of which is either a string or a further ParseStruct object.
The function returned is used to set a parseAction for a _pattern.
    
### separatedList(_pattern, sep=',')
Similar to a delimited list of instances from a ParseStruct subclass, but includes the separator in its ParseResults. Returns a delimitedList object with a special parse action. If a resultsName for the delimitedList was specified, the corresponding label is applied to all occurrences of the _pattern.

DATA
    alphanums = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz01234...
    alphas = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    alphas8bit = 'ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøù...
    anyCloseTag = </any tag>
    anyOpenTag = <any tag>
    cStyleComment = C style comment
    commaSeparatedList = commaSeparatedList
    commonHTMLEntity = common HTML entity
    cppStyleComment = C++ style comment
    dblQuotedString = string enclosed in double quotes
    dblSlashComment = // comment
    empty = empty
    hexnums = '0123456789ABCDEFabcdef'
    htmlComment = HTML comment
    javaStyleComment = C++ style comment
    lineEnd = lineEnd
    lineStart = lineStart
    nums = '0123456789'
    opAssoc = <pyparsing._Constants object>
    printables = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRST...
    punc8bit = '¡¢£¤¥¦§¨©ª«¬\xad®¯°±²³´µ¶·¸¹º»¼½¾¿×÷'
    pythonStyleComment = Python style comment
    quotedString = quotedString using single or double quotes
    restOfLine = rest of line
    sglQuotedString = string enclosed in single quotes
    stringEnd = stringEnd
    stringStart = stringStart
    unicodeString = unicode string literal



