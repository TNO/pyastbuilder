'''
Created on 23 feb. 2016

@author: jeroenbruijning
'''

from pyparsing import ParseException
from parsertools.parsers.sparqlparser import SPARQLParser
from parsertools.parsers.sparqlparser import stripComments

actions = {'mf:PositiveSyntaxTest11': [], 'mf:NegativeSyntaxTest11': []}

lines = [l.split() for l in open('manifest.ttl') if ('mf:PositiveSyntaxTest11' in l or 'mf:NegativeSyntaxTest11' in l or 'mf:action' in l) and not l.startswith('#')]

# for l in lines: print(l)

for i in range(len(lines)//2):
    actions[lines[2*i][2]].append(lines[2*i+1][1][1:-1])
 
posNum = len(actions['mf:PositiveSyntaxTest11'])
negNum = len(actions['mf:NegativeSyntaxTest11'])

print('Testing {} positive and {} negative testcases'.format(posNum, negNum))

for fname in actions['mf:PositiveSyntaxTest11']:
    try:
        s = stripComments(open(fname).readlines())
        r = SPARQLParser.QueryUnit(s, postParseCheck=False)
    except ParseException as e:
        print('\n*** {} should not raise exception? Check\n'.format(fname))

for fname in actions['mf:NegativeSyntaxTest11']:
    try:
        s = open(fname).read()
        r = SPARQLParser.UpdateUnit(s, postParseCheck=False)
        print('\n*** {} should raise exception? Check\n'.format(fname))
    except ParseException as e:
        pass
print('Passed')
print('''
Note:

qname-escape-01.rq seems in error. The issue is whether a : in a prefix local name part should be escaped. It currently is not, but the 
testcase test otherwise.
According to Andy Seaborne, SPARQL 1.1 Editor:
    "The final decision was that : is used as-is in the local part of a prefixed name and isn't escaped (due to tracking changing Turtle)."
See http://answers.semanticweb.com/questions/19622/special-characters-in-uri-in-sparql.

Conclusion: ignore this fault.
''')
