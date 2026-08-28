// Files on X
let
	Source = Csv.Document(File.Contents("H:\Files on X.csv"),[Delimiter=",", Columns=6, Encoding=1252, QuoteStyle=QuoteStyle.None]),
	#"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
	#"Renamed Columns" = Table.RenameColumns(#"Promoted Headers",{{"PSChildName", "Name"}, {"LastWriteTime", "Date Modified"}, {"CreationTime", "Date Created"}, {"PSParentPath", "Folder Path"}, {"Length", "Size"}}),
	#"Changed Type" = Table.TransformColumnTypes(#"Renamed Columns",{{"Name", type text}, {"Extension", type text}, {"Size", Int64.Type}, {"Date Modified", type datetime}, {"Date Created", type datetime}, {"Folder Path", type text}}),
	#"Replaced Value" = Table.ReplaceValue(#"Changed Type","Microsoft.PowerShell.Core\FileSystem::","",Replacer.ReplaceText,{"Folder Path"})
in
	#"Replaced Value"

// Files on X root
let
	Source = Folder.Contents("X:\")
in
	Source

// SharePoint DataTeam
let
	Source = SharePoint.Files("https://contoso.sharepoint.com/teams/DataTeam/", [ApiVersion = 15]),
	#"Expanded Attributes" = Table.ExpandRecordColumn(Source, "Attributes", {"Size", "Content Type", "Kind"}, {"Size", "Content Type", "Kind"}),
	#"Removed Columns" = Table.RemoveColumns(#"Expanded Attributes",{"Date accessed"}),
	#"Renamed Columns" = Table.RenameColumns(#"Removed Columns",{{"Date modified", "Date Modified"}, {"Date created", "Date Created"}}),
	#"Changed Type" = Table.TransformColumnTypes(#"Renamed Columns",{{"Size", Int64.Type}}),
	#"Removed Columns1" = Table.RemoveColumns(#"Changed Type",{"Content"}),
	#"Replaced Value" = Table.ReplaceValue(#"Removed Columns1","https://contoso.sharepoint.com/teams/","",Replacer.ReplaceText,{"Folder Path"})
in
	#"Replaced Value"

// SharePoint DataTeam root
let
	Source = SharePoint.Contents("https://contoso.sharepoint.com/teams/DataTeam/", [ApiVersion = 15]),
	#"Shared Documents" = Source{[Name="Shared Documents"]}[Content],
	#"Expanded Attributes" = Table.ExpandRecordColumn(#"Shared Documents", "Attributes", {"Size", "Content Type", "Kind"}, {"Size", "Content Type", "Kind"}),
	#"Removed Columns" = Table.RemoveColumns(#"Expanded Attributes",{"Date accessed"}),
	#"Renamed Columns" = Table.RenameColumns(#"Removed Columns",{{"Date modified", "Date Modified"}, {"Date created", "Date Created"}}),
	#"Replaced Value" = Table.ReplaceValue(#"Renamed Columns", each _, each if _[Kind] <> "Folder" then null else _[Content], (state, apply, current) => (current), {"Content"})
in
	#"Replaced Value"

// SharePoint DataOps-Data & Product Delivery
let
	Source = SharePoint.Files("https://contoso.sharepoint.com/teams/Dataops-DataProductDelivery/", [ApiVersion = 15]),
	#"Expanded Attributes" = Table.ExpandRecordColumn(Source, "Attributes", {"Size", "Content Type", "Kind"}, {"Size", "Content Type", "Kind"}),
	#"Renamed Columns" = Table.RenameColumns(#"Expanded Attributes",{{"Date modified", "Date Modified"}, {"Date created", "Date Created"}}),
	#"Removed Columns" = Table.RemoveColumns(#"Renamed Columns",{"Date accessed"}),
	#"Removed Columns1" = Table.RemoveColumns(#"Removed Columns",{"Content"}),
	#"Changed Type" = Table.TransformColumnTypes(#"Removed Columns1",{{"Size", Int64.Type}}),
	ReplacedValue = Table.ReplaceValue(#"Changed Type","https://contoso.sharepoint.com/teams/","",Replacer.ReplaceText,{"Folder Path"})
in
	ReplacedValue

// All Files
let
	Source = Table.Combine({#"SharePoint DataTeam", #"SharePoint DataOps-Data & Product Delivery", #"Files on X"}),
	#"Filtered Rows" = Table.SelectRows(Source, each ([Name] <> null))
in
	#"Filtered Rows"

// All File Extensions
let
	Source = #"All Files"
,	#"Removed Other Columns"	=	Table.SelectColumns(Source,{"Extension"})
,	#"Removed Duplicates"		=	Table.Distinct(#"Removed Other Columns")
,	#"Sorted Rows"				=	Table.Sort(
										#"Removed Duplicates"
									,	{	{	each		if		Text.Length([Extension]) > 2
																and	Text.Middle([Extension], 1, 1) = "D"
																and	List.Contains({"0".."9"}, Text.Middle([Extension], 2, 1))				then	"2" & Text.Lower([Extension])
													else	if		Text.Length([Extension]) > 2
																and	Text.Middle([Extension], 1, 1) = "T"
																and	List.Contains({"0".."9"}, Text.Middle([Extension], 2, 1))				then	"3" & Text.Lower([Extension])
													else	if		Text.Length([Extension]) > 1
																and	List.Contains({"0".."9"}, Text.Middle([Extension], 1, 1))				then	"4" & Text.Lower([Extension])
													else	if		List.Contains({"a".."z"}, Text.Lower(Text.Middle([Extension], 1, 1)))	then	"0" & Text.Lower([Extension])
													else																							"1" & Text.Lower([Extension])
											,	Order.Ascending}
										}
									)
in
	#"Sorted Rows"

// fnFilesByExtensions
let
	fn	=	(	Extensions	as	any)	=>

		let
			lstExtensions	=	if	Value.Is(Extensions, type list)	then	Extensions	else	{Extensions}
		,	FilteredTable	=	Table.SelectRows(#"All Files", each 
									List.AnyTrue(
										List.Transform(
											lstExtensions
										,	(ext) => (
												Text.StartsWith(Text.Lower([Extension]), Text.Lower(if Text.StartsWith(ext, ".") then ext else "." & ext))
											)
										)
									)
								)
		,	Sorted			=	Table.Sort(
									FilteredTable
								,	{{"Date Modified", Order.Descending}}
								)
		in	Sorted

// Define the types for the function parameters with metadata
,	anyExtensionsParm	=	type any meta 
	[	Documentation.FieldCaption		=	"Extensions"
	,	Documentation.FieldDescription	=	"Specify an extention or a list of extensions (e.g., {""csv"", ""txt""})."
	]

// Define the type for the function with metadata
,	typFn	=	type function	(	anyExtensions	as	anyExtensionsParm
								)	as table
				meta	[	Documentation.Name				=	"fnFilesByExtensions"
						,	Documentation.LongDescription	=	"Return list of files whose extension begins with a specified extension or one of a specified list of extensions."
						,	Documentation.Examples			=	{	[	Description	=	"Example 1"
																	,	Code		=	"fnFilesByExtensions(""csv"")"
																	,	Result		=	"CSV* files"
																	]
																,	[	Description	=	"Example 2"
																	,	Code		=	"fnFilesByExtensions({""csv"", ""txt""})"
																	,	Result		=	"CSV* and TXT* files"
																	]
																}
						]

// Apply the types and metadata to the function
,	fnResult	=	Value.ReplaceType(fn, typFn)

in	fnResult

// All SQL Files
let
	Source = fnFilesByExtensions("sql")
in
	Source

// All Excel Files
let
	Source = fnFilesByExtensions("xl")
in
	Source

// All PowerPoint Files
let
	Source = fnFilesByExtensions("pp")
in
	Source

// All PDF Files
let
	Source = fnFilesByExtensions("pdf")
in
	Source

// All ZIP Files
let
	Source = fnFilesByExtensions({"zip", "7z"})
in
	Source

// All Word Files
let
	Source = fnFilesByExtensions("doc")
in
	Source

// All Script Files
let
	Source = fnFilesByExtensions({"bat", "cmd", "ps1"})
in
	Source

// All CSV Files
let
	Source = fnFilesByExtensions("csv")
in
	Source

// All TXT Files
let
	Source = fnFilesByExtensions("txt")
in
	Source