'''
Created on 23 feb. 2016

@author: jeroenbruijning
'''
from pyparsing import ParseException
from parsertools.parsers.sparqlparser import SPARQLParser
from parsertools.parsers.sparqlparser import stripComments

actions = {'mf:PositiveUpdateSyntaxTest11': [], 'mf:NegativeUpdateSyntaxTest11': []}

lines = [l.split() for l in open('manifest.ttl') if ('mf:PositiveUpdateSyntaxTest11' in l or 'mf:NegativeUpdateSyntaxTest11' in l or 'mf:action' in l) and not l.startswith('#')]


for i in range(len(lines)//2):
    actions[lines[2*i][2]].append(lines[2*i+1][1][1:-1])
 
posNum = len(actions['mf:PositiveUpdateSyntaxTest11'])
negNum = len(actions['mf:NegativeUpdateSyntaxTest11'])

print('Testing {} positive and {} negative testcases'.format(posNum, negNum))

for fname in actions['mf:PositiveUpdateSyntaxTest11']:
    try:
        s = stripComments(open(fname).readlines())
        r = SPARQLParser.UpdateUnit(s, postParseCheck=False)
    except Exception as e:
        print('\n*** {} should not raise exception? Check'.format(fname))

for fname in actions['mf:NegativeUpdateSyntaxTest11']:
    try:
        s = open(fname).read()
        r = SPARQLParser.UpdateUnit(s, postParseCheck=False)
        print('\n*** {} should raise exception? Check'.format(fname))
    except Exception as e:
        pass
print('\nPassed')
print('''
Note:

syntax-update-01.ru and syntax-ypdate-02.ru seem to be in error. The IRIs from their BASE clause contain a '#' and therefore seem not to be an absolute IRIs,
as required by the SPARQL 1.1 definition.

A question has been asked on answers.semanticweb.com.

For the time being, ignore these errors.

syntax-update-54.ru seems in error. The syntax seems to be OK; the issue is that a bNode label is used across operations,
which is a separate issue than conformance to the EBNF. 
Apart from that, the status is dawgt:NotClassified, as opposed to all other testcases which are dawgt:Approved.

Conclusion: ignore this fault.
''')