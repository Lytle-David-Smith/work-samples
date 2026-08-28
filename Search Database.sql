--	Search schema names, table names, view names, synonym names and targets, column names, 
--	module names, and module code in a single database (for compatibility with Azure).
--	For cross-database search, see dbo.SearchDatabases.

--	Usage:
--		Use SSMS to connect to a database server.
--		Open this file within SSMS.
--		Select the database to be searched on the SSMS toolbar.
--		Press [Ctrl-Shift-M] to open a dialog box prompting for parameter values.
--		Specify the search pattern, search locations (1 or 0 to enable/disable each), and click OK.
--		Execute the query.

	declare	@SearchValue				nvarchar(max)	=	'<SearchPattern				, nvarchar(max)	, >'
	declare	@SearchModules				bit				=	<SearchModules				, bit			, 0>
	declare	@SearchViewNames			bit				=	<SearchViewNames			, bit			, 1>
	declare	@SearchViewColumnNames		bit				=	<SearchViewColumnNames		, bit			, 1>
	declare	@SearchViewColumnDataTypes	bit				=	<SearchViewColumnDataTypes	, bit			, 0>
	declare	@SearchSchemaNames			bit				=	<SearchSchemaNames			, bit			, 0>
	declare	@SearchSynonyms				bit				=	<SearchSynonyms				, bit			, 1>
	declare @SearchForeignKeys			bit				=	<SearchForeignKeys			, bit			, 1>
	declare	@SearchTableNames			bit				=	<SearchTableNames			, bit			, 1>
	declare	@SearchTableColumnNames		bit				=	<SearchTableColumnNames		, bit			, 1>
	declare	@SearchTableColumnDataTypes	bit				=	<SearchTableColumnDataTypes	, bit			, 0>

	set nocount on

	declare	@sql				varchar(max)
	declare	@FullyQualObjName	nvarchar(523)
	declare	@ModuleDefinition	nvarchar(max)
	declare	@Created			datetime
	declare	@Modified			datetime
	declare	@ReversedDefinition	nvarchar(max)
	declare	@LineBreakIndex		int
	declare	@SearchLength		int

	if object_id(N'tempdb..#result', N'U') is not null
		drop table #result

	create table #result (
		[FullyQualifiedObjectName]	nvarchar(523)
	,	[SchemaName]				nvarchar(128)
	,	[TableName]					nvarchar(128)
	,	[ViewName]					nvarchar(128)
	,	[SynonymName]				nvarchar(128)
	,	[SynonymObject]				nvarchar(128)
	,	[ColumnName]				nvarchar(128)
	,	[DataType]					nvarchar(128)
	,	[ForeignKeyConstraint]		nvarchar(128)
	,	[ParentTableName]			nvarchar(128)
	,	[ParentColumnName]			nvarchar(128)
	,	[Rows]						bigint
	,	[SizeKB]					bigint
	,	[ModuleName]				nvarchar(128)
	,	[ModuleType]				nvarchar(128)
	,	[ModuleDefinition]			nvarchar(max)
	,	[Created]					datetime
	,	[Modified]					datetime
	)

	if	@SearchSchemaNames	=	1	begin
		select	@sql	=	'
			select 
				quotename(s.Name)			as	[FullyQualifiedObjectName]
			,	s.Name						as	[SchemaName]
			,	null						as	[TableName] 
			,	null						as	[ViewName]
			,	null						as	[SynonymName]
			,	null						as	[SynonymObject]
			,	null						as	[ColumnName]
			,	null						as	[DataType]
			,	null						as	[ForeignKeyConstraint]
			,	null						as	[ParentTableName]
			,	null						as	[ParentColumnName]
			,	null						as	[Rows]
			,	null						as	[SizeKB]
			,	null						as	[ModuleName]
			,	null						as	[ModuleType]
			,	null						as	[ModuleDefinition]
			,	null						as	[Created]
			,	null						as	[Modified]
			from 
				sys.schemas		as	s
			where 
				lower(s.Name) like (''%'' + lower(''' + @SearchValue + ''') + ''%'')
			group by
				s.[Name]
			;
		'
		begin try
			insert into	#result
			exec (@sql)
		end try
		begin catch
		end catch
	end

	if	@SearchTableNames	=	1	begin
		select	@sql	=	'
			select 
					quotename(s.Name)
				+	''.''
				+	quotename(t.Name)		as	[FullyQualifiedObjectName]
			,	s.Name						as	[SchemaName]
			,	t.Name						as	[TableName] 
			,	null						as	[ViewName]
			,	null						as	[SynonymName]
			,	null						as	[SynonymObject]
			,	null						as	[ColumnName]
			,	null						as	[DataType]
			,	null						as	[ForeignKeyConstraint]
			,	null						as	[ParentTableName]
			,	null						as	[ParentColumnName]
			,	(
					select
						sum(p2.[rows])
					from
									sys.indexes		as	i2 
						inner join	sys.partitions	as	p2
							on	i2.object_id	=	p2.object_id
							and	i2.index_id		=	p2.index_id
					where
						i2.object_id	=	t.object_id
					and	i2.object_id	>	255
					and	(	i2.index_id	=	0
						or	i2.index_id	=	1
						)
				)							as	[Rows]
			,	(	d.in_row_data_page_count
				+	d.lob_used_page_count
				+	d.row_overflow_used_page_count
				) * 8						as	[SizeKB]
			,	null						as	[ModuleName]
			,	null						as	[ModuleType]
			,	null						as	[ModuleDefinition]
			,	t.[create_date]				as	[Created]
			,	t.[modify_date]				as	[Modified]
			from 
							sys.tables		as	t
				inner join	sys.schemas		as	s
					on	t.[schema_id]	=	s.[schema_id] 
				inner join	sys.partitions	as	p
					on	p.object_id		=	t.object_id
				inner join	sys.dm_db_partition_stats	as	d
					on	d.object_id		=	t.object_id
			where 
				lower(t.Name) like (''%'' + lower(''' + @SearchValue + ''') + ''%'')
			group by
				s.[Name]
			,	t.[Name]
			,	t.object_id
			,	t.[create_date]
			,	t.[modify_date]
			,	d.in_row_data_page_count
			,	d.lob_used_page_count
			,	d.row_overflow_used_page_count
			;
		'
		begin try
			insert into	#result
			exec (@sql)
		end try
		begin catch
		end catch
	end
	
	if	@SearchViewNames	=	1	begin
		select	@sql	=	'
			select 
					quotename(s.Name)
				+	''.''
				+	quotename(v.Name)		as	[FullyQualifiedObjectName]
			,	s.Name						as	[SchemaName]
			,	null						as	[TableName] 
			,	v.[Name]					as	[ViewName]
			,	null						as	[SynonymName]
			,	null						as	[SynonymObject]
			,	null						as	[ColumnName]
			,	null						as	[DataType]
			,	null						as	[ForeignKeyConstraint]
			,	null						as	[ParentTableName]
			,	null						as	[ParentColumnName]
			,	null						as	[Rows]
			,	null						as	[SizeKB]
			,	null						as	[ModuleName]
			,	null						as	[ModuleType]
			,	null						as	[ModuleDefinition]
			,	v.[create_date]				as	[Created]
			,	v.[modify_date]				as	[Modified]
			from 
							sys.views		as	v
				inner join	sys.schemas		as	s
					on	s.[schema_id]	=	v.[schema_id]
			where 
				lower(v.Name) like (''%'' + lower(''' + @SearchValue + ''') + ''%'')
			group by
				s.[Name]
			,	v.[Name]
			,	v.[create_date]
			,	v.[modify_date]
			;
		'
		begin try
			insert into	#result
			exec (@sql)
		end try
		begin catch
		end catch
	end

	if	@SearchSynonyms	=	1	begin
		select	@sql	=	'
			select 
					quotename(s.Name)
				+	''.''
				+	quotename(sy.Name)		as	[FullyQualifiedObjectName]
			,	s.Name						as	[SchemaName]
			,	null						as	[TableName] 
			,	null						as	[ViewName]
			,	sy.[Name]					as	[SynonymName]
			,	sy.base_object_name			as	[SynonymObject]
			,	null						as	[ColumnName]
			,	null						as	[DataType]
			,	null						as	[ForeignKeyConstraint]
			,	null						as	[ParentTableName]
			,	null						as	[ParentColumnName]
			,	null						as	[Rows]
			,	null						as	[SizeKB]
			,	null						as	[ModuleName]
			,	null						as	[ModuleType]
			,	null						as	[ModuleDefinition]
			,	sy.[create_date]			as	[Created]
			,	sy.[modify_date]			as	[Modified]
			from 
							sys.synonyms		as	sy
				inner join	sys.schemas		as	s
					on	s.[schema_id]	=	sy.[schema_id]
			where 
				lower(sy.Name) like (''%'' + lower(''' + @SearchValue + ''') + ''%'')
			or	lower(sy.base_object_name) like (''%'' + lower(''' + @SearchValue + ''') + ''%'')
			group by
				s.[Name]
			,	sy.[Name]
			,	sy.base_object_name
			,	sy.[create_date]
			,	sy.[modify_date]
			;
		'
		begin try
			insert into	#result
			exec (@sql)
		end try
		begin catch
		end catch
	end

	if	@SearchTableColumnNames		=	1
	or	@SearchTableColumnDataTypes	=	1
	begin
		select	@sql	=	'
			select 
					quotename(s.Name)
				+	''.''
				+	quotename(t.Name)
				+	''.''
				+	quotename(c.Name)		as	[FullyQualifiedObjectName]
			,	s.Name						as	[SchemaName]
			,	t.Name						as	[TableName]
			,	null						as	[ViewName]
			,	null						as	[SynonymName]
			,	null						as	[SynonymObject]
			,	c.Name						as	[ColumnName]
			,	typ.[name]
			+	case
					when	styp.[name]		in	(''float'', ''decimal'', ''numeric'', ''binary'', ''varbinary'', ''image'', ''char'', ''nchar'', ''varchar'', ''nvarchar'', ''xml'')
						and	(	c.precision		<>	0
							or	c.scale			<>	0
							or	c.max_length	<>	0
						)
						then	''(''
					else		''''
				end
			+	substring(
						case
							when	styp.[name]		in	(''float'', ''decimal'', ''numeric'')
								then	'', '' + convert(varchar(4), c.precision)
							else		''''
						end
					+	case
							when	styp.[name]		in	(''decimal'', ''numeric'')
								then	'', '' + convert(varchar(4), c.scale)
							else		''''
						end
					+	case
							when	c.max_length	=	-1
								then	'', '' + ''max''
							when	styp.[name]		in	(''binary'', ''varbinary'', ''image'', ''char'', ''nchar'', ''varchar'', ''nvarchar'', ''xml'')
								then	'', '' + convert(varchar(4), c.max_length)
							else		''''
						end
				,	3
				,	255
				)
			+	case
					when	styp.[name]		in	(''float'', ''decimal'', ''numeric'', ''binary'', ''varbinary'', ''image'', ''char'', ''nchar'', ''varchar'', ''nvarchar'', ''xml'')
						and	(	c.precision		<>	0
							or	c.scale			<>	0
							or	c.max_length	<>	0
						)
						then	'')''
					else		''''
				end							as	[DataType]
			,	null						as	[ForeignKeyConstraint]
			,	null						as	[ParentTableName]
			,	null						as	[ParentColumnName]
			,	sum(p.[Rows])				as	[Rows]
			,	null						as	[SizeKB]
			,	null						as	[ModuleName]
			,	null						as	[ModuleType]
			,	null						as	[ModuleDefinition]
			,	t.[create_date]				as	[Created]
			,	t.[modify_date]				as	[Modified]
			from 
							sys.columns		as	c
				inner join	sys.tables		as	t
					on	c.[object_id]	=	t.[object_id] 
				inner join	sys.schemas		as	s
					on	t.[schema_id]	=	s.[schema_id] 
				inner join	sys.partitions	as	p
					on	p.object_id		=	t.object_id
				left join	sys.types		as	typ
					on	typ.user_type_id	=	c.user_type_id
				left join	sys.types		as	styp
					on	styp.user_type_id	=	typ.system_type_id
			where 
				(	(	' + convert(varchar(1), @SearchTableColumnNames		)	+ ' = 1
					and	lower(c.Name) LIKE (''%'' + lower(''' + @SearchValue + ''') + ''%'')
					)
				or	(	' + convert(varchar(1), @SearchTableColumnDataTypes	)	+ ' = 1
					and	lower(
							typ.[name]
						+	case
								when	styp.[name]		in	(''float'', ''decimal'', ''numeric'', ''binary'', ''varbinary'', ''image'', ''char'', ''nchar'', ''varchar'', ''nvarchar'', ''xml'')
									and	(	c.precision		<>	0
										or	c.scale			<>	0
										or	c.max_length	<>	0
									)
									then	''(''
								else		''''
							end
						+	substring(
									case
										when	styp.[name]		in	(''float'', ''decimal'', ''numeric'')
											then	'', '' + convert(varchar(4), c.precision)
										else		''''
									end
								+	case
										when	styp.[name]		in	(''decimal'', ''numeric'')
											then	'', '' + convert(varchar(4), c.scale)
										else		''''
									end
								+	case
										when	c.max_length	=	-1
											then	'', '' + ''max''
										when	styp.[name]		in	(''binary'', ''varbinary'', ''image'', ''char'', ''nchar'', ''varchar'', ''nvarchar'', ''xml'')
											then	'', '' + convert(varchar(4), c.max_length)
										else		''''
									end
							,	3
							,	255
							)
						+	case
								when	styp.[name]		in	(''float'', ''decimal'', ''numeric'', ''binary'', ''varbinary'', ''image'', ''char'', ''nchar'', ''varchar'', ''nvarchar'', ''xml'')
									and	(	c.precision		<>	0
										or	c.scale			<>	0
										or	c.max_length	<>	0
									)
									then	'')''
								else		''''
							end
						) LIKE (''%'' + lower(''' + @SearchValue + ''') + ''%'')
					)
				)
			and	p.index_id	<	2
			group by
				s.[Name]
			,	t.[Name]
			,	c.[Name]
			,	c.max_length
			,	c.precision
			,	c.scale
			,	typ.[name]
			,	styp.[name]
			,	t.[create_date]
			,	t.[modify_date]
			;
		'

		begin try
			insert into	#result
			exec (@sql)
		end try
		begin catch
		end catch
	end

	if	@SearchViewColumnNames		=	1
	or	@SearchViewColumnDataTypes	=	1
	begin
		select	@sql	=	'
			select 
					quotename(s.Name)
				+	''.''
				+	quotename(v.Name)
				+	''.''
				+	quotename(c.Name)		as	[FullyQualifiedObjectName]
			,	s.Name						as	[SchemaName]
			,	null						as	[TableName]
			,	v.[Name]					as	[ViewName]
			,	null						as	[SynonymName]
			,	null						as	[SynonymObject]
			,	c.Name						as	[ColumnName]
			,	typ.[name]
			+	case
					when	styp.[name]		in	(''float'', ''decimal'', ''numeric'', ''binary'', ''varbinary'', ''image'', ''char'', ''nchar'', ''varchar'', ''nvarchar'', ''xml'')
						and	(	c.precision		<>	0
							or	c.scale			<>	0
							or	c.max_length	<>	0
						)
						then	''(''
					else		''''
				end
			+	substring(
						case
							when	styp.[name]		in	(''float'', ''decimal'', ''numeric'')
								then	'', '' + convert(varchar(4), c.precision)
							else		''''
						end
					+	case
							when	styp.[name]		in	(''decimal'', ''numeric'')
								then	'', '' + convert(varchar(4), c.scale)
							else		''''
						end
					+	case
							when	c.max_length	=	-1
								then	'', '' + ''max''
							when	styp.[name]		in	(''binary'', ''varbinary'', ''image'', ''char'', ''nchar'', ''varchar'', ''nvarchar'', ''xml'')
								then	'', '' + convert(varchar(4), c.max_length)
							else		''''
						end
				,	3
				,	255
				)
			+	case
					when	styp.[name]		in	(''float'', ''decimal'', ''numeric'', ''binary'', ''varbinary'', ''image'', ''char'', ''nchar'', ''varchar'', ''nvarchar'', ''xml'')
						and	(	c.precision		<>	0
							or	c.scale			<>	0
							or	c.max_length	<>	0
						)
						then	'')''
					else		''''
				end							as	[DataType]
			,	null						as	[ForeignKeyConstraint]
			,	null						as	[ParentTableName]
			,	null						as	[ParentColumnName]
			,	null						as	[Rows]
			,	null						as	[SizeKB]
			,	null						as	[ModuleName]
			,	null						as	[ModuleType]
			,	null						as	[ModuleDefinition]
			,	v.[create_date]				as	[Created]
			,	v.[modify_date]				as	[Modified]
			from 
							sys.columns		as	c
				inner join	sys.views		as	v
					on	v.[object_id]	=	c.[object_id] 
				inner join	sys.schemas		as	s
					on	s.[schema_id]	=	v.[schema_id] 
				left join	sys.types		as	typ
					on	typ.user_type_id	=	c.user_type_id
				left join	sys.types		as	styp
					on	styp.user_type_id	=	typ.system_type_id
			where 
				(	(	' + convert(varchar(1), @SearchViewColumnNames		)	+ ' = 1
					and	lower(c.Name) LIKE (''%'' + lower(''' + @SearchValue + ''') + ''%'')
					)
				or	(	' + convert(varchar(1), @SearchViewColumnDataTypes	)	+ ' = 1
					and	lower(
							typ.[name]
						+	case
								when	styp.[name]		in	(''float'', ''decimal'', ''numeric'', ''binary'', ''varbinary'', ''image'', ''char'', ''nchar'', ''varchar'', ''nvarchar'', ''xml'')
									and	(	c.precision		<>	0
										or	c.scale			<>	0
										or	c.max_length	<>	0
									)
									then	''(''
								else		''''
							end
						+	substring(
									case
										when	styp.[name]		in	(''float'', ''decimal'', ''numeric'')
											then	'', '' + convert(varchar(4), c.precision)
										else		''''
									end
								+	case
										when	styp.[name]		in	(''decimal'', ''numeric'')
											then	'', '' + convert(varchar(4), c.scale)
										else		''''
									end
								+	case
										when	c.max_length	=	-1
											then	'', '' + ''max''
										when	styp.[name]		in	(''binary'', ''varbinary'', ''image'', ''char'', ''nchar'', ''varchar'', ''nvarchar'', ''xml'')
											then	'', '' + convert(varchar(4), c.max_length)
										else		''''
									end
							,	3
							,	255
							)
						+	case
								when	styp.[name]		in	(''float'', ''decimal'', ''numeric'', ''binary'', ''varbinary'', ''image'', ''char'', ''nchar'', ''varchar'', ''nvarchar'', ''xml'')
									and	(	c.precision		<>	0
										or	c.scale			<>	0
										or	c.max_length	<>	0
									)
									then	'')''
								else		''''
							end
						) LIKE (''%'' + lower(''' + @SearchValue + ''') + ''%'')
					)
				)
			group by
				s.[Name]
			,	v.[Name]
			,	c.[Name]
			,	c.max_length
			,	c.precision
			,	c.scale
			,	typ.[name]
			,	styp.[name]
			,	v.[create_date]
			,	v.[modify_date]
		'

		begin try
			insert into	#result
			exec (@sql)
		end try
		begin catch
		end catch
	end

	if	@SearchModules	=	1	begin
		select	@sql	=	'
			select 
					quotename(s.Name)
				+	''.''
				+	quotename(o.Name)		as	[FullyQualifiedObjectName]
			,	s.name						as	[SchemaName]
			,	null						as	[TableName] 
			,	null						as	[ViewName]
			,	null						as	[SynonymName]
			,	null						as	[SynonymObject]
			,	null						as	[ColumnName]
			,	null						as	[DataType]
			,	null						as	[ForeignKeyConstraint]
			,	null						as	[ParentTableName]
			,	null						as	[ParentColumnName]
			,	null						as	[Rows]
			,	null						as	[SizeKB]
			,	o.name						as	[ModuleName]
			,	o.type_desc					as	[ModuleType]
			,	m.definition				as	[ModuleDefinition]
			,	o.[create_date]				as	[Created]
			,	o.[modify_date]				as	[Modified]
			from 
							sys.sql_modules	as	m
				inner join	sys.objects		as	o
					on	o.[object_id]	=	m.[object_id]
				inner join	sys.schemas		as	s
					on	s.[schema_id]	=	o.[schema_id]
			where 
				lower(o.name) like (''%'' + lower(''' + @SearchValue + ''') + ''%'')
			or	lower(m.definition) like (''%'' + lower(''' + @SearchValue + ''') + ''%'')
			group by
				s.[name]
			,	o.[name]
			,	o.[type_desc]
			,	m.definition
			,	o.[create_date]
			,	o.[modify_date]
			;
		'
		begin try
			insert into	#result
			exec (@sql)
		end try
		begin catch
		end catch
	end

	if	@SearchForeignKeys	=	1	begin
		select	@sql	=	'
			select 
					quotename(s.Name)
				+	''.''
				+	quotename(ft.Name)
				+	''.''
				+	quotename(fc.Name)					as	[FullyQualifiedObjectName]
			,	s.name									as	[SchemaName]
			,	t.name									as	[TableName] 
			,	null									as	[ViewName]
			,	null									as	[SynonymName]
			,	null									as	[SynonymObject]
			,	c.name									as	[ColumnName]
			,	null									as	[DataType]
			,	object_name(fk.constraint_object_id)	as	[ForeignKeyConstraint]
			,	ft.name									as	[ParentTable]
			,	fc.name									as	[ParentColumn]
			,	(
					select
						sum(p2.[rows])
					from
									sys.indexes		as	i2 
						inner join	sys.partitions	as	p2
							on	i2.object_id	=	p2.object_id
							and	i2.index_id		=	p2.index_id
					where
						i2.object_id	=	t.object_id
					and	i2.object_id	>	255
					and	(	i2.index_id	=	0
						or	i2.index_id	=	1
						)
				)										as	[Rows]
			,	null									as	[SizeKB]
			,	null									as	[ModuleName]
			,	null									as	[ModuleType]
			,	null									as	[ModuleDefinition]
			,	t.[create_date]							as	[Created]
			,	t.[modify_date]							as	[Modified]
			from 
							sys.foreign_key_columns	as	fk
				inner join	sys.tables				as	t
					on	t.object_id			=	fk.parent_object_id
				inner join	sys.columns				as	c
					on	c.object_id			=	fk.parent_object_id
					and	c.column_id			=	fk.parent_column_id
				inner join	sys.objects				as	o
					on	o.object_id			=	t.object_id
				inner join	sys.schemas				as	s
					on	s.schema_id			=	o.schema_id
				inner join	sys.tables				as	ft
					on	ft.object_id		=	fk.referenced_object_id
				inner join	sys.columns				as	fc
					on	fc.object_id		=	fk.referenced_object_id
					and	fc.column_id		=	fk.referenced_column_id
			where
				lower(ft.name) + ''.'' + lower(fc.name)	like	(''%'' + lower(''' + @SearchValue + ''') + ''%'')
			group by
				s.name
			,	t.name
			,	c.name
			,	fk.constraint_object_id
			,	ft.name
			,	fc.name
			,	t.object_id
			,	t.[create_date]
			,	t.[modify_date]
			;
		'
		begin try
			insert into	#result
			exec (@sql)
		end try
		begin catch
		end catch
	end

	--	Show results.
	select
		*
	from
		#result
	order by
		[FullyQualifiedObjectName]

	--	Print modules.
	declare modDefs cursor for
	select
		[FullyQualifiedObjectName]
	,	[ModuleDefinition]
	,	[Created]
	,	[Modified]
	from
		#result
	where
		len(ModuleDefinition)	>	0

	open		modDefs

	fetch next
	from	modDefs
	into
		@FullyQualObjName
	,	@ModuleDefinition
	,	@Created
	,	@Modified

	while @@fetch_status	=	0
	begin

		if @FullyQualObjName	is not null
			print
				char(13) + char(10)
			+	char(13) + char(10)
			+	'--' + char(9) + 'Module:' + char(9) + @FullyQualObjName + char(13) + char(10)
			+	'--' + char(9) + 'Created:' + char(9) + format(@Created, 'yyyy-MM-dd hh:mm:ss') + char(13) + char(10)
			+	'--' + char(9) + 'Modified:' + char(9) + format(@Modified, 'yyyy-MM-dd hh:mm:ss') + char(13) + char(10)

		set @SearchLength = 4000;

		while len(@ModuleDefinition) > @SearchLength
		begin
			set @ReversedDefinition	= left(@ModuleDefinition collate database_default, @SearchLength);
			set @ReversedDefinition	= reverse(@ReversedDefinition collate database_default);
			set @LineBreakIndex		= charindex(char(10) + char(13), @ReversedDefinition collate database_default);
			print left(@ModuleDefinition, @SearchLength - @LineBreakIndex + 1);
			set @ModuleDefinition			= right(@ModuleDefinition, len(@ModuleDefinition) - @SearchLength + @LineBreakIndex - 1);
		end;
	
		if len(@ModuleDefinition) > 0
			print @ModuleDefinition;

		print
			'go'
		+	char(13)
		+	char(10)

		fetch next
		from	modDefs
		into
			@FullyQualObjName
		,	@ModuleDefinition
		,	@Created
		,	@Modified

	end

	close		modDefs

	deallocate	modDefs
