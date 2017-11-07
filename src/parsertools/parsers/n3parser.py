'''
Created on 29 apr. 2016

@author: jeroenbruijning
'''
from pyparsing import *
from parsertools.base import ParseStruct, parseStructFunc, separatedList
from parsertools import ParsertoolsException
from pip._vendor.pyparsing import stringEnd

# Custom exception. This is optional when defining a N3Parser. When present, it can be used in methods of the Parser class as defined below.

class N3ParseException(ParsertoolsException):
    '''Custom exception. This is optional when defining a N3Parser. When present, it can be used in methods of a ParseStruct subclass if
    defined below.'''
    
    pass

#
# Define the N3Element class
#

class N3Element(ParseStruct):
    '''Optional subclass of ParseStruct for the language. Typically, this class contains attributes and methods for the language that
    go beyond context free parsing, such as pre- and post processing, checking for conditions not covered by the grammar, etc.'''
    
    def __init__(self, expr):
        '''This constructor has an optional argument "base". This is the externally determined base iri, as per SPARQL definition par. 4.1.1.2.
        It is only applied when the constructor is called with a string as expression to be parsed. (For internal bootstrapping purposes,
        the constructor can also be called with expr equal to "None". See also the documentation for the ParseStruct constructor.)'''
        ParseStruct.__init__(self, expr)
        if not expr is None:
            newexpr = _applyKeywords(expr)
#             if postCheck:
#                 self._checkParsedQuery()

    def _applyKeywords(self, keywords=[], keywordsDecl=False):
        for elt in self.getItems():
            if isinstance(elt, KEYWORDS):
                print('found keyword:', elt)
                keywordsDecl = True
                keywords += str(elt)
            
                
                
            
#                     
#     def _applyPrefixesAndBase(self, prefixes={}, baseiri=None, isexternalbase=True):
#         '''Recursively attaches information to the element about the prefixes and base-iri valid at this point
#         in the expression, as determined by PREFIX and BASE declarations in the query.
#         The parameter isexternalbase is True when there is not yet a BASE declaration in force, as per the Turtle
#         specification. This indicates that the provided baseiri is externally determined, and should be overridden
#         by the first BASE declaration encountered (if any).
#         The first BASE declaration thus will replaces the externally determined base iri, instead
#         of being appended to it, which is what happens with subsequent BASE declarations.
#         Successful termination of this method does not guarantee that the base and prefixes conform to RFC 3987.
#         This is purely a syntactic (substitution) operation. Use other available tests to check BASE declarations and iri
#         expansion for conformance once this method has run.'''
#         
#         self.__dict__['_prefixes'] = prefixes
#         self.__dict__['_baseiri'] = baseiri
#         prefixes = prefixes.copy()
#         for elt in self.getChildren():
#             if isinstance(elt, N3Parser.Prologue):
#                 for decl in elt.getChildren():
#                     if isinstance(decl, N3Parser.PrefixDecl):
#                         assert str(decl.prefix) not in prefixes, 'Prefixes: {}, prefix: {}'.format(prefixes, decl.prefix)
#                         prefixes[str(decl.prefix)] = str(decl.namespace)[1:-1]
#                     else:
#                         assert isinstance(decl, N3Parser.BaseDecl)
#                         if isexternalbase or not baseiri:
#                             baseiri = str(decl.baseiri)[1:-1]
#                             isexternalbase = False
#                         else:
#                             baseiri = baseiri + str(decl.baseiri)[1:-1]
#                             
#             elt._applyPrefixesAndBase(prefixes, baseiri, isexternalbase)
#             
#     def getPrefixes(self):
#         return self._prefixes
#     
#     def getBaseiri(self):
#         return self._baseiri   
#         
#     def expandIris(self):
#         '''Converts all contained iri elements to normal form, taking into account the prefixes and base in force at the location of the iri.
#         The expansions are performed in place.'''
#         for elt in self.searchElements(element_type=N3Parser.iri):
#             children = elt.getChildren()
#             assert len(children) == 1, children
#             child = children[0]
# #             newiriref = '<' + getExpansion(str(child), elt._prefixes, elt._baseiri) + '>'
#             newiriref = '<' + getExpansion(child) + '>'
#             elt.updateWith(newiriref)
#             
#     def processEscapeSeqs(self):
#         for stringtype in [N3Parser.STRING_LITERAL2, N3Parser.STRING_LITERAL1, N3Parser.STRING_LITERAL_LONG1, N3Parser.STRING_LITERAL_LONG2]:
#             for elt in self.searchElements(element_type=stringtype):
#                 elt.updateWith(stringEscape(str(elt)))
# 
#     def _checkParsedQuery(self):
#         '''Used to perform additional checks on the ParseStruct resulting from a parsing action. These are conditions that are not covered by the EBNF syntax.
#         See the applicable comments and remarks in https://www.w3.org/TR/sparql11-query/, sections 19.1 - 19.8.'''
#         
#         # See 19.5 "IRI References"
#         self._checkBaseDecls()
#         self._checkIriExpansion()
#     #  TODO: finish
#                     
#     def _checkBaseDecls(self):
#         for elt in self.searchElements(element_type=N3Parser.BaseDecl):
#             rfc3987.parse(str(elt.baseiri)[1:-1], rule='absolute_IRI')
#     
#     def _checkIriExpansion(self):
#         '''Checks if all IRIs, after prefix processing and expansion, conform to RFC3987'''
#         for iri in self.searchElements(element_type=N3Parser.iri):
#             expanded = getExpansion(iri)
#             try:
#                 rfc3987.parse(expanded)
#             except ValueError as e:
#                 raise N3ParseException(str(e))  

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
    def addElement(self, pattern, newclass=None):
        if newclass:
            assert issubclass(newclass, self.__class)
        else:
            newclass = self.class_ 
        setattr(self, pattern.name, type(pattern.name, (newclass,), {'_pattern': pattern}))
        pattern.setParseAction(parseStructFunc(getattr(self, pattern.name)))

#
# Create the N3Parser object, optionally with a custom ParseStruct subclass
#

N3Parser = Parser(N3Element)

def _applyKeywords(expr):
    newexpr = ''
    keywords = set(['a', 'is', 'of'])
    keywordsDeclared = False
    inKeywordDeclaration = False
    tokens = iter(expr.split())
    while True:
        token = next(tokens)
        print(token)
            
            
    
# #
# # Main function to call. This is a convenience function, adapted to the SPARQL definition.
# #
# 
# def parseQuery(querystring, base=''):
#     '''Entry point to parse any SPARQL query'''
#     
#     s = prepareQuery(querystring)
#     
#     # In SPARQL, there are two entry points to the grammar: QueryUnit and UpdateUnit. These are tried in order.
#     
#     try:
#         result = N3Parser.QueryUnit(s, base=base)
#     except ParseException:
#         try:
#             result = N3Parser.UpdateUnit(s, base=base)
#         except ParseException:
#             raise N3ParseException('Query {} cannot be parsed'.format(querystring))
#         
#     result.processEscapeSeqs()    
#     
#     return result
# 
# #
# # Utility functions for SPARQL
# #
# 
# def prepareQuery(querystring):
#     '''Used to prepare a string for parsing. See the applicable comments and remarks in https://www.w3.org/TR/sparql11-query/, sections 19.1 - 19.8.'''
#     # See 19.4 "Comments"
#     querystring = stripComments(querystring)
#     # See 19.2 "Codepoint Escape Sequences"
#     querystring = unescapeUcode(querystring)
#     return querystring
# 
# 
# def stripComments(text):
#     '''Strips SPARQL-style comments from a multiline string'''
#     if isinstance(text, list):
#         text = '\n'.join(text)
#     Comment = Literal('#') + SkipTo(lineEnd)
#     NormalText = Regex('[^#<\'"]+')    
#     Line = ZeroOrMore(String | (IRIREF | Literal('<')) | NormalText) + Optional(Comment) + lineEnd
#     Line.ignore(Comment)
#     Line.setParseAction(lambda tokens: ' '.join([t if isinstance(t, str) else t.__str__() for t in tokens]))
#     lines = text.split('\n')
#     return '\n'.join([Line.parseString(l)[0] for l in lines])
# 
# def unescapeUcode(s):
#     
#     def escToUcode(s):
#         assert (s[:2] == r'\u' and len(s) == 6) or (s[:2] == r'\U' and len(s) == 10)
#         return chr(int(s[2:], 16))
#                    
#     smallUcodePattern = r'\\u[0-9a-fA-F]{4}'
#     largeUcodePattern = r'\\U[0-9a-fA-F]{8}'
#     s = re.sub(smallUcodePattern, lambda x: escToUcode(x.group()), s)
#     s = re.sub(largeUcodePattern, lambda x: escToUcode(x.group()), s)  
#       
#     return s
# 
# # helper function to determing the expanded form of an iri, in a given context of prefixes and base-iri.
#     
# # def getExpansion(iri, prefixes, baseiri):
# def getExpansion(iri):
#     '''Converts iri to normal form by replacing prefixes, if any, with their value and resolving the result, if relative, to absolute form.'''
#     assert isinstance(iri, (N3Parser.iri, N3Parser.PrefixedName, N3Parser.IRIREF)), 'Cannot expand non-iri element "{}" ({})'.format(iri, iri.__class__.__name__)        
#     if isinstance(iri, N3Parser.iri):
#         children = iri.getChildren()
#         assert len(children) == 1
#         oldiri = children[0]
#     else:
#         oldiri = iri
#     if isinstance(oldiri, N3Parser.PrefixedName):
#         splitiri = str(oldiri).split(':', maxsplit=1)
#         assert len(splitiri) == 2, splitiri
#         if splitiri[0] != '':
#             newiristr = oldiri.getPrefixes()[splitiri[0] + ':'][1:-1] + splitiri[1]
#         else:
#             newiristr = splitiri[1]
#     else:
#         assert isinstance(oldiri, N3Parser.IRIREF)
#         newiristr = str(oldiri)[1:-1]
#     if rfc3987.match(newiristr, 'irelative_ref'):
#         assert oldiri.getBaseiri() != None
#         newiristr = rfc3987.resolve(oldiri.getBaseiri(), newiristr)
#     assert rfc3987.match(newiristr), 'String "{}" cannot be expanded as absolute iri'.format(newiristr)
#     return newiristr
# 
#     
#     
# def stringEscape(s):
#     s = s.replace(r'\t', '\u0009')   
#     s = s.replace(r'\n', '\u000A')   
#     s = s.replace(r'\r', '\u000D')   
#     s = s.replace(r'\b', '\u0008')   
#     s = s.replace(r'\f', '\u000C')   
#     s = s.replace(r'\"', '\u0022')   
#     s = s.replace(r"\'", '\u0027')   
#     s = s.replace(r'\\', '\u005C')
#     return s

#
# Patterns
#

#
# Brackets and interpunction
#
LPAR = Literal('(').setName('LPAR')
N3Parser.addElement(LPAR)

RPAR = Literal(')').setName('RPAR')
N3Parser.addElement(RPAR)

LBRACK = Literal('[').setName('LBRACK')
N3Parser.addElement(LBRACK)

RBRACK = Literal(']').setName('RBRACK')
N3Parser.addElement(RBRACK)

LCURL = Literal('{').setName('LCURL')
N3Parser.addElement(LCURL)

RCURL = Literal('}').setName('RCURL')
N3Parser.addElement(RCURL)
#
# Operators
#

#
# Keywords
#
TRUE = Literal('@true').setName('TRUE')
N3Parser.addElement(TRUE)

FALSE = Literal('@false').setName('FALSE')
N3Parser.addElement(FALSE)

BASE = Literal('@base').setName('BASE')
N3Parser.addElement(BASE)

KEYWORDS = Literal('@keywords').setName('KEYWORDS')
N3Parser.addElement(KEYWORDS)

PREFKW = Literal('@prefix').setName('PREFKW')
N3Parser.addElement(PREFKW)

IMPLIESREV = Literal('<=').setName('IMPLIESREV')
N3Parser.addElement(IMPLIESREV)

ISEQUAL = Literal('=').setName('ISEQUAL')
N3Parser.addElement(ISEQUAL)

IMPLIES = Literal('=>').setName('IMPLIES')
N3Parser.addElement(IMPLIES)

ISA = Literal('@a').setName('ISA')
N3Parser.addElement(ISA)

HAS = Literal('@has').setName('HAS')
N3Parser.addElement(HAS)

IS = Literal('@is').setName('IS')
N3Parser.addElement(IS)

OF = Literal('@of').setName('OF')
N3Parser.addElement(OF)

FORSOME = Literal('@forSome').setName('FORSOME')
N3Parser.addElement(FORSOME)

FORALL = Literal('@forAll').setName('FORALL')
N3Parser.addElement(FORALL)

# 
# Parsers and classes for terminals
#

# unsignedint ::=    [0-9]+
UNSIGNEDINT_e = r'[0-9]+'
UNSIGNEDINT = Regex(UNSIGNEDINT_e).setName('UNSIGNEDINT')
N3Parser.addElement(UNSIGNEDINT)

# langcode ::=    [a-z]+(-[a-z0-9]+)*
LANGCODE_e = r'[a-z]+(-[a-z0-9]+)*'
LANGCODE = Regex(LANGCODE_e).setName('LANGCODE')
N3Parser.addElement(LANGCODE)

# integer ::=    [-+]?[0-9]+
INTEGER_e = r'[-+]?[0-9]+'
INTEGER = Regex(INTEGER_e).setName('INTEGER')
N3Parser.addElement(INTEGER)

# rational ::=        |    integer  "/"  unsignedint
RATIONAL_e = r'{}\/{}'.format(INTEGER_e, UNSIGNEDINT_e)
RATIONAL = Regex(RATIONAL_e).setName('RATIONAL')
N3Parser.addElement(RATIONAL)

# double ::=    [-+]?[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)
DOUBLE_e = r'[-+]?[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)'
DOUBLE = Regex(DOUBLE_e).setName('DOUBLE')
N3Parser.addElement(DOUBLE)

# decimal ::=    [-+]?[0-9]+(\.[0-9]+)?
DECIMAL_e = r'[-+]?[0-9]+(\.[0-9]+)?'
DECIMAL = Regex(DECIMAL_e).setName('DECIMAL')
N3Parser.addElement(DECIMAL)

# string ::=    ("""[^"\\]*(?:(?:\\.|"(?!""))[^"\\]*)*""")|("[^"\\]*(?:\\.[^"\\]*)*")
STRING_e = r'("""[^"\\]*(?:(?:\\.|"(?!""))[^"\\]*)*""")|("[^"\\]*(?:\\.[^"\\]*)*")'
STRING = Regex(STRING_e).setName('STRING')
N3Parser.addElement(STRING)

# quickvariable ::=    \?[A-Z_a-z#x00c0-#x00d6#x00d8-#x00f6#x00f8-#x02ff#x0370-#x037d#x037f-#x1fff#x200c-#x200d#x2070-#x218f#x2c00-#x2fef#x3001-#xd7ff#xf900-#xfdcf#xfdf0-#xfffd#x00010000-#x000effff][\-0-9A-Z_a-z#x00b7#x00c0-#x00d6#x00d8-#x00f6#x00f8-#x037d#x037f-#x1fff#x200c-#x200d#x203f-#x2040#x2070-#x218f#x2c00-#x2fef#x3001-#xd7ff#xf900-#xfdcf#xfdf0-#xfffd#x00010000-#x000effff]*
QUICKVARIABLE_e = r'\?[A-Z_a-z\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u02ff\u0370-\u037d\u037f-\u1fff\u200c-\u200d\u2070-\u218f\u2c00-\u2fef\u3001-\ud7ff\uf900-\ufdcf\ufdf0-\ufffd\U00010000-\U000effff][\-0-9A-Z_a-z\u00b7\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u037d\u037f-\u1fff\u200c-\u200d\u203f-\u2040\u2070-\u218f\u2c00-\u2fef\u3001-\ud7ff\uf900-\ufdcf\ufdf0-\ufffd\U00010000-\U000effff]*'

QUICKVARIABLE = Regex(QUICKVARIABLE_e).setName('QUICKVARIABLE')
N3Parser.addElement(QUICKVARIABLE)

# qname ::=    (([A-Z_a-z#x00c0-#x00d6#x00d8-#x00f6#x00f8-#x02ff#x0370-#x037d#x037f-#x1fff#x200c-#x200d#x2070-#x218f#x2c00-#x2fef#x3001-#xd7ff#xf900-#xfdcf#xfdf0-#xfffd#x00010000-#x000effff][\-0-9A-Z_a-z#x00b7#x00c0-#x00d6#x00d8-#x00f6#x00f8-#x037d#x037f-#x1fff#x200c-#x200d#x203f-#x2040#x2070-#x218f#x2c00-#x2fef#x3001-#xd7ff#xf900-#xfdcf#xfdf0-#xfffd#x00010000-#x000effff]*)?:)?[A-Z_a-z#x00c0-#x00d6#x00d8-#x00f6#x00f8-#x02ff#x0370-#x037d#x037f-#x1fff#x200c-#x200d#x2070-#x218f#x2c00-#x2fef#x3001-#xd7ff#xf900-#xfdcf#xfdf0-#xfffd#x00010000-#x000effff][\-0-9A-Z_a-z#x00b7#x00c0-#x00d6#x00d8-#x00f6#x00f8-#x037d#x037f-#x1fff#x200c-#x200d#x203f-#x2040#x2070-#x218f#x2c00-#x2fef#x3001-#xd7ff#xf900-#xfdcf#xfdf0-#xfffd#x00010000-#x000effff]*
QNAME_e = r'(([A-Z_a-z\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u02ff\u0370-\u037d\u037f-\u1fff\u200c-\u200d\u2070-\u218f\u2c00-\u2fef\u3001-\ud7ff\uf900-\ufdcf\ufdf0-\ufffd\U00010000-\U000effff][\-0-9A-Z_a-z\u00b7\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u037d\u037f-\u1fff\u200c-\u200d\u203f-\u2040\u2070-\u218f\u2c00-\u2fef\u3001-\ud7ff\uf900-\ufdcf\ufdf0-\ufffd\U00010000-\U000effff]*)?:)?[A-Z_a-z\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u02ff\u0370-\u037d\u037f-\u1fff\u200c-\u200d\u2070-\u218f\u2c00-\u2fef\u3001-\ud7ff\uf900-\ufdcf\ufdf0-\ufffd\U00010000-\U000effff][\-0-9A-Z_a-z\u00b7\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u037d\u037f-\u1fff\u200c-\u200d\u203f-\u2040\u2070-\u218f\u2c00-\u2fef\u3001-\ud7ff\uf900-\ufdcf\ufdf0-\ufffd\U00010000-\U000effff]*'
QNAME = Regex(QNAME_e).setName('QNAME')
N3Parser.addElement(QNAME)

# prefix ::=    ([A-Z_a-z#x00c0-#x00d6#x00d8-#x00f6#x00f8-#x02ff#x0370-#x037d#x037f-#x1fff#x200c-#x200d#x2070-#x218f#x2c00-#x2fef#x3001-#xd7ff#xf900-#xfdcf#xfdf0-#xfffd#x00010000-#x000effff][\-0-9A-Z_a-z#x00b7#x00c0-#x00d6#x00d8-#x00f6#x00f8-#x037d#x037f-#x1fff#x200c-#x200d#x203f-#x2040#x2070-#x218f#x2c00-#x2fef#x3001-#xd7ff#xf900-#xfdcf#xfdf0-#xfffd#x00010000-#x000effff]*)?:
PREFIX_e = r'([A-Z_a-z\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u02ff\u0370-\u037d\u037f-\u1fff\u200c-\u200d\u2070-\u218f\u2c00-\u2fef\u3001-\ud7ff\uf900-\ufdcf\ufdf0-\ufffd\U00010000-\U000effff][\-0-9A-Z_a-z\u00b7\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u037d\u037f-\u1fff\u200c-\u200d\u203f-\u2040\u2070-\u218f\u2c00-\u2fef\u3001-\ud7ff\uf900-\ufdcf\ufdf0-\ufffd\U00010000-\U000effff]*)?:'
PREFIX = Regex(PREFIX_e).setName('PREFIX')
N3Parser.addElement(PREFIX)

# barename ::=    [A-Z_a-z#x00c0-#x00d6#x00d8-#x00f6#x00f8-#x02ff#x0370-#x037d#x037f-#x1fff#x200c-#x200d#x2070-#x218f#x2c00-#x2fef#x3001-#xd7ff#xf900-#xfdcf#xfdf0-#xfffd#x00010000-#x000effff][\-0-9A-Z_a-z#x00b7#x00c0-#x00d6#x00d8-#x00f6#x00f8-#x037d#x037f-#x1fff#x200c-#x200d#x203f-#x2040#x2070-#x218f#x2c00-#x2fef#x3001-#xd7ff#xf900-#xfdcf#xfdf0-#xfffd#x00010000-#x000effff]*
BARENAME_e = r'[A-Z_a-z\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u02ff\u0370-\u037d\u037f-\u1fff\u200c-\u200d\u2070-\u218f\u2c00-\u2fef\u3001-\ud7ff\uf900-\ufdcf\ufdf0-\ufffd\U00010000-\U000effff][\-0-9A-Z_a-z\u00b7\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u037d\u037f-\u1fff\u200c-\u200d\u203f-\u2040\u2070-\u218f\u2c00-\u2fef\u3001-\ud7ff\uf900-\ufdcf\ufdf0-\ufffd\U00010000-\U000effff]*'
BARENAME = Regex(BARENAME_e).setName('BARENAME')
N3Parser.addElement(BARENAME)

# explicituri ::=    <[^>]*>
EXPLICITURI_e = r'<[^>]*>'
EXPLICITURI = Regex(EXPLICITURI_e).setName('EXPLICITURI')
N3Parser.addElement(EXPLICITURI)

#
# Parsers and classes for non-terminals
#

# numericliteral ::=        |    decimal
#        |    double
#        |    integer
#        |    rational
NumericLiteral = Group(RATIONAL | DOUBLE | DECIMAL | INTEGER).setName('NumericLiteral')
N3Parser.addElement(NumericLiteral)

# boolean ::=        |     "@false" 
#         |     "@true" 
Boolean = Group(TRUE | FALSE).setName('Boolean')
N3Parser.addElement(Boolean)

# barename_csl ::=        |    barename barename_csl_tail
#         |    void
# barename_csl_tail ::=        |     ","  barename barename_csl_tail
#         |    void
# Change this to:
# barename_csl = barename ["," barename]*
Barename_csl = Group(separatedList(BARENAME)).setName('Barename_csl')
N3Parser.addElement(Barename_csl)

# declaration ::=        |     "@base"  explicituri
#        |     "@keywords"  barename_csl
#        |     "@prefix"  prefix explicituri
Declaration = Group(BASE + EXPLICITURI |
                    KEYWORDS + Barename_csl |
                    PREFKW + PREFIX + EXPLICITURI).setName('Declaration')
N3Parser.addElement(Declaration)

## symbol ::=        |    explicituri
##        |    qname
Symbol = Group(EXPLICITURI | QNAME).setName('Symbol')
N3Parser.addElement(Symbol)

# symbol_csl ::=        |    symbol symbol_csl_tail
#         |    void
# symbol_csl_tail ::=        |     ","  symbol symbol_csl_tail
#         |    void
# Change this to:
# symbol_csl = symbol ["," symbol]*
Symbol_csl = Group(separatedList(Symbol)).setName('Symbol_csl')
N3Parser.addElement(Symbol_csl)

# existential ::=        |     "@forSome"  symbol_csl
Existential = Group(FORSOME + Symbol_csl).setName('Existential')
N3Parser.addElement(Existential)

# universal ::=        |     "@forAll"  symbol_csl
Universal = Group(FORALL + Symbol_csl).setName('Universal')
N3Parser.addElement(Universal)

Expression = Forward().setName('Expression')
N3Parser.addElement(Expression)
# Expression << Literal('baseexpression') # temporary, will be changed down below

# predicate ::=        |     "<=" 
#         |     "=" 
#         |     "=>" 
#         |     "@a" 
#         |     "@has"  expression
#         |     "@is"  expression  "@of" 
#         |    expression
Predicate = Group(IMPLIESREV | IMPLIES | ISEQUAL | ISA | HAS + Expression | IS + Expression + OF | Expression).setName('Predicate')
N3Parser.addElement(Predicate)

# subject ::=        |    expression
Subject = Group(Expression).setName('Subject')
N3Parser.addElement(Subject)

# object ::=        |    expression
Object = Group(Expression).setName('Object')
N3Parser.addElement(Object)

# objecttail ::=        |     ","  object objecttail
#         |    void
#
# objecttail only occurs in combination with object at the front (in the propertylist production).
# We define this combination as objectlist, and skip objecttail.
# objectlist ::=    |   object ["," object]*
Objectlist = Group(separatedList(Object)).setName('Objectlist')
N3Parser.addElement(Objectlist)

# propertylist ::=        |    predicate object objecttail propertylisttail
#         |    void
# We can now replace this by:
# propertylist ::=     |    predicate objectlist propertylisttail
# Looking at this production:
# propertylisttail ::=        |     ";"  propertylist
#         |    void
# we find that if we define:
# property ::=     | predicate objectlist
# propertylist ::=     | property [";" property]*
# we end up with the same language, but easier to specify with pyparsing,
# and easier to understand.
# 
# property ::=     | predicate objectlist
Property = Group(Predicate + Objectlist).setName('Property')
N3Parser.addElement(Property)

# propertylist ::=     | property [";" property]*
Propertylist = Optional(Group(separatedList(Property, sep=';'))).setName('Propertylist')
N3Parser.addElement(Propertylist)

# simpleStatement ::=        |    subject propertylist
SimpleStatement = Group(Subject + Propertylist).setName('SimpleStatement')
N3Parser.addElement(SimpleStatement)

# statement ::=        |    declaration
#         |    existential
#         |    simpleStatement
#         |    universal
Statement = Group(Declaration |
                  Existential |
                  SimpleStatement |
                  Universal).setName('Statement')
N3Parser.addElement(Statement)

# statementlist ::=        |    statement statementtail
#         |    void
# statementtail ::=        |     "."  statementlist
#         |    void
# Change this to:
# statementlist ::=     | statement ["." statement]*
Statementlist = Group(separatedList(Statement, sep='.')).setName('Statementlist')
N3Parser.addElement(Statementlist)

## formulacontent ::=        |    statementlist
FormulaContent = Group(Statementlist).setName('FormulaContent')
N3Parser.addElement(FormulaContent)

# statements_optional ::=        |    statement  "."  statements_optional
#        |    void
StatementsOptional = Optional(Group(Statementlist)).setName('StatementsOptional')
N3Parser.addElement(StatementsOptional)

# dtlang ::=        |     "@"  langcode
#         |     "^^"  symbol
#         |    void
DTLang = Optional(Group(Literal('@') + LANGCODE |
               Literal('^^') + Symbol)).setName('DTLang')
N3Parser.addElement(DTLang)

# literal ::=        |    string dtlang
N3Literal = Group(STRING + DTLang).setName('N3Literal')
N3Parser.addElement(N3Literal)

Pathlist = Forward().setName('Pathlist')
N3Parser.addElement(Pathlist)
Pathlist << Literal('baseexpression baseexpression') # temporary, will be changed down below

# pathitem ::=        |     "("  pathlist  ")" 
#        |     "["  propertylist  "]" 
#        |     "{"  formulacontent  "}" 
#        |    boolean
#        |    literal
#        |    numericliteral
#        |    quickvariable
#        |    symbol
PathItem = Group(LPAR + Pathlist + RPAR |
                 LBRACK + Propertylist + RBRACK |
                 LCURL + FormulaContent + RCURL |
                 Boolean |
                 N3Literal |
                 NumericLiteral |
                 QUICKVARIABLE |
                 Symbol).setName('PathItem')
N3Parser.addElement(PathItem)

# pathtail ::=        |     "!"  expression
#        |     "^"  expression
#        |    void
#
# This we change in:
# pathstep ::=  | "!" expression 
#               | "^" Expression
# and also
# expression ::=     | pathitem [pathstep]*
# changing recursion into repetition
#
# pathstep ::=  | "!" expression 
#               | "^" Expression
PathStep = Group(Literal('!') + Expression |
                 Literal('^') + Expression).setName('PathStep')
N3Parser.addElement(PathStep)

# expression ::=     | pathitem [pathstep]*
Expression << Group(PathItem + ZeroOrMore(PathStep))

# pathlist ::=        |    expression pathlist
#        |    void
# change to:
# pathlist ::=        |    [expression]+
#            | void
Pathlist = Optional(Group(OneOrMore(Expression))).setName('Pathlist')
N3Parser.addElement(Pathlist)

# document ::=        |    statements_optional EOF
Document = Group(StatementsOptional).setName('Document') 
N3Parser.addElement(Document)



