# pyAST

pyAST is a python framework for building parsers that constructs an *object tree* that reflects the language's *abstract syntax tree* (AST), which can be pythonically navigated, searched and modified. Included in the package is one demonstrative example: a parser for the W3C SPARQL language, i.e., `sparqlparser.py`, which implements [Sparql v1.1](https://www.w3.org/TR/2013/REC-sparql11-query-20130321/). However, any other BNF-specified language can be facilitated.

Many specific or generic parsers exist, however the reason for developing pyAST is ***TBD***

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

You need to install the following software:
* python 
    * v3.3 (or higher); 
    * v2.7 (or higher) ["wide builds"](https://www.python.org/dev/peps/pep-0261/) for full Unicode support.
* [pyparsing](http://pyparsing.wikispaces.com/)
* [rfc3987](https://pypi.python.org/pypi/rfc3987)

### Installing

Use of pyAST is based on python code integration, i.e., use of the libraries that pyAST provides. Installation is (to be) supported in two distinct ways: either by cloning the sources from Git and make them available to your code base, or installing the code with `pip`. 
Both ways result in the same setup: having the sources available in your python path.

*Setup by Git*

1. Just clone this project in your local directory, i.e.,
```
$ cd /path/to/my/git/directory
$ git clone https://github.com/TNO/pyAST.git
```

2. Make it available on your python path 
```
Example to be included
```

*Setup by `pip`*

This method *YET TO BE PROVIDED*

### Testing your installation
Here's a demo of what pyAST can do once it has been set up. We use the `sparqlparser` for that.

First, create a python source file; you can call it `sparqltest.py` and paste the following python code:

```python
from parsertools.parsers.sparqlparser import parseQuery

# Parsing a complete query
# For this, only the import parseQuery is needed

# Define a valid sparql SELECT-query
querystring = '''
ASK { 
    SELECT * {}
    } 
'''

# Parse the query string
query = parseQuery(querystring)

# Show its AST
print(query.dump())
```

Now, run the python script you've just created:
```
$ python sparqltest.py
```

If your installation was correct, it will produce the following output (or very similar to it):
```
parsertools version 0.2.6, build 2676
[QueryUnit] /ASK { SELECT * { } }/
|  [Query] /ASK { SELECT * { } }/
|  |  > prologue:
|  |  [Prologue] //
|  |  [AskQuery] /ASK { SELECT * { } }/
|  |  |  [ASK] /ASK/
|  |  |  |  ASK
|  |  |  > where:
|  |  |  [WhereClause] /{ SELECT * { } }/
|  |  |  |  [GroupGraphPattern] /{ SELECT * { } }/
|  |  |  |  |  [LCURL] /{/
|  |  |  |  |  |  {
|  |  |  |  |  > pattern:
|  |  |  |  |  [SubSelect] /SELECT * { }/
|  |  |  |  |  |  [SelectClause] /SELECT */
|  |  |  |  |  |  |  [SELECT] /SELECT/
|  |  |  |  |  |  |  |  SELECT
|  |  |  |  |  |  |  [ALL_VALUES] /*/
|  |  |  |  |  |  |  |  *
|  |  |  |  |  |  > where:
|  |  |  |  |  |  [WhereClause] /{ }/
|  |  |  |  |  |  |  [GroupGraphPattern] /{ }/
|  |  |  |  |  |  |  |  [LCURL] /{/
|  |  |  |  |  |  |  |  |  {
|  |  |  |  |  |  |  |  > pattern:
|  |  |  |  |  |  |  |  [GroupGraphPatternSub] //
|  |  |  |  |  |  |  |  [RCURL] /}/
|  |  |  |  |  |  |  |  |  }
|  |  |  |  |  |  [SolutionModifier] //
|  |  |  |  |  |  [ValuesClause] //
|  |  |  |  |  [RCURL] /}/
|  |  |  |  |  |  }
|  |  |  [SolutionModifier] //
|  |  [ValuesClause] //
```
The first line identifies the version and build of the tool. The rest of the output presents the parsed AST. Indeed, dumping an AST results in a rather verbose tree, but you will find it very useful as reference when building your particular code. 

### More Information

Check out the [API Documentation](docs/API/1-Overview.md) for more information.

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Documentation
The Github environment provides for two locations to document the project: (i) README.md files like this in the code tree, and (ii) wiki pages. In addition, every source code will contain in-code comments. Here we will specify how these three locations for documentation has been used in this project, in order to provide for consistency for the reader, users of the project and developers to the project alike.

### README.md files
These will contain that part of the documentation that involves the generic design about the source code that is available in the particular part of the tree. This documentation is aimed at the developers of the project with the purpose to provide them with a thorough understanding of:

i. the design approach, 
ii. the internal logic of the principle process, 
iii. the structural framework of the project, and
iv. how these relate to the source tree structure with its different categories of classes that are grouped into distinct directories.

## Contributing

Please read [CONTRIBUTING.md](docs/Contributing.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/TNO/pyAST/tags). 

## Authors

* **Jeroen Bruijning** - *Initial work* - [parser](https://github.com/Jeroen537/parser)

See also the list of [contributors](https://github.com/TNO/pyAST/contributors) who participate(d) in this project.

## License

This project is licensed under the XXX **TBD** License - see the [LICENSE.md](docs/LICENSE.md) file for details

## Acknowledgments

* Hat tip to Paul McGuire, the author of [pyparsing](http://pyparsing.wikispaces.com/). We have left the exhaustive parsing work to this package and build our package on top of that.
* Support for URIs and IRIs (their prefix processing and base expansion) and conformance to RFC 3987 would not have got at this level of quality without the excellent work of Daniel Gerber, the author of [rfc3987](https://github.com/dgerber/rfc3987): Parsing and validation of URIs (RFC 3896) and IRIs (RFC 3987).

