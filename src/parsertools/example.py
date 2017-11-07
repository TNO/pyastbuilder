'''
Created on 1 apr. 2016

@author: jeroenbruijning
'''

#
# Example program for the use of parsertools
#

# Running a SPARQL SPARQLParser

from parsertools.parsers.sparqlparser import parseQuery

# Parsing a complete query
# For this, only the import parseQuery is needed

querystring = '''
ASK { 
    SELECT * {}
    } 
    GROUP BY ROUND ("*Expression*")
    HAVING <test:227>
    (DISTINCT "*Expression*", "*Expression*", "*Expression*" )
'''

query = parseQuery(querystring)

print(query.dump())

# parseQuery above is actually a convenience function. It does some preprocessing (such as stripping
# comments from the query) and some postprocessing (to perform additional checks on the query that are
# part of the SPARQL specification outside the EBNF grammar). In between the query string is parsed against 
# a top level production of the grammar.
# For this, an actual SPARQL SPARQLParser object is used. It has attributes for every production in the grammar (except for
# the "whitespace" production which is not needed with pyparsing).
# Such an attribute can be used to parse a valid string for that production. This is the basic mode of parsing.

# As an example, below a string is parsed against the RDFLiteral production.
# For this, we need to import sparqlparser.

from parsertools.parsers.sparqlparser import SPARQLParser

rdfliteral = '"work"@en-bf'

rdf = SPARQLParser.RDFLiteral(rdfliteral)

print(rdf.dump())

# A parsed element can be searched for elements conforming to a specified pattern.
# Any of the following can be matched, in any combination:
# - type (class)
# - label
# - string content
# Any of these conditions can be None, which acts as a wildcard.
# In addition, a "labeledOnly" flag can be specified. If True, only elements with an assigned label will qualify.
# The default for this flag is False (all elements considered).

wheres = query.searchElements(label = None, element_type=SPARQLParser.WhereClause, value=None)
for w in wheres:
    print()
    print(w.dump())
    
# A (sub)element can be changed in place through the updateWith method.
# The element can be found through searchElements, or it can be accessed through dot access.
# An example of the latter:

print(rdf.lexical_form) # prints "work" (the double quotes are part of the string)
rdf.lexical_form.updateWith('"play"')
print(rdf.dump()) # lexical_form labeled element changed in place

# Many other methods are available, and documented in docstrings. See "base.py":

print(help('base'))


