'''
Created on 3 mrt. 2016

@author: jeroenbruijning
'''
from pyparsing import *
from parsertools import ParsertoolsException

class ParseStruct:
    '''Parent class for all ParseStruct subclasses. These subclasses will typically correspond to productions in a given grammar,
    e.g. an EBNF grammar.'''
    
    @classmethod
    def getPattern(cls):
        return cls._pattern
    
    def __init__(self, expr):
        '''A ParseStruct object contains a _pattern attribute, that corresponds to a pyparsing _pattern.
        It can be initialized wih either a valid string for the subclass concerned,
        using its own _pattern attribute to parse it, or it can be initialized with an explicit "None" as argument. This latter option is only
        meant to be used by internal parser processes. The normal use case is to feed it with a string.
        This will build the _items attribute. This is a list. Each element is either
        
        - a string, or
        - another ParseStruct object.
        
        This nested list is the basic internal structure for the class.
        The other attibutes: _label and _parent_, are context dependent and will be set by a containing higher level ParseStruct, if that exists.'''
        
        self.__dict__['_items'] = None
        self.__dict__['_label'] = None
        self.__dict__['_parent'] = None
        
        if not expr is None:
            assert isinstance(expr, str), type(expr)
            other = self.__getPattern().parseString(expr, parseAll=True)[0]
            for attr in other.__dict__:
                self.__dict__[attr] = other.__dict__[attr]
            self.createParentPointers()
                
    def __eq__(self, other):
        '''Compares the instances for equality of:
        - class
        - string representation.
        This means that the labels, parent pointers etc. are not taken into account. This is because
        these are a form of annotation and/or context, separate from the parse tree in terms of resolved production rules.'''
        
        return self.__class__ == other.__class__ and str(self) == str(other)
    
    def __ne__(self, other):
        return not self == other
    
    def __getattr__(self, att):
        '''Retrieves the unique, direct subelement having a label equal to the argument, if it exists.
        Raises an exception if zero, or more than one values exist for that label.'''
        
        if att in self.getLabels():
            values = self.getValuesForLabel(att)
            if len(values) == 1:
                return values[0] 
        else:
            raise AttributeError('No attribute, or unique label found for argument "{}".'.format(att))
#         
    def __setattr__(self, label, value):
        '''Raises exception when trying to set attributes directly.Elements are to be changed using "updateWith()".'''
        
        raise AttributeError('Direct setting of attributes not allowed. To change an element e, try e.updateWith() instead.')
    
    def __repr__(self):
        return self.__class__.__name__ + '("' + str(self) + '")'
    
    def __str__(self):
        '''Generates a string corresponding to the object. Except for possible whitespace variation, 
        this is identical to the string that was used to create the object.'''
        
        result = []
        for t in self._items:
            if isinstance(t, str):
                result.append(t) 
            else:
                assert isinstance(t, ParseStruct), '__str__: found value {} of type {} instead of ParseStruct instance'.format(t, type(t))
                result.append(str(t))
        return ' '.join([r for r in result if r != ''])

    def __getPattern(self):
        '''Returns the _pattern used to parse expressions for this class.'''
        return self.__class__.getPattern()
    
    def __getElements(self, labeledOnly = True):
        '''Returns a flat list of all enmbedded ParseStruct instances (inclusing itself),
        at any depth of recursion.
        If labeledOnly is True, then in addition label may not be None.'''
        
        def flattenElement(p):
            result = []
            if isinstance(p, ParseStruct):
                result.extend(p.__getElements(labeledOnly=labeledOnly))
            else:
                assert isinstance(p, str), type(p)
            return result
        
        def flattenList(l):
            result = []
            for p in l:
                result.extend(flattenElement(p))
            return result
        
        result = []
        if self.getLabel() or not labeledOnly:
                result.append(self)
        result.extend(flattenList(self.getItems()))
        return result  
    
    def createParentPointers(self, recursive=True):
        for i in self.getItems():
            if isinstance(i, ParseStruct):
                i.__dict__['_parent'] = self
                if recursive:
                    i.createParentPointers()

    def copy(self):
        '''Returns a deep copy of itself.'''
        result = self._pattern.parseString(str(self))[0]
        assert result == self
        return result
    
    def setItems(self, items):
        self.__dict__['_items'] = items
    
    def searchElements(self, *, label=None, element_type = None, value = None, labeledOnly=False):
        '''Returns a list of all elements with the specified search _pattern. If labeledOnly is True,
        only elements with label not None are considered for inclusion. Otherwise (the default case) all elements are considered.
        Keyword arguments label, element_type, value are used as a wildcard if None. All must be matched for an element to be included in the result.'''
        
        result = []
        
        for e in [self] + self.__getElements(labeledOnly=labeledOnly):
#             print('DEBUG: e.name =', e.getLabel())

            if labeledOnly and not e.getLabel():
                continue
            if label and label != e.getLabel():
                continue
            if element_type and element_type != e.__class__:
                continue
            if value:
                try:
                    e1 = e._pattern.parseString(value)[0]
                    if e != e1:
                        continue
                except ParseException:
                    continue
            result.append(e)
        return result    

    def updateWith(self, new_content):
        '''Replaces the items attribute with the items attribute of a freshly parsed new_content, which must be a string.
        The parsing is done with the _pattern of the element being updated.
        This is the core function to change elements in place.'''
        
        assert isinstance(new_content, str), 'UpdateFrom function needs a string'
        try:
            other = self._pattern.parseString(new_content, parseAll=True)[0]
        except ParseException:
            raise ParsertoolsException('{} is not a valid string for {} element'.format(new_content, self.__class__.__name__))        
        self.__dict__['_items'] = other.__dict__['_items']
        self.createParentPointers(recursive=False)
        assert self.isValid()
    
    def check(self, *, report = False, render=False, dump=False):
        '''Runs various checks. Returns True if all checks pass, else False. Optionally prints a report with the check results, renders, and/or dumps itself.'''
        if report:
            print('{} renders {} expression ({})'.format(self, 'a valid' if self.yieldsValidExpression() else 'an invalid', self.__str__()))
            print('{} is{}a valid parse object'.format(self, ' ' if self.isValid() else ' not '))
        if render:
            print('--rendering:')
            self.render()
        if dump:
            print('--dump:')
            print(self.dump())
        return self.yieldsValidExpression() and self.isValid()

    def getLabel(self):
        '''Returns name attribute.'''
        return self._label

    def getItems(self):
        '''Returns items attribute.'''
        return self._items

    def hasLabel(self, k):
        '''True if k present as label of a direct descendant.'''
        return k in self.getLabels()
     
    def getLabels(self):
        '''Returns list of all labels from direct descendants.'''
        return(filter(None, [i.getLabel() for i in self.getItems() if isinstance(i, ParseStruct)]))
    
    def getValuesForLabel(self, k):
        '''Returns list of all direct descendants with k as label.'''
        return [i for i in self.getItems() if isinstance(i, ParseStruct) and i._label == k]
    
    def getChildren(self):
        '''Returns a list of all its non-string child elements.'''
        return [i for i in self.getItems() if isinstance(i, ParseStruct)]
    
    def getParent(self):
        '''Returns its parent element, which is the first element encountered when going up in the parse tree.
        For the top element, the method returns None'''
        return self._parent
    
    def getAncestors(self):
        '''Returns the list of parent nodes, starting with the direct parent and ending with the top element.'''
        result = []
        parent = self.getParent()
        while parent:
            result.append(parent)
            parent = parent.getParent()
        return result
    
    def isBranch(self):
        '''Checks whether the node branches.'''
        return len(self.getItems()) > 1
            
    def isAtom(self):
        '''Test whether the node has a string as its single descendant.'''
        return len(self.getItems()) == 1 and isinstance(self._items[0], str)
    
    def descend(self):
        '''Descends until either an atom or a branch node is encountered; returns that node.'''
        result = self
        while not result.isAtom() and not result.isBranch():
            result = result.getItems()[0]
        return result
        
    def dump(self, indent='', step='|  '):
        '''Returns a dump of the object, with rich information'''
        result = ''
        def dumpString(s, indent, step):
            return indent + s + '\n'
        
        def dumpItems(items, indent, step):
            result = ''
            for i in items:
                if isinstance(i, str):
                    result += dumpString(i, indent+step, step)
                else:
                    assert isinstance(i, ParseStruct) 
                    result += i.dump(indent+step, step)
            return result       
       
        result += indent + ('> '+ self.getLabel() + ':\n' + indent if self.getLabel() else '') + '[' + self.__class__.__name__ + '] ' + '/' + self.__str__() + '/' + '\n'
        result += dumpItems(self._items, indent, step)
        
        return result
    
    def render(self):
        print(self.__str__())
    
    def yieldsValidExpression(self):
        '''Returns True if the rendered expression can be parsed again to an element of the same class.
        This should normally be the case.'''
        try:
            self.__getPattern().parseString(self.__str__(), parseAll=True)
            return True
        except ParseException:
            return False
        
    def isValid(self):
        '''Returns True if the object is equal to the result of re-parsing its own rendering.
        This should normally be the case.'''
        return self == self.__getPattern().parseString(self.__str__())[0]
    
    def hasParentPointers(self):
        for item in [i for i in self.getItems() if isinstance(i, ParseStruct)]:
            if not item.getParent() == self or not item.hasParentPointers():
                return False
        return True
    
def parseStructFunc(class_):
    '''Returns the function that converts a ParseResults object to a ParseStruct object of class "class_", with label set to None, and
    items set to a recursive list of objects, each of which is either a string or a further ParseStruct object.
    The function returned is used to set a parseAction for a _pattern.'''
            
    def itemList(parseresults):
        '''For internal use. Converts a ParseResults object to a recursive structure consisting of a list of objects,
        which will serve as the items attribute of a ParseStruct object.'''
        
        while len(parseresults) == 1 and isinstance(parseresults[0], ParseResults):
            parseresults = parseresults[0]
        valuedict = dict((id(t), k) for (k, t) in parseresults.items())
        assert len(valuedict) == len(list(parseresults.items())), 'internal error: len(valuedict) = {}, len(parseresults.items) = {}'.format(len(valuedict), len(list(parseresults.items)))
        result = []
        for t in parseresults:
            if isinstance(t, str):
                result.append(t)
            elif isinstance(t, ParseStruct):
                if t.__dict__['_label'] == None:
                    t.__dict__['_label'] = valuedict.get(id(t))
                result.append(t)
            elif isinstance(t, list):
                result.append(t)
            else:
                assert isinstance(t, ParseResults), type(t)
                assert valuedict.get(id(t)) == None, 'Error: found label ({}) for compound expression {}'.format(valuedict.get(id(t)), t.__str__())
                result.extend(itemList(t))
        return result
    
    def makeparseinfo(parseresults):
        # The function to be returned.
        assert issubclass(class_, ParseStruct)
        assert isinstance(parseresults, ParseResults)
        result = class_(None)
        result.setItems(itemList(parseresults))
        return result
    
    return makeparseinfo

# Helper function for delimited lists where the delimiters must be included in the result

def separatedList(_pattern, sep=','):
    '''Similar to a delimited list of instances from a ParseStruct subclass, but includes the separator in its ParseResults. Returns a 
    delimitedList object with a special parse action. If a resultsName for the delimitedList was specified, the corresponding
    label is applied to all occurrences of the _pattern.'''
      
    def makeList(parseresults):
        assert len(parseresults) > 0, 'internal error'
        assert len(list((parseresults.keys()))) <= 1, 'internal error, got more than one key: {}'.format(list(parseresults.keys()))
        label = list(parseresults.keys())[0] if len(list(parseresults.keys())) == 1 else None
        assert all([p.__class__._pattern == _pattern for p in parseresults if isinstance(p, ParseStruct)]), 'internal error: _pattern mismatch ({}, {})'.format(p.__class__._pattern, _pattern)
        templist = []
        for item in parseresults:
            if isinstance(item, ParseStruct):
                item.__dict__['_label'] = label
                templist.append(item)
            else:
                assert isinstance(item, str)
                templist.append(item)
        result = []
        result.append(templist[0])
        for p in templist[1:]:
            result.append(sep)
            result.append(p)
        return result
  
      
    result = delimitedList(_pattern, sep)
    result.setParseAction(makeList)
    return result

                           
