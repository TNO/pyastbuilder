# pyAST

pyAST is a python framework for building parsers that construct an *abstract syntax tree* (AST), which can be pythonically browsed, searched and modified. We have included a parser for SPARQL statements, i.e., sparqlparser.py, which implements [Sparql v1.1](https://www.w3.org/TR/2013/REC-sparql11-query-20130321/)

Many specific or generic parsers exist, however the reason for developing pyAST is ***TBD***

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

You need to install the following software:
* python 3.3 or higher (***TBC***)


### Installing

Use of pyAST is based on python code integration, i.e., use of the libraries that pyAST provides. Installation is (to be) supported in two distinct ways: either by cloning the sources from Git and make them available to your code base, or installing the code with `pip`. 
Both ways result in the same setup: having the sources available in your python path.

*Setup by Git*

1. Just clone this project in your local directory, i.e.,
```
$ cd /path/to/my/git/directory
$ git clone https://github.com/TNO/pyAST.git
```

1. Make it available on your python path 
```
Example to be included
```

*Setup by `pip`*
This method *YET TO BE PROVIDED*


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


## Contributing

Please read [CONTRIBUTING.md](https://github.com/TNO/pyAST/tree/master/docs/Contributing.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/TNO/pyAST/tags). 

## Authors

* **Jeroen Bruijning** - *Initial work* - [parser](https://github.com/Jeroen537/parser)

See also the list of [contributors](https://github.com/TNO/pyAST/contributors) who participate(d) in this project.

## License

This project is licensed under the XXX **TBD** License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to Paul McGuire, the author of [pyparsing](http://pyparsing.wikispaces.com/). We have left the exhaustive parsing work to this package and build our package on top of that.
* Support for URIs and IRIs (their prefix processing and base expansion) and conformance to RFC 3987 would not have got at this level of quality without the excellent work of Daniel Gerber, the author of [rfc3987](https://github.com/dgerber/rfc3987): Parsing and validation of URIs (RFC 3896) and IRIs (RFC 3987).
* etc

