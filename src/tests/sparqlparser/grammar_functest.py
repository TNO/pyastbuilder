'''
Created on 24 feb. 2016

@author: jeroenbruijning
'''
from parsertools.base import ParseResults
from parsertools.parsers.sparqlparser import SPARQLParser
from parsertools import NoPrefixError
import warnings

# Next lines are temporary during development, to be deleted as implementions added to .grammar
# Expression_p << Literal('"*Expression*"')
# GroupGraphPattern_p << Literal('{}')
# TriplesNodePath_p << Literal('($TriplesNodePath)')
# TriplesNode_p << Literal('($TriplesNode)')
# PropertyListPathNotEmpty_p << Literal('$VerbPath ?ObjectListPath') 
# PropertyListNotEmpty_p << Literal('$Verb $ObjectList')
# Path_p << Literal('<Path>')
# ConstructTriples_p << Literal('?ConstructTriples')
# ExpressionList_p << Literal('()')
# SubSelect_p << Literal('SELECT * {}')
# Prologue_p << 'BASE <prologue:22> PREFIX prologue: <prologue:33>'


def printResults(l, rule, dump=False):
    element = eval('SPARQLParser.' + rule)
    for s in l:
        r = element._pattern.parseString(s, parseAll=True)
        while len(r) == 1 and isinstance(r[0], ParseResults):
            r = r[0]
        rendering = str(r[0])
#         try:
#             checkIri(r[0])
#         except NoPrefixError:
#             warnings.warn('No prefix declaration found for prefix, ignoring')
        assert ''.join(r[0].__str__().upper().split()) == ''.join(s.upper().split()), 'Parsed expression: "{}" conflicts with original: "{}"'.format(r[0].__str__(), s)
        if s != rendering:
            print()
            print(rule)
            print('\nParse :', s)
            print('Render:', rendering)
            print('Note: rendering (len={}) differs from input (len={})'.format(len(rendering), len(s)))
        if dump:
            print('\ndump:\n')
            print(r[0].dump())
            print()
        
if __name__ == '__main__':
    
        
    # [173]   PN_LOCAL_ESC      ::=   '\' ( '_' | '~' | '.' | '-' | '!' | '$' | '&' | "'" | '(' | ')' | '*' | '+' | ',' | ';' | '=' | '/' | '?' | '#' | '@' | '%' ) 
    l = ['\\&', '\\,']
    printResults(l, 'PN_LOCAL_ESC', dump=False)
                  
    # [172]   HEX       ::=   [0-9] | [A-F] | [a-f] 
    l = ['D']
    printResults(l, 'HEX', dump=False)
                      
    # [171]   PERCENT   ::=   '%' HEX HEX
    l = ['%F0']
    printResults(l, 'PERCENT', dump=False)
                      
    # [170]   PLX       ::=   PERCENT | PN_LOCAL_ESC 
    l = ['%FA', '\\*']
    printResults(l, 'PLX', dump=False)
                     
    # [164]   PN_CHARS_BASE     ::=   [A-Z] | [a-z] | [#x00C0-#x00D6] | [#x00D8-#x00F6] | [#x00F8-#x02FF] | [#x0370-#x037D] | [#x037F-#x1FFF] | [#x200C-#x200D] | [#x2070-#x218F] | [#x2C00-#x2FEF] | [#x3001-#xD7FF] | [#xF900-#xFDCF] | [#xFDF0-#xFFFD] | [#x10000-#xEFFFF] 
    l = ['a', 'Z', '\u022D', '\u218F']
    printResults(l, 'PN_CHARS_BASE', dump=False)
                     
    # [165]   PN_CHARS_U        ::=   PN_CHARS_BASE | '_' 
    l = ['a', 'Z', '\u022D', '\u218F', '_']
    printResults(l, 'PN_CHARS_U', dump=False)
                     
    # # [167]   PN_CHARS          ::=   PN_CHARS_U | '-' | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] 
    l = ['a', 'Z', '\u022D', '\u218F', '_', '7', '\u203F']
    printResults(l, 'PN_CHARS', dump=False)
                      
    # [169]   PN_LOCAL          ::=   (PN_CHARS_U | ':' | [0-9] | PLX ) ((PN_CHARS | '.' | ':' | PLX)* (PN_CHARS | ':' | PLX) )?
    l = ['aA', 'Z.a', '\u022D%FA.:', '\u218F0:']
    printResults(l, 'PN_LOCAL', dump=False)
                     
    # [168]   PN_PREFIX         ::=   PN_CHARS_BASE ((PN_CHARS|'.')* PN_CHARS)?
    l = ['aA', 'Z.8', 'zDFA.-', '\u218F0']
    printResults(l, 'PN_PREFIX', dump=False)
                     
    # [166]   VARNAME   ::=   ( PN_CHARS_U | [0-9] ) ( PN_CHARS_U | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] )* 
    l = ['aA', '8fes', '_zDFA', '9_\u218B7']
    printResults(l, 'VARNAME', dump=False)
                    
    # [163]   ANON      ::=   '[' WS* ']' 
    l = ['[]', '[ ]', '[\t]']
    printResults(l, 'ANON', dump=False)
                   
    # [161]   NIL       ::=   '(' WS* ')' 
    l = ['()', '(    )', '(\t)']
    printResults(l, 'NIL', dump=False)
                     
    # [160]   ECHAR     ::=   '\' [tbnrf\"']
    l = [r'\t', r'\"']
    printResults(l, 'ECHAR', dump=False)
                     
    # [159]   STRING_LITERAL_LONG2      ::=   '"""' ( ( '"' | '""' )? ( [^"\] | ECHAR ) )* '"""'  
    l = ['"""abc def"\t ghi""x yz"""']
    printResults(l, 'STRING_LITERAL_LONG2', dump=False)
                     
    # [158]   STRING_LITERAL_LONG1      ::=   "'''" ( ( "'" | "''" )? ( [^'\] | ECHAR ) )* "'''" 
    l = ["'''abc def'\t ghi''x yz'''"]
    printResults(l, 'STRING_LITERAL_LONG1', dump=False)
                     
    # [157]   STRING_LITERAL2   ::=   '"' ( ([^#x22#x5C#xA#xD]) | ECHAR )* '"' 
    l = ['"abc d\'ef\t ghix yz"']
    printResults(l, 'STRING_LITERAL2', dump=False)
                     
    # [156]   STRING_LITERAL1   ::=   "'" ( ([^#x27#x5C#xA#xD]) | ECHAR )* "'" 
    l = ["'abc d\"ef\t ghix yz'"]
    printResults(l, 'STRING_LITERAL1', dump=False)
                     
    # [155]   EXPONENT          ::=   [eE] [+-]? [0-9]+ 
    l = ['e-12', 'E+13']
    printResults(l, 'EXPONENT', dump=False)
                     
    # [148]   DOUBLE    ::=   [0-9]+ '.' [0-9]* EXPONENT | '.' ([0-9])+ EXPONENT | ([0-9])+ EXPONENT 
    l = ['088.77e+24', '.88e+24', '88e+24']
    printResults(l, 'DOUBLE', dump=False)
                     
    # [154]   DOUBLE_NEGATIVE   ::=   '-' DOUBLE 
    l = ['-088.77e+24', '-.88e+24', '-88e+24']
    printResults(l, 'DOUBLE_NEGATIVE', dump=False)
                     
    # [151]   DOUBLE_POSITIVE   ::=   '+' DOUBLE 
    l = ['+088.77e+24', '+.88e+24', '+88e+24']
    printResults(l, 'DOUBLE_POSITIVE', dump=False)
                     
    # [147]   DECIMAL   ::=   [0-9]* '.' [0-9]+ 
    l = ['.33', '03.33']
    printResults(l, 'DECIMAL', dump=False)
                     
    # [153]   DECIMAL_NEGATIVE          ::=   '-' DECIMAL 
    l = ['-.33', '-03.33']
    printResults(l, 'DECIMAL_NEGATIVE', dump=False)
                     
    # [150]   DECIMAL_POSITIVE          ::=   '+' DECIMAL 
    l = ['+.33', '+03.33']
    printResults(l, 'DECIMAL_POSITIVE', dump=False)
                     
    # [146]   INTEGER   ::=   [0-9]+ 
    l = ['33']
    printResults(l, 'INTEGER', dump=False)
                     
    # [152]   INTEGER_NEGATIVE          ::=   '-' INTEGER
    l = ['-33']
    printResults(l, 'INTEGER_NEGATIVE', dump=False)
                     
    # [149]   INTEGER_POSITIVE          ::=   '+' INTEGER 
    l = ['+33']
    printResults(l, 'INTEGER_POSITIVE', dump=False)
                     
    # [145]   LANGTAG   ::=   '@' [a-zA-Z]+ ('-' [a-zA-Z0-9]+)* 
    l = ['@Test', '@Test-nl-be']
    printResults(l, 'LANGTAG', dump=False)
                     
    # [144]   VAR2      ::=   '$' VARNAME 
    l = ['$aA', '$8fes', '$_zDFA', '$9_\u218B7']
    printResults(l, 'VAR2', dump=False)
                     
    # [143]   VAR1      ::=   '?' VARNAME 
    l = ['?aA', '?8fes', '?_zDFA', '?9_\u218B7']
    printResults(l, 'VAR1', dump=False)
                     
    # [142]   BLANK_NODE_LABEL          ::=   '_:' ( PN_CHARS_U | [0-9] ) ((PN_CHARS|'.')* PN_CHARS)?
    l = ['_:test9.33']
    printResults(l, 'BLANK_NODE_LABEL', dump=False)
                     
    # [140]   PNAME_NS          ::=   PN_PREFIX? ':'
    l = ['aA:', 'Z.8:', ':']
    printResults(l, 'PNAME_NS', dump=False)
                     
    # [141]   PNAME_LN          ::=   PNAME_NS PN_LOCAL 
    l = ['aA:Z.a', 'Z.8:AA']
    printResults(l, 'PNAME_LN', dump=False)
                     
    # [139]   IRIREF    ::=   '<' ([^<>"{}|^`\]-[#x00-#x20])* '>' 
    l = ['<work:22?>']
    printResults(l, 'IRIREF', dump=False)
                    
    # [138]   BlankNode         ::=   BLANK_NODE_LABEL | ANON 
    l = ['_:test9.33', '[ ]']
    printResults(l, 'BlankNode', dump=False)
                    
    # [137]   PrefixedName      ::=   PNAME_LN | PNAME_NS 
    l = ['aA:Z.a', 'Z.8:AA', 'aA:', 'Z.8:', ':']
    printResults(l, 'PrefixedName', dump=False)
                   
    # [136]   iri       ::=   IRIREF | PrefixedName 
    l = ['<work:22?>','aA:Z.a', 'Z.8:AA', 'aA:', 'Z.8:', ':']
    printResults(l, 'iri', dump=False)
                  
    # [135]   String    ::=   STRING_LITERAL1 | STRING_LITERAL2 | STRING_LITERAL_LONG1 | STRING_LITERAL_LONG2 
    l = ['"""abc def"\t ghi""x yz"""', "'''abc def'\t ghi''x yz'''", '"abc d\'ef\t ghix yz"', '"abc d\'ef   ghix yz"', "'abc d\"ef\t ghix yz'"]
    printResults(l, 'String', dump=False)
                  
    # [134]   BooleanLiteral    ::=   'true' | 'false' 
    l = ['true']
    printResults(l, 'BooleanLiteral', dump=False)
                  
    # [133]   NumericLiteralNegative    ::=   INTEGER_NEGATIVE | DECIMAL_NEGATIVE | DOUBLE_NEGATIVE 
    l = ['-33', '-22.33', '-22.33e-44']
    printResults(l, 'NumericLiteralNegative', dump=False)
                  
    # [132]   NumericLiteralPositive    ::=   INTEGER_POSITIVE | DECIMAL_POSITIVE | DOUBLE_POSITIVE 
    l = ['+33', '+22.33', '+22.33e-44']
    printResults(l, 'NumericLiteralPositive', dump=False)
                  
    # [131]   NumericLiteralUnsigned    ::=   INTEGER | DECIMAL | DOUBLE 
    l = ['33', '22.33', '22.33e-44']
    printResults(l, 'NumericLiteralUnsigned', dump=False)
                  
    # [130]   NumericLiteral    ::=   NumericLiteralUnsigned | NumericLiteralPositive | NumericLiteralNegative 
    l = ['33', '+22.33', '-22.33e-44']
    printResults(l, 'NumericLiteral', dump=False)
           
    # [129]   RDFLiteral        ::=   String ( LANGTAG | ( '^^' iri ) )? 
    l = ['"work"', '"work" @en-bf', "'work' ^^ <work>", "'work'^^:"]
    printResults(l, 'RDFLiteral', dump=False)
           
    # [71]    ArgList   ::=   NIL | '(' 'DISTINCT'? Expression ( ',' Expression )* ')' 
    l = ['()', '( "*Expression*") ', '("*Expression*", "*Expression*")', '(DISTINCT "*Expression*",  "*Expression*",   "*Expression*" )']
    printResults(l, 'ArgList', dump=False)
           
    # [128]   iriOrFunction     ::=   iri ArgList? 
    l = ['<work:22?>','aA:Z.a', 'Z.8:AA', 'aA:', 'Z.8:', ':', '<work:22?>()','aA:Z.a ("*Expression*")']
    printResults(l, 'iriOrFunction', dump=False)
 
    # [127]   Aggregate         ::=     'COUNT' '(' 'DISTINCT'? ( '*' | Expression ) ')' 
    #             | 'SUM' '(' 'DISTINCT'? Expression ')' 
    #             | 'MIN' '(' 'DISTINCT'? Expression ')' 
    #             | 'MAX' '(' 'DISTINCT'? Expression ')' 
    #             | 'AVG' '(' 'DISTINCT'? Expression ')' 
    #             | 'SAMPLE' '(' 'DISTINCT'? Expression ')' 
    #             | 'GROUP_CONCAT' '(' 'DISTINCT'? Expression ( ';' 'SEPARATOR' '=' String )? ')' 
    l = ['avg(*)', 'count (distinct *)', 'min("*Expression*")', 'GROUP_CONCAT ( distinct "*Expression*" ; SEPARATOR = "sep")']
    printResults(l, 'Aggregate', dump=False)
    
    # [126]   NotExistsFunc     ::=   'NOT' 'EXISTS' GroupGraphPattern 
    l = ['NOT Exists {}']
    printResults(l, 'NotExistsFunc', dump=False)

    # [125]   ExistsFunc        ::=   'EXISTS' GroupGraphPattern 
    l = ['Exists {}']
    printResults(l, 'ExistsFunc', dump=False)
    
    # [124]   StrReplaceExpression      ::=   'REPLACE' '(' Expression ',' Expression ',' Expression ( ',' Expression )? ')' 
    l = ['REPLACE ("*Expression*", "*Expression*", "*Expression*")', 'REPLACE ("*Expression*", "*Expression*", "*Expression*", "*Expression*")']
    printResults(l, 'StrReplaceExpression', dump=False)
    
    # [123]   SubstringExpression       ::=   'SUBSTR' '(' Expression ',' Expression ( ',' Expression )? ')' 
    l = ['SUBSTR ("*Expression*", "*Expression*")', 'SUBSTR ("*Expression*", "*Expression*", "*Expression*")']
    printResults(l, 'SubstringExpression', dump=False)

    # [122]   RegexExpression   ::=   'REGEX' '(' Expression ',' Expression ( ',' Expression )? ')' 
    l = ['REGEX ("*Expression*", "*Expression*")', 'REGEX ("*Expression*", "*Expression*", "*Expression*")']
    printResults(l, 'RegexExpression', dump=False)
    
    # [108]   Var       ::=   VAR1 | VAR2 
    l = ['$aA', '?9_\u218B7']
    printResults(l, 'Var', dump=False)

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
    l = ['STRUUID()', 'ROUND ( "*Expression*")', 'isBLANK ("*Expression*")', 'COUNT ( * )']
    printResults(l, 'BuiltInCall', dump=False)
    
    # [120]   BrackettedExpression      ::=   '(' Expression ')' 
    l = ['("*Expression*")']
    printResults(l, 'BracketedExpression', dump=False)
    
    # [119]   PrimaryExpression         ::=   BrackettedExpression | BuiltInCall | iriOrFunction | RDFLiteral | NumericLiteral | BooleanLiteral | Var 
    l = ['("*Expression*")', 'AVG ("*Expression*")', '<work:22?>()', '"work"^^<test>', '113.44', 'true', '$algebra']
    printResults(l, 'PrimaryExpression', dump=False)
    
    # [118]   UnaryExpression   ::=     '!' PrimaryExpression 
    #             | '+' PrimaryExpression 
    #             | '-' PrimaryExpression 
    #             | PrimaryExpression 
    l = ['("*Expression*")', '!AVG ("*Expression*")', '+ <work:22?>()', '-"work"^^<test>']
    printResults(l, 'UnaryExpression', dump=False)

    # [117]   MultiplicativeExpression          ::=   UnaryExpression ( '*' UnaryExpression | '/' UnaryExpression )* 
    l = ['<test()> * !$algebra / true']
    printResults(l, 'MultiplicativeExpression', dump=False)

    # [116]   AdditiveExpression        ::=   MultiplicativeExpression ( '+' MultiplicativeExpression | '-' MultiplicativeExpression | ( NumericLiteralPositive | NumericLiteralNegative ) ( ( '*' UnaryExpression ) | ( '/' UnaryExpression ) )* )* 
    l = ['33*<test>() + 44*55 - 77']
    printResults(l, 'AdditiveExpression', dump=False)
    
    # [115]   NumericExpression         ::=   AdditiveExpression 
    l = ['33*<test>() + 44*55 - 77']
    printResults(l, 'NumericExpression', dump=False)
        
    # [114]   RelationalExpression      ::=   NumericExpression ( '=' NumericExpression | '!=' NumericExpression | '<' NumericExpression | '>' NumericExpression | '<=' NumericExpression | '>=' NumericExpression | 'IN' ExpressionList | 'NOT' 'IN' ExpressionList )? 
    l = ['33*<test>() = 33 * 75', '33 IN ()', '44 * 75 NOT IN ()']
    printResults(l, 'RelationalExpression', dump=False)
        
    # [113]   ValueLogical      ::=   RelationalExpression 
    l = ['33*<test>() = 33 * 75', '33 IN ()', '44 * 75 NOT IN ()']
    printResults(l, 'ValueLogical', dump=False)
    
    # [112]   ConditionalAndExpression          ::=   ValueLogical ( '&&' ValueLogical )* 
    l = ['33*<test>() = 33 * 44 && 33 IN ()', '44 * 75 NOT IN ()']
    printResults(l, 'ConditionalAndExpression', dump=False)

    # [111]   ConditionalOrExpression   ::=   ConditionalAndExpression ( '||' ConditionalAndExpression )* 
    l = ['("*Expression*")', '33*<test>() = 33 * 44 && 33 IN ()']
    printResults(l, 'ConditionalOrExpression', dump=False)
        
    # [110]   Expression        ::=   ConditionalOrExpression 
    l = ['("*Expression*")', '33*<test>() = 33 * 44 && 33 IN ()  || 44 * 75 NOT IN ()']
    printResults(l, 'Expression', dump=False)
        
    # [109]   GraphTerm         ::=   iri | RDFLiteral | NumericLiteral | BooleanLiteral | BlankNode | NIL 
    l = ['aA:Z.a', '"work" @en-bf', '-22.33e-44', 'true', '_:test9.33', '[ ]', '()']
    printResults(l, 'GraphTerm', dump=False)
        
    # [107]   VarOrIri          ::=   Var | iri 
    l = ['$algebra', '<test>', 'az:Xy']
    printResults(l, 'VarOrIri', dump=False)
    
    # [106]   VarOrTerm         ::=   Var | GraphTerm 
    l = ['$algebra', '"work" @en-bf', '-22.33e-44']
    printResults(l, 'VarOrTerm', dump=False)
        
    # [105]   GraphNodePath     ::=   VarOrTerm | TriplesNodePath 
    l = ['$algebra', '($TriplesNodePath)']
    printResults(l, 'GraphNodePath', dump=False)
            
    # [104]   GraphNode         ::=   VarOrTerm | TriplesNode 
    l = ['$algebra', '($TriplesNode)']
    printResults(l, 'GraphNode', dump=False)
    
    # [103]   CollectionPath    ::=   '(' GraphNodePath+ ')' 
    l = ['($algebra)', '(($TriplesNodePath) $algebra )']
    printResults(l, 'CollectionPath', dump=False)
        
    # [102]   Collection        ::=   '(' GraphNode+ ')' 
    l = ['($algebra)', '($algebra ($TriplesNode))']
    printResults(l, 'Collection', dump=False)
        
    # [101]   BlankNodePropertyListPath         ::=   '[' PropertyListPathNotEmpty ']' 
    l = ['[ $VerbPath ?ObjectListPath ]']
    printResults(l, 'BlankNodePropertyListPath', dump=False)
            
    # [100]   TriplesNodePath   ::=   CollectionPath | BlankNodePropertyListPath 
    l = ['($algebra)', '(($TriplesNodePath) $algebra )', '[ $VerbPath ?ObjectListPath ]']
    printResults(l, 'TriplesNodePath', dump=False)
        
    # [99]    BlankNodePropertyList     ::=   '[' PropertyListNotEmpty ']' 
    l = ['[ $Verb $ObjectList ]']
    printResults(l, 'BlankNodePropertyList', dump=False)
        
    # [98]    TriplesNode       ::=   Collection | BlankNodePropertyList 
    l = ['($algebra)', '($algebra ($TriplesNode))', '[ $Verb $ObjectList ]']
    printResults(l, 'TriplesNode', dump=False)    
    
    # [97]    Integer   ::=   INTEGER 
    l = ['33']
    printResults(l, 'Integer', dump=False)
    
    # [96]    PathOneInPropertySet      ::=   iri | 'a' | '^' ( iri | 'a' ) 
    l = ['<test>', 'a', '^<test>', '^ a']
    printResults(l, 'PathOneInPropertySet', dump=False)    
    
    # [95]    PathNegatedPropertySet    ::=   PathOneInPropertySet | '(' ( PathOneInPropertySet ( '|' PathOneInPropertySet )* )? ')' 
    l = ['(^<testIri>|^<testIri>)', '()', '(^ a|^<testIri>)']
    printResults(l, 'PathNegatedPropertySet', dump=False)    
    
    # [94]    PathPrimary       ::=   iri | 'a' | '!' PathNegatedPropertySet | '(' Path ')' 
    l = ['<testIri>', 'a', '!(^<testIri>|^<testIri>)', '! ( )', '! ( ^ a | ^ <testIri> )', '(<Path>)']
    printResults(l, 'PathPrimary', dump=False)    
        
    # [93]    PathMod   ::=   '?' | '*' | '+' 
    l = ['*']
    printResults(l, 'PathMod', dump=False)    
     
    # [91]    PathElt   ::=   PathPrimary PathMod? 
    l = ['! ( ^ <testIri> | ^ <testIri> )', 'a ?']
    printResults(l, 'PathElt', dump=False)    

    # [92]    PathEltOrInverse          ::=   PathElt | '^' PathElt 
    l = ['! ( ^ <testIri> | ^ <testIri> )', 'a ?', '^ ! ( ^ <testIri> | ^ <testIri> )', '^a ?']
    printResults(l, 'PathEltOrInverse', dump=False)   
        
    # [90]    PathSequence      ::=   PathEltOrInverse ( '/' PathEltOrInverse )* 
    l = ['a ? / ^ ! ( ^ <testIri> | ^ <testIri> )']
    printResults(l, 'PathSequence', dump=False)    
    
    # [89]    PathAlternative   ::=   PathSequence ( '|' PathSequence )* 
    l = ['a ? / ^ ! ( ^ <testIri> | ^ <testIri> ) | a ? / ^ ! ( ^ <testIri> | ^ <testIri> )']
    printResults(l, 'PathAlternative', dump=False)   
        
    # [88]    Path      ::=   PathAlternative 
    l = ['a ? / ^ ! ( ^ <testIri> | ^ <testIri> ) | a ? / ^ ! ( ^ <testIri> | ^ <testIri> )']
    printResults(l, 'Path', dump=False)   
            
    # [87]    ObjectPath        ::=   GraphNodePath 
    l = ['$algebra', '($TriplesNodePath)']
    printResults(l, 'ObjectPath', dump=False)   
    
    # [86]    ObjectListPath    ::=   ObjectPath ( ',' ObjectPath )* 
    l = ['$algebra', '(?TriplesNodePath), $algebra']
    printResults(l, 'ObjectListPath', dump=False)     
    
    # [85]    VerbSimple        ::=   Var 
    l = ['$aA', '?9_\u218B7']
    printResults(l, 'VerbSimple', dump=False)
    
    # [84]    VerbPath          ::=   Path 
    l = ['a ? / ^ ! ( ^ <testIri> | ^ <testIri> ) | a ? / ^ ! ( ^ <testIri> | ^ <testIri> )']
    printResults(l, 'VerbPath', dump=False)  
        
    # [80]    Object    ::=   GraphNode 
    l = ['$algebra', '($TriplesNode)']
    printResults(l, 'Object', dump=False)
        
    # [79]    ObjectList        ::=   Object ( ',' Object )* 
    l = ['$algebra, ($TriplesNode)']
    printResults(l, 'ObjectList', dump=False)
        
    # [83]    PropertyListPathNotEmpty          ::=   ( VerbPath | VerbSimple ) ObjectListPath ( ';' ( ( VerbPath | VerbSimple ) ObjectList )? )* 
    l = ['<test> ?path ; <test2> $algebra, ($TriplesNode) ;;', '<test> ? ?path']
    printResults(l, 'PropertyListPathNotEmpty', dump=False)
        
    # [82]    PropertyListPath          ::=   PropertyListPathNotEmpty? 
    l = ['<test> ?path ; <test2> $algebra, ($TriplesNode) ;;', '<test> ? ?path', '']
    printResults(l, 'PropertyListPath', dump=False)
        
    # [81]    TriplesSameSubjectPath    ::=   VarOrTerm PropertyListPathNotEmpty | TriplesNodePath PropertyListPath 
    l = ['[] <test> ? ?path', '"work" @en-bf <test> ?path ; <test2> $algebra, ($TriplesNode) ;;', '(($TriplesNodePath) $algebra )', '(($TriplesNodePath) $algebra ) <test> ? ?path']
    printResults(l, 'TriplesSameSubjectPath', dump=False)
    
    # [78]    Verb      ::=   VarOrIri | 'a' 
    l = ['$algebra', '<test>', 'az:Xy', 'a']
    printResults(l, 'Verb', dump=False)
        
    # [77]    PropertyListNotEmpty      ::=   Verb ObjectList ( ';' ( Verb ObjectList )? )* 
    l = ['$algebra $algebra, ($TriplesNode)', '<test> $algebra, ($TriplesNode) ; a ?algebra, ($TriplesNode)']
    printResults(l, 'PropertyListNotEmpty', dump=False)
        
    # [76]    PropertyList      ::=   PropertyListNotEmpty? 
    l = ['$algebra $algebra, ($TriplesNode)', '<test> $algebra, ($TriplesNode) ; a ?algebra, ($TriplesNode)', '']
    printResults(l, 'PropertyList', dump=False)
    
    # [75]    TriplesSameSubject        ::=   VarOrTerm PropertyListNotEmpty | TriplesNode PropertyList 
    l = ['?var $algebra $algebra, ($TriplesNode)', '_:test9.33 <test> $algebra, ($TriplesNode) ; a ?algebra, ($TriplesNode)', '[ $Verb $ObjectList ]']
    printResults(l, 'TriplesSameSubject', dump=False)

    # [74]    ConstructTriples          ::=   TriplesSameSubject ( '.' ConstructTriples? )? 
    l = ['_:test9.33 <test> $algebra, ($TriplesNode) ; a ?algebra, ($TriplesNode). [ $Verb $ObjectList ]']
    printResults(l, 'ConstructTriples', dump=False)
        
    # [73]    ConstructTemplate         ::=   '{' ConstructTriples? '}' 
    l = ['{_:test9.33 <test> $algebra, ($TriplesNode) ; a ?algebra, ($TriplesNode)}']
    printResults(l, 'ConstructTemplate', dump=False)
    
    # [72]    ExpressionList    ::=   NIL | '(' Expression ( ',' Expression )* ')' 
    l = ['()', '(("*Expression*"), 33*<test>() = 33 * 44 && 33 IN ()  || 44 * 75 NOT IN ())']
    printResults(l, 'ExpressionList', dump=False)
        
    # [70]    FunctionCall      ::=   iri ArgList 
    l = ['<test:227> (DISTINCT "*Expression*",  "*Expression*",   "*Expression*" )']
    printResults(l, 'FunctionCall', dump=False)
            
    # [69]    Constraint        ::=   BrackettedExpression | BuiltInCall | FunctionCall 
    l = ['<test:227> (DISTINCT "*Expression*",  "*Expression*",   "*Expression*" )', 'STRUUID()', 'ROUND ( "*Expression*")', 'isBLANK ("*Expression*")', 'COUNT ( * )', '("*Expression*")']
    printResults(l, 'Constraint', dump=False)
        
    # [68]    Filter    ::=   'FILTER' Constraint 
    l = ['FILTER <test:227> (DISTINCT "*Expression*",  "*Expression*",   "*Expression*" )', 'FILTER STRUUID()', 'FILTER ROUND ( "*Expression*")', 'FILTER isBLANK ("*Expression*")', 'FILTER COUNT ( * )', 'FILTER ("*Expression*")']
    printResults(l, 'Filter', dump=False)
            
    # [67]    GroupOrUnionGraphPattern          ::=   GroupGraphPattern ( 'UNION' GroupGraphPattern )* 
    l = ['{}', '{} UNION {}', '{} UNION {} UNION {}']
    printResults(l, 'GroupOrUnionGraphPattern', dump=False)
        
    # [66]    MinusGraphPattern         ::=   'MINUS' GroupGraphPattern 
    l = ['MINUS {}']
    printResults(l, 'MinusGraphPattern', dump=False)
            
    # [65]    DataBlockValue    ::=   iri | RDFLiteral | NumericLiteral | BooleanLiteral | 'UNDEF' 
    l = ['<work:22?>', '"test" ^^ <test>', '333.55', 'true', 'UNDEF']
    printResults(l, 'DataBlockValue', dump=False)
                
    # [64]    InlineDataFull    ::=   ( NIL | '(' Var* ')' ) '{' ( '(' DataBlockValue* ')' | NIL )* '}' 
    l = ['( $4℀ $4℀ )  { ( true true ) }']
    printResults(l, 'InlineDataFull', dump=False)
        
    # [63]    InlineDataOneVar          ::=   Var '{' DataBlockValue* '}' 
    l = ['$S { <testIri> <testIri> }']
    printResults(l, 'InlineDataOneVar', dump=False)
            
    # [62]    DataBlock         ::=   InlineDataOneVar | InlineDataFull 
    l = ['( $4℀ $4℀ )  { ( true true ) }', '$S { <testIri> <testIri> }']
    printResults(l, 'DataBlock', dump=False)
        
    # [61]    InlineData        ::=   'VALUES' DataBlock 
    l = ["VALUES  ( $4℀ $4℀ )  { ( 'te\\n' 'te\\n' ) }"]
    printResults(l, 'InlineData', dump=False)
            
    l = ['BIND ( ("*Expression*") AS $var)']
    printResults(l, 'Bind', dump=False)
            
    # [59]    ServiceGraphPattern       ::=   'SERVICE' 'SILENT'? VarOrIri GroupGraphPattern 
    l = ['SERVICE <test> {}', 'SERVICE SILENT ?var {}']
    printResults(l, 'ServiceGraphPattern', dump=False)
                
    # [58]    GraphGraphPattern         ::=   'GRAPH' VarOrIri GroupGraphPattern 
    l = ['GRAPH <test> {}', 'GRAPH ?var {}']
    printResults(l, 'GraphGraphPattern', dump=False)
        
    # [57]    OptionalGraphPattern      ::=   'OPTIONAL' GroupGraphPattern 
    l = ['OPTIONAL {}']
    printResults(l, 'OptionalGraphPattern', dump=False)
    
    # [56]    GraphPatternNotTriples    ::=   GroupOrUnionGraphPattern | OptionalGraphPattern | MinusGraphPattern | GraphGraphPattern | ServiceGraphPattern | Filter | Bind | InlineData 
    l = ['{} UNION {} UNION {}', 'OPTIONAL {}', 'MINUS {}', 'GRAPH <test> {}', 'SERVICE SILENT ?var {}',
         'FILTER <test:227> (DISTINCT "*Expression*",  "*Expression*",   "*Expression*" )','BIND ( ("*Expression*") AS $var)', "VALUES  ( $4℀ $4℀ )  { ( 'te\\n' 'te\\n' ) }"]
    printResults(l, 'GraphPatternNotTriples', dump=False)
        
    # [55]    TriplesBlock      ::=   TriplesSameSubjectPath ( '.' TriplesBlock? )? 
    l = ['(($TriplesNodePath) $algebra ) . "TriplesBlock" @en-bf <test> ?path ; <test2> $algebra, ($TriplesBlock)']
    printResults(l, 'TriplesBlock', dump=False)
    
    # [54]    GroupGraphPatternSub      ::=   TriplesBlock? ( GraphPatternNotTriples '.'? TriplesBlock? )* 
    l = ['(($TriplesNodePath) $algebra ) . SERVICE SILENT ?var {} . (($TriplesNodePath) $algebra )']
    printResults(l, 'GroupGraphPatternSub', dump=False)
    
    # [53]    GroupGraphPattern         ::=   '{' ( SubSelect | GroupGraphPatternSub ) '}' 
    l = ['{ SELECT * {} }', '{ (($TriplesNodePath) $algebra ) . SERVICE SILENT ?var {} . (($TriplesNodePath) $algebra ) }']
    printResults(l, 'GroupGraphPattern', dump=False)
    
    # [52]    TriplesTemplate   ::=   TriplesSameSubject ( '.' TriplesTemplate? )? 
    l = ['?var $algebra $algebra, ($TriplesNode) . ?var $algebra $algebra, ($TriplesNode)']
    printResults(l, 'TriplesTemplate', dump=False)
        
    # [51]    QuadsNotTriples   ::=   'GRAPH' VarOrIri '{' TriplesTemplate? '}' 
    l = ['GRAPH $var { ?var $algebra $algebra, ($TriplesNode) . ?var $algebra $algebra, ($TriplesNode) }']
    printResults(l, 'QuadsNotTriples', dump=False)
    
    # [50]    Quads     ::=   TriplesTemplate? ( QuadsNotTriples '.'? TriplesTemplate? )* 
    l = ['?var $algebra $algebra, ($TriplesNode) . ?var $algebra $algebra, ($TriplesNode) GRAPH $var { ?var $algebra $algebra, ($TriplesNode) . ?var $algebra $algebra, ($TriplesNode) } GRAPH $var { }']
    printResults(l, 'Quads', dump=False)
    
    # [49]    QuadData          ::=   '{' Quads '}' 
    l = ['{ ?var $algebra $algebra, ($TriplesNode) . ?var $algebra $algebra, ($TriplesNode) GRAPH $var { ?var $algebra $algebra, ($TriplesNode) . ?var $algebra $algebra, ($TriplesNode) } GRAPH $var { } }']
    printResults(l, 'QuadData', dump=False)
        
    # [48]    QuadPattern       ::=   '{' Quads '}' 
    l = ['{ }', '{ ?var $algebra $algebra, ($TriplesNode) . ?var $algebra $algebra, ($TriplesNode) GRAPH $var { ?var $algebra $algebra, ($TriplesNode) . ?var $algebra $algebra, ($TriplesNode) } GRAPH $var { } }']
    printResults(l, 'QuadPattern', dump=False)
        
    # [46]    GraphRef          ::=   'GRAPH' iri 
    l = ['GRAPH <test:2?>']
    printResults(l, 'GraphRef', dump=False)
    
    # [47]    GraphRefAll       ::=   GraphRef | 'DEFAULT' | 'NAMED' | 'ALL' 
    l = ['GRAPH <test:2?>', 'DEFAULT', 'NAMED', 'ALL']
    printResults(l, 'GraphRefAll', dump=False)
    
    # [45]    GraphOrDefault    ::=   'DEFAULT' | 'GRAPH'? iri 
    l = ['DEFAULT', '<test:22?>', 'GRAPH <test:22?>']
    printResults(l, 'GraphOrDefault', dump=False)
    
    # [44]    UsingClause       ::=   'USING' ( iri | 'NAMED' iri ) 
    l = ['USING <test:22?>', 'USING NAMED <test:22?>']
    printResults(l, 'UsingClause', dump=False)
        
    # [43]    InsertClause      ::=   'INSERT' QuadPattern 
    l = ['INSERT { ?var $algebra $algebra, ($TriplesNode) . ?var $algebra $algebra, ($TriplesNode) GRAPH $var { ?var $algebra $algebra, ($TriplesNode) . ?var $algebra $algebra, ($TriplesNode) } GRAPH $var { } }']
    printResults(l, 'InsertClause', dump=False)
            
    # [42]    DeleteClause      ::=   'DELETE' QuadPattern 
    l = ['DELETE { ?var $algebra $algebra, ($TriplesNode) . ?var $algebra $algebra, ($TriplesNode) GRAPH $var { ?var $algebra $algebra, ($TriplesNode) . ?var $algebra $algebra, ($TriplesNode) } GRAPH $var { } }']
    printResults(l, 'DeleteClause', dump=False)
                 
    # [41]    Modify    ::=   ( 'WITH' iri )? ( DeleteClause InsertClause? | InsertClause ) UsingClause* 'WHERE' GroupGraphPattern 
    l = ['WITH <test:22?> DELETE { } INSERT { } USING NAMED aA:Z.a USING <abc:def> WHERE { SELECT * {} }']
    printResults(l, 'Modify', dump=False)
                    
    # [40]    DeleteWhere       ::=   'DELETE WHERE' QuadPattern 
    l = ['DELETE WHERE { }']
    printResults(l, 'DeleteWhere', dump=False)
    
    # [39]    DeleteData        ::=   'DELETE DATA' QuadData 
    l = ['DELETE DATA { }']
    printResults(l, 'DeleteData', dump=False)
      
    # [38]    InsertData        ::=   'INSERT DATA' QuadData 
    l = ['INSERT DATA  { }']
    printResults(l, 'InsertData', dump=False)
    
    # [37]    Copy      ::=   'COPY' 'SILENT'? GraphOrDefault 'TO' GraphOrDefault 
    l = ['COPY SILENT GRAPH <test:22?> TO DEFAULT']
    printResults(l, 'Copy', dump=False)
        
    # [36]    Move      ::=   'MOVE' 'SILENT'? GraphOrDefault 'TO' GraphOrDefault 
    l = ['MOVE GRAPH <test:22?> TO <test:22?>']
    printResults(l, 'Move', dump=False)
    
    # [35]    Add       ::=   'ADD' 'SILENT'? GraphOrDefault 'TO' GraphOrDefault 
    l = ['ADD <test:22?> TO GRAPH <test:22?>']
    printResults(l, 'Add', dump=False)
    
    # [34]    Create    ::=   'CREATE' 'SILENT'? GraphRef 
    l = ['CREATE GRAPH <test:2?>']
    printResults(l, 'Create', dump=False)
    
    # [33]    Drop      ::=   'DROP' 'SILENT'? GraphRefAll 
    l = ['DROP SILENT GRAPH <test:2?>']
    printResults(l, 'Drop', dump=False)
    
    # [32]    Clear     ::=   'CLEAR' 'SILENT'? GraphRefAll 
    l = ['CLEAR SILENT NAMED']
    printResults(l, 'Clear', dump=False)
    
    # [31]    Load      ::=   'LOAD' 'SILENT'? iri ( 'INTO' GraphRef )? 
    l = ['LOAD <test:22?>', 'LOAD <test:22?> INTO GRAPH <test:29?>']
    printResults(l, 'Load', dump=False)
    
    # [30]    Update1   ::=   Load | Clear | Drop | Add | Move | Copy | Create | InsertData | DeleteData | DeleteWhere | Modify 
    l = ['LOAD <test:22?>', 'INSERT DATA  { }', 'WITH <test:22?> DELETE { } INSERT { } USING NAMED aA:Z.a USING <abc:def> WHERE { SELECT * {} }']
    printResults(l, 'Update1', dump=False)
    
    # [29]    Update    ::=   Prologue ( Update1 ( ';' Update )? )? 
    l = ['BASE <prologue:22> PREFIX prologue: <prologue:33> LOAD <testIri> ; BASE <prologue:22> PREFIX prologue: <prologue:33>']
    printResults(l, 'Update', dump=False)
    
    # [28]    ValuesClause      ::=   ( 'VALUES' DataBlock )? 
    l = ['', 'VALUES $S { <testIri> <testIri> }']
    printResults(l, 'ValuesClause', dump=False)
    
    # [27]    OffsetClause      ::=   'OFFSET' INTEGER 
    l = ['OFFSET 3']
    printResults(l, 'OffsetClause', dump=False)
    
    # [26]    LimitClause       ::=   'LIMIT' INTEGER 
    l = ['LIMIT 3']
    printResults(l, 'LimitClause', dump=False)
    
    # [25]    LimitOffsetClauses        ::=   LimitClause OffsetClause? | OffsetClause LimitClause? 
    l = ['LIMIT 3', 'OFFSET 3', 'LIMIT 3 OFFSET 3', 'OFFSET 3 LIMIT 3']
    printResults(l, 'LimitOffsetClauses', dump=False)
    
    # [24]    OrderCondition    ::=   ( ( 'ASC' | 'DESC' ) BrackettedExpression )  | ( Constraint | Var ) 
    l = ['ASC ("*Expression*")', 'DESC ("*Expression*")', 'isBLANK ("*Expression*")', '$var']
    printResults(l, 'OrderCondition', dump=False)
    
    # [23]    OrderClause       ::=   'ORDER' 'BY' OrderCondition+ 
    l = ['ORDER BY $var']
    printResults(l, 'OrderClause', dump=False)
    
    # [22]    HavingCondition   ::=   Constraint 
    l = ['<test:227> (DISTINCT "*Expression*",  "*Expression*",   "*Expression*" )', 'STRUUID()', 'ROUND ( "*Expression*")', 'isBLANK ("*Expression*")', 'COUNT ( * )', '("*Expression*")']
    printResults(l, 'HavingCondition', dump=False)
    
    # [21]    HavingClause      ::=   'HAVING' HavingCondition+ 
    l = ['HAVING <test:227> (DISTINCT "*Expression*",  "*Expression*",   "*Expression*" )']
    printResults(l, 'HavingClause', dump=False)
        
    # [20]    GroupCondition    ::=   BuiltInCall | FunctionCall | '(' Expression ( 'AS' Var )? ')' | Var 
    l = ['ROUND ( "*Expression*")', '<test:227> (DISTINCT "*Expression*",  "*Expression*",   "*Expression*" )', '( ("*Expression*") AS ?var )', '$var']
    printResults(l, 'GroupCondition', dump=False)
    
    # [19]    GroupClause       ::=   'GROUP' 'BY' GroupCondition+ 
    l = ['GROUP BY ROUND ( "*Expression*")', 'GROUP BY <test:227> (DISTINCT "*Expression*",  "*Expression*",   "*Expression*" ) ( ("*Expression*") AS ?var )']
    printResults(l, 'GroupClause', dump=False)
    
    # [18]    SolutionModifier          ::=   GroupClause? HavingClause? OrderClause? LimitOffsetClauses? 
    l = ['GROUP BY ROUND ( "*Expression*") HAVING <test:227> (DISTINCT "*Expression*",  "*Expression*",   "*Expression*" )']
    printResults(l, 'SolutionModifier', dump=False)
    
    # [17]    WhereClause       ::=   'WHERE'? GroupGraphPattern 
    l = ['{ SELECT * {} }', 'WHERE { SELECT * {} }']
    printResults(l, 'WhereClause', dump=False)    

    # [16]    SourceSelector    ::=   iri 
    l = ['<work:22?>','aA:Z.a', 'Z.8:AA', 'aA:', 'Z.8:', ':']
    printResults(l, 'SourceSelector', dump=False)
        
    # [15]    NamedGraphClause          ::=   'NAMED' SourceSelector 
    l = ['NAMED <work:22?>']
    printResults(l, 'NamedGraphClause', dump=False)
            
    # [14]    DefaultGraphClause        ::=   SourceSelector 
    l = ['<work:22?>','aA:Z.a', 'Z.8:AA', 'aA:', 'Z.8:', ':']
    printResults(l, 'DefaultGraphClause', dump=False)
        
    # [13]    DatasetClause     ::=   'FROM' ( DefaultGraphClause | NamedGraphClause ) 
    l = ['FROM <work:22?>', 'FROM NAMED <work:22?>']
    printResults(l, 'DatasetClause', dump=False)
    
    # [12]    AskQuery          ::=   'ASK' DatasetClause* WhereClause SolutionModifier 
    l = ['ASK { SELECT * {} } GROUP BY ROUND ( "*Expression*") HAVING <test:227> (DISTINCT "*Expression*",  "*Expression*",   "*Expression*" )',
         'ASK FROM <work:22?> { SELECT * {} } GROUP BY ROUND ( "*Expression*") HAVING <test:227> (DISTINCT "*Expression*",  "*Expression*",   "*Expression*" )']
    printResults(l, 'AskQuery', dump=False)    

    # [11]    DescribeQuery     ::=   'DESCRIBE' ( VarOrIri+ | '*' ) DatasetClause* WhereClause? SolutionModifier 
    l = ['DESCRIBE * FROM NAMED <work:22?> WHERE { SELECT * {} } GROUP BY ROUND ( "*Expression*")']
    printResults(l, 'DescribeQuery', dump=False)
                
    # [10]    ConstructQuery    ::=   'CONSTRUCT' ( ConstructTemplate DatasetClause* WhereClause SolutionModifier | DatasetClause* 'WHERE' '{' TriplesTemplate? '}' SolutionModifier ) 
    l = ['CONSTRUCT { _:test9.33 <test> $algebra, ($TriplesNode) ; a ?algebra, ($TriplesNode) } WHERE { SELECT * {} } GROUP BY ROUND ( "*Expression*")', 'CONSTRUCT FROM <work:22?> WHERE { } GROUP BY ROUND ( "*Expression*")']
    printResults(l, 'ConstructQuery', dump=False)
    
    # [9]     SelectClause      ::=   'SELECT' ( 'DISTINCT' | 'REDUCED' )? ( ( Var | ( '(' Expression 'AS' Var ')' ) )+ | '*' ) 
    l = ['SELECT REDUCED $var1 ?var2 (("*Expression*") AS $var3)']
    printResults(l, 'SelectClause', dump=False)
    
    # [8]     SubSelect         ::=   SelectClause WhereClause SolutionModifier ValuesClause 
    l = ['SELECT REDUCED $var1 ?var2 (("*Expression*") AS $var3) { SELECT * {} } GROUP BY ROUND ( "*Expression*") VALUES $S { <testIri> <testIri> }']
    printResults(l, 'SubSelect', dump=False)
    
    # [7]     SelectQuery       ::=   SelectClause DatasetClause* WhereClause SolutionModifier 
    l = ['SELECT REDUCED $var1 ?var2 (("*Expression*") AS $var3) { SELECT * {} } GROUP BY ROUND ( "*Expression*")']
    printResults(l, 'SelectQuery', dump=False)
        
    # [6]     PrefixDecl        ::=   'PREFIX' PNAME_NS IRIREF 
    l = ['PREFIX Z.8: <work:22?>']
    printResults(l, 'PrefixDecl', dump=False)
            
    # [5]     BaseDecl          ::=   'BASE' IRIREF 
    l = ['BASE <work:22?>']
    printResults(l, 'BaseDecl', dump=False)
    
    # [4]     Prologue          ::=   ( BaseDecl | PrefixDecl )* 
    l = ['BASE <work:22?> PREFIX Z.8: <work:22?>']
    printResults(l, 'Prologue', dump=False)
    
    # [3]     UpdateUnit        ::=   Update 
    l = ['BASE <prologue:22> PREFIX prologue: <prologue:33> LOAD <testIri> ; BASE <prologue:22> PREFIX prologue: <prologue:33>']
    printResults(l, 'UpdateUnit', dump=False)
        
    # [2]     Query     ::=   Prologue ( SelectQuery | ConstructQuery | DescribeQuery | AskQuery ) ValuesClause 
    l = ['BASE <work:22?> SELECT REDUCED $var1 ?var2 (("*Expression*") AS $var3) { SELECT * {} } GROUP BY ROUND ( "*Expression*") VALUES $S { <testIri> <testIri> }',
         'CONSTRUCT { _:test9.33 <test> $algebra, ($TriplesNode) ; a ?algebra, ($TriplesNode) } WHERE { SELECT * {} } GROUP BY ROUND ( "*Expression*")',
         'DESCRIBE * FROM NAMED <work:22?> WHERE { SELECT * {} } GROUP BY ROUND ( "*Expression*")',
         'ASK { SELECT * {} } GROUP BY ROUND ( "*Expression*") HAVING <test:227> (DISTINCT "*Expression*",  "*Expression*",   "*Expression*" )']
    printResults(l, 'Query', dump=False)
    
    # [1]     QueryUnit         ::=   Query 
    l = ['BASE <work:22?> SELECT REDUCED $var1 ?var2 (("*Expression*") AS $var3) { SELECT * {} } GROUP BY ROUND ( "*Expression*") VALUES $S { <testIri> <testIri> }',
         'CONSTRUCT { _:test9.33 <test> $algebra, ($TriplesNode) ; a ?algebra, ($TriplesNode) } WHERE { SELECT * {} } GROUP BY ROUND ( "*Expression*")',
         'DESCRIBE * FROM NAMED <work:22?> WHERE { SELECT * {} } GROUP BY ROUND ( "*Expression*")',
         'ASK { SELECT * {} } GROUP BY ROUND ( "*Expression*") HAVING <test:227> (DISTINCT "*Expression*",  "*Expression*",   "*Expression*" )']
    printResults(l, 'QueryUnit', dump=False)
    
    print('\nPassed')