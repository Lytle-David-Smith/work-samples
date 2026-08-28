// fnQueryProfile_ServerSideSQL
let
	ColumnCTEs	=	(	txtDatabase	as	text
					,	txtSchema	as	text
					,	txtTable	as	text
					,	tblSchema	as	table
					,	sql			as	text
					,	index		as	number
					)	=>
		let
			colName	=	Record.Field(tblSchema{index}, "Name")
		,	colType	=	Record.Field(tblSchema{index}, "Kind")
		,	colSQL	=	sql & "
				,	uniq_vals_" & Text.From(index) & "	as	(
						select	[" & colName & "]
						from	src
						group by
							[" & colName & "]
						having
							count(*)	=	1
					)
				,	uniq_ct_" & Text.From(index) & "	as	(
						select
							count(*)	as	val_ct
						from	uniq_vals_" & Text.From(index) & "
					)
				,	datatype_" & Text.From(index) & "	as	(
						select	[DATA_TYPE]	as	[Data Type]
						from	[" & txtDatabase & "].[INFORMATION_SCHEMA].[COLUMNS]
						where
							[TABLE_SCHEMA]	=	'" & txtSchema & "'
						and	[TABLE_NAME]	=	'" & txtTable & "' 
						and	[COLUMN_NAME]	=	'" & colName & "'
					)
				,	profile_" & Text.From(index) & "	as	(
						select
						top	1
							'" & colName & "'	as	[Column]
						,	" & Text.From(index+1) & "	as	[Ordinal Position]
						,	[Data Type]
						,	(	select	count(*)
								from	src
							)			as	[Total Count]
						,	count(distinct [" & colName & "]) as [Distinct]
						,	(	select	val_ct
								from	uniq_ct_" & Text.From(index) & "
							)			as	[Unique]
						,	(	select	count(*)
								from	src
								where	[" & colName & "]	is null
							)			as	[Nulls]
						,	(	select	count(*)
								from	src
								where	"	&	(	if	colType = "text"
													then	"nullif([" & colName & "], '')	is null"
													else	"[" & colName & "]	is null"
												)
											&	"
							)			as	[Empty]
						,	" & (if colType <> "number" then "null" else "min([" & colName & "])") & " as [Min]
						,	" & (if colType <> "number" then "null" else "max([" & colName & "])") & " as [Max]
						,	" & (if colType <> "number" then "null" else "avg(convert(float, [" & colName & "]))") & " as [Average]
						,	(	select	top 1
									count(*)	as	[Mode Freq]
								from	src
								group by
									[" & colName & "]
								order by
									count(*)	desc
							)			as	[Mode Freq]
						,	(	select	top 1
									count(*)	as	[Mode Freq]
								from	src
								group by
									[" & colName & "]
								order by
									count(*)
							)			as	[Anti-Mode Freq]
						,	min(len([" & colName & "])) as [Min Length]
						,	max(len([" & colName & "])) as [Max Length]
						,	avg(len([" & colName & "])) as [Average Length]
						from			datatype_" & Text.From(index) & "
							left join	src			on	1	=	1
						group by	[Data Type]
					)
"
		in
			colSQL
					
,	ColumnQuery	=	(	Schema	as	table
					,	sql		as	text
					,	index	as	number
					)	=>
		let
			colName	=	Record.Field(Schema{index}, "Name")
		,	colType	=	Record.Field(Schema{index}, "Kind")
		,	colSQL	=	sql & (
							if index = 0 then "
						"	else	"
				union	" 
						) & "select	*	from	profile_" & Text.From(index)
		in
			colSQL
					
,	TblProfile	=	(	Server		as	text
					,	Database	as	text
					,	Schema		as	text
					,	Table		as	text
					)	=>
		let
//			txtTable	=	"[" & Server & "].[" & Database & "].[" & Schema & "].[" & Table & "]"
			txtTable	=	"[" & Database & "].[" & Schema & "].[" & Table & "]"
		,	sqlQuery	=	Text.Format("
						select	* 
						from #{0} (nolock)", {txtTable})
		,	tblSchema	=	Table.Schema(fnODBC_Table(Server, Database, Schema, Table, 0))
		,	sqlInit		=	"
				with
					src			as	(" & sqlQuery & "
					)
"
		,	sqlCTEs		=	List.Accumulate({0..(Table.RowCount(tblSchema)-1)}, sqlInit, (state, current) => ColumnCTEs(Database, Schema, Table, tblSchema, state, current))
		,	sqlMain		=	List.Accumulate({0..(Table.RowCount(tblSchema)-1)}, sqlCTEs, (state, current) => ColumnQuery(tblSchema, state, current))
		in
			sqlMain
in
	TblProfile
