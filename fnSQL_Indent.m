//	fnSQL_Indent
let
	fn = (txtCode as text) as text =>
	let
		// Define the list of pairs of text expressions
		expressionPairs = {
			{"(", ")"}
		,	{"[", "]"}
		,	{"{", "}"}
		}

		// Trim whitespace from the input text
	,	trimmedCode = Text.Trim(txtCode)

		// Initialize indent level
	,	ProcessLine = (line as text, indentLevel as number) as record =>
			let
				updatedLine = List.Accumulate(
					expressionPairs
				,	line
				,	(currentLine, pair) =>
						let
							openExpression	=	pair{0}
						,	closeExpression	=	pair{1}

							// Insert line feed and additional indent for open expression
						,	afterOpen	=	Text.Replace(
								currentLine
							,	openExpression
							,		openExpression
								&	"#(lf)"
								&	Text.Repeat("#(tab)", indentLevel + 1)
							)

							// Insert line feed and reduced indent for close expression
						,	afterClose	=	Text.Replace(
								afterOpen
							,	closeExpression
							,		"#(lf)"
								&	Text.Repeat(
										"#(tab)"
									,	if	indentLevel - 1	<	0	then	0
										else								indentLevel - 1
									)
								&	closeExpression
							)
						in
							afterClose
				)

				// Adjust indent level for this line
			,	newIndentLevel = List.Accumulate(
					expressionPairs
				,	indentLevel
				,	(currentIndent, pair) =>
						let
							openExpression	=	pair{0}
						,	closeExpression	=	pair{1}

						,	incrementIndent	=	if	Text.Contains(line, openExpression)		then	currentIndent	+	1	else	currentIndent
						,	decrementIndent	=	if	Text.Contains(line, closeExpression)	then	incrementIndent	-	1	else	incrementIndent
						in
							decrementIndent
				)
			in
				[UpdatedLine = updatedLine, NewIndentLevel = newIndentLevel]

		// Split text into lines and process each line
	,	lines						=	Text.Split(trimmedCode, "#(lf)")
	,	processedLinesAndIndents	=	List.Accumulate(
			lines
		,	[ProcessedLines = {}, CurrentIndent = 0]
		,	(state, line) =>
				let
					result = ProcessLine(line, state[CurrentIndent])
				in
					[	ProcessedLines	=	List.Combine({state[ProcessedLines], {result[UpdatedLine]}})
					,	CurrentIndent	=	result[NewIndentLevel]
					]
		)

		// Combine the processed lines back into a single text
	,	result = Text.Combine(processedLinesAndIndents[ProcessedLines], "#(lf)")
	in
		result
in
	fn


//	fnSQL_Indent
let
	fn = (txtCode as text) as text =>
	let
		//	Define the list of pairs of text expressions.
		lstExpressions	=	{	{"/*", "*/"}
							,	{"--", "#(lf)"}
							,	{"(", ")"}
							,	{"[", "]"}
							,	{"{", "}"}
							}

		//	Trim whitespace from the input text.
	,	txtTrimmed		=	Text.Trim(Text.Replace(txtCode, "#(cr)", ""))

		//	Initialize stack.
	,	lstStack		=	{}

		// Initialize indent level
	,	IndentLine	=	(	txtLine		as	text
						,	intIndent	as	number
						,	lstStack	as	list
						)	as	record	=>
			let
				intCursor		=	0
			,	txtIndented		=	List.Last(
										List.Generate(
											()	=>	[	txtLine		=	txtLine
													,	intCursor	=	intCursor
													,	intIndent	=	intIndent
													,	lstStack	=	lstStack
													]
										,	each	intCursor	<	Text.Length(txtLine)	//	Condition to continue
										,	each	
											each [Total = [Total] + [Counter],			// Update logic
												  Counter = [Counter] + 1]
										)
									)

			,	txtIndented		=	List.Accumulate(
										lstExpressions
									,	[	txtLine		=	txtLine
										,	intCursor	=	intCursor
										,	intIndent	=	intIndent
										]
									,	(recState, pair) =>
											let
												openExpression	=	pair{0}
											,	closeExpression	=	pair{1}
	
												// Insert line feed and additional indent for open expression
											,	afterOpen	=	Text.Replace(
													recState
												,	openExpression
												,		openExpression
													&	"#(lf)"
													&	Text.Repeat("#(tab)", intIndent + 1)
												)
	
												// Insert line feed and reduced indent for close expression
											,	afterClose	=	Text.Replace(
													afterOpen
												,	closeExpression
												,		"#(lf)"
													&	Text.Repeat(
															"#(tab)"
														,	if	intIndent - 1	<	0	then	0
															else								intIndent - 1
														)
													&	closeExpression
												)
											in
												afterClose
									)

				// Adjust indent level for this line
			,	newIndentLevel	=	List.Accumulate(
										lstExpressions
									,	intIndent
									,	(currentIndent, pair) =>
											let
												openExpression	=	pair{0}
											,	closeExpression	=	pair{1}

											,	incrementIndent	=	if	Text.Contains(txtLine, openExpression)		then	currentIndent	+	1	else	currentIndent
											,	decrementIndent	=	if	Text.Contains(txtLine, closeExpression)	then	incrementIndent	-	1	else	incrementIndent
											in
												decrementIndent
									)
			in
				[	txtIndented	=	txtIndented
				,	intIndent	=	newIndentLevel
				]

		// Split text into lines and process each line
	,	lstLines	=	Text.Split(txtTrimmed, "#(lf)")
	,	lstIndented	=	List.Accumulate(
							lstLines
						,	[	lstIndented	=	{}
							,	intIndent	=	0
							]
						,	(recState, txtLine) =>
								let
									recIndented	=	IndentLine(
														txtLine
													,	recState[intIndent]
													)
								in
									[	lstIndented	=	List.Combine({
															recState[lstIndented]
														,	{recIndented[txtIndented]}
														})
									,	intIndent	=	recIndented[intIndent]
									]
						)

		// Combine the processed lines back into a single text
	,	txtResult	=	Text.Combine(
							lstIndented[lstIndented]
						,	"#(lf)"
						)
	in
		txtResult
in
	fn
