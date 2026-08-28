let
	TypeFromText		=	(	TypeName	as	text	)	as	type	=>
		let
			Result	=			if	TypeName	=	"Binary.Type"		then	Binary.Type
						else	if	TypeName	=	"Byte.Type"			then	Byte.Type
						else	if	TypeName	=	"Currency.Type"		then	Currency.Type
						else	if	TypeName	=	"Date.Type"			then	Date.Type
						else	if	TypeName	=	"DateTime.Type"		then	DateTime.Type
						else	if	TypeName	=	"DateTimeZone.Type"	then	DateTimeZone.Type
						else	if	TypeName	=	"Decimal.Type"		then	Decimal.Type
						else	if	TypeName	=	"Double.Type"		then	Double.Type
						else	if	TypeName	=	"Duration.Type"		then	Duration.Type
						else	if	TypeName	=	"Function.Type"		then	Function.Type
						else	if	TypeName	=	"Int16.Type"		then	Int16.Type
						else	if	TypeName	=	"Int32.Type"		then	Int32.Type
						else	if	TypeName	=	"Int64.Type"		then	Int64.Type
						else	if	TypeName	=	"Int8.Type"			then	Int8.Type
						else	if	TypeName	=	"List.Type"			then	List.Type
						else	if	TypeName	=	"Logical.Type"		then	Logical.Type
						else	if	TypeName	=	"Null.Type"			then	Null.Type
						else	if	TypeName	=	"Number.Type"		then	Number.Type
						else	if	TypeName	=	"Percentage.Type"	then	Percentage.Type
						else	if	TypeName	=	"Record.Type"		then	Record.Type
						else	if	TypeName	=	"Single.Type"		then	Single.Type
						else	if	TypeName	=	"Table.Type"		then	Table.Type
						else	if	TypeName	=	"Text.Type"			then	Text.Type
						else	if	TypeName	=	"Time.Type"			then	Time.Type
						else	if	TypeName	=	"Type.Type"			then	Type.Type
						else													Any.Type
		in	Result

,	tblAddGroupIndexColumn	=	(				tblInput			as	table	//	Table to which group index column is to be added
								,				lstSort				as	list	//	{{"Name", Order.Ascending}, {"ID", Order.Ascending}}
								,				lstGroupBy			as	list	//	{"Column1", "Column2"}
								,				txtIndexColumnName	as	text	//	"CustomerIndex"
								,	optional	intIndexBase		as	number	//	1
								,	optional	intIndexIncrement	as	number	//	1
								)	=>
		let
			tbl					=	Table.Buffer(tblInput)

		,	Schema				=	Table.Schema(tbl)

		,	Columns				=	Table.ColumnNames(
										tbl
									)

		,	ColumnTypes		=	List.Transform(
										List.Transform(
											Columns
										,	each	{	_
													,	Record.Field(
															Schema{[Name=_]}
														,	"TypeName"
														)
													}
										)
									,	(sublist) =>
											{	sublist{0}
											,	TypeFromText(sublist{1})
											}
									)

		,	AddIndex		=	Table.ExpandTableColumn(
									Table.Group(
										tbl
									,	lstGroupBy
									,	{	{	"Index"
											,	each	Table.RemoveColumns(
															Table.AddIndexColumn(
																Table.Sort(
																	_
																,	lstSort
																)
															,	txtIndexColumnName
															,	if	intIndexBase		=	null	then	1	else	intIndexBase
															,	if	intIndexIncrement	=	null	then	1	else	intIndexIncrement
															)
														,	lstGroupBy
														)
		
											,	Int64.Type
											}
										}
									)
								,	"Index"
								,	List.Combine(
										{	List.RemoveItems(
												Table.ColumnNames(
													tbl
												)
											,	lstGroupBy
											)
										,	{	txtIndexColumnName	}
										}
									)
								)

		,	RestoreColTypes	=	Table.TransformColumnTypes(
									AddIndex
								,	ColumnTypes
								)

		in	RestoreColTypes

in	tblAddGroupIndexColumn
