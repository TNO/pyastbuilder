'''
Created on 24 feb. 2016

@author: jeroenbruijning
'''

import unittest
from pyparsing import ParseException
from parsertools.base import ParseResults
from parsertools.parsers.n3parser import N3Parser

class Test(unittest.TestCase):
    @classmethod
    def makeTestFunc(self, rule, testCases, *, info=False, debug=0):
        pattern = eval('N3Parser.' + rule + '._pattern')
        def testFunc():
            if info:
                print('\ntesting', rule, 'with', len(testCases[rule]['pass']), 'pass case(s) and', len(testCases[rule]['fail']), 'fail case(s)')
            if debug >= 3:
                print('\npass cases:', testCases[rule]['pass'])
                print('\nfail cases:', testCases[rule]['fail'])
                print()
            for p in testCases[rule]['pass']:
                if debug >= 1:
                    print('\npass:', p, end=''), 
                if debug >= 3:
                    print(' ( = ' + ' '.join([str(ord(c)) for c in p]), end=' )')
                e = pattern.parseString(p, parseAll=True)
                while len(e) == 1 and isinstance(e[0], ParseResults):
                    e = e[0]
                if debug >= 2:
                    print()
                    print(e[0].dump())
                    print()
                if debug >= 1:
                    print(' --> ' + str(e), end='')
                    if debug >= 3:
                        print(' ( = ' + ' '.join([str(ord(c)) for c in str(e)[2:-2]]), end=' )')
                assert e[0].isValid()
                assert ''.join(e[0].__str__().upper().split()) == ''.join(p.upper().split()), 'Parsed expression: "{}" conflicts with original: "{}"'.format(e[0].__str__(), p)
            for f in testCases[rule]['fail']: 
                if debug >= 1:
                    print('\nfail:', f, end='')
                try:
                    e = pattern.parseString(f, parseAll=True)
                    if debug >= 1:
                        print(' --> ', e)
                    if debug >= 3:
                        print(' '.join([str(ord(c)) for c in f]), end=' = ')
                    assert False, 'Should raise ParseException'
                except ParseException:
                    pass
        return testFunc
    
    def setUp(self):
        self.testCases = {}
        

# unsignedint ::=    [0-9]+
        self.testCases['UNSIGNEDINT'] = {'pass': ['123', '0'],
                                         'fail': ['', '0a'] }
                
# langcode ::=    [a-z]+(-[a-z0-9]+)*
        self.testCases['LANGCODE'] = {'pass': ['x', 'xb-90cx-aa'],
                                      'fail': ['', '0a-dd'] }

# integer ::=    [-+]?[0-9]+
        self.testCases['INTEGER'] = {'pass': ['0', '-0', '33', '+33', '-33'],
                                      'fail': ['', '0a', '+-33'] }
                 
# rational ::=        |    integer  "/"  unsignedint
        self.testCases['RATIONAL'] = {'pass': ['0/0', '-0/4', '33/66', '+33/77', '-33/77'],
                                      'fail': ['', '0/-0', '-33', '+55/-55', '0/ 4'] }
                 
# double ::=    [-+]?[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)
        self.testCases['DOUBLE'] = {'pass': ['44.66e44', '+33.44e-99', '-33e09', '88.09E0'],
                                      'fail': ['', '-+33.', '33', '44e66.9'] }

# decimal ::=    [-+]?[0-9]+(\.[0-9]+)?
        self.testCases['DECIMAL'] = {'pass': ['33', '-3.99'],
                                      'fail': ['', '33.'] }
   
# string ::=    ("""[^"\\]*(?:(?:\\.|"(?!""))[^"\\]*)*""")|("[^"\\]*(?:\\.[^"\\]*)*")
        self.testCases['STRING'] = {'pass': ['"33"', '"-3.99"', '"tset\\nasdf\\t\\r sdfaf"', '"""3"3"""', '"""-3.99"""'],
                                      'fail': ['', 'sdfasdf\\', '"tset\\nasdf"\\t\\r sdfaf"', r'"""tset\\nasdf\\t\\r sdfaf""'] }              
      
# quickvariable ::=    \?[A-Z_a-z#x00c0-#x00d6#x00d8-#x00f6#x00f8-#x02ff#x0370-#x037d#x037f-#x1fff#x200c-#x200d#x2070-#x218f#x2c00-#x2fef#x3001-#xd7ff#xf900-#xfdcf#xfdf0-#xfffd#x00010000-#x000effff][\-0-9A-Z_a-z#x00b7#x00c0-#x00d6#x00d8-#x00f6#x00f8-#x037d#x037f-#x1fff#x200c-#x200d#x203f-#x2040#x2070-#x218f#x2c00-#x2fef#x3001-#xd7ff#xf900-#xfdcf#xfdf0-#xfffd#x00010000-#x000effff]*
        self.testCases['QUICKVARIABLE'] = {'pass': ['?sfasf', '?d4sfas-dfasda-sdfasfh'],
                                      'fail': ['-dsfasdf-asdasdf-asfh', '?4dsfasdf-asdasdf-asfh'] }              
      
# qname ::=    (([A-Z_a-z#x00c0-#x00d6#x00d8-#x00f6#x00f8-#x02ff#x0370-#x037d#x037f-#x1fff#x200c-#x200d#x2070-#x218f#x2c00-#x2fef#x3001-#xd7ff#xf900-#xfdcf#xfdf0-#xfffd#x00010000-#x000effff][\-0-9A-Z_a-z#x00b7#x00c0-#x00d6#x00d8-#x00f6#x00f8-#x037d#x037f-#x1fff#x200c-#x200d#x203f-#x2040#x2070-#x218f#x2c00-#x2fef#x3001-#xd7ff#xf900-#xfdcf#xfdf0-#xfffd#x00010000-#x000effff]*)?:)?[A-Z_a-z#x00c0-#x00d6#x00d8-#x00f6#x00f8-#x02ff#x0370-#x037d#x037f-#x1fff#x200c-#x200d#x2070-#x218f#x2c00-#x2fef#x3001-#xd7ff#xf900-#xfdcf#xfdf0-#xfffd#x00010000-#x000effff][\-0-9A-Z_a-z#x00b7#x00c0-#x00d6#x00d8-#x00f6#x00f8-#x037d#x037f-#x1fff#x200c-#x200d#x203f-#x2040#x2070-#x218f#x2c00-#x2fef#x3001-#xd7ff#xf900-#xfdcf#xfdf0-#xfffd#x00010000-#x000effff]*
        self.testCases['QNAME'] = {'pass': ['sfasf:d4sfas-dfasda-sdfasfh', 'asdfas', ':sfs', 'd4sfas-dfasda-sdfasfh'],
                                      'fail': ['-dsfasdf-asdasdf-asfh:sdf', '?4dsfasdf-asdasdf-asfh:sdfg'] }              
 
# prefix ::=    ([A-Z_a-z#x00c0-#x00d6#x00d8-#x00f6#x00f8-#x02ff#x0370-#x037d#x037f-#x1fff#x200c-#x200d#x2070-#x218f#x2c00-#x2fef#x3001-#xd7ff#xf900-#xfdcf#xfdf0-#xfffd#x00010000-#x000effff][\-0-9A-Z_a-z#x00b7#x00c0-#x00d6#x00d8-#x00f6#x00f8-#x037d#x037f-#x1fff#x200c-#x200d#x203f-#x2040#x2070-#x218f#x2c00-#x2fef#x3001-#xd7ff#xf900-#xfdcf#xfdf0-#xfffd#x00010000-#x000effff]*)?:
        self.testCases['PREFIX'] = {'pass': ['sfasf-d4sfas-dfasda-sdfasfh:', ':', 'asdfas:', 'sfs:', 'd4sfas-dfasda-sdfasfh:'],
                                      'fail': ['-dsfasdf-asdasdf-asfh:sdf', '?4dsfasdf-asdasdf-asfh:sdfg'] }              

# barename ::=    [A-Z_a-z#x00c0-#x00d6#x00d8-#x00f6#x00f8-#x02ff#x0370-#x037d#x037f-#x1fff#x200c-#x200d#x2070-#x218f#x2c00-#x2fef#x3001-#xd7ff#xf900-#xfdcf#xfdf0-#xfffd#x00010000-#x000effff][\-0-9A-Z_a-z#x00b7#x00c0-#x00d6#x00d8-#x00f6#x00f8-#x037d#x037f-#x1fff#x200c-#x200d#x203f-#x2040#x2070-#x218f#x2c00-#x2fef#x3001-#xd7ff#xf900-#xfdcf#xfdf0-#xfffd#x00010000-#x000effff]*
        self.testCases['BARENAME'] = {'pass': ['sfasf-d4sfas-dfasda-sdfasfh', 'asdfas', 'sfs', 'd4sfas-dfasda-sdfasfh'],
                                      'fail': ['-dsfasdf-asdasdf-asfh:sdf', 'asdf asdf', '?4dsfasdf-asdasdf-asfh:sdfg'] }              

# explicituri ::=    <[^>]*>
        self.testCases['EXPLICITURI'] = {'pass': ['<fasd fasdf  asf\na asd>'],
                                         'fail': ['asdfasdf asf>'] }

# numericliteral ::=        |    decimal
#        |    double
#        |    integer
#        |    rational
        self.testCases['NumericLiteral'] = {'pass': [],
                                      'fail': [] }
        self.testCases['NumericLiteral']['pass'] += self.testCases['DECIMAL']['pass']        
        self.testCases['NumericLiteral']['pass'] += self.testCases['DOUBLE']['pass']        
        self.testCases['NumericLiteral']['pass'] += self.testCases['INTEGER']['pass']        
        self.testCases['NumericLiteral']['pass'] += self.testCases['RATIONAL']['pass']
        self.testCases['NumericLiteral']['fail'] += ['sdf', '33.44.5']

# boolean ::=        |     "@false" 
#         |     "@true" 
        self.testCases['Boolean'] = {'pass': ['@false', '@true'],
                                      'fail': ['no', '@False', '@True'] }    

# barename_csl = barename ["," barename]*
        self.testCases['Barename_csl'] = {'pass': ['sfasf-d4sfas-dfasda-sdfasfh, asdfas, sfs, d4sfas-dfasda-sdfasfh'],
                                      'fail': ['as dfas, no', 'asdfas, @False', '@True'] }  

# declaration ::=        |     "@base"  explicituri
#        |     "@keywords"  barename_csl
#        |     "@prefix"  prefix explicituri
        self.testCases['Declaration'] = {'pass': ['@base <test1 test2\ntest3>', '@keywords b1, b2, b3', '@prefix tsg: <prefixeduri>'],
                                      'fail': ['NoDeclaration'] }
        
# symbol ::=        |    explicituri
#        |    qname
        self.testCases['Symbol'] = {'pass': [],
                                      'fail': [] }
        self.testCases['Symbol']['pass'] += self.testCases['EXPLICITURI']['pass']        
        self.testCases['Symbol']['pass'] += self.testCases['QNAME']['pass']     
        self.testCases['Symbol']['fail'] += ['-NoSymbol']
        
# symbol_csl = symbol ["," symbol]*
        self.testCases['Symbol_csl'] = {'pass': [],
                                      'fail': [] }
        self.testCases['Symbol_csl']['pass'] += [p1 + ', ' + p2 for p1 in self.testCases['Symbol']['pass'] for p2 in self.testCases['Symbol']['pass']]      
        self.testCases['Symbol_csl']['fail'] += ['-NoSymbol_csl']

# existential ::=        |     "@forSome"  symbol_csl
        self.testCases['Existential'] = {'pass': [],
                                      'fail': [] }
        self.testCases['Existential']['pass'] += ['@forSome ' + p1 for p1 in self.testCases['Symbol_csl']['pass']]      

                
# universal ::=        |     "@forAll"  symbol_csl
        self.testCases['Universal'] = {'pass': [],
                                      'fail': [] }
        self.testCases['Universal']['pass'] += ['@forAll ' + p1 for p1 in self.testCases['Symbol_csl']['pass']]      

# Expression
# "Expression" at this point is a Forward declaration.
# Testcases are valid.
        self.testCases['Expression_base'] = {'pass': ['baseexpression'],
                                             'fail': ['-noexpression'] }

# predicate ::=        |     "<=" 
#         |     "=" 
#         |     "=>" 
#         |     "@a" 
#         |     "@has"  expression
#         |     "@is"  expression  "@of" 
#         |    expression
        self.testCases['Predicate'] = {'pass': [],
                                      'fail': [] }
        self.testCases['Predicate']['pass'] += ['<=', '=', '=>', '@a']
        self.testCases['Predicate']['pass'] += ['@has ' + e for e in self.testCases['Expression_base']['pass']]
        self.testCases['Predicate']['pass'] += ['@is ' + e + ' @of' for e in self.testCases['Expression_base']['pass']]
        self.testCases['Predicate']['pass'] += self.testCases['Expression_base']['pass']
        self.testCases['Predicate']['fail'] = ['@noPredicate']
        
# subject ::=        |    expression
        self.testCases['Subject'] = {'pass': self.testCases['Expression_base']['pass'],
                                             'fail': self.testCases['Expression_base']['fail'] }
        
# object ::=        |    expression
        self.testCases['Object'] = {'pass': self.testCases['Expression_base']['pass'],
                                             'fail': self.testCases['Expression_base']['fail'] }
           
# objectlist ::=    |   object ["," object]*
        self.testCases['Objectlist'] = {'pass': [],
                                      'fail': [] }
        self.testCases['Objectlist']['pass'] += self.testCases['Object']['pass']
        self.testCases['Objectlist']['pass'] += [o1 + ', ' + o2 for o1 in self.testCases['Object']['pass'] for o2 in self.testCases['Object']['pass']]
        self.testCases['Objectlist']['fail'] = ['@noObjectlist']

# property ::= predicate objectlist
        self.testCases['Property'] = {'pass': [],
                                      'fail': [] }
        self.testCases['Property']['pass'] += [p + ' ' + o for p in self.testCases['Predicate']['pass'] for o in self.testCases['Object']['pass']]
        self.testCases['Property']['fail'] = ['@noProperty']

# propertylist ::= property [";" property]*
        self.testCases['Propertylist'] = {'pass': [],
                                      'fail': [] }
        self.testCases['Propertylist']['pass'] += self.testCases['Property']['pass']
        self.testCases['Propertylist']['pass'] += [p1 + '; ' + p2 for p1 in self.testCases['Property']['pass'] for p2 in self.testCases['Property']['pass']]
        self.testCases['Propertylist']['fail'] = ['@noObjectlist']

# simpleStatement ::=        |    subject propertylist
        self.testCases['SimpleStatement'] = {'pass': [],
                                      'fail': [] }
        self.testCases['SimpleStatement']['pass'] += [s + ' ' + p for s in self.testCases['Subject']['pass'] for p in self.testCases['Propertylist']['pass']]
        self.testCases['SimpleStatement']['fail'] = ['@noSimpleStatement']    
    
# statement ::=        |    declaration
#         |    existential
#         |    simpleStatement
#         |    universal
        self.testCases['Statement'] = {'pass': [],
                                      'fail': [] }
        self.testCases['Statement']['pass'] += self.testCases['Declaration']['pass']        
        self.testCases['Statement']['pass'] += self.testCases['Existential']['pass']        
        self.testCases['Statement']['pass'] += self.testCases['SimpleStatement']['pass']        
        self.testCases['Statement']['pass'] += self.testCases['Universal']['pass']
        self.testCases['Statement']['fail'] += ['@noStatement']

# statementlist ::= statement ["." statement]*
        self.testCases['Statementlist'] = {'pass': [],
                                      'fail': [] }
        self.testCases['Statementlist']['pass'] += self.testCases['Statement']['pass']
        self.testCases['Statementlist']['pass'] += [p1 + ' . ' + p2 for p1 in self.testCases['Statement']['pass'][::10] for p2 in self.testCases['Statement']['pass'][::10]]
        self.testCases['Statementlist']['fail'] = ['@noStatementlist']
        
## formulacontent ::=        |    statementlist
        self.testCases['FormulaContent'] = {'pass': self.testCases['Statementlist']['pass'],
                                             'fail': self.testCases['Statementlist']['fail'] }
        
# statements_optional ::=        |    statement  "."  statements_optional
#        |    void
        self.testCases['StatementsOptional'] = {'pass': [],
                                      'fail': [] }
        self.testCases['StatementsOptional']['pass'] += ['']
        self.testCases['StatementsOptional']['pass'] += self.testCases['Statementlist']['pass']
        self.testCases['StatementsOptional']['fail'] += ['@noStatementsOptional']

# dtlang ::=        |     "@"  langcode
#         |     "^^"  symbol
#         |    void
        self.testCases['DTLang'] = {'pass': [],
                                      'fail': [] }
        self.testCases['DTLang']['pass'] += ['@' + l for l in self.testCases['LANGCODE']['pass']]
        self.testCases['DTLang']['pass'] += ['^^' + s for s in self.testCases['Symbol']['pass']]
        self.testCases['DTLang']['fail'] += ['@noDTLang']

# literal ::=        |    string dtlang
        self.testCases['N3Literal'] = {'pass': [],
                                      'fail': [] }
        self.testCases['N3Literal']['pass'] += [s + ' ' + d for s in self.testCases['STRING']['pass'] for d in self.testCases['DTLang']['pass']]
        self.testCases['N3Literal']['fail'] = ['@noProperty']
        
# PathList
# "PathList" at this point is a Forward declaration.
# Testcases are valid.
        self.testCases['Pathlist_base'] = {'pass': ['baseexpression baseexpression'],
                                             'fail': ['-noPathList'] }        
        
# pathitem ::=        |     "("  pathlist  ")" 
#        |     "["  propertylist  "]" 
#        |     "{"  formulacontent  "}" 
#        |    boolean
#        |    literal
#        |    numericliteral
#        |    quickvariable
#        |    symbol
        self.testCases['PathItem'] = {'pass': [],
                                      'fail': [] }
        self.testCases['PathItem']['pass'] += ['(' + p + ')' for p in self.testCases['Pathlist_base']['pass']]        
        self.testCases['PathItem']['pass'] += ['[' + p + ']' for p in self.testCases['Propertylist']['pass']]        
        self.testCases['PathItem']['pass'] += ['{' + f + '}' for f in self.testCases['FormulaContent']['pass']]        
        self.testCases['PathItem']['pass'] += self.testCases['Boolean']['pass']        
        self.testCases['PathItem']['pass'] += self.testCases['N3Literal']['pass']        
        self.testCases['PathItem']['pass'] += self.testCases['NumericLiteral']['pass']        
        self.testCases['PathItem']['pass'] += self.testCases['QUICKVARIABLE']['pass']        
        self.testCases['PathItem']['pass'] += self.testCases['Symbol']['pass']        
        self.testCases['PathItem']['fail'] += ['@noPathItem']

# pathstep ::=  | "!" expression 
#               | "^" Expression
        self.testCases['PathStep'] = {'pass': [],
                                      'fail': [] }
        self.testCases['PathStep']['pass'] += ['!' + e for e in self.testCases['Expression_base']['pass']]        
        self.testCases['PathStep']['pass'] += ['^' + e for e in self.testCases['Expression_base']['pass']]                
        self.testCases['PathStep']['fail'] += ['@noPathStep']

# expression ::=     | pathitem [pathstep]*
        self.testCases['Expression'] = {'pass': [],
                                      'fail': [] }
        self.testCases['Expression']['pass'] += [p for p in self.testCases['PathItem']['pass']]        
        self.testCases['Expression']['pass'] += [p + ' '  + ps  for p in self.testCases['PathItem']['pass'][::20]
                                                                for ps in self.testCases['PathStep']['pass']]        
        self.testCases['Expression']['pass'] += [p + ' '  + ps  for p in self.testCases['PathItem']['pass'][1::20]
                                                                for ps in self.testCases['PathStep']['pass']]        
        self.testCases['Expression']['pass'] += [p + ' '  + ps1 + ' ' + ps2 for p in self.testCases['PathItem']['pass'][1::20]
                                                                            for ps1 in self.testCases['PathStep']['pass']
                                                                            for ps2 in self.testCases['PathStep']['pass']]        
        self.testCases['Expression']['fail'] += ['@noExpression']
        
# pathlist ::=        |    [expression]+
#            | void
        self.testCases['Pathlist'] = {'pass': [],
                                      'fail': [] }
        self.testCases['Pathlist']['pass'] += ['']        
        self.testCases['Pathlist']['pass'] += self.testCases['Expression']['pass']       
        self.testCases['Pathlist']['pass'] += [e1 + ' ' + e2 for e1 in self.testCases['Expression']['pass'][::50] for e2 in self.testCases['Expression']['pass'][1::50]]              
        self.testCases['Pathlist']['fail'] += ['@noPathlist']
           
# document ::=        |    statements_optional EOF
        self.testCases['Document'] = {'pass': [],
                                      'fail': [] }
        self.testCases['Document']['pass'] += self.testCases['StatementsOptional']['pass']       
        self.testCases['Document']['fail'] += ['@noDocument']
        

    def tearDown(self):
        pass
    
#
#
# All Tests
#
#
                                        
    def testUNSIGNEDINT(self):
        Test.makeTestFunc('UNSIGNEDINT', self.testCases, debug=0)()                                    
             
    def testLANGCODE(self):
        Test.makeTestFunc('LANGCODE', self.testCases, debug=0)()      
                 
    def testINTEGER(self):
        Test.makeTestFunc('INTEGER', self.testCases, debug=0)()   
                                           
    def testRATIONAL(self):
        Test.makeTestFunc('RATIONAL', self.testCases, debug=0)()   
                                           
    def testDOUBLE(self):
        Test.makeTestFunc('DOUBLE', self.testCases, debug=0)()   
                                           
    def testDECIMAL(self):
        Test.makeTestFunc('DECIMAL', self.testCases, debug=0)()   
                                           
    def testSTRING(self):
        Test.makeTestFunc('STRING', self.testCases, debug=0)()   
                                           
    def testQUICKVARIABLE(self):
        Test.makeTestFunc('QUICKVARIABLE', self.testCases, debug=0)()   
                                           
    def testQNAME(self):
        Test.makeTestFunc('QNAME', self.testCases, debug=0)()   
     
    def testPREFIX(self):
        Test.makeTestFunc('PREFIX', self.testCases, debug=0)()   
                                           
    def testBARENAME(self):
        Test.makeTestFunc('BARENAME', self.testCases, debug=0)()   
                                               
    def testEXPLICITURI(self):
        Test.makeTestFunc('EXPLICITURI', self.testCases, debug=0)()   
                                               
    def testNumericLiteral(self):
        Test.makeTestFunc('NumericLiteral', self.testCases, debug=0)()   
                                           
    def testBoolean(self):
        Test.makeTestFunc('Boolean', self.testCases, debug=0)()   
                                         
    def testBarename_csl(self):
        Test.makeTestFunc('Barename_csl', self.testCases, debug=0)()   
                                         
    def testDeclaration(self):
        Test.makeTestFunc('Declaration', self.testCases, debug=0)()   
                                         
    def testSymbol(self):
        Test.makeTestFunc('Symbol', self.testCases, debug=0)()   
                                         
    def testSymbol_csl(self):
        Test.makeTestFunc('Symbol_csl', self.testCases, debug=0)()   
           
    def testExistential(self):
        Test.makeTestFunc('Existential', self.testCases, debug=0)()   
           
    def testUniversal(self):
        Test.makeTestFunc('Universal', self.testCases, debug=0)()   
                                         
    def testPredicate(self):
        Test.makeTestFunc('Predicate', self.testCases, debug=0)()   
                                         
    def testSubject(self):
        Test.makeTestFunc('Subject', self.testCases, debug=0)()   
                                         
    def testObject(self):
        Test.makeTestFunc('Object', self.testCases, debug=0)()   
                                         
    def testObjectlist(self):
        Test.makeTestFunc('Objectlist', self.testCases, debug=0)()   
                                          
    def testProperty(self):
        Test.makeTestFunc('Property', self.testCases, debug=0)()   
                                          
    def testPropertylist(self):
        Test.makeTestFunc('Propertylist', self.testCases, debug=0)()   
                                         
    def testSimpleStatement(self):
        Test.makeTestFunc('SimpleStatement', self.testCases, debug=0)()   
                                         
    def testStatement(self):
        Test.makeTestFunc('Statement', self.testCases, debug=0)()   
                                         
    def testStatementlist(self):
        Test.makeTestFunc('Statementlist', self.testCases, debug=0)()   
   
    def testFormulaContent(self):
        Test.makeTestFunc('FormulaContent', self.testCases, debug=0)()   
                                         
    def testStatementsOptional(self):
        Test.makeTestFunc('StatementsOptional', self.testCases, debug=0)()   
                                         
    def testDTLang(self):
        Test.makeTestFunc('DTLang', self.testCases, debug=0)()   
                                         
    def testLiteral(self):
        Test.makeTestFunc('N3Literal', self.testCases, debug=0)()   
                                        
    def testPathItem(self):
        Test.makeTestFunc('PathItem', self.testCases, debug=0)()   
  
    def testPathStep(self):
        Test.makeTestFunc('PathStep', self.testCases, debug=0)()   
                                        
    def testExpression(self):
        Test.makeTestFunc('Expression', self.testCases, debug=0)()   
                                       
    def testPathlist(self):
        Test.makeTestFunc('Pathlist', self.testCases, debug=0)()   

    def testDocument(self):
        Test.makeTestFunc('Document', self.testCases, debug=0)()   

                                       
        
if __name__ == "__main__":
    unittest.main()
