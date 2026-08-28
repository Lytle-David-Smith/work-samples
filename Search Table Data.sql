--	Search for a value within specified columns in specified tables of a database.
--	Adapted from a query by Reto Egeter, fullparam.wordpress.com
--	Compatible with SQL Server 2000 (doesn't use sys.tables).

--	Usage:
--		Use SSMS to connect to a database server.
--		Open this file within SSMS.
--		Select the database to be searched on the SSMS toolbar.
--		Press [Ctrl-Shift-M] to open a dialog box prompting for parameter values.
--		Specify the search pattern, options, and click OK.
--		Execute the query.

--	Execution time depends on the amount of data.
--	Invalid views might return errors which can be ignored.

declare
	@SearchStrTableName   nvarchar(255)
,	@SearchStrColumnName  nvarchar(255)
,	@SearchStrColumnValue nvarchar(255)
,	@SearchStrInXML       bit
,	@FullRowResult        bit
,	@FullRowResultRows    int

set @SearchStrColumnValue	=	'<SearchPattern				, nvarchar(max)	, >'	--	Use LIKE syntax
set @SearchStrTableName		=	'<TableNamesPattern			, nvarchar(max)	, %>'	--	Use LIKE syntax
set @SearchStrColumnName	=	'<ColumnNamesPattern		, nvarchar(max)	, %>'	--	Use LIKE syntax
set @FullRowResult			=	<FullRowResults				, bit			, 0>
set @FullRowResultRows		=	<FullRowResultRows			, int			, 3>	--	0 for all rows
set @SearchStrInXML			=	<SearchInXML				, bit			, 0>	--	Searching XML data may be slow

if object_id('tempdb..#Results') is not null
	drop table #Results

create table #Results
	(	TableName   nvarchar(128)
	,	ColumnName  nvarchar(128)
	,	ColumnValue nvarchar(max)
	,	ColumnType  nvarchar(20)
	)

set nocount on

declare
	@TableName                  nvarchar(256) = ''
,	@ColumnName                 nvarchar(128)
,	@ColumnType                 nvarchar(20)
,	@QuotedSearchStrColumnValue nvarchar(110)
,	@QuotedSearchStrColumnName  nvarchar(110)
,	@FullRowResultRowsClause	nvarchar(255)
,	@Sql						varchar(max)

set @QuotedSearchStrColumnValue =	quotename('%' + lower(@SearchStrColumnValue) + '%', '''')
set	@SearchStrTableName			=	lower(@SearchStrTableName)
set	@SearchStrColumnName		=	lower(@SearchStrColumnName)
set	@FullRowResultRowsClause	=	case	@FullRowResultRows
										when	0	then	''
										else				'	top ' + cast(@FullRowResultRows as varchar(3))
									end

declare
	@ColumnNameTable table
	(
	COLUMN_NAME nvarchar(128),
	DATA_TYPE   nvarchar(20)
	)

while @TableName is not null
	begin
		set	@Sql	=	'
	select
		min(quotename(TABLE_SCHEMA) + ''.'' + quotename(TABLE_NAME))
	from
		INFORMATION_SCHEMA.tables
	where
		lower(TABLE_NAME)	like	''' + @SearchStrTableName + '''
--	and	TABLE_TYPE			=		''BASE TABLE''
	and	quotename(TABLE_SCHEMA) + ''.'' + quotename(TABLE_NAME)	>	''' + @TableName + '''
	and	objectproperty(object_id(quotename(TABLE_SCHEMA) + ''.'' + quotename(TABLE_NAME)), ''IsMSShipped'') = 0'
		print @Sql
		set @TableName =
			(	select
					min(quotename(TABLE_SCHEMA) + '.' + quotename(TABLE_NAME))
				from
					INFORMATION_SCHEMA.tables
				where
					lower(TABLE_NAME)	like	@SearchStrTableName
--				and	TABLE_TYPE			=		'BASE TABLE'
				and	quotename(TABLE_SCHEMA) + '.' + quotename(TABLE_NAME)	>	@TableName
				and	objectproperty(object_id(quotename(TABLE_SCHEMA) + '.' + quotename(TABLE_NAME)), 'IsMSShipped') = 0
			)
		if @TableName is not null
			begin
				set	@Sql	=	'
		select
			quotename(column_name)
		,	data_type
		from
			information_schema.columns
		where
			table_schema	=		parsename(''' + @TableName + ''', 2)
		and	table_name		=		parsename(''' + @TableName + ''', 1)
		and	data_type		in		('
			+	case
					when	isnumeric(replace(replace(replace(replace(replace(
								@SearchStrColumnValue, '%', ''), '_', ''), '[', ''), ']', ''), '-', '')
							)	=	1
						then	'''tinyint'', ''int'', ''smallint'', ''bigint'', ''numeric'', ''decimal'', ''smallmoney'', ''money'', '
					else		''
				end
			+	'''char'', ''varchar'', ''nchar'', ''nvarchar'', ''timestamp'', ''uniqueidentifier'''
			+	case	@SearchStrInXML
					when	1	then	',''xml'''
					else				''
				end
			+	')
		and	column_name		like	coalesce('
			+	case
					when	@SearchStrColumnName	is null	then	'null'
					else											'''' + @SearchStrColumnName + ''''
				end
			+	', column_name)'
				print @Sql
				insert into @ColumnNameTable
				exec (@Sql)
				while exists
					(
						select top 1
							COLUMN_NAME
						from
							@ColumnNameTable
					)
					begin
					--	print @ColumnName
						select top 1
							@ColumnName = COLUMN_NAME
						,	@ColumnType = DATA_TYPE
						from
							@ColumnNameTable
						set	@Sql	=	'
			select 
				'''	+	@TableName	+	'''
			,	'''	+	@ColumnName	+	'''
			,	'	+	case	@ColumnType
							when 'xml'			then	'left(cast(' + @ColumnName + ' AS nvarchar(MAX)), 4096)'
							when 'timestamp'	then	'master.dbo.fn_varbintohexstr(' + @ColumnName + ')'
							else						'left(' + @ColumnName + ', 4096)'
						end			+	'
			,	'''	+	@ColumnType	+	'''
			from	'	+	@TableName + '	(nolock)
			where	'	+	case	@ColumnType
								when	'xml'		then	'cast(' + @ColumnName + ' AS nvarchar(MAX))'
								when	'timestamp'	then	'master.dbo.fn_varbintohexstr(' + @ColumnName + ')'
								else						'lower(' + @ColumnName + ')'
							end	+	'	like	' + @QuotedSearchStrColumnValue
						print @Sql
						insert into #Results
						exec (@Sql)
						if
							@@RowCount > 0
							if
								@FullRowResult = 1
								begin
									set	@Sql	=	'
				select'	+	@FullRowResultRowsClause	+	'
					'''	+	@TableName	+	'''	as	[TableFound]
				,	'''	+	@ColumnName	+	'''	as	[ColumnFound]
				,	''FullRow->''				as	[FullRow>]
				,	*
				from	'	+	@TableName	+	'	(nolock)
				where	'	+	case @ColumnType
									when	'xml'		then	'cast(' + @ColumnName + ' as nvarchar(MAX))'
									when	'timestamp'	then	'master.dbo.fn_varbintohexstr(' + @ColumnName + ')'
									else						'lower(' + @ColumnName + ')'
								end	+	'	like	' + @QuotedSearchStrColumnValue
									print @Sql
									exec (@Sql)
							end
						delete from @ColumnNameTable
						where
							column_name = @ColumnName
					end
			end
	end

set nocount off

select
	count(*) as Count
,	TableName
,	ColumnName
,	ColumnValue
,	ColumnType
from
	#Results
group by
	TableName
,	ColumnName
,	ColumnValue
,	ColumnType
order by
	count(*) desc
,	TableName
,	ColumnName
,	ColumnValue

select
	TableName
,	ColumnName
,	ColumnValue
,	ColumnType
,	count(*) as Count
from
	#Results
group by
	TableName
,	ColumnName
,	ColumnValue
,	ColumnType
order by
	TableName
,	ColumnName
,	ColumnValue
