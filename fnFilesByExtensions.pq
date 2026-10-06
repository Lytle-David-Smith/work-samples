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

// Files on X
let
	Source = Csv.Document(File.Contents("H:\Files on X.csv"),[Delimiter=",", Columns=6, Encoding=1252, QuoteStyle=QuoteStyle.None]),
	#"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
	#"Renamed Columns" = Table.RenameColumns(#"Promoted Headers",{{"PSChildName", "Name"}, {"LastWriteTime", "Date Modified"}, {"CreationTime", "Date Created"}, {"PSParentPath", "Folder Path"}, {"Length", "Size"}}),
	#"Changed Type" = Table.TransformColumnTypes(#"Renamed Columns",{{"Name", type text}, {"Extension", type text}, {"Size", Int64.Type}, {"Date Modified", type datetime}, {"Date Created", type datetime}, {"Folder Path", type text}}),
	#"Replaced Value" = Table.ReplaceValue(#"Changed Type","Microsoft.PowerShell.Core\FileSystem::","",Replacer.ReplaceText,{"Folder Path"})
in
	#"Replaced Value"

// All Files
let
	Source = Table.Combine({#"SharePoint DataTeam", #"SharePoint DataOps-Data & Product Delivery", #"Files on X"}),
	#"Filtered Rows" = Table.SelectRows(Source, each ([Name] <> null))
in
	#"Filtered Rows"

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