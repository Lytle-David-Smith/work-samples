let
	TabsToSpaces	=	(txt	as	text)	as	text	=>
		let
			tabWidth		=	4
		,	parts			=	Text.Split(txt, "#(tab)")
		,	lst				=	List.Accumulate(
									List.RemoveFirstN(parts, 1)
								,	{List.First(parts)} // Start with the first part
								,	(state, part) => 
										let
											previousLength	=	Text.Length(
																	Text.Combine(state, "")
																)
										,	padding			=	tabWidth - Number.Mod(previousLength, tabWidth)
										,	newPart			=	Text.Repeat(" ", padding) & part
										in
											List.Combine({state, {newPart}})
								)
		,	result			=	Text.Combine(lst, "")
		in
			result

,	fn				=	(txt	as	text)	as	text	=>
		let
			lines	=	Text.SplitAny(txt, "#(cr)#(lf)")
		,	lst		=	List.Accumulate(
							List.RemoveFirstN(
								lines
							,	1
							)
						,	{List.First(lines)}
						,	(state, current) => (
								List.Combine({
									state
								,	{TabsToSpaces(current)}
								})
							)
						)
		,	result	=	Text.Combine(lst, "#(lf)")
		in
			result
in
	fn
