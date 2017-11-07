# pyastbuilder

***Building an abstract syntax tree parser for your own domain specific language***

`pyastbuilder` is a python framework for building parsers that constructs an *object tree* that reflects the language's *abstract syntax tree* (AST), which can be pythonically navigated, searched and modified. Included in the package is one demonstrative example: a parser for the W3C SPARQL language, i.e., `sparqlparser.py`, which implements [Sparql v1.1](https://www.w3.org/TR/2013/REC-sparql11-query-20130321/). However, any other BNF-specified language can be facilitated.

Many specific or generic parsers exist, however the reason for developing `pyastbuilder` is ***TBD***


## Documentation
The Github environment provides for two locations to document the project: (i) README.md files like this in the code tree, and (ii) wiki pages. In addition, every source code will contain in-code comments. Here we will specify how these three locations for documentation has been used in this project, in order to provide for consistency for the reader, users of the project and developers to the project alike.

### README.md files
These will contain that part of the documentation that involves the generic design about the source code that is available in the particular part of the tree. This documentation is aimed at the developers of the project with the purpose to provide them with a thorough understanding of:

i. the design approach, 
ii. the internal logic of the principle process, 
iii. the structural framework of the project, and
iv. how these relate to the source tree structure with its different categories of classes that are grouped into distinct directories.

### Wiki pages

### In-code comments

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

