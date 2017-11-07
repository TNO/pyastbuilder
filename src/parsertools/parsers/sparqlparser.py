'''
Created on 28 mrt. 2016

@author: jeroenbruijning
'''
from pyparsing import *
from parsertools.base import ParseStruct, parseStructFunc, separatedList
from parsertools import ParsertoolsException, NoPrefixError
import rfc3987
import re

# Custom exception. This is optional when defining a SPARQLParser. When present, it can be used in methods of the Parser class as defined below.

class SPARQLParseException(ParsertoolsException):
    '''Custom exception. This is optional when defining a SPARQLParser. When present, it can be used in methods of a ParseStruct subclass if
    defined below.'''
    
    pass

#
# Define the SPARQLElement class
#

class SPARQLElement(ParseStruct):
    '''Optional subclass of ParseStruct for the language. Typically, this class contains attributes and methods for the language that
    go beyond context free parsing, such as pre- and post processing, checking for conditions not covered by the grammar, etc.'''
    
    def __init__(self, expr, base=None, postParseCheck=True):
        '''This constructor has an optional argument "base". This is the externally determined base iri, as per SPARQL definition par. 4.1.1.2.
        It is only applied when the constructor is called with a string as expression to be parsed. (For internal bootstrapping purposes,
        the constructor can also be called with expr equal to "None". See also the documentation for the ParseStruct constructor.)'''
        ParseStruct.__init__(self, expr)
        self.__dict__['_prefixes'] = {}
        self.__dict__['_baseiri'] = None
        if not expr is None:
            self._applyPrefixesAndBase(baseiri=base)
            if postParseCheck:
                self._checkParsedQuery()
                    
    def _applyPrefixesAndBase(self, prefixes={}, baseiri=None):
        '''Recursively attaches information to the element about the prefixes and base-iri valid at this point
        in the expression, as determined by PREFIX and BASE declarations in the query.
        The parameter baseiri is as determined by the environment or an enveloping parsed entity. It must be an absolute
        IRI, or None.
        The treatment of BASE declarations depends on whether the IRI provided in the declaration is an absolute IRI or not.
        If an absolute IRI, it replaces from this point on the base IRI for the query. If relative, it is resolved
        using the baseiri parameter (which may not be None in this case) to give the next base IRI in force.
        Successful termination of this method does not guarantee that IRI expansion is possible, or that expanded IRIs conform to RFC 3987.
        This is purely a syntactic (substitution) operation. Use other available tests afterwards to check whether iris can be correctly
        expanded using base and prefixes in force at their location. The function _checkParsedQuery can be used for this.'''
        
        self.__dict__['_prefixes'] = prefixes
        self.__dict__['_baseiri'] = baseiri
        if baseiri:
            assert rfc3987.parse(baseiri, rule='absolute_IRI')
        prefixes = prefixes.copy()
        for elt in self.getChildren():
            if isinstance(elt, SPARQLParser.Prologue):
                for decl in elt.getChildren():
                    if isinstance(decl, SPARQLParser.PrefixDecl):
                        assert str(decl.prefix) not in prefixes, 'Prefixes: {}, prefix: {}'.format(prefixes, decl.prefix)
                        prefixes[str(decl.prefix)] = str(decl.namespace)[1:-1]
                    else:
                        assert isinstance(decl, SPARQLParser.BaseDecl)
                        iripart = str(decl.baseiri)[1:-1]
                        try:
                            rfc3987.parse(iripart, rule='absolute_IRI')
                            baseiri = iripart
                        except ValueError:
                            baseiri = rfc3987.resolve(baseiri, str(decl.baseiri)[1:-1])
                            assert rfc3987.parse(baseiri, rule='absolute_IRI')                            
            elt._applyPrefixesAndBase(prefixes, baseiri)
            
    def getPrefixes(self):
        return self._prefixes
    
    def getBaseiri(self):
        return self._baseiri   
        
    def expandIris(self):
        '''Converts all contained iri elements to normal form, taking into account the prefixes and base in force at the location of the iri.
        The expansions are performed in place.'''
        for elt in self.searchElements(element_type=SPARQLParser.iri):
            children = elt.getChildren()
            assert len(children) == 1, children
            child = children[0]
            newiriref = '<' + getExpansion(child) + '>'
            elt.updateWith(newiriref)
             
    def processEscapeSeqs(self):
        for stringtype in [SPARQLParser.STRING_LITERAL2, SPARQLParser.STRING_LITERAL1, SPARQLParser.STRING_LITERAL_LONG1, SPARQLParser.STRING_LITERAL_LONG2]:
            for elt in self.searchElements(element_type=stringtype):
                elt.updateWith(stringEscape(str(elt)))

    def _checkExpansion(self):
        iris = self.searchElements(element_type=SPARQLParser.PrefixedName) + self.searchElements(element_type=SPARQLParser.IRIREF)
        for iri in iris:
            expansion = getExpansion(iri)
            assert rfc3987.match(expansion, rule='IRI_reference'), 'Expression "{}" with expansion "{}" is not an IRI Reference'.format(iri, expansion)

    def _checkParsedQuery(self):
        '''Used to perform additional checks on the ParseStruct resulting from a parsing action. These are conditions that are not covered by the EBNF syntax.
        See the applicable comments and remarks in https://www.w3.org/TR/sparql11-query/, sections 19.1 - 19.8.'''
        
        # See 19.5 "IRI References"
        self._checkExpansion()
            
        
    #  TODO: finish

#
# The following is boilerplate code, to be included in every Parsertools parser definition module
#

class Parser:
    '''Class to be instantiated to contain a parser for the language being implemented.
    This code must be present in the parser definition file for the language.
    Optionally, it takes a class argument if the language demands functionality in its
    ParseStruct elements that goes beyond what is provided in base.py. The argument must be
    a subclass of ParseStruct. The default is to instantiate the parser as a ParseStruct 
    parser.'''
    
    def __init__(self, class_=ParseStruct):
        self.class_ = class_
#     def addElement(self, pattern):
#         setattr(self, pattern.name, type(pattern.name, (self.class_,), {'_pattern': pattern}))
#         pattern.setParseAction(parseStructFunc(getattr(self, pattern.name)))
    def addElement(self, pattern, newclass=None):
        if newclass:
            assert issubclass(newclass, self.class_)
        else:
            newclass = self.class_ 
        setattr(self, pattern.name, type(pattern.name, (newclass,), {'_pattern': pattern}))
        pattern.setParseAction(parseStructFunc(getattr(self, pattern.name)))
#
# Create the SPARQLParser object, optionally with a custom ParseStruct subclass
#

SPARQLParser = Parser(SPARQLElement)

#
# Main function to call. This is a convenience function, adapted to the SPARQL definition.
#

def parseQuery(querystring, base=None):
    '''Entry point to parse any SPARQL query'''
    
    s = prepareQuery(querystring)
    
    # In SPARQL, there are two entry points to the grammar: QueryUnit and UpdateUnit. These are tried in order.
    
    try:
        result = SPARQLParser.QueryUnit(s, base=base)
    except ParseException:
        try:
            result = SPARQLParser.UpdateUnit(s, base=base)
        except ParseException:
            raise SPARQLParseException('Query {} cannot be parsed'.format(querystring))
        
    result.processEscapeSeqs()    
    
    return result

#
# Utility functions for SPARQL
#

def prepareQuery(querystring):
    '''Used to prepare a string for parsing. See the applicable comments and remarks in https://www.w3.org/TR/sparql11-query/, sections 19.1 - 19.8.'''
    # See 19.4 "Comments"
    querystring = stripComments(querystring)
    # See 19.2 "Codepoint Escape Sequences"
    querystring = unescapeUcode(querystring)
    return querystring


def stripComments(text):
    '''Strips SPARQL-style comments from a multiline string'''
    if isinstance(text, list):
        text = '\n'.join(text)
    Comment = Literal('#') + SkipTo(lineEnd)
    NormalText = Regex('[^#<\'"]+')    
    Line = ZeroOrMore(String | (IRIREF | Literal('<')) | NormalText) + Optional(Comment) + lineEnd
    Line.ignore(Comment)
    Line.setParseAction(lambda tokens: ' '.join([t if isinstance(t, str) else t.__str__() for t in tokens]))
    lines = text.split('\n')
    return '\n'.join([Line.parseString(l)[0] for l in lines])

def unescapeUcode(s):
    
    def escToUcode(s):
        assert (s[:2] == r'\u' and len(s) == 6) or (s[:2] == r'\U' and len(s) == 10)
        return chr(int(s[2:], 16))
                   
    smallUcodePattern = r'\\u[0-9a-fA-F]{4}'
    largeUcodePattern = r'\\U[0-9a-fA-F]{8}'
    s = re.sub(smallUcodePattern, lambda x: escToUcode(x.group()), s)
    s = re.sub(largeUcodePattern, lambda x: escToUcode(x.group()), s)  
      
    return s

# various helper functions

# def isInScope(variable, element):
#     assert isinstance(element, (SPARQLParser.GroupGraphPattern, SPARQLParser.Path, SPARQLParser.GroupOrUnionGraphPattern, SPARQLParser.GraphGraphPattern, SPARQLParser.InlineData, SPARQLParser., SPARQLParser.SubSelect, ))
#     if isinstance(element, SPARQLParser.GroupGraphPattern):
#         return element in variable.getAncestors()
    
def getExpansion(iri):
    '''Converts iri (or PrefixedName, or IRIREF) to normal form by replacing prefixes, if any, with their value and resolving the result, if relative, to absolute form.'''
    assert isinstance(iri, (SPARQLParser.iri, SPARQLParser.PrefixedName, SPARQLParser.IRIREF)), 'Cannot expand non-iri element "{}" ({})'.format(iri, iri.__class__.__name__)        
    if isinstance(iri, SPARQLParser.iri):
        children = iri.getChildren()
        assert len(children) == 1
        oldiri = children[0]
    else:
        oldiri = iri
#     print('found oldiri:', oldiri)
    if isinstance(oldiri, SPARQLParser.PrefixedName):
        splitiri = str(oldiri).split(':', maxsplit=1)
        assert len(splitiri) == 2, splitiri
        newiristr = oldiri.getPrefixes()[splitiri[0] + ':'] + splitiri[1]
    else:
        assert isinstance(oldiri, SPARQLParser.IRIREF)
        newiristr = str(oldiri)[1:-1]
    if rfc3987.match(newiristr, 'irelative_ref'):
#         print('found relative iri:', oldiri)
        assert oldiri.getBaseiri() != None
        newiristr = rfc3987.resolve(oldiri.getBaseiri(), newiristr)
    assert rfc3987.match(newiristr), 'String "{}" cannot be expanded as absolute iri'.format(newiristr)
    return newiristr

    
    
def stringEscape(s):
    s = s.replace(r'\t', '\u0009')   
    s = s.replace(r'\n', '\u000A')   
    s = s.replace(r'\r', '\u000D')   
    s = s.replace(r'\b', '\u0008')   
    s = s.replace(r'\f', '\u000C')   
    s = s.replace(r'\"', '\u0022')   
    s = s.replace(r"\'", '\u0027')   
    s = s.replace(r'\\', '\u005C')
    return s

#
# Patterns
#

#
# Brackets and interpunction
#

LPAR = Literal('(').setName('LPAR')
SPARQLParser.addElement(LPAR)

RPAR = Literal(')').setName('RPAR')
SPARQLParser.addElement(RPAR)

LBRACK = Literal('[').setName('LBRACK')
SPARQLParser.addElement(LBRACK)

RBRACK = Literal(']').setName('RBRACK')
SPARQLParser.addElement(RBRACK)

LCURL = Literal('{').setName('LCURL')
SPARQLParser.addElement(LCURL)

RCURL = Literal('}').setName('RCURL')
SPARQLParser.addElement(RCURL)

SEMICOL = Literal(';').setName('SEMICOL')
SPARQLParser.addElement(SEMICOL)

PERIOD = Literal('.').setName('PERIOD')
SPARQLParser.addElement(PERIOD)

COMMA = Literal(',').setName('COMMA')
SPARQLParser.addElement(COMMA)

#
# Operators
#

NEGATE = Literal('!').setName('NEGATE')
SPARQLParser.addElement(NEGATE)

PLUS = Literal('+').setName('PLUS')
SPARQLParser.addElement(PLUS)

MINUS = Literal('-').setName('MINUS')
SPARQLParser.addElement(MINUS)

TIMES = Literal('*').setName('TIMES')
SPARQLParser.addElement(TIMES)

DIV = Literal('/').setName('DIV')
SPARQLParser.addElement(DIV)

EQ = Literal('=').setName('EQ')
SPARQLParser.addElement(EQ)

NE = Literal('!=').setName('NE')
SPARQLParser.addElement(NE)

GT = Literal('>').setName('GT')
SPARQLParser.addElement(GT)

LT = Literal('<').setName('LT')
SPARQLParser.addElement(LT)

GE = Literal('>=').setName('GE')
SPARQLParser.addElement(GE)

LE = Literal('<=').setName('LE')
SPARQLParser.addElement(LE)

AND = Literal('&&').setName('AND')
SPARQLParser.addElement(AND)

OR = Literal('||').setName('OR')
SPARQLParser.addElement(OR)

INVERSE = Literal('^').setName('INVERSE')
SPARQLParser.addElement(INVERSE)

#
# Keywords
#

ALL_VALUES = Literal('*').setName('ALL_VALUES')
SPARQLParser.addElement(ALL_VALUES)

TYPE = Keyword('a').setName('TYPE')
SPARQLParser.addElement(TYPE)

DISTINCT = CaselessKeyword('DISTINCT').setName('DISTINCT')
SPARQLParser.addElement(DISTINCT)

COUNT = CaselessKeyword('COUNT').setName('COUNT')
SPARQLParser.addElement(COUNT)

SUM = CaselessKeyword('SUM').setName('SUM')
SPARQLParser.addElement(SUM)

MIN = CaselessKeyword('MIN').setName('MIN')
SPARQLParser.addElement(MIN)

MAX = CaselessKeyword('MAX').setName('MAX')
SPARQLParser.addElement(MAX)

AVG = CaselessKeyword('AVG').setName('AVG')
SPARQLParser.addElement(AVG)

SAMPLE = CaselessKeyword('SAMPLE').setName('SAMPLE')
SPARQLParser.addElement(SAMPLE)

GROUP_CONCAT = CaselessKeyword('GROUP_CONCAT').setName('GROUP_CONCAT')
SPARQLParser.addElement(GROUP_CONCAT)

SEPARATOR = CaselessKeyword('SEPARATOR').setName('SEPARATOR')
SPARQLParser.addElement(SEPARATOR)

NOT = (CaselessKeyword('NOT') + NotAny(CaselessKeyword('EXISTS') | CaselessKeyword('IN'))).setName('NOT')
SPARQLParser.addElement(NOT)

EXISTS = CaselessKeyword('EXISTS').setName('EXISTS')
SPARQLParser.addElement(EXISTS)

NOT_EXISTS = Combine(CaselessKeyword('NOT') + CaselessKeyword('EXISTS'), joinString=' ', adjacent=False).setName('NOT_EXISTS')
SPARQLParser.addElement(NOT_EXISTS)

REPLACE = CaselessKeyword('REPLACE').setName('REPLACE')
SPARQLParser.addElement(REPLACE)

SUBSTR = CaselessKeyword('SUBSTR').setName('SUBSTR')
SPARQLParser.addElement(SUBSTR)

REGEX = CaselessKeyword('REGEX').setName('REGEX')
SPARQLParser.addElement(REGEX)

STR = CaselessKeyword('STR').setName('STR')
SPARQLParser.addElement(STR)

LANG = CaselessKeyword('LANG').setName('LANG')
SPARQLParser.addElement(LANG)

LANGMATCHES = CaselessKeyword('LANGMATCHES').setName('LANGMATCHES')
SPARQLParser.addElement(LANGMATCHES)

DATATYPE = CaselessKeyword('DATATYPE').setName('DATATYPE')
SPARQLParser.addElement(DATATYPE)

BOUND = CaselessKeyword('BOUND').setName('BOUND')
SPARQLParser.addElement(BOUND)

IRI = CaselessKeyword('IRI').setName('IRI')
SPARQLParser.addElement(IRI)

URI = CaselessKeyword('URI').setName('URI')
SPARQLParser.addElement(URI)

BNODE = CaselessKeyword('BNODE').setName('BNODE')
SPARQLParser.addElement(BNODE)

RAND = CaselessKeyword('RAND').setName('RAND')
SPARQLParser.addElement(RAND)

ABS = CaselessKeyword('ABS').setName('ABS')
SPARQLParser.addElement(ABS)

CEIL = CaselessKeyword('CEIL').setName('CEIL')
SPARQLParser.addElement(CEIL)

FLOOR = CaselessKeyword('FLOOR').setName('FLOOR')
SPARQLParser.addElement(FLOOR)

ROUND = CaselessKeyword('ROUND').setName('ROUND')
SPARQLParser.addElement(ROUND)

CONCAT = CaselessKeyword('CONCAT').setName('CONCAT')
SPARQLParser.addElement(CONCAT)

STRLEN = CaselessKeyword('STRLEN').setName('STRLEN')
SPARQLParser.addElement(STRLEN)

UCASE = CaselessKeyword('UCASE').setName('UCASE')
SPARQLParser.addElement(UCASE)

LCASE = CaselessKeyword('LCASE').setName('LCASE')
SPARQLParser.addElement(LCASE)

ENCODE_FOR_URI = CaselessKeyword('ENCODE_FOR_URI').setName('ENCODE_FOR_URI')
SPARQLParser.addElement(ENCODE_FOR_URI)

CONTAINS = CaselessKeyword('CONTAINS').setName('CONTAINS')
SPARQLParser.addElement(CONTAINS)

STRSTARTS = CaselessKeyword('STRSTARTS').setName('STRSTARTS')
SPARQLParser.addElement(STRSTARTS)

STRENDS = CaselessKeyword('STRENDS').setName('STRENDS')
SPARQLParser.addElement(STRENDS)

STRBEFORE = CaselessKeyword('STRBEFORE').setName('STRBEFORE')
SPARQLParser.addElement(STRBEFORE)

STRAFTER = CaselessKeyword('STRAFTER').setName('STRAFTER')
SPARQLParser.addElement(STRAFTER)

YEAR = CaselessKeyword('YEAR').setName('YEAR')
SPARQLParser.addElement(YEAR)

MONTH = CaselessKeyword('MONTH').setName('MONTH')
SPARQLParser.addElement(MONTH)

DAY = CaselessKeyword('DAY').setName('DAY')
SPARQLParser.addElement(DAY)

HOURS = CaselessKeyword('HOURS').setName('HOURS')
SPARQLParser.addElement(HOURS)

MINUTES = CaselessKeyword('MINUTES').setName('MINUTES')
SPARQLParser.addElement(MINUTES)

SECONDS = CaselessKeyword('SECONDS').setName('SECONDS')
SPARQLParser.addElement(SECONDS)

TIMEZONE = CaselessKeyword('TIMEZONE').setName('TIMEZONE')
SPARQLParser.addElement(TIMEZONE)

TZ = CaselessKeyword('TZ').setName('TZ')
SPARQLParser.addElement(TZ)

NOW = CaselessKeyword('NOW').setName('NOW')
SPARQLParser.addElement(NOW)

UUID = CaselessKeyword('UUID').setName('UUID')
SPARQLParser.addElement(UUID)

STRUUID = CaselessKeyword('STRUUID').setName('STRUUID')
SPARQLParser.addElement(STRUUID)

MD5 = CaselessKeyword('MD5').setName('MD5')
SPARQLParser.addElement(MD5)

SHA1 = CaselessKeyword('SHA1').setName('SHA1')
SPARQLParser.addElement(SHA1)

SHA256 = CaselessKeyword('SHA256').setName('SHA256')
SPARQLParser.addElement(SHA256)

SHA384 = CaselessKeyword('SHA384').setName('SHA384')
SPARQLParser.addElement(SHA384)

SHA512 = CaselessKeyword('SHA512').setName('SHA512')
SPARQLParser.addElement(SHA512)

COALESCE = CaselessKeyword('COALESCE').setName('COALESCE')
SPARQLParser.addElement(COALESCE)

IF = CaselessKeyword('IF').setName('IF')
SPARQLParser.addElement(IF)

STRLANG = CaselessKeyword('STRLANG').setName('STRLANG')
SPARQLParser.addElement(STRLANG)

STRDT = CaselessKeyword('STRDT').setName('STRDT')
SPARQLParser.addElement(STRDT)

sameTerm = CaselessKeyword('sameTerm').setName('sameTerm')
SPARQLParser.addElement(sameTerm)

isIRI = CaselessKeyword('isIRI').setName('isIRI')
SPARQLParser.addElement(isIRI)

isURI = CaselessKeyword('isURI').setName('isURI')
SPARQLParser.addElement(isURI)

isBLANK = CaselessKeyword('isBLANK').setName('isBLANK')
SPARQLParser.addElement(isBLANK)

isLITERAL = CaselessKeyword('isLITERAL').setName('isLITERAL')
SPARQLParser.addElement(isLITERAL)

isNUMERIC = CaselessKeyword('isNUMERIC').setName('isNUMERIC')
SPARQLParser.addElement(isNUMERIC)

IN = CaselessKeyword('IN').setName('IN')
SPARQLParser.addElement(IN)

NOT_IN = Combine(CaselessKeyword('NOT') + CaselessKeyword('IN'), joinString=' ', adjacent=False).setName('NOT_IN')
SPARQLParser.addElement(NOT_IN)

FILTER = CaselessKeyword('FILTER').setName('FILTER')
SPARQLParser.addElement(FILTER)

UNION = CaselessKeyword('UNION').setName('UNION')
SPARQLParser.addElement(UNION)

SUBTRACT = CaselessKeyword('MINUS').setName('SUBTRACT')
SPARQLParser.addElement(SUBTRACT)

UNDEF = CaselessKeyword('UNDEF').setName('UNDEF')
SPARQLParser.addElement(UNDEF)

VALUES = CaselessKeyword('VALUES').setName('VALUES')
SPARQLParser.addElement(VALUES)

BIND = CaselessKeyword('BIND').setName('BIND')
SPARQLParser.addElement(BIND)

AS = CaselessKeyword('AS').setName('AS')
SPARQLParser.addElement(AS)

SERVICE = CaselessKeyword('SERVICE').setName('SERVICE')
SPARQLParser.addElement(SERVICE)

SILENT = CaselessKeyword('SILENT').setName('SILENT')
SPARQLParser.addElement(SILENT)

GRAPH = CaselessKeyword('GRAPH').setName('GRAPH')
SPARQLParser.addElement(GRAPH)

OPTIONAL = CaselessKeyword('OPTIONAL').setName('OPTIONAL')
SPARQLParser.addElement(OPTIONAL)

DEFAULT = CaselessKeyword('DEFAULT').setName('DEFAULT')
SPARQLParser.addElement(DEFAULT)

NAMED = CaselessKeyword('NAMED').setName('NAMED')
SPARQLParser.addElement(NAMED)

ALL = CaselessKeyword('ALL').setName('ALL')
SPARQLParser.addElement(ALL)

USING = CaselessKeyword('USING').setName('USING')
SPARQLParser.addElement(USING)

INSERT = CaselessKeyword('INSERT').setName('INSERT')
SPARQLParser.addElement(INSERT)

DELETE = CaselessKeyword('DELETE').setName('DELETE')
SPARQLParser.addElement(DELETE)

WITH = CaselessKeyword('WITH').setName('WITH')
SPARQLParser.addElement(WITH)

WHERE = CaselessKeyword('WHERE').setName('WHERE')
SPARQLParser.addElement(WHERE)

DELETE_WHERE = Combine(CaselessKeyword('DELETE') + CaselessKeyword('WHERE'), joinString=' ', adjacent=False).setName('DELETE_WHERE')
SPARQLParser.addElement(DELETE_WHERE)

DELETE_DATA = Combine(CaselessKeyword('DELETE') + CaselessKeyword('DATA'), joinString=' ', adjacent=False).setName('DELETE_DATA')
SPARQLParser.addElement(DELETE_DATA)

INSERT_DATA = Combine(CaselessKeyword('INSERT') + CaselessKeyword('DATA'), joinString=' ', adjacent=False).setName('INSERT_DATA')
SPARQLParser.addElement(INSERT_DATA)

COPY = CaselessKeyword('COPY').setName('COPY')
SPARQLParser.addElement(COPY)

MOVE = CaselessKeyword('MOVE').setName('MOVE')
SPARQLParser.addElement(MOVE)

ADD = CaselessKeyword('ADD').setName('ADD')
SPARQLParser.addElement(ADD)

CREATE = CaselessKeyword('CREATE').setName('CREATE')
SPARQLParser.addElement(CREATE)

DROP = CaselessKeyword('DROP').setName('DROP')
SPARQLParser.addElement(DROP)

CLEAR = CaselessKeyword('CLEAR').setName('CLEAR')
SPARQLParser.addElement(CLEAR)

LOAD = CaselessKeyword('LOAD').setName('LOAD')
SPARQLParser.addElement(LOAD)

TO = CaselessKeyword('TO').setName('TO')
SPARQLParser.addElement(TO)

INTO = CaselessKeyword('INTO').setName('INTO')
SPARQLParser.addElement(INTO)

OFFSET = CaselessKeyword('OFFSET').setName('OFFSET')
SPARQLParser.addElement(OFFSET)

LIMIT = CaselessKeyword('LIMIT').setName('LIMIT')
SPARQLParser.addElement(LIMIT)

ASC = CaselessKeyword('ASC').setName('ASC')
SPARQLParser.addElement(ASC)

DESC = CaselessKeyword('DESC').setName('DESC')
SPARQLParser.addElement(DESC)

ORDER_BY = Combine(CaselessKeyword('ORDER') + CaselessKeyword('BY'), joinString=' ', adjacent=False).setName('ORDER_BY')
SPARQLParser.addElement(ORDER_BY)

HAVING = CaselessKeyword('HAVING').setName('HAVING')
SPARQLParser.addElement(HAVING)

GROUP_BY = Combine(CaselessKeyword('GROUP') + CaselessKeyword('BY'), joinString=' ', adjacent=False).setName('GROUP_BY')
SPARQLParser.addElement(GROUP_BY)

FROM = CaselessKeyword('FROM').setName('FROM')
SPARQLParser.addElement(FROM)

ASK = CaselessKeyword('ASK').setName('ASK')
SPARQLParser.addElement(ASK)

DESCRIBE = CaselessKeyword('DESCRIBE').setName('DESCRIBE')
SPARQLParser.addElement(DESCRIBE)

CONSTRUCT = CaselessKeyword('CONSTRUCT').setName('CONSTRUCT')
SPARQLParser.addElement(CONSTRUCT)

SELECT = CaselessKeyword('SELECT').setName('SELECT')
SPARQLParser.addElement(SELECT)

REDUCED = CaselessKeyword('REDUCED').setName('REDUCED')
SPARQLParser.addElement(REDUCED)

PREFIX = CaselessKeyword('PREFIX').setName('PREFIX')
SPARQLParser.addElement(PREFIX)

BASE = CaselessKeyword('BASE').setName('BASE')
SPARQLParser.addElement(BASE)

# 
# Parsers and classes for terminals
#

# [173]   PN_LOCAL_ESC      ::=   '\' ( '_' | '~' | '.' | '-' | '!' | '$' | '&' | "'" | '(' | ')' | '*' | '+' | ',' | ';' | '=' | '/' | '?' | '#' | '@' | '%' ) 
PN_LOCAL_ESC_e = r'\\[_~.\-!$&\'()*+,;=/?#@%]'
PN_LOCAL_ESC = Regex(PN_LOCAL_ESC_e).setName('PN_LOCAL_ESC')
SPARQLParser.addElement(PN_LOCAL_ESC)


# [172]   HEX       ::=   [0-9] | [A-F] | [a-f] 
HEX_e = r'[0-9A-Fa-f]'
HEX = Regex(HEX_e).setName('HEX')
SPARQLParser.addElement(HEX)

# [171]   PERCENT   ::=   '%' HEX HEX
PERCENT_e = r'%({})({})'.format( HEX_e, HEX_e)
PERCENT = Regex(PERCENT_e).setName('PERCENT')
SPARQLParser.addElement(PERCENT)

# [170]   PLX       ::=   PERCENT | PN_LOCAL_ESC 
PLX_e = r'({})|({})'.format( PERCENT_e, PN_LOCAL_ESC_e)
PLX = Regex(PLX_e).setName('PLX')
SPARQLParser.addElement(PLX)

# [164]   PN_CHARS_BASE     ::=   [A-Z] | [a-z] | [#x00C0-#x00D6] | [#x00D8-#x00F6] | [#x00F8-#x02FF] | [#x0370-#x037D] | [#x037F-#x1FFF] | [#x200C-#x200D] | [#x2070-#x218F] | [#x2C00-#x2FEF] | [#x3001-#xD7FF] | [#xF900-#xFDCF] | [#xFDF0-#xFFFD] | [#x10000-#xEFFFF] 
PN_CHARS_BASE_e = r'[A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\U00010000-\U000EFFFF]'
PN_CHARS_BASE = Regex(PN_CHARS_BASE_e).setName('PN_CHARS_BASE')
SPARQLParser.addElement(PN_CHARS_BASE)

# [165]   PN_CHARS_U        ::=   PN_CHARS_BASE | '_' 
PN_CHARS_U_e = r'({})|({})'.format( PN_CHARS_BASE_e, r'_')
PN_CHARS_U = Regex(PN_CHARS_U_e).setName('PN_CHARS_U')
SPARQLParser.addElement(PN_CHARS_U)

# [167]   PN_CHARS          ::=   PN_CHARS_U | '-' | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] 
PN_CHARS_e = r'({})|({})|({})|({})|({})|({})'.format( PN_CHARS_U_e, r'\-', r'[0-9]',  r'\u00B7', r'[\u0300-\u036F]', r'[\u203F-\u2040]')
PN_CHARS = Regex(PN_CHARS_e).setName('PN_CHARS')
SPARQLParser.addElement(PN_CHARS)

# [169]   PN_LOCAL          ::=   (PN_CHARS_U | ':' | [0-9] | PLX ) ((PN_CHARS | '.' | ':' | PLX)* (PN_CHARS | ':' | PLX) )?
PN_LOCAL_e = r'(({})|({})|({})|({}))((({})|({})|({})|({}))*(({})|({})|({})))?'.format( PN_CHARS_U_e, r':', r'[0-9]', PLX_e, PN_CHARS_e, r'\.', r':', PLX_e, PN_CHARS_e, r':', PLX_e) 
PN_LOCAL = Regex(PN_LOCAL_e).setName('PN_LOCAL')
SPARQLParser.addElement(PN_LOCAL)
            
# [168]   PN_PREFIX         ::=   PN_CHARS_BASE ((PN_CHARS|'.')* PN_CHARS)?
PN_PREFIX_e = r'({})((({})|({}))*({}))?'.format( PN_CHARS_BASE_e, PN_CHARS_e, r'\.', PN_CHARS_e)
PN_PREFIX = Regex(PN_PREFIX_e).setName('PN_PREFIX')
SPARQLParser.addElement(PN_PREFIX)

# [166]   VARNAME   ::=   ( PN_CHARS_U | [0-9] ) ( PN_CHARS_U | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] )* 
VARNAME_e = r'(({})|({}))(({})|({})|({})|({})|({}))*'.format( PN_CHARS_U_e, r'[0-9]', PN_CHARS_U_e, r'[0-9]', r'\u00B7', r'[\u0030-036F]', r'[\u0203-\u2040]')
VARNAME = Regex(VARNAME_e).setName('VARNAME')
SPARQLParser.addElement(VARNAME)

# [163]   ANON      ::=   '[' WS* ']' 
ANON = Combine(Literal('[') + Literal(']'), joinString=' ', adjacent=False).setName('ANON')
SPARQLParser.addElement(ANON)

# [162]   WS        ::=   #x20 | #x9 | #xD | #xA 
# WS is not used
# In the SPARQL EBNF this production is used for defining NIL and ANON, but in this pyparsing implementation those are implemented differently

# [161]   NIL       ::=   '(' WS* ')' 
NIL = Combine(Literal('(') + Literal(')'), joinString=' ', adjacent=False).setName('NIL')
SPARQLParser.addElement(NIL)

# [160]   ECHAR     ::=   '\' [tbnrf\"']
ECHAR_e = r'\\[tbnrf\\"\']'
ECHAR = Regex(ECHAR_e).setName('ECHAR')
SPARQLParser.addElement(ECHAR)
 
# [159]   STRING_LITERAL_LONG2      ::=   '"""' ( ( '"' | '""' )? ( [^"\] | ECHAR ) )* '"""'  
STRING_LITERAL_LONG2_e = r'"""((""|")?(({})|({})))*"""'.format(r'[^"\\]', ECHAR_e)
STRING_LITERAL_LONG2 = Regex(STRING_LITERAL_LONG2_e).parseWithTabs().setName('STRING_LITERAL_LONG2')
SPARQLParser.addElement(STRING_LITERAL_LONG2)

# [158]   STRING_LITERAL_LONG1      ::=   "'''" ( ( "'" | "''" )? ( [^'\] | ECHAR ) )* "'''" 
STRING_LITERAL_LONG1_e = r"'''(('|'')?(({})|({})))*'''".format(r"[^'\\]", ECHAR_e)
STRING_LITERAL_LONG1 = Regex(STRING_LITERAL_LONG1_e).parseWithTabs().setName('STRING_LITERAL_LONG1')
SPARQLParser.addElement(STRING_LITERAL_LONG1)

# [157]   STRING_LITERAL2   ::=   '"' ( ([^#x22#x5C#xA#xD]) | ECHAR )* '"' 
STRING_LITERAL2_e = r'"(({})|({}))*"'.format(ECHAR_e, r'[^\u0022\u005C\u000A\u000D]')
STRING_LITERAL2 = Regex(STRING_LITERAL2_e).parseWithTabs().setName('STRING_LITERAL2')
SPARQLParser.addElement(STRING_LITERAL2)
                           
# [156]   STRING_LITERAL1   ::=   "'" ( ([^#x27#x5C#xA#xD]) | ECHAR )* "'" 
STRING_LITERAL1_e = r"'(({})|({}))*'".format(ECHAR_e, r'[^\u0027\u005C\u000A\u000D]')
STRING_LITERAL1 = Regex(STRING_LITERAL1_e).parseWithTabs().setName('STRING_LITERAL1')
SPARQLParser.addElement(STRING_LITERAL1)
                            
# [155]   EXPONENT          ::=   [eE] [+-]? [0-9]+ 
EXPONENT_e = r'[eE][+-][0-9]+'
EXPONENT = Regex(EXPONENT_e).setName('EXPONENT')
SPARQLParser.addElement(EXPONENT)

# [148]   DOUBLE    ::=   [0-9]+ '.' [0-9]* EXPONENT | '.' ([0-9])+ EXPONENT | ([0-9])+ EXPONENT 
DOUBLE_e = r'([0-9]+\.[0-9]*({}))|(\.[0-9]+({}))|([0-9]+({}))'.format(EXPONENT_e, EXPONENT_e, EXPONENT_e)
DOUBLE = Regex(DOUBLE_e).setName('DOUBLE')
SPARQLParser.addElement(DOUBLE)

# [154]   DOUBLE_NEGATIVE   ::=   '-' DOUBLE 
DOUBLE_NEGATIVE_e = r'\-({})'.format(DOUBLE_e)
DOUBLE_NEGATIVE = Regex(DOUBLE_NEGATIVE_e).setName('DOUBLE_NEGATIVE')
SPARQLParser.addElement(DOUBLE_NEGATIVE)

# [151]   DOUBLE_POSITIVE   ::=   '+' DOUBLE 
DOUBLE_POSITIVE_e = r'\+({})'.format(DOUBLE_e)
DOUBLE_POSITIVE = Regex(DOUBLE_POSITIVE_e).setName('DOUBLE_POSITIVE')
SPARQLParser.addElement(DOUBLE_POSITIVE)

# [147]   DECIMAL   ::=   [0-9]* '.' [0-9]+ 
DECIMAL_e = r'[0-9]*\.[0-9]+'
DECIMAL = Regex(DECIMAL_e).setName('DECIMAL')
SPARQLParser.addElement(DECIMAL)

# [153]   DECIMAL_NEGATIVE          ::=   '-' DECIMAL 
DECIMAL_NEGATIVE_e = r'\-({})'.format(DECIMAL_e)
DECIMAL_NEGATIVE = Regex(DECIMAL_NEGATIVE_e).setName('DECIMAL_NEGATIVE')
SPARQLParser.addElement(DECIMAL_NEGATIVE)

# [150]   DECIMAL_POSITIVE          ::=   '+' DECIMAL 
DECIMAL_POSITIVE_e = r'\+({})'.format(DECIMAL_e)
DECIMAL_POSITIVE = Regex(DECIMAL_POSITIVE_e).setName('DECIMAL_POSITIVE')
SPARQLParser.addElement(DECIMAL_POSITIVE)

# [146]   INTEGER   ::=   [0-9]+ 
INTEGER_e = r'[0-9]+'
INTEGER = Regex(INTEGER_e).setName('INTEGER')
SPARQLParser.addElement(INTEGER)

# [152]   INTEGER_NEGATIVE          ::=   '-' INTEGER
INTEGER_NEGATIVE_e = r'\-({})'.format(INTEGER_e)
INTEGER_NEGATIVE = Regex(INTEGER_NEGATIVE_e).setName('INTEGER_NEGATIVE')
SPARQLParser.addElement(INTEGER_NEGATIVE)

# [149]   INTEGER_POSITIVE          ::=   '+' INTEGER 
INTEGER_POSITIVE_e = r'\+({})'.format(INTEGER_e)
INTEGER_POSITIVE = Regex(INTEGER_POSITIVE_e).setName('INTEGER_POSITIVE')
SPARQLParser.addElement(INTEGER_POSITIVE)

# [145]   LANGTAG   ::=   '@' [a-zA-Z]+ ('-' [a-zA-Z0-9]+)* 
LANGTAG_e = r'@[a-zA-Z]+(\-[a-zA-Z0-9]+)*'
LANGTAG = Regex(LANGTAG_e).setName('LANGTAG')
SPARQLParser.addElement(LANGTAG)

# [144]   VAR2      ::=   '$' VARNAME 
VAR2_e = r'\$({})'.format(VARNAME_e)
VAR2 = Regex(VAR2_e).setName('VAR2')
SPARQLParser.addElement(VAR2)

# [143]   VAR1      ::=   '?' VARNAME 
VAR1_e = r'\?({})'.format(VARNAME_e)
VAR1 = Regex(VAR1_e).setName('VAR1')
SPARQLParser.addElement(VAR1)

# [142]   BLANK_NODE_LABEL          ::=   '_:' ( PN_CHARS_U | [0-9] ) ((PN_CHARS|'.')* PN_CHARS)?
BLANK_NODE_LABEL_e = r'_:(({})|[0-9])((({})|\.)*({}))?'.format(PN_CHARS_U_e, PN_CHARS_e, PN_CHARS_e)
BLANK_NODE_LABEL = Regex(BLANK_NODE_LABEL_e).setName('BLANK_NODE_LABEL')
SPARQLParser.addElement(BLANK_NODE_LABEL)

# [140]   PNAME_NS          ::=   PN_PREFIX? ':'
PNAME_NS_e = r'({})?:'.format(PN_PREFIX_e)
PNAME_NS = Regex(PNAME_NS_e).setName('PNAME_NS')
SPARQLParser.addElement(PNAME_NS)

# [141]   PNAME_LN          ::=   PNAME_NS PN_LOCAL 
PNAME_LN_e = r'({})({})'.format(PNAME_NS_e, PN_LOCAL_e)
PNAME_LN = Regex(PNAME_LN_e).setName('PNAME_LN')
SPARQLParser.addElement(PNAME_LN)

# [139]   IRIREF    ::=   '<' ([^<>"{}|^`\]-[#x00-#x20])* '>' 
IRIREF_e = r'<[^<>"{}|^`\\\\\u0000-\u0020]*>'
IRIREF = Regex(IRIREF_e).setName('IRIREF')
SPARQLParser.addElement(IRIREF)

#
# Parsers and classes for non-terminals
#

# [138]   BlankNode         ::=   BLANK_NODE_LABEL | ANON 
BlankNode = Group(BLANK_NODE_LABEL | ANON).setName('BlankNode')
SPARQLParser.addElement(BlankNode)

# [137]   PrefixedName      ::=   PNAME_LN | PNAME_NS 
PrefixedName = Group(PNAME_LN | PNAME_NS).setName('PrefixedName')
SPARQLParser.addElement(PrefixedName)

# [136]   iri       ::=   IRIREF | PrefixedName 
iri = Group(IRIREF | PrefixedName).setName('iri')
SPARQLParser.addElement(iri)

# [135]   String    ::=   STRING_LITERAL1 | STRING_LITERAL2 | STRING_LITERAL_LONG1 | STRING_LITERAL_LONG2 
String = Group(STRING_LITERAL_LONG1 | STRING_LITERAL_LONG2 | STRING_LITERAL1 | STRING_LITERAL2).setName('String')
SPARQLParser.addElement(String)
 
# [134]   BooleanLiteral    ::=   'true' | 'false' 
BooleanLiteral = Group(Literal('true') | Literal('false')).setName('BooleanLiteral')
SPARQLParser.addElement(BooleanLiteral)
 
# [133]   NumericLiteralNegative    ::=   INTEGER_NEGATIVE | DECIMAL_NEGATIVE | DOUBLE_NEGATIVE 
NumericLiteralNegative = Group(DOUBLE_NEGATIVE | DECIMAL_NEGATIVE | INTEGER_NEGATIVE).setName('NumericLiteralNegative')
SPARQLParser.addElement(NumericLiteralNegative)
 
# [132]   NumericLiteralPositive    ::=   INTEGER_POSITIVE | DECIMAL_POSITIVE | DOUBLE_POSITIVE 
NumericLiteralPositive = Group(DOUBLE_POSITIVE | DECIMAL_POSITIVE | INTEGER_POSITIVE).setName('NumericLiteralPositive')
SPARQLParser.addElement(NumericLiteralPositive)
 
# [131]   NumericLiteralUnsigned    ::=   INTEGER | DECIMAL | DOUBLE 
NumericLiteralUnsigned = Group(DOUBLE | DECIMAL | INTEGER).setName('NumericLiteralUnsigned')
SPARQLParser.addElement(NumericLiteralUnsigned)

# # [130]   NumericLiteral    ::=   NumericLiteralUnsigned | NumericLiteralPositive | NumericLiteralNegative 
NumericLiteral = Group(NumericLiteralUnsigned | NumericLiteralPositive | NumericLiteralNegative).setName('NumericLiteral')
SPARQLParser.addElement(NumericLiteral)

# [129]   RDFLiteral        ::=   String ( LANGTAG | ( '^^' iri ) )? 
RDFLiteral = Group(String('lexical_form') + Optional(Group ((LANGTAG('langtag') | ('^^' + iri('datatype_uri')))))).setName('RDFLiteral')
SPARQLParser.addElement(RDFLiteral)

Expression = Forward().setName('Expression')
SPARQLParser.addElement(Expression)

# [71]    ArgList   ::=   NIL | '(' 'DISTINCT'? Expression ( ',' Expression )* ')' 
ArgList = Group((NIL('nil')) | (LPAR + Optional(DISTINCT)('distinct') + separatedList(Expression)('argument') + RPAR)).setName('ArgList')
SPARQLParser.addElement(ArgList)


# [128]   iriOrFunction     ::=   iri ArgList? 
iriOrFunction = Group(iri('iri') + Optional(ArgList)('argList')).setName('iriOrFunction')
SPARQLParser.addElement(iriOrFunction)

# [127]   Aggregate         ::=     'COUNT' '(' 'DISTINCT'? ( '*' | Expression ) ')' 
#             | 'SUM' '(' 'DISTINCT'? Expression ')' 
#             | 'MIN' '(' 'DISTINCT'? Expression ')' 
#             | 'MAX' '(' 'DISTINCT'? Expression ')' 
#             | 'AVG' '(' 'DISTINCT'? Expression ')' 
#             | 'SAMPLE' '(' 'DISTINCT'? Expression ')' 
#             | 'GROUP_CONCAT' '(' 'DISTINCT'? Expression ( ';' 'SEPARATOR' '=' String )? ')' 
Aggregate = Group((COUNT('count') + LPAR + Optional(DISTINCT('distinct')) + ( ALL_VALUES('all') | Expression('expression') ) + RPAR ) | 
            ( SUM('sum') + LPAR + Optional(DISTINCT('distinct')) + ( ALL_VALUES('all') | Expression('expression') ) + RPAR ) | 
            ( MIN('min') + LPAR + Optional(DISTINCT('distinct')) + ( ALL_VALUES('all') | Expression('expression') ) + RPAR ) | 
            ( MAX('max') + LPAR + Optional(DISTINCT('distinct')) + ( ALL_VALUES('all') | Expression('expression') ) + RPAR ) | 
            ( AVG('avg') + LPAR + Optional(DISTINCT('distinct')) + ( ALL_VALUES('all') | Expression('expression') ) + RPAR ) | 
            ( SAMPLE('sample') + LPAR + Optional(DISTINCT('distinct')) + ( ALL_VALUES('all') | Expression('expression') ) + RPAR ) | 
            ( GROUP_CONCAT('group_concat') + LPAR + Optional(DISTINCT('distinct')) + Expression('expression') + Optional( SEMICOL + SEPARATOR + '=' + String('separator') ) + RPAR)).setName('Aggregate')
SPARQLParser.addElement(Aggregate)

GroupGraphPattern = Forward().setName('GroupGraphPattern')
SPARQLParser.addElement(GroupGraphPattern)
 
# [126]   NotExistsFunc     ::=   'NOT' 'EXISTS' GroupGraphPattern 
NotExistsFunc = Group(NOT_EXISTS + GroupGraphPattern('groupgraph')).setName('NotExistsFunc')
SPARQLParser.addElement(NotExistsFunc)
 
# [125]   ExistsFunc        ::=   'EXISTS' GroupGraphPattern 
ExistsFunc = Group(EXISTS + GroupGraphPattern('groupgraph')).setName('ExistsFunc')
SPARQLParser.addElement(ExistsFunc)
 
# [124]   StrReplaceExpression      ::=   'REPLACE' '(' Expression ',' Expression ',' Expression ( ',' Expression )? ')' 
StrReplaceExpression = Group(REPLACE + LPAR + Expression('arg') + COMMA + Expression('pattern') + COMMA + Expression('replacement') + Optional(COMMA + Expression('flags')) + RPAR).setName('StrReplaceExpression')
SPARQLParser.addElement(StrReplaceExpression)
 
# [123]   SubstringExpression       ::=   'SUBSTR' '(' Expression ',' Expression ( ',' Expression )? ')' 
SubstringExpression = Group(SUBSTR + LPAR + Expression('source') + COMMA + Expression('startloc') + Optional(COMMA + Expression('length')) + RPAR).setName('SubstringExpression')
SPARQLParser.addElement(SubstringExpression)
 
# [122]   RegexExpression   ::=   'REGEX' '(' Expression ',' Expression ( ',' Expression )? ')' 
RegexExpression = Group(REGEX + LPAR + Expression('text') + COMMA + Expression('pattern') + Optional(COMMA + Expression('flags')) + RPAR).setName('RegexExpression')
SPARQLParser.addElement(RegexExpression)

# [108]   Var       ::=   VAR1 | VAR2 
Var = Group(VAR1 | VAR2).setName('Var')
SPARQLParser.addElement(Var)

ExpressionList = Forward().setName('ExpressionList')
SPARQLParser.addElement(ExpressionList)


# [121]   BuiltInCall       ::=     Aggregate 
#             | 'STR' '(' Expression ')' 
#             | 'LANG' '(' Expression ')' 
#             | 'LANGMATCHES' '(' Expression ',' Expression ')' 
#             | 'DATATYPE' '(' Expression ')' 
#             | 'BOUND' '(' Var ')' 
#             | 'IRI' '(' Expression ')' 
#             | 'URI' '(' Expression ')' 
#             | 'BNODE' ( '(' Expression ')' | NIL ) 
#             | 'RAND' NIL 
#             | 'ABS' '(' Expression ')' 
#             | 'CEIL' '(' Expression ')' 
#             | 'FLOOR' '(' Expression ')' 
#             | 'ROUND' '(' Expression ')' 
#             | 'CONCAT' ExpressionList 
#             | SubstringExpression 
#             | 'STRLEN' '(' Expression ')' 
#             | StrReplaceExpression 
#             | 'UCASE' '(' Expression ')' 
#             | 'LCASE' '(' Expression ')' 
#             | 'ENCODE_FOR_URI' '(' Expression ')' 
#             | 'CONTAINS' '(' Expression ',' Expression ')' 
#             | 'STRSTARTS' '(' Expression ',' Expression ')' 
#             | 'STRENDS' '(' Expression ',' Expression ')' 
#             | 'STRBEFORE' '(' Expression ',' Expression ')' 
#             | 'STRAFTER' '(' Expression ',' Expression ')' 
#             | 'YEAR' '(' Expression ')' 
#             | 'MONTH' '(' Expression ')' 
#             | 'DAY' '(' Expression ')' 
#             | 'HOURS' '(' Expression ')' 
#             | 'MINUTES' '(' Expression ')' 
#             | 'SECONDS' '(' Expression ')' 
#             | 'TIMEZONE' '(' Expression ')' 
#             | 'TZ' '(' Expression ')' 
#             | 'NOW' NIL 
#             | 'UUID' NIL 
#             | 'STRUUID' NIL 
#             | 'MD5' '(' Expression ')' 
#             | 'SHA1' '(' Expression ')' 
#             | 'SHA256' '(' Expression ')' 
#             | 'SHA384' '(' Expression ')' 
#             | 'SHA512' '(' Expression ')' 
#             | 'COALESCE' ExpressionList 
#             | 'IF' '(' Expression ',' Expression ',' Expression ')' 
#             | 'STRLANG' '(' Expression ',' Expression ')' 
#             | 'STRDT' '(' Expression ',' Expression ')' 
#             | 'sameTerm' '(' Expression ',' Expression ')' 
#             | 'isIRI' '(' Expression ')' 
#             | 'isURI' '(' Expression ')' 
#             | 'isBLANK' '(' Expression ')' 
#             | 'isLITERAL' '(' Expression ')' 
#             | 'isNUMERIC' '(' Expression ')' 
#             | RegexExpression 
#             | ExistsFunc 
#             | NotExistsFunc 
BuiltInCall = Group(Aggregate | 
                STR + LPAR + Expression('expression') + RPAR    | 
                LANG + LPAR + Expression('expression') + RPAR    | 
                LANGMATCHES + LPAR + Expression('language-tag') + COMMA + Expression('language-range') + RPAR    | 
                DATATYPE + LPAR + Expression('expression') + RPAR    | 
                BOUND + LPAR + Var('var') + RPAR    | 
                IRI + LPAR + Expression('expression') + RPAR    | 
                URI + LPAR + Expression('expression') + RPAR    | 
                BNODE + (LPAR + Expression('expression') + RPAR | NIL)    | 
                RAND + NIL    | 
                ABS + LPAR + Expression('expression') + RPAR    | 
                CEIL + LPAR + Expression('expression') + RPAR    | 
                FLOOR + LPAR + Expression('expression') + RPAR    | 
                ROUND + LPAR + Expression('expression') + RPAR    | 
                CONCAT + ExpressionList('expressionList')    | 
                SubstringExpression   | 
                STRLEN + LPAR + Expression('expression') + RPAR    | 
                StrReplaceExpression  | 
                UCASE + LPAR + Expression('expression') + RPAR    | 
                LCASE + LPAR + Expression('expression') + RPAR    | 
                ENCODE_FOR_URI + LPAR + Expression('expression') + RPAR    | 
                CONTAINS + LPAR + Expression('arg1') + COMMA + Expression('arg2') + RPAR    | 
                STRSTARTS + LPAR + Expression('arg1') + COMMA + Expression('arg2') + RPAR    | 
                STRENDS + LPAR + Expression('arg1') + COMMA + Expression('arg2') + RPAR    | 
                STRBEFORE + LPAR + Expression('arg1') + COMMA + Expression('arg2') + RPAR    | 
                STRAFTER + LPAR + Expression('arg1') + COMMA + Expression('arg2') + RPAR    | 
                YEAR + LPAR + Expression('expression') + RPAR    | 
                MONTH + LPAR + Expression('expression') + RPAR    | 
                DAY + LPAR + Expression('expression') + RPAR    | 
                HOURS + LPAR + Expression('expression') + RPAR    | 
                MINUTES + LPAR + Expression('expression') + RPAR    | 
                SECONDS + LPAR + Expression('expression') + RPAR    | 
                TIMEZONE + LPAR + Expression('expression') + RPAR    | 
                TZ + LPAR + Expression('expression') + RPAR    | 
                NOW + NIL    | 
                UUID + NIL    | 
                STRUUID + NIL    | 
                MD5 + LPAR + Expression('expression') + RPAR    | 
                SHA1 + LPAR + Expression('expression') + RPAR    | 
                SHA256 + LPAR + Expression('expression') + RPAR    | 
                SHA384 + LPAR + Expression('expression') + RPAR    | 
                SHA512 + LPAR + Expression('expression') + RPAR    | 
                COALESCE + ExpressionList('expressionList')    | 
                IF + LPAR + Expression('expression1') + COMMA + Expression('expression2') + COMMA + Expression('expression3') + RPAR    | 
                STRLANG + LPAR + Expression('lexicalForm') + COMMA + Expression('langTag') + RPAR    | 
                STRDT + LPAR + Expression('lexicalForm') + COMMA + Expression('datatypeIRI') + RPAR    | 
                sameTerm + LPAR + Expression('term1') + COMMA + Expression('term2') + RPAR    | 
                isIRI + LPAR + Expression('expression') + RPAR    | 
                isURI + LPAR + Expression('expression') + RPAR    | 
                isBLANK + LPAR + Expression('expression') + RPAR    | 
                isLITERAL + LPAR + Expression('expression') + RPAR    | 
                isNUMERIC + LPAR + Expression('expression') + RPAR    | 
                RegexExpression | 
                ExistsFunc | 
                NotExistsFunc ).setName('BuiltInCall')
SPARQLParser.addElement(BuiltInCall)

# [120]   BrackettedExpression      ::=   '(' Expression ')' 
BracketedExpression = Group(LPAR + Expression('expression') + RPAR).setName('BracketedExpression')
SPARQLParser.addElement(BracketedExpression)

# [119]   PrimaryExpression         ::=   BrackettedExpression | BuiltInCall | iriOrFunction | RDFLiteral | NumericLiteral | BooleanLiteral | Var 
PrimaryExpression = Group(BracketedExpression | BuiltInCall | iriOrFunction('iriOrFunction') | RDFLiteral | NumericLiteral | BooleanLiteral | Var).setName('PrimaryExpression')
SPARQLParser.addElement(PrimaryExpression)

# [118]   UnaryExpression   ::=     '!' PrimaryExpression 
#             | '+' PrimaryExpression 
#             | '-' PrimaryExpression 
#             | PrimaryExpression 
UnaryExpression = Group(NEGATE + PrimaryExpression | PLUS + PrimaryExpression | MINUS + PrimaryExpression | PrimaryExpression).setName('UnaryExpression')
SPARQLParser.addElement(UnaryExpression)

# [117]   MultiplicativeExpression          ::=   UnaryExpression ( '*' UnaryExpression | '/' UnaryExpression )* 
MultiplicativeExpression = Group(UnaryExpression + ZeroOrMore( TIMES + UnaryExpression | DIV + UnaryExpression )).setName('MultiplicativeExpression')
SPARQLParser.addElement(MultiplicativeExpression)

# [116]   AdditiveExpression        ::=   MultiplicativeExpression ( '+' MultiplicativeExpression | '-' MultiplicativeExpression | ( NumericLiteralPositive | NumericLiteralNegative ) ( ( '*' UnaryExpression ) | ( '/' UnaryExpression ) )* )* 
AdditiveExpression = Group(MultiplicativeExpression + ZeroOrMore (PLUS + MultiplicativeExpression | MINUS  + MultiplicativeExpression | (NumericLiteralPositive | NumericLiteralNegative) + ZeroOrMore (TIMES + UnaryExpression | DIV + UnaryExpression))).setName('AdditiveExpression')
SPARQLParser.addElement(AdditiveExpression)

# [115]   NumericExpression         ::=   AdditiveExpression 
NumericExpression = Group(AdditiveExpression + Empty()).setName('NumericExpression')
SPARQLParser.addElement(NumericExpression)

# [114]   RelationalExpression      ::=   NumericExpression ( '=' NumericExpression | '!=' NumericExpression | '<' NumericExpression | '>' NumericExpression | '<=' NumericExpression | '>=' NumericExpression | 'IN' ExpressionList | 'NOT' 'IN' ExpressionList )? 
RelationalExpression = Group(NumericExpression + Optional( EQ + NumericExpression | 
                                                         NE + NumericExpression | 
                                                         LT + NumericExpression | 
                                                         GT + NumericExpression | 
                                                         LE + NumericExpression | 
                                                         GE + NumericExpression | 
                                                         IN + ExpressionList | 
                                                         NOT_IN + ExpressionList) ).setName('RelationalExpression')
SPARQLParser.addElement(RelationalExpression)

# [113]   ValueLogical      ::=   RelationalExpression 
ValueLogical = Group(RelationalExpression + Empty()).setName('ValueLogical')
SPARQLParser.addElement(ValueLogical)

# [112]   ConditionalAndExpression          ::=   ValueLogical ( '&&' ValueLogical )* 
ConditionalAndExpression = Group(ValueLogical + ZeroOrMore(AND + ValueLogical)).setName('ConditionalAndExpression')
SPARQLParser.addElement(ConditionalAndExpression)

# [111]   ConditionalOrExpression   ::=   ConditionalAndExpression ( '||' ConditionalAndExpression )* 
ConditionalOrExpression = Group(ConditionalAndExpression + ZeroOrMore(OR + ConditionalAndExpression)).setName('ConditionalOrExpression')
SPARQLParser.addElement(ConditionalOrExpression)

# [110]   Expression        ::=   ConditionalOrExpression 
Expression << Group(ConditionalOrExpression + Empty())

# [109]   GraphTerm         ::=   iri | RDFLiteral | NumericLiteral | BooleanLiteral | BlankNode | NIL 
GraphTerm =   Group(iri | 
                RDFLiteral | 
                NumericLiteral | 
                BooleanLiteral | 
                BlankNode | 
                NIL ).setName('GraphTerm')
SPARQLParser.addElement(GraphTerm)
                
# [107]   VarOrIri          ::=   Var | iri 
VarOrIri = Group(Var | iri).setName('VarOrIri')
SPARQLParser.addElement(VarOrIri)

# [106]   VarOrTerm         ::=   Var | GraphTerm 
VarOrTerm = Group(Var | GraphTerm).setName('VarOrTerm')
SPARQLParser.addElement(VarOrTerm)

TriplesNodePath = Forward().setName('TriplesNodePath')
SPARQLParser.addElement(TriplesNodePath)

# [105]   GraphNodePath     ::=   VarOrTerm | TriplesNodePath 
GraphNodePath = Group(VarOrTerm | TriplesNodePath ).setName('GraphNodePath')
SPARQLParser.addElement(GraphNodePath)

TriplesNode = Forward().setName('TriplesNode')
SPARQLParser.addElement(TriplesNode)

# [104]   GraphNode         ::=   VarOrTerm | TriplesNode 
GraphNode = Group(VarOrTerm | TriplesNode).setName('GraphNode')
SPARQLParser.addElement(GraphNode)

# [103]   CollectionPath    ::=   '(' GraphNodePath+ ')' 
CollectionPath = Group(LPAR + OneOrMore(GraphNodePath) + RPAR).setName('CollectionPath')
SPARQLParser.addElement(CollectionPath)

# [102]   Collection        ::=   '(' GraphNode+ ')' 
Collection = Group(LPAR + OneOrMore(GraphNode) + RPAR).setName('Collection')
SPARQLParser.addElement(Collection)

PropertyListPathNotEmpty = Forward().setName('PropertyListPathNotEmpty')
SPARQLParser.addElement(PropertyListPathNotEmpty)

# [101]   BlankNodePropertyListPath         ::=   '[' PropertyListPathNotEmpty ']'
BlankNodePropertyListPath = Group(LBRACK + PropertyListPathNotEmpty + RBRACK ).setName('BlankNodePropertyListPath')
SPARQLParser.addElement(BlankNodePropertyListPath)

# [100]   TriplesNodePath   ::=   CollectionPath | BlankNodePropertyListPath 
TriplesNodePath << Group(CollectionPath | BlankNodePropertyListPath)

PropertyListNotEmpty = Forward().setName('PropertyListNotEmpty')
SPARQLParser.addElement(PropertyListNotEmpty)

# [99]    BlankNodePropertyList     ::=   '[' PropertyListNotEmpty ']' 
BlankNodePropertyList = Group(LBRACK + PropertyListNotEmpty + RBRACK ).setName('BlankNodePropertyList')
SPARQLParser.addElement(BlankNodePropertyList)

# [98]    TriplesNode       ::=   Collection | BlankNodePropertyList 
TriplesNode << Group(Collection | BlankNodePropertyList)

# [97]    Integer   ::=   INTEGER 
Integer = Group(INTEGER + Empty()).setName('Integer')
SPARQLParser.addElement(Integer)

# [96]    PathOneInPropertySet      ::=   iri | 'a' | '^' ( iri | 'a' ) 
PathOneInPropertySet = Group(iri | TYPE | (INVERSE  + ( iri | TYPE ))).setName('PathOneInPropertySet')
SPARQLParser.addElement(PathOneInPropertySet)

# [95]    PathNegatedPropertySet    ::=   PathOneInPropertySet | '(' ( PathOneInPropertySet ( '|' PathOneInPropertySet )* )? ')' 
PathNegatedPropertySet = Group(PathOneInPropertySet | (LPAR + Group(Optional(separatedList(PathOneInPropertySet, sep='|'))('pathinonepropertyset')) + RPAR)).setName('PathNegatedPropertySet')
SPARQLParser.addElement(PathNegatedPropertySet)

Path = Forward().setName('Path')
SPARQLParser.addElement(Path)

# [94]    PathPrimary       ::=   iri | 'a' | '!' PathNegatedPropertySet | '(' Path ')' 
PathPrimary = Group(iri | TYPE | (NEGATE + PathNegatedPropertySet) | (LPAR + Path + RPAR)).setName('PathPrimary')
SPARQLParser.addElement(PathPrimary)

# [93]    PathMod   ::=   '?' | '*' | '+' 
PathMod = Group((~VAR1 + Literal('?')) | Literal('*') | Literal('+')).setName('PathMod')
SPARQLParser.addElement(PathMod)

# [91]    PathElt   ::=   PathPrimary PathMod? 
PathElt = Group(PathPrimary + Optional(PathMod) ).setName('PathElt')
SPARQLParser.addElement(PathElt)

# [92]    PathEltOrInverse          ::=   PathElt | '^' PathElt 
PathEltOrInverse = Group(PathElt | (INVERSE + PathElt)).setName('PathEltOrInverse')
SPARQLParser.addElement(PathEltOrInverse)

# [90]    PathSequence      ::=   PathEltOrInverse ( '/' PathEltOrInverse )* 
PathSequence = Group(separatedList(PathEltOrInverse, sep='/')).setName('PathSequence')
SPARQLParser.addElement(PathSequence)

# [89]    PathAlternative   ::=   PathSequence ( '|' PathSequence )* 
PathAlternative = Group(separatedList(PathSequence, sep='|')).setName('PathAlternative')
SPARQLParser.addElement(PathAlternative)
 
# [88]    Path      ::=   PathAlternative
Path << Group(PathAlternative + Empty())

# [87]    ObjectPath        ::=   GraphNodePath 
ObjectPath = Group(GraphNodePath + Empty() ).setName('ObjectPath')
SPARQLParser.addElement(ObjectPath)

# [86]    ObjectListPath    ::=   ObjectPath ( ',' ObjectPath )* 
ObjectListPath = Group(separatedList(ObjectPath)).setName('ObjectListPath')
SPARQLParser.addElement(ObjectListPath)

# [85]    VerbSimple        ::=   Var 
VerbSimple = Group(Var + Empty() ).setName('VerbSimple')
SPARQLParser.addElement(VerbSimple)

# [84]    VerbPath          ::=   Path
VerbPath = Group(Path + Empty() ).setName('VerbPath')
SPARQLParser.addElement(VerbPath)

# [80]    Object    ::=   GraphNode 
Object = Group(GraphNode + Empty() ).setName('Object')
SPARQLParser.addElement(Object)
 
# [79]    ObjectList        ::=   Object ( ',' Object )* 
ObjectList = Group(separatedList(Object)).setName('ObjectList')
SPARQLParser.addElement(ObjectList)

# [83]    PropertyListPathNotEmpty          ::=   ( VerbPath | VerbSimple ) ObjectListPath ( ';' ( ( VerbPath | VerbSimple ) ObjectList )? )* 
PropertyListPathNotEmpty << Group((VerbPath | VerbSimple) + ObjectListPath +  ZeroOrMore(SEMICOL + Optional(( VerbPath | VerbSimple) + ObjectList)))

# [82]    PropertyListPath          ::=   PropertyListPathNotEmpty? 
PropertyListPath = Group(Optional(PropertyListPathNotEmpty)).setName('PropertyListPath')
SPARQLParser.addElement(PropertyListPath)

# [81]    TriplesSameSubjectPath    ::=   VarOrTerm PropertyListPathNotEmpty | TriplesNodePath PropertyListPath 
TriplesSameSubjectPath = Group((VarOrTerm + PropertyListPathNotEmpty) | (TriplesNodePath + PropertyListPath)).setName('TriplesSameSubjectPath')
SPARQLParser.addElement(TriplesSameSubjectPath)

# [78]    Verb      ::=   VarOrIri | 'a' 
Verb = Group(VarOrIri | TYPE).setName('Verb')
SPARQLParser.addElement(Verb)

# [77]    PropertyListNotEmpty      ::=   Verb ObjectList ( ';' ( Verb ObjectList )? )* 
PropertyListNotEmpty << Group(Verb + ObjectList + ZeroOrMore(SEMICOL + Optional(Verb + ObjectList)))

# [76]    PropertyList      ::=   PropertyListNotEmpty?
PropertyList = Group(Optional(PropertyListNotEmpty) ).setName('PropertyList')
SPARQLParser.addElement(PropertyList)

# [75]    TriplesSameSubject        ::=   VarOrTerm PropertyListNotEmpty | TriplesNode PropertyList
TriplesSameSubject = Group((VarOrTerm + PropertyListNotEmpty) | (TriplesNode + PropertyList) ).setName('TriplesSameSubject')
SPARQLParser.addElement(TriplesSameSubject)

# [74]    ConstructTriples          ::=   TriplesSameSubject ( '.' ConstructTriples? )? 
ConstructTriples = Group(separatedList(TriplesSameSubject, sep='.') + Optional(PERIOD)).setName('ConstructTriples')
SPARQLParser.addElement(ConstructTriples)

# [73]    ConstructTemplate         ::=   '{' ConstructTriples? '}'
ConstructTemplate = Group(LCURL + Optional(ConstructTriples) + RCURL ).setName('ConstructTemplate')
SPARQLParser.addElement(ConstructTemplate)

# [72]    ExpressionList    ::=   NIL | '(' Expression ( ',' Expression )* ')' 
ExpressionList << Group(NIL | (LPAR + separatedList(Expression) + RPAR))

# [70]    FunctionCall      ::=   iri ArgList 
FunctionCall = Group(iri + ArgList).setName('FunctionCall')
SPARQLParser.addElement(FunctionCall)

# [69]    Constraint        ::=   BrackettedExpression | BuiltInCall | FunctionCall 
Constraint = Group(BracketedExpression | BuiltInCall | FunctionCall).setName('Constraint')
SPARQLParser.addElement(Constraint)

# [68]    Filter    ::=   'FILTER' Constraint
Filter = Group(FILTER + Constraint('constraint')).setName('Filter')
SPARQLParser.addElement(Filter)

# [67]    GroupOrUnionGraphPattern          ::=   GroupGraphPattern ( 'UNION' GroupGraphPattern )* 
GroupOrUnionGraphPattern = Group(GroupGraphPattern + ZeroOrMore(UNION + GroupGraphPattern) ).setName('GroupOrUnionGraphPattern')
SPARQLParser.addElement(GroupOrUnionGraphPattern)

# [66]    MinusGraphPattern         ::=   'MINUS' GroupGraphPattern
MinusGraphPattern = Group(SUBTRACT + GroupGraphPattern ).setName('MinusGraphPattern')
SPARQLParser.addElement(MinusGraphPattern)

# [65]    DataBlockValue    ::=   iri | RDFLiteral | NumericLiteral | BooleanLiteral | 'UNDEF' 
DataBlockValue = Group(iri | RDFLiteral | NumericLiteral | BooleanLiteral | UNDEF).setName('DataBlockValue')
SPARQLParser.addElement(DataBlockValue)

# [64]    InlineDataFull    ::=   ( NIL | '(' Var* ')' ) '{' ( '(' DataBlockValue* ')' | NIL )* '}' 
InlineDataFull = Group(( NIL | (LPAR + ZeroOrMore(Var) + RPAR)) + LCURL +  ZeroOrMore((LPAR + ZeroOrMore(DataBlockValue) + RPAR) | NIL) + RCURL ).setName('InlineDataFull')
SPARQLParser.addElement(InlineDataFull)

# [63]    InlineDataOneVar          ::=   Var '{' DataBlockValue* '}' 
InlineDataOneVar = Group(Var + LCURL + ZeroOrMore(DataBlockValue) + RCURL ).setName('InlineDataOneVar')
SPARQLParser.addElement(InlineDataOneVar)

# [62]    DataBlock         ::=   InlineDataOneVar | InlineDataFull 
DataBlock = Group(InlineDataOneVar | InlineDataFull).setName('DataBlock')
SPARQLParser.addElement(DataBlock)

# [61]    InlineData        ::=   'VALUES' DataBlock 
InlineData = Group(VALUES + DataBlock ).setName('InlineData')
SPARQLParser.addElement(InlineData)

# [60]    Bind      ::=   'BIND' '(' Expression 'AS' Var ')' 
Bind = Group(BIND + LPAR + Expression + AS + Var + RPAR ).setName('Bind')
SPARQLParser.addElement(Bind)

# [59]    ServiceGraphPattern       ::=   'SERVICE' 'SILENT'? VarOrIri GroupGraphPattern 
ServiceGraphPattern = Group(SERVICE + Optional(SILENT) + VarOrIri + GroupGraphPattern ).setName('ServiceGraphPattern')
SPARQLParser.addElement(ServiceGraphPattern)

# [58]    GraphGraphPattern         ::=   'GRAPH' VarOrIri GroupGraphPattern 
GraphGraphPattern = Group(GRAPH + VarOrIri + GroupGraphPattern ).setName('GraphGraphPattern')
SPARQLParser.addElement(GraphGraphPattern)

# [57]    OptionalGraphPattern      ::=   'OPTIONAL' GroupGraphPattern 
OptionalGraphPattern = Group(OPTIONAL + GroupGraphPattern ).setName('OptionalGraphPattern')
SPARQLParser.addElement(OptionalGraphPattern)

# [56]    GraphPatternNotTriples    ::=   GroupOrUnionGraphPattern | OptionalGraphPattern | MinusGraphPattern | GraphGraphPattern | ServiceGraphPattern | Filter | Bind | InlineData 
GraphPatternNotTriples = Group(GroupOrUnionGraphPattern | OptionalGraphPattern | MinusGraphPattern | GraphGraphPattern | ServiceGraphPattern | Filter | Bind | InlineData ).setName('GraphPatternNotTriples')
SPARQLParser.addElement(GraphPatternNotTriples)
                                           
# [55]    TriplesBlock      ::=   TriplesSameSubjectPath ( '.' TriplesBlock? )? 
TriplesBlock = Group(separatedList(TriplesSameSubjectPath, sep='.')('subjpath') + Optional(PERIOD)).setName('TriplesBlock')
SPARQLParser.addElement(TriplesBlock)

# [54]    GroupGraphPatternSub      ::=   TriplesBlock? ( GraphPatternNotTriples '.'? TriplesBlock? )* 
GroupGraphPatternSub = Group(Optional(TriplesBlock) + ZeroOrMore(GraphPatternNotTriples + Optional(PERIOD) + Optional(TriplesBlock)) ).setName('GroupGraphPatternSub')
SPARQLParser.addElement(GroupGraphPatternSub)

SubSelect = Forward().setName('SubSelect')
SPARQLParser.addElement(SubSelect)

# [53]    GroupGraphPattern         ::=   '{' ( SubSelect | GroupGraphPatternSub ) '}' 
GroupGraphPattern << Group(LCURL + (SubSelect | GroupGraphPatternSub)('pattern') + RCURL)

# [52]    TriplesTemplate   ::=   TriplesSameSubject ( '.' TriplesTemplate? )? 
TriplesTemplate = Group(separatedList(TriplesSameSubject, sep='.') + Optional(PERIOD)).setName('TriplesTemplate')
SPARQLParser.addElement(TriplesTemplate)

# [51]    QuadsNotTriples   ::=   'GRAPH' VarOrIri '{' TriplesTemplate? '}' 
QuadsNotTriples = Group(GRAPH + VarOrIri + LCURL + Optional(TriplesTemplate) + RCURL ).setName('QuadsNotTriples')
SPARQLParser.addElement(QuadsNotTriples)

# [50]    Quads     ::=   TriplesTemplate? ( QuadsNotTriples '.'? TriplesTemplate? )* 
Quads = Group(Optional(TriplesTemplate) + ZeroOrMore(QuadsNotTriples + Optional(PERIOD) + Optional(TriplesTemplate)) ).setName('Quads')
SPARQLParser.addElement(Quads)

# [49]    QuadData          ::=   '{' Quads '}' 
QuadData = Group(LCURL + Quads + RCURL ).setName('QuadData')
SPARQLParser.addElement(QuadData)

# [48]    QuadPattern       ::=   '{' Quads '}' 
QuadPattern = Group(LCURL + Quads + RCURL ).setName('QuadPattern')
SPARQLParser.addElement(QuadPattern)

# [46]    GraphRef          ::=   'GRAPH' iri 
GraphRef = Group(GRAPH + iri ).setName('GraphRef')
SPARQLParser.addElement(GraphRef)

# [47]    GraphRefAll       ::=   GraphRef | 'DEFAULT' | 'NAMED' | 'ALL' 
GraphRefAll = Group(GraphRef | DEFAULT | NAMED | ALL ).setName('GraphRefAll')
SPARQLParser.addElement(GraphRefAll)

# [45]    GraphOrDefault    ::=   'DEFAULT' | 'GRAPH'? iri 
GraphOrDefault = Group(DEFAULT | (Optional(GRAPH) + iri) ).setName('GraphOrDefault')
SPARQLParser.addElement(GraphOrDefault)

# [44]    UsingClause       ::=   'USING' ( iri | 'NAMED' iri ) 
UsingClause = Group(USING + (iri | (NAMED + iri)) ).setName('UsingClause')
SPARQLParser.addElement(UsingClause)

# [43]    InsertClause      ::=   'INSERT' QuadPattern 
InsertClause = Group(INSERT + QuadPattern ).setName('InsertClause')
SPARQLParser.addElement(InsertClause)

# [42]    DeleteClause      ::=   'DELETE' QuadPattern 
DeleteClause = Group(DELETE + QuadPattern ).setName('DeleteClause')
SPARQLParser.addElement(DeleteClause)

# [41]    Modify    ::=   ( 'WITH' iri )? ( DeleteClause InsertClause? | InsertClause ) UsingClause* 'WHERE' GroupGraphPattern 
Modify = Group(Optional(WITH + iri) + ( (DeleteClause + Optional(InsertClause) ) | InsertClause ) + ZeroOrMore(UsingClause) + WHERE + GroupGraphPattern ).setName('Modify')
SPARQLParser.addElement(Modify)

# [40]    DeleteWhere       ::=   'DELETE WHERE' QuadPattern 
DeleteWhere = Group(DELETE_WHERE + QuadPattern ).setName('DeleteWhere')
SPARQLParser.addElement(DeleteWhere)

# [39]    DeleteData        ::=   'DELETE DATA' QuadData 
DeleteData = Group(DELETE_DATA + QuadData ).setName('DeleteData')
SPARQLParser.addElement(DeleteData)

# [38]    InsertData        ::=   'INSERT DATA' QuadData 
InsertData = Group(INSERT_DATA + QuadData ).setName('InsertData')
SPARQLParser.addElement(InsertData)

# [37]    Copy      ::=   'COPY' 'SILENT'? GraphOrDefault 'TO' GraphOrDefault 
Copy = Group(COPY + Optional(SILENT) + GraphOrDefault + TO + GraphOrDefault ).setName('Copy')
SPARQLParser.addElement(Copy)

# [36]    Move      ::=   'MOVE' 'SILENT'? GraphOrDefault 'TO' GraphOrDefault 
Move = Group(MOVE + Optional(SILENT) + GraphOrDefault + TO + GraphOrDefault ).setName('Move')
SPARQLParser.addElement(Move)

# [35]    Add       ::=   'ADD' 'SILENT'? GraphOrDefault 'TO' GraphOrDefault 
Add = Group(ADD + Optional(SILENT) + GraphOrDefault + TO + GraphOrDefault ).setName('Add')
SPARQLParser.addElement(Add)

# [34]    Create    ::=   'CREATE' 'SILENT'? GraphRef 
Create = Group(CREATE + Optional(SILENT) + GraphRef).setName('Create')
SPARQLParser.addElement(Create)

# [33]    Drop      ::=   'DROP' 'SILENT'? GraphRefAll 
Drop = Group(DROP + Optional(SILENT) + GraphRefAll).setName('Drop')
SPARQLParser.addElement(Drop)

# [32]    Clear     ::=   'CLEAR' 'SILENT'? GraphRefAll 
Clear = Group(CLEAR + Optional(SILENT) + GraphRefAll ).setName('Clear')
SPARQLParser.addElement(Clear)

# [31]    Load      ::=   'LOAD' 'SILENT'? iri ( 'INTO' GraphRef )? 
Load = Group(LOAD + Optional(SILENT) + iri  + Optional(INTO + GraphRef)).setName('Load')
SPARQLParser.addElement(Load)

# [30]    Update1   ::=   Load | Clear | Drop | Add | Move | Copy | Create | InsertData | DeleteData | DeleteWhere | Modify 
Update1 = Group(Load | Clear | Drop | Add | Move | Copy | Create | InsertData | DeleteData | DeleteWhere | Modify ).setName('Update1')
SPARQLParser.addElement(Update1)

Prologue = Forward().setName('Prologue')
SPARQLParser.addElement(Prologue)

Update = Forward().setName('Update')
SPARQLParser.addElement(Update)

# [29]    Update    ::=   Prologue ( Update1 ( ';' Update )? )? 
Update << Group(Prologue('prologue') + Optional(Update1 + Optional(SEMICOL + Update)))

# [28]    ValuesClause      ::=   ( 'VALUES' DataBlock )? 
ValuesClause = Group(Optional(VALUES + DataBlock) ).setName('ValuesClause')
SPARQLParser.addElement(ValuesClause)

# [27]    OffsetClause      ::=   'OFFSET' INTEGER 
OffsetClause = Group(OFFSET + INTEGER ).setName('OffsetClause')
SPARQLParser.addElement(OffsetClause)

# [26]    LimitClause       ::=   'LIMIT' INTEGER 
LimitClause = Group(LIMIT + INTEGER ).setName('LimitClause')
SPARQLParser.addElement(LimitClause)

# [25]    LimitOffsetClauses        ::=   LimitClause OffsetClause? | OffsetClause LimitClause? 
LimitOffsetClauses = Group((LimitClause + Optional(OffsetClause)) | (OffsetClause + Optional(LimitClause))).setName('LimitOffsetClauses')
SPARQLParser.addElement(LimitOffsetClauses)

# [24]    OrderCondition    ::=   ( ( 'ASC' | 'DESC' ) BrackettedExpression ) | ( Constraint | Var ) 
OrderCondition =   Group(((ASC | DESC) + BracketedExpression) | (Constraint('constraint') | Var)).setName('OrderCondition')
SPARQLParser.addElement(OrderCondition)

# [23]    OrderClause       ::=   'ORDER' 'BY' OrderCondition+ 
OrderClause = Group(ORDER_BY + OneOrMore(OrderCondition) ).setName('OrderClause')
SPARQLParser.addElement(OrderClause)

# [22]    HavingCondition   ::=   Constraint 
HavingCondition = Group(Constraint('constraint')).setName('HavingCondition')
SPARQLParser.addElement(HavingCondition)

# [21]    HavingClause      ::=   'HAVING' HavingCondition+ 
HavingClause = Group(HAVING + OneOrMore(HavingCondition) ).setName('HavingClause')
SPARQLParser.addElement(HavingClause)

# [20]    GroupCondition    ::=   BuiltInCall | FunctionCall | '(' Expression ( 'AS' Var )? ')' | Var 
GroupCondition = Group(BuiltInCall | FunctionCall | (LPAR + Expression + Optional(AS + Var) + RPAR) | Var ).setName('GroupCondition')
SPARQLParser.addElement(GroupCondition)

# [19]    GroupClause       ::=   'GROUP' 'BY' GroupCondition+ 
GroupClause = Group(GROUP_BY + OneOrMore(GroupCondition) ).setName('GroupClause')
SPARQLParser.addElement(GroupClause)

# [18]    SolutionModifier          ::=   GroupClause? HavingClause? OrderClause? LimitOffsetClauses? 
SolutionModifier = Group(Optional(GroupClause) + Optional(HavingClause) + Optional(OrderClause) + Optional(LimitOffsetClauses) ).setName('SolutionModifier')
SPARQLParser.addElement(SolutionModifier)

# [17]    WhereClause       ::=   'WHERE'? GroupGraphPattern 
WhereClause = Group(Optional(WHERE) + GroupGraphPattern ).setName('WhereClause')
SPARQLParser.addElement(WhereClause)

# [16]    SourceSelector    ::=   iri 
SourceSelector = Group(iri).setName('SourceSelector')
SPARQLParser.addElement(SourceSelector)

# [15]    NamedGraphClause          ::=   'NAMED' SourceSelector 
NamedGraphClause = Group(NAMED + SourceSelector ).setName('NamedGraphClause')
SPARQLParser.addElement(NamedGraphClause)

# [14]    DefaultGraphClause        ::=   SourceSelector 
DefaultGraphClause = Group(SourceSelector).setName('DefaultGraphClause')
SPARQLParser.addElement(DefaultGraphClause)

# [13]    DatasetClause     ::=   'FROM' ( DefaultGraphClause | NamedGraphClause ) 
DatasetClause = Group(FROM + (DefaultGraphClause | NamedGraphClause) ).setName('DatasetClause')
SPARQLParser.addElement(DatasetClause)

# [12]    AskQuery          ::=   'ASK' DatasetClause* WhereClause SolutionModifier 
AskQuery = Group(ASK + ZeroOrMore(DatasetClause) + WhereClause('where') + SolutionModifier ).setName('AskQuery')
SPARQLParser.addElement(AskQuery)

# [11]    DescribeQuery     ::=   'DESCRIBE' ( VarOrIri+ | '*' ) DatasetClause* WhereClause? SolutionModifier 
DescribeQuery = Group(DESCRIBE + (OneOrMore(VarOrIri) | ALL_VALUES) + ZeroOrMore(DatasetClause) + Optional(WhereClause('where')) + SolutionModifier ).setName('DescribeQuery')
SPARQLParser.addElement(DescribeQuery)

# [10]    ConstructQuery    ::=   'CONSTRUCT' ( ConstructTemplate DatasetClause* WhereClause SolutionModifier | DatasetClause* 'WHERE' '{' TriplesTemplate? '}' SolutionModifier ) 
ConstructQuery = Group(CONSTRUCT + ((ConstructTemplate + ZeroOrMore(DatasetClause) + WhereClause('where') + SolutionModifier) | 
                                      (ZeroOrMore(DatasetClause) + WHERE + LCURL +  Optional(TriplesTemplate) + RCURL + SolutionModifier))).setName('ConstructQuery')
SPARQLParser.addElement(ConstructQuery)

# [9]     SelectClause      ::=   'SELECT' ( 'DISTINCT' | 'REDUCED' )? ( ( Var | ( '(' Expression 'AS' Var ')' ) )+ | '*' ) 
SelectClause = Group(SELECT + Optional(DISTINCT | REDUCED) + ( OneOrMore(Var | (LPAR + Expression + AS + Var + RPAR)) | ALL_VALUES ) ).setName('SelectClause')
SPARQLParser.addElement(SelectClause)

# [8]     SubSelect         ::=   SelectClause WhereClause SolutionModifier ValuesClause 
SubSelect << Group(SelectClause + WhereClause('where') + SolutionModifier + ValuesClause)

# [7]     SelectQuery       ::=   SelectClause DatasetClause* WhereClause SolutionModifier 
SelectQuery = Group(SelectClause + ZeroOrMore(DatasetClause) + WhereClause('where') + SolutionModifier ).setName('SelectQuery')
SPARQLParser.addElement(SelectQuery)

# [6]     PrefixDecl        ::=   'PREFIX' PNAME_NS IRIREF 
PrefixDecl = Group(PREFIX + PNAME_NS('prefix') + IRIREF('namespace')).setName('PrefixDecl')
SPARQLParser.addElement(PrefixDecl)

# [5]     BaseDecl          ::=   'BASE' IRIREF 
BaseDecl = Group(BASE + IRIREF('baseiri')).setName('BaseDecl')
SPARQLParser.addElement(BaseDecl)

# [4]     Prologue          ::=   ( BaseDecl | PrefixDecl )* 
Prologue << Group(ZeroOrMore(BaseDecl | PrefixDecl))

# [3]     UpdateUnit        ::=   Update 
UpdateUnit = Group(Update('update')).setName('UpdateUnit')
SPARQLParser.addElement(UpdateUnit)

# [2]     Query     ::=   Prologue ( SelectQuery | ConstructQuery | DescribeQuery | AskQuery ) ValuesClause 
Query = Group(Prologue('prologue') + ( SelectQuery | ConstructQuery | DescribeQuery | AskQuery ) + ValuesClause ).setName('Query')
SPARQLParser.addElement(Query)

# [1]     QueryUnit         ::=   Query 
QueryUnit = Group(Query).setName('QueryUnit')
SPARQLParser.addElement(QueryUnit)


