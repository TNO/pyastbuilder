'''
Created on 20 apr. 2016

@author: jeroenbruijning
'''
import unittest

from parsertools.parsers.sparqlparser import SPARQLParser, SPARQLParseException
from parsertools.parsers.sparqlparser import stripComments, parseQuery, unescapeUcode


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass

# ParseStruct tests

    def testParse(self):
        s = "'work' ^^<work:>"
        r = SPARQLParser.RDFLiteral(s)
        assert r.check()
        
    def testCopy(self):
        s = "'work' ^^<work:>"
        r = SPARQLParser.RDFLiteral(s)
        r_copy = r.copy()
        assert r_copy == r
        assert not r_copy is r
        
    def testStr(self):
        s = "'work' ^^<work:>"
        r = SPARQLParser.RDFLiteral(s)
        assert r.__str__() == "'work' ^^ <work:>" 

    def testLabelDotAccess(self):
        s = "'work' ^^<work:>"
        r = SPARQLParser.RDFLiteral(s)
        assert str(r.lexical_form) == "'work'", r.lexical_form
        r_copy = r.copy()
        try:
            r_copy.lexical_form = SPARQLParser.String("'work2'")
        except AttributeError as e:
            assert str(e) == 'Direct setting of attributes not allowed. To change an element e, try e.updateWith() instead.'
            
        s = '<c:check#22?> ( $var, ?var )'
        r = SPARQLParser.PrimaryExpression(s, postParseCheck=False)
        assert r.iriOrFunction.iri == SPARQLParser.iri('<c:check#22?>', postParseCheck=False)
    
    def testUpdateWith(self):
        s = "'work' ^^<work:>"
        r = SPARQLParser.RDFLiteral(s)
        r_copy = r.copy()
        r_copy.lexical_form.updateWith("'work2'")
        assert r_copy != r
        r_copy.lexical_form.updateWith("'work'")
        assert r_copy == r
        
        q = '''
PREFIX foaf:   <http://xmlns.com/foaf/0.1/>

SELECT ?p WHERE 
    {
        ?p a foaf:Person
    } 
'''
        r = parseQuery(q)
        r.expandIris()
        subjpath = r.searchElements(element_type=SPARQLParser.IRIREF, value=None)[1]
        assert str(subjpath.getParent()) == '<http://xmlns.com/foaf/0.1/Person>'
        assert str(subjpath.getAncestors()) == '[iri("<http://xmlns.com/foaf/0.1/Person>"), GraphTerm("<http://xmlns.com/foaf/0.1/Person>"), VarOrTerm("<http://xmlns.com/foaf/0.1/Person>"), GraphNodePath("<http://xmlns.com/foaf/0.1/Person>"), ObjectPath("<http://xmlns.com/foaf/0.1/Person>"), ObjectListPath("<http://xmlns.com/foaf/0.1/Person>"), PropertyListPathNotEmpty("a <http://xmlns.com/foaf/0.1/Person>"), TriplesSameSubjectPath("?p a <http://xmlns.com/foaf/0.1/Person>"), TriplesBlock("?p a <http://xmlns.com/foaf/0.1/Person>"), GroupGraphPatternSub("?p a <http://xmlns.com/foaf/0.1/Person>"), GroupGraphPattern("{ ?p a <http://xmlns.com/foaf/0.1/Person> }"), WhereClause("WHERE { ?p a <http://xmlns.com/foaf/0.1/Person> }"), SelectQuery("SELECT ?p WHERE { ?p a <http://xmlns.com/foaf/0.1/Person> }"), Query("PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT ?p WHERE { ?p a <http://xmlns.com/foaf/0.1/Person> }"), QueryUnit("PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT ?p WHERE { ?p a <http://xmlns.com/foaf/0.1/Person> }")]'
        assert r.hasParentPointers()
        
    def testBranchAndAtom(self):
        s = "'work' ^^<work:>"
        r = SPARQLParser.RDFLiteral(s)
        assert r.isBranch()
        assert not r.isAtom()
        assert (SPARQLParser.IRIREF('<ftp://test>')).isAtom()
        
    def testDescend(self):
        
        s = '(DISTINCT "*Expression*",  "*Expression*",   "*Expression*" )'
        r = SPARQLParser.ArgList(s)
        assert r.descend() == r        
        v = r.searchElements(element_type=SPARQLParser.STRING_LITERAL2)
        assert v[0].isAtom()
        assert not v[0].isBranch()
        e = r.searchElements(element_type=SPARQLParser.Expression)[0]
        d = e.descend()
        assert d.isAtom()
        
    def testStripComments(self):
        s1 = """
<c:check#22?> ( $var, ?var )
# bla
'sdfasf# sdfsfd' # comment
"""[1:-1].split('\n')
         
        s2 = """
<c:check#22?> ( $var, ?var )

'sdfasf# sdfsfd'
"""[1:-1]
        assert stripComments(s1) == s2
    
    def testSearchElements(self):
        
        s = '<c:check#22?> ( $var, ?var )'
        r = SPARQLParser.PrimaryExpression(s, postParseCheck=False)
        
        found = r.searchElements()
        assert len(found) == 32, len(found)
        
        found = r.searchElements(labeledOnly=False)
        assert len(found) == 32, len(found)
        
        found = r.searchElements(labeledOnly=True)
        assert len(found) == 4, len(found)
        
        found = r.searchElements(value='<c:check#22?>') 
        assert len(found) == 2, len(found)
        assert type(found[0]) == SPARQLParser.iri
        assert found[0].getLabel() == 'iri'
        assert found[0].__str__() == '<c:check#22?>'

    def testGetChildOrAncestors(self):
        s = '<c:check#22?> ( $var, ?var )'
        r = SPARQLParser.PrimaryExpression(s, postParseCheck=False)
        found = r.searchElements(element_type=SPARQLParser.ArgList)
        arglist = found[0]
        assert(len(arglist.getChildren())) == 4, len(arglist.getChildren())
         
        ancestors = arglist.getAncestors()
        assert str(ancestors) == '[iriOrFunction("<c:check#22?> ( $var , ?var )"), PrimaryExpression("<c:check#22?> ( $var , ?var )")]', str(ancestors)

    def testParseQuery(self):
        s = 'BASE <work:22?> SELECT REDUCED $var1 ?var2 (("*Expression*") AS $var3) { SELECT * {} } GROUP BY ROUND ( "*Expression*") VALUES $S { <t:testIri> <t:testIri> }'
        parseQuery(s)
        s = 'BASE <prologue:22> PREFIX prologue: <prologue:33> LOAD <t:testIri> ; BASE <prologue2:42> PREFIX prologue2: <prologue3:33>'
        parseQuery(s)
    
    def testDump(self):
        s = '(DISTINCT "*Expression*",  "*Expression*",   "*Expression*" )'
        s_dump = '''
[ArgList] /( DISTINCT "*Expression*" , "*Expression*" , "*Expression*" )/
|  [LPAR] /(/
|  |  (
|  > distinct:
|  [DISTINCT] /DISTINCT/
|  |  DISTINCT
|  > argument:
|  [Expression] /"*Expression*"/
|  |  [ConditionalOrExpression] /"*Expression*"/
|  |  |  [ConditionalAndExpression] /"*Expression*"/
|  |  |  |  [ValueLogical] /"*Expression*"/
|  |  |  |  |  [RelationalExpression] /"*Expression*"/
|  |  |  |  |  |  [NumericExpression] /"*Expression*"/
|  |  |  |  |  |  |  [AdditiveExpression] /"*Expression*"/
|  |  |  |  |  |  |  |  [MultiplicativeExpression] /"*Expression*"/
|  |  |  |  |  |  |  |  |  [UnaryExpression] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  [PrimaryExpression] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  |  [RDFLiteral] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  |  |  > lexical_form:
|  |  |  |  |  |  |  |  |  |  |  |  [String] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  |  |  |  [STRING_LITERAL2] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  |  |  |  |  "*Expression*"
|  ,
|  > argument:
|  [Expression] /"*Expression*"/
|  |  [ConditionalOrExpression] /"*Expression*"/
|  |  |  [ConditionalAndExpression] /"*Expression*"/
|  |  |  |  [ValueLogical] /"*Expression*"/
|  |  |  |  |  [RelationalExpression] /"*Expression*"/
|  |  |  |  |  |  [NumericExpression] /"*Expression*"/
|  |  |  |  |  |  |  [AdditiveExpression] /"*Expression*"/
|  |  |  |  |  |  |  |  [MultiplicativeExpression] /"*Expression*"/
|  |  |  |  |  |  |  |  |  [UnaryExpression] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  [PrimaryExpression] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  |  [RDFLiteral] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  |  |  > lexical_form:
|  |  |  |  |  |  |  |  |  |  |  |  [String] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  |  |  |  [STRING_LITERAL2] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  |  |  |  |  "*Expression*"
|  ,
|  > argument:
|  [Expression] /"*Expression*"/
|  |  [ConditionalOrExpression] /"*Expression*"/
|  |  |  [ConditionalAndExpression] /"*Expression*"/
|  |  |  |  [ValueLogical] /"*Expression*"/
|  |  |  |  |  [RelationalExpression] /"*Expression*"/
|  |  |  |  |  |  [NumericExpression] /"*Expression*"/
|  |  |  |  |  |  |  [AdditiveExpression] /"*Expression*"/
|  |  |  |  |  |  |  |  [MultiplicativeExpression] /"*Expression*"/
|  |  |  |  |  |  |  |  |  [UnaryExpression] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  [PrimaryExpression] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  |  [RDFLiteral] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  |  |  > lexical_form:
|  |  |  |  |  |  |  |  |  |  |  |  [String] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  |  |  |  [STRING_LITERAL2] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  |  |  |  |  "*Expression*"
|  [RPAR] /)/
|  |  )
'''[1:]
 
        r = SPARQLParser.ArgList(s)
        assert r.dump() == s_dump
        
    def testPrefixesAndBase(self):
        s = 'BASE <prologue:22/> PREFIX prologue1: <prologue:33> LOAD <t:testIri> ; BASE <prologue:44> BASE </exttra> PREFIX prologue2: <prologue:55>'
        
        r = parseQuery(s)
        
        answer1 = '''
UpdateUnit
BASE <prologue:22/> PREFIX prologue1: <prologue:33> LOAD <t:testIri> ; BASE <prologue:44> BASE </exttra> PREFIX prologue2: <prologue:55>
[]
None

UpdateUnit
BASE <prologue:22/> PREFIX prologue1: <prologue:33> LOAD <t:testIri> ; BASE <prologue:44> BASE </exttra> PREFIX prologue2: <prologue:55>
[]
None

Update
BASE <prologue:22/> PREFIX prologue1: <prologue:33> LOAD <t:testIri> ; BASE <prologue:44> BASE </exttra> PREFIX prologue2: <prologue:55>
[]
None

Prologue
BASE <prologue:22/> PREFIX prologue1: <prologue:33>
[('prologue1:', 'prologue:33')]
prologue:22/

BaseDecl
BASE <prologue:22/>
[('prologue1:', 'prologue:33')]
prologue:22/

BASE
BASE
[('prologue1:', 'prologue:33')]
prologue:22/

IRIREF
<prologue:22/>
[('prologue1:', 'prologue:33')]
prologue:22/

PrefixDecl
PREFIX prologue1: <prologue:33>
[('prologue1:', 'prologue:33')]
prologue:22/

PREFIX
PREFIX
[('prologue1:', 'prologue:33')]
prologue:22/

PNAME_NS
prologue1:
[('prologue1:', 'prologue:33')]
prologue:22/

IRIREF
<prologue:33>
[('prologue1:', 'prologue:33')]
prologue:22/

Update1
LOAD <t:testIri>
[('prologue1:', 'prologue:33')]
prologue:22/

Load
LOAD <t:testIri>
[('prologue1:', 'prologue:33')]
prologue:22/

LOAD
LOAD
[('prologue1:', 'prologue:33')]
prologue:22/

iri
<t:testIri>
[('prologue1:', 'prologue:33')]
prologue:22/

IRIREF
<t:testIri>
[('prologue1:', 'prologue:33')]
prologue:22/

SEMICOL
;
[('prologue1:', 'prologue:33')]
prologue:22/

Update
BASE <prologue:44> BASE </exttra> PREFIX prologue2: <prologue:55>
[('prologue1:', 'prologue:33')]
prologue:22/

Prologue
BASE <prologue:44> BASE </exttra> PREFIX prologue2: <prologue:55>
[('prologue1:', 'prologue:33'), ('prologue2:', 'prologue:55')]
prologue:/exttra

BaseDecl
BASE <prologue:44>
[('prologue1:', 'prologue:33'), ('prologue2:', 'prologue:55')]
prologue:/exttra

BASE
BASE
[('prologue1:', 'prologue:33'), ('prologue2:', 'prologue:55')]
prologue:/exttra

IRIREF
<prologue:44>
[('prologue1:', 'prologue:33'), ('prologue2:', 'prologue:55')]
prologue:/exttra

BaseDecl
BASE </exttra>
[('prologue1:', 'prologue:33'), ('prologue2:', 'prologue:55')]
prologue:/exttra

BASE
BASE
[('prologue1:', 'prologue:33'), ('prologue2:', 'prologue:55')]
prologue:/exttra

IRIREF
</exttra>
[('prologue1:', 'prologue:33'), ('prologue2:', 'prologue:55')]
prologue:/exttra

PrefixDecl
PREFIX prologue2: <prologue:55>
[('prologue1:', 'prologue:33'), ('prologue2:', 'prologue:55')]
prologue:/exttra

PREFIX
PREFIX
[('prologue1:', 'prologue:33'), ('prologue2:', 'prologue:55')]
prologue:/exttra

PNAME_NS
prologue2:
[('prologue1:', 'prologue:33'), ('prologue2:', 'prologue:55')]
prologue:/exttra

IRIREF
<prologue:55>
[('prologue1:', 'prologue:33'), ('prologue2:', 'prologue:55')]
prologue:/exttra
'''     
        r_answer1 = ''
        for elt in r.searchElements():
            for e in [elt.__class__.__name__, elt, sorted(elt.getPrefixes().items()), elt.getBaseiri()]:
                r_answer1 += str(e) + '\n'
            r_answer1 += '\n'            
        assert answer1.strip() == r_answer1.strip()
        
        r = parseQuery(s, base='ftp://nothing/')
         
        answer2 = '''
UpdateUnit
BASE <prologue:22/> PREFIX prologue1: <prologue:33> LOAD <t:testIri> ; BASE <prologue:44> BASE </exttra> PREFIX prologue2: <prologue:55>
[]
ftp://nothing/

UpdateUnit
BASE <prologue:22/> PREFIX prologue1: <prologue:33> LOAD <t:testIri> ; BASE <prologue:44> BASE </exttra> PREFIX prologue2: <prologue:55>
[]
ftp://nothing/

Update
BASE <prologue:22/> PREFIX prologue1: <prologue:33> LOAD <t:testIri> ; BASE <prologue:44> BASE </exttra> PREFIX prologue2: <prologue:55>
[]
ftp://nothing/

Prologue
BASE <prologue:22/> PREFIX prologue1: <prologue:33>
[('prologue1:', 'prologue:33')]
prologue:22/

BaseDecl
BASE <prologue:22/>
[('prologue1:', 'prologue:33')]
prologue:22/

BASE
BASE
[('prologue1:', 'prologue:33')]
prologue:22/

IRIREF
<prologue:22/>
[('prologue1:', 'prologue:33')]
prologue:22/

PrefixDecl
PREFIX prologue1: <prologue:33>
[('prologue1:', 'prologue:33')]
prologue:22/

PREFIX
PREFIX
[('prologue1:', 'prologue:33')]
prologue:22/

PNAME_NS
prologue1:
[('prologue1:', 'prologue:33')]
prologue:22/

IRIREF
<prologue:33>
[('prologue1:', 'prologue:33')]
prologue:22/

Update1
LOAD <t:testIri>
[('prologue1:', 'prologue:33')]
prologue:22/

Load
LOAD <t:testIri>
[('prologue1:', 'prologue:33')]
prologue:22/

LOAD
LOAD
[('prologue1:', 'prologue:33')]
prologue:22/

iri
<t:testIri>
[('prologue1:', 'prologue:33')]
prologue:22/

IRIREF
<t:testIri>
[('prologue1:', 'prologue:33')]
prologue:22/

SEMICOL
;
[('prologue1:', 'prologue:33')]
prologue:22/

Update
BASE <prologue:44> BASE </exttra> PREFIX prologue2: <prologue:55>
[('prologue1:', 'prologue:33')]
prologue:22/

Prologue
BASE <prologue:44> BASE </exttra> PREFIX prologue2: <prologue:55>
[('prologue1:', 'prologue:33'), ('prologue2:', 'prologue:55')]
prologue:/exttra

BaseDecl
BASE <prologue:44>
[('prologue1:', 'prologue:33'), ('prologue2:', 'prologue:55')]
prologue:/exttra

BASE
BASE
[('prologue1:', 'prologue:33'), ('prologue2:', 'prologue:55')]
prologue:/exttra

IRIREF
<prologue:44>
[('prologue1:', 'prologue:33'), ('prologue2:', 'prologue:55')]
prologue:/exttra

BaseDecl
BASE </exttra>
[('prologue1:', 'prologue:33'), ('prologue2:', 'prologue:55')]
prologue:/exttra

BASE
BASE
[('prologue1:', 'prologue:33'), ('prologue2:', 'prologue:55')]
prologue:/exttra

IRIREF
</exttra>
[('prologue1:', 'prologue:33'), ('prologue2:', 'prologue:55')]
prologue:/exttra

PrefixDecl
PREFIX prologue2: <prologue:55>
[('prologue1:', 'prologue:33'), ('prologue2:', 'prologue:55')]
prologue:/exttra

PREFIX
PREFIX
[('prologue1:', 'prologue:33'), ('prologue2:', 'prologue:55')]
prologue:/exttra

PNAME_NS
prologue2:
[('prologue1:', 'prologue:33'), ('prologue2:', 'prologue:55')]
prologue:/exttra

IRIREF
<prologue:55>
[('prologue1:', 'prologue:33'), ('prologue2:', 'prologue:55')]
prologue:/exttra
'''
        
        r_answer2 = ''
        for elt in r.searchElements():
            for e in [elt.__class__.__name__, elt, sorted(elt.getPrefixes().items()), elt.getBaseiri()]:
                r_answer2 += str(e) + '\n'
            r_answer2 += '\n'
        
        assert answer2.strip() == r_answer2.strip()
        
    def testExpandIris(self):
        s1 = '''
PREFIX  dc: <http://purl.org/dc/elements/1.1/>
SELECT  ?title
WHERE   { <http://example.org/book/book1> dc:title ?title }  
'''[1:-1]
    
        s2 = '''
PREFIX  dc: <http://purl.org/dc/elements/1.1/>
PREFIX  : <http://example.org/book/>

SELECT  $title
WHERE   { :book1  dc:title  $title }
'''[1:-1]
    
        s3 = '''
BASE    <http://example.org/book/>
PREFIX  dc: <http://purl.org/dc/elements/1.1/>

SELECT  $title
WHERE   { <book1>  dc:title  ?title }
'''[1:-1]
    
        r1 = parseQuery(s1)
        r2 = parseQuery(s2)
        r3 = parseQuery(s3)
        r1.expandIris()
        r2.expandIris()
        r3.expandIris()
        assert str(r1) == 'PREFIX dc: <http://purl.org/dc/elements/1.1/> SELECT ?title WHERE { <http://example.org/book/book1> <http://purl.org/dc/elements/1.1/title> ?title }'
        assert str(r2) == 'PREFIX dc: <http://purl.org/dc/elements/1.1/> PREFIX : <http://example.org/book/> SELECT $title WHERE { <http://example.org/book/book1> <http://purl.org/dc/elements/1.1/title> $title }'
        assert str(r3) == 'BASE <http://example.org/book/> PREFIX dc: <http://purl.org/dc/elements/1.1/> SELECT $title WHERE { <http://example.org/book/book1> <http://purl.org/dc/elements/1.1/title> ?title }'

    def testUnescapeUcode(self):
        s = 'abra\\U000C00AAcada\\u00AAbr\u99DDa'
        assert unescapeUcode(s) == 'abra󀂪cadaªbr駝a'


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()