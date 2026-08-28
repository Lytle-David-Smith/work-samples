// fnMySQLSelectFromValues
let
	sqlValuesFromRecord	=
		(	rec								as	record
		)						=>
			let				
				txtValues	=		"row("
								&	Text.Combine(
										List.Transform(
											Record.ToList(rec)
										,	each
														if	Type.Is(Value.Type(_), type number		) then	Text.From(_)
												else	if	Type.Is(Value.Type(_), type text		) then	"'" & Text.Replace(_, "'", "''") & "'"
												else	if	Type.Is(Value.Type(_), type datetime	) then	"'" & DateTime.ToText(_, "yyyy-MM-dd hh:mm:ss") & "'"
												else	if	Type.Is(Value.Type(_), type date		) then	"'" & Date.ToText(_, "yyyy-MM-dd") & "'"
												else	if	Type.Is(Value.Type(_), type time		) then	"'" & Time.ToText(_, "hh:mm:ss") & "'"
												else														"null"
										)
									,	", "
									)
								&	")"
			in	txtValues
			
,	sqlSelectValues	=
		(				tblValues			as	table
		,	optional	blnDistinct			as	logical		//	Default is false.
		,	optional	blnIncludeEmptyRows	as	logical		//	Default is false.
		,	optional	txtInto				as	text		//	Default is none.
		)				=>
			let
				tblValuesDistinct	=	if		blnDistinct	<>	null
											and	blnDistinct
											then
												Table.Distinct(tblValues)
											else
												tblValues

			,	sqlSelect			=	if		Table.RowCount(tblValues)	=	0
												then	null
										else if	txtInto	<>	null
												then	"
		drop table if exists " & txtInto & "

		select	*
		into	" & txtInto & "
"											else	"
		select	*"

			,	sqlSelectValues		=	sqlSelect
									&	"
		from	(
			values
				"						&	Text.Combine(
												Table.TransformRows(
													tblValuesDistinct
												,	each	sqlValuesFromRecord(_)
												)
											,	"
			,	"							)
										&	"
		)	as	`Values`(
					"					&	Text.Combine(
												List.Transform(
													Table.ColumnNames(
														tblValues
													)
												,	each	"`" & _ & "`"
												)
											,	"
				,	"
											)
										&	"
				)"						
										&	(	if	(	blnIncludeEmptyRows		=	null
													or	not blnIncludeEmptyRows
												)	then
															"
		where
			not	(	"									&	Text.Combine(
																List.Transform(
																	Table.ColumnNames(
																		tblValues
																	)
																,	each	"`" & _ & "`	is null"
																)
															,	"
				and	"									)
													&	"
			)"									else	""
											)
			in	sqlSelectValues
in
	sqlSelectValues
