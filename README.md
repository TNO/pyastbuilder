# pyastbuilder

***Building an abstract syntax tree parser for your own domain specific language***

`pyastbuilder` is a python framework for building parsers that constructs an *object tree* that reflects the language's *abstract syntax tree* (AST), which can be pythonically navigated, searched and modified. Included in the package is one demonstrative example: a parser for the W3C SPARQL language, i.e., `sparqlparser.py`, which implements [Sparql v1.1](https://www.w3.org/TR/2013/REC-sparql11-query-20130321/). However, any other BNF-specified language can be facilitated.

Many specific or generic parsers exist, however the reason for developing `pyastbuilder` is that often the parsing is considered a streaming, dynamic process in which several hooks exist to which one can attach ones own code, as opposed to the generation of a static, abstract syntax tree of the electronic "document", with an API for its access for post-parsed processing. 

## Documentation 
### Documentation principle
We follow our following
> DESIGN PRINCIPLE: Be Predictive. Define clear criteria for the location of documentation. What part of the documentation is put in the README files, what parts can be found on the wiki pages, and what information do you put in-code as comments? Define and document your documentation criteria, preferably in the principle piece of documentation that your user or developer will hit, which probably is the project's README.md file.

### Documentation criteria
We therefore follow the following criteria regarding documentation:
1. All aspects regarding the *use* of the software, as well as its *installation*, including a sanity test for establishing correct installation, will be documented on this WIKI. 
1. All aspects regarding the *development of Your Particular Parser* for your own EBNF-defined language, will be documented on the wiki as separate manual.
1. All *description of source code files* that are involved with `pyastparser`, will be documented as README.md files in every folder of the source tree.
1. *Design documentation* about `pyastbuilder`, as well as all detailed, *code-specific documentation* will be available through [python pydoc](https://docs.python.org/devguide/documenting.html) in the [reStructuredText (reST)](http://docutils.sourceforge.net/rst.html) markup syntax.

### Documentation sources
#### README.md files
These will contain that part of the documentation that involves the generic design about the source code that is available in the particular part of the tree. This documentation is aimed at the developers of the project with the purpose to provide them with a thorough understanding of:

* the design approach, 
* the internal logic of the principle process, 
* the structural framework of the project, and
* how these relate to the source tree structure with its different categories of classes that are grouped into distinct directories.

#### Wiki pages
A complete overview of the wiki documentation can be found at the [wiki Home page](wiki). One can expext the following entries:
1. **User Manual**, where descriptions, how-to's and patterns can be found with regards to using the `sparqlparser` as library in your own python code, as well as any other out-of-the-box `xxxparser` that might be provided in the future of this project. Since any other `xxxparser` will be based on this same project, we can safely assume to find many references to very similar or even identical use-cases from the `sparqlparser`. 
1. **Parser Development Manual**, which will document the generic steps to take in order to create your own EBNF-specified language parser. Whenever you have created your own `xxxparser`, please share this with this project and provide for your own Chapter in our User Manual about the use of this parser. However: **Do Not Duplicate documentation**, but use the `sparqlparser` manual as reference manual instead.

## Contributing

Please read [CONTRIBUTING.md](docs/Contributing.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/TNO/pyastbuilder/tags). 

## Authors

* **Jeroen Bruijning** - *Father of idea, main author* - [parser](https://github.com/Jeroen537/parser)
* **Barry Nouwt** (TNO) - *Restructuring in compliance with Code of Conduct, maintenance*
* **Paul Brandt** (TNO) - *User of project* - [mediator](https://github.com/plbt5/Mediator)


See also the list of [contributors](https://github.com/TNO/pyastbuilder/contributors) who participate(d) in this project.

## License

This project is licensed under the XXX **TBD** License - see the [LICENSE.md](docs/LICENSE.md) file for details

## Acknowledgments

* Hat tip to Paul McGuire, the author of [pyparsing](http://pyparsing.wikispaces.com/). We have left the exhaustive parsing work to this package and build our package on top of that.
* Support for URIs and IRIs (their prefix processing and base expansion) and conformance to RFC 3987 would not have got at this level of quality without the excellent work of Daniel Gerber, the author of [rfc3987](https://github.com/dgerber/rfc3987): Parsing and validation of URIs (RFC 3896) and IRIs (RFC 3987).

