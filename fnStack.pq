//	fnStack
let
	fn	=	()	=>
		let
			// Initialize the stack (empty list)
			lstStack	=	{}

			// Push method: adds a new item to the stack
		,	fnPush		=	(anyItem)	=>
				List.Combine(
					{	{anyItem}
					,	lstStack
					}
				)

			// Pop method: removes and returns the top item from the stack
		,	fnPop		=	()		=>
				let
					anyItem		=	List.First(lstStack)				// Retrieve the top item
				,	lstNewStack	=	List.RemoveFirstN(lstStack, 1)		// Remove the top item
				in
					[	Stack	=	lstNewStack
					,	Top		=	anyItem
					]

			// Peek method: returns the top item without removing it
		,	fnPeek		=	()		=>
				List.First(lstStack)

			// IsEmpty method: checks if the stack is empty
		,	fnIsEmpty	=	()		=>
				List.IsEmpty(lstStack)
		in
			// Return the stack record with methods and properties
			[	Stack	=	lstStack	// The stack (initially empty)
			,	Push	=	fnPush		// Push method
			,	Pop		=	fnPop		// Pop method
			,	Peek	=	fnPeek		// Peek method
			,	IsEmpty	=	fnIsEmpty	// IsEmpty method
			]
in
	fn
