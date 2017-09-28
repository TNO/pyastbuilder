## Examples

Here are some examples of how to use Project.

### Example 1 - parsing a language element


What is being parsed in this example is the string `"work"@en-bf` for a rule called `RDFLiteral`. (The double quotes here are part of the [RDFLiteral (URL **TBD**)]() specification, and hence part of the string to be parsed.)

A fragment of the program follows:
```
	s = '"work" @en-bf'
	r = parser.RDFLiteral(s)
	print(r.dump())
```
This prints:
```
	[RDFLiteral] /"work" @en-bf/
	|  > lexical_form:
	|  [String] /"work"/
	|  |  [STRING_LITERAL2] /"work"/
	|  |  |  "work"
	|  > langtag:
	|  [LANGTAG] /@en-bf/
	|  |  @en-bf
```
Elements between `[` and `]` denote grammar rules matched. They are followed on the same line by a linear string representation of the string matched, between `/` and `/` delimiters.
Elements preceded by `>` are labels that can be used for navigating the parse object and for direct addressing of subelements. The remaining elements are the strings
matched by the terminal productions (these are, by (SPARQL) convention, denoted in capitals).

These labels are defined in the pattern using the `setResultsName()` method from pyparsing. The names used for the grammar rules are defined using the `setName()` method.

The relevant patterns for this example are, in the order in which they are defined in the source file, preceded by their EBNF definition taken from the SPARQL
specification document (https://www.w3.org/TR/2013/REC-sparql11-query-20130321/), and followed by the code that registers them with the parser:
```
	# [145]   LANGTAG   ::=   '@' [a-zA-Z]+ ('-' [a-zA-Z0-9]+)* 
	LANGTAG_e = r'@[a-zA-Z]+(\-[a-zA-Z0-9]+)*'
	LANGTAG = Regex(LANGTAG_e).setName('LANGTAG')
	parser.addElement(LANGTAG)
	
	# [157]   STRING_LITERAL2   ::=   '"' ( ([^#x22#x5C#xA#xD]) | ECHAR )* '"' 
	STRING_LITERAL2_e = r'"(({})|({}))*"'.format(ECHAR_e, r'[^\u0022\u005C\u000A\u000D]')
	STRING_LITERAL2 = Regex(STRING_LITERAL2_e).parseWithTabs().setName('STRING_LITERAL2')
	parser.addElement(STRING_LITERAL2)

	# [135]   String    ::=   STRING_LITERAL1 | STRING_LITERAL2 | STRING_LITERAL_LONG1 | STRING_LITERAL_LONG2 
	String = Group(STRING_LITERAL_LONG1 | STRING_LITERAL_LONG2 | STRING_LITERAL1 | STRING_LITERAL2).setName('String')
	parser.addElement(String)
			
	# [129]   RDFLiteral        ::=   String ( LANGTAG | ( '^^' iri ) )? 
	RDFLiteral = Group(String('lexical_form') + Optional(Group ((LANGTAG('langtag') | ('^^' + iri('datatype_uri')))))).setName('RDFLiteral')
	parser.addElement(RDFLiteral)
```
(To be extended)
