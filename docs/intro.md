## What is pyAST?

pyAST is a python framework for building parsers that construct an *abstract syntax tree* (AST), which can be pythonically browsed, searched and modified. We have included a parser for SPARQL statements, i.e., sparqlparser.py, which implements [https://www.w3.org/TR/2013/REC-sparql11-query-20130321/](Sparql v1.1)

Many specific or generic parsers exist, however the reason for developing pyAST <TBD>

### Getting Started

#### Installation
Use of pyAST is based on python code integration, i.e., use of the libraries that pyAST provides. Installation is (to be) supported in two distinct ways: either by cloning the sources from Git and make them available to your code base, or installing the code with 'pip'. 
Both ways result in the same setup: having the sources available in your python path.

**Setup by Git**

1. Just clone this project
1. Make it available on your python path 

**Setup by 'pip'** (This method *YET TO BE PROVIDED*)

#### Validating its installation

Validating that pyAST has been correctly installed is by means of calling 

### Demo

Here's a demo of what Project looks like once it's set up. We use the sparqlparser for that.



<pre><code>
from parsertools.parsers.sparqlparser import parseQuery

# Parsing a complete query
# For this, only the import parseQuery is needed

# Define a valid sparql SELECT-query
querystring = '''
ASK { 
    SELECT * {}
    } 
    GROUP BY ROUND ("*Expression*")
    HAVING <test:227>
    (DISTINCT "*Expression*", "*Expression*", "*Expression*" )
'''

# Parse the query string
query = parseQuery(querystring)

# Show its AST
print(query.dump())
</code></pre>

<div class="hs-doc-callout hs-doc-callout-info">
<h4>Demo Notes</h4>
<p>Note that this demo has demo notes.</p>
</div>

### More Information

Check out the [docs/API/1-Overview.md](API Documentation) for more information.