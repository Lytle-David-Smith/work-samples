	--	Each column, table, or clause on a separate line makes it easy to comment-out 
	--		individual elements for testing, or to disable them without removing
	--		them entirely for possible future use.


	--	Commas at the beginning of lines makes it easy to quickly verify syntax at a glance.


	--	Similar elements (e.g., AS, ON, WHEN, OVER, PARTITION, ORDER BY, THEN, operators) 
	--		aligned vertically makes it easy to quickly verify syntax at a glance, and to 
	--		compare associated elements across multiple lines.


	--	Common Table Expressions (CTEs) instead of inline subqueries reduces clutter and 
	--		makes logic easier to follow.


	--	Careful use of BETWEEN operator (not shown)
	--	The BETWEEN operator is equivalent to >= .. AND .. <=. Care must be
	--		exercised when used with DATETIME values because, for example, 
	--		BETWEEN 1/1/2024 AND 12/31/2024 does not include 12/31/2024 00:00:01 AM
	--		or after. It might be better to use >=1/1/2024 AND .. <1/1/2025
	--		instead.


	--	QUALIFY clause (Databricks)
	--	Filters results using WINDOW function. Eliminates usual requirement 
	--		to evaluate WINDOW function(s) in one query then filter on the 
	--		values returned in a downstream query.
	
		select
			`FAC PRVDR NAME ORG`
		,	`FAC PRVDR NPI NUM`
		,	`PRVDR OSCAR NUM`
		,	`PRVDR FAC FIPS ST`
		,	`MR MBI`
		,	`STAY ID`
		,	`STAY FROM DT`
		,	`STAY THRU DT`
		,	`STAY FROM ACO`
		,	`STAY THRU ACO`
		,	`CLM FROM ACO`
		,	`CLM THRU ACO`
		,	`STAY SRVC DAYS`
		,	`STAY DURATION`
		,	`STAY PMT AMT`
		,	case	when	`TRANSFER`		=	1	then	'Transfer'
					else									null
			end						as	`TRANSFER`
		,	case	when	`READMISSION`	=	1	then	'Readmission'
					else									null
			end						as	`READMISSION`
		,	`LENGTH OF READMIT STAY`
		from	claims
		where	`CLM TYPE`	ilike	'%SNF claim'
		qualify	first_value(`MR MBI SEQ`)	over	(	partition by	`MR MBI`
																	,	`STAY ID`
														order by		`MR MBI SEQ`	desc
													)	=	`MR MBI SEQ`
		order by
			`FAC PRVDR NAME ORG`
		,	`FAC PRVDR NPI NUM`
		,	`PRVDR OSCAR NUM`
		,	`MR MBI`
		,	`STAY ID`
		,	`STAY FROM DT`
		,	`STAY THRU DT`


	--	Named WINDOW (SQL Server, MySQL, Databricks, PostgreSQL)
	--	Eliminates clutter by avoiding repetition of the same PARTITION BY / ORDER BY 
	--		clauses for multiple evaluations of the same WINDOW.
	
	--	ILIKE function (Databricks, PostgreSQL)
	--	Case-insensitive comparison is a welcome change from LOWER(a.Col1)	LIKE	LOWER(b.Col2)
	
		select
			MR_MBI
		,	CLM_TYPE_CD
		,	CLM_TYPE
		,	CLM_FROM_DT
		,	CLM_THRU_DT
		,	datediff(
				CLM_THRU_DT
			,	CLM_FROM_DT
			)	+	1				as	CLM_SRVC_DAYS
		,	PRVDR_OSCAR_NUM
		,	CUR_CLM_UNIQ_ID
		,	CLM_BILL_FAC_TYPE_CD
		,	CLM_BILL_FAC_TYPE
		,	case
						--	First MBI SNF Claim
					when	lag(MR_MBI)								over	MBIClaimsByDate	is null
						and	CLM_TYPE														ilike		'%SNF claim'
							then	1		--	Beginning of Stay
						--	First MBI Claim
					when	lag(MR_MBI)								over	MBIClaimsByDate	is null
							then	null	--	Not a Stay
						--	MBI continued, SNF Claim, previous SNF Claim, Provider continued, <=5 days since previous SNF Claim
					when	lag(MR_MBI)								over	MBIClaimsByDate	is not null
						and	lag(CLM_TYPE)							over	MBIClaimsByDate	ilike		'%SNF claim'
						and	CLM_TYPE														ilike		'%SNF claim'
						and	FAC_PRVDR_NPI_NUM												=			lag(FAC_PRVDR_NPI_NUM)	over	MBIClaimsByDate
						and	datediff(
								CLM_FROM_DT
							,	lag(CLM_THRU_DT)					over	MBIClaimsByDate
							)																<=			5
							then	0		--	Continuation of Stay
						--	SNF claim
					when	CLM_TYPE														ilike		'%SNF claim'
							then	1		--	Beginning of Stay
					else			null	--	Not a Stay
			end									as	STAY_ID
		,	CLM_BILL_CLSFCTN_CD
		,	CLM_BILL_CLSFCTN
		,	CLM_PMT_AMT
		,	PRVDR_FAC_FIPS_ST_CD
		,	PRVDR_FAC_FIPS_ST
		,	BENE_PTNT_STUS_CD
		,	BENE_PTNT_STUS
		,	FAC_PRVDR_NPI_NUM
		,	FAC_PRVDR_NAME_LAST
		,	FAC_PRVDR_NAME_FIRST
		,	FAC_PRVDR_NAME_ORG
		,	CLM_ADMSN_TYPE_CD
		,	CLM_ADMSN_TYPE
		,	CLM_BILL_FREQ_CD
		,	CLM_BILL_FREQ
		,	CLM_IDR_LD_DT
		from	cclf1
		window	MBIClaimsByDate	as	(	partition by
											MR_MBI
										order by
											coalesce(
												CLM_FROM_DT
											,	CLM_THRU_DT
											)
										,	CLM_IDR_LD_DT
										,	CUR_CLM_UNIQ_ID
									)


	--	Recursive CTE (SQL Server, MySQL, PostgreSQL)
	--	Enables traversal of hierarchical data.
	
		with recursive

		--	Episode Claims (recursively) sequenced chronologically into Initial and Recertification Claims for later combination into Episodes
 			episode_claims	as	(
				-- HHA claims with no corresponding HHA claim for same MBI/Provider within previous 60 days
				-- Beginning of Initial Episode
				select
					cur.MR_MBI
				,	cur.CLM_FROM_DT
				,	cur.CLM_THRU_DT
				,	year(cur.CLM_FROM_DT)							as	YR
				,	cur.CLM_FROM_DT									as	STAY_ID_FROM_DT
				,	cur.CLM_THRU_DT									as	STAY_ID_THRU_DT
				,	cur.PRVDR_OSCAR_NUM								as	STAY_ID_PRVDR_OSCAR_NUM
				,	1												as	STAY_SEQ
				,	cur.CLM_FROM_DT									as	STAY_FROM_DT
				,	cur.MR_MBI_SEQ
				,	cur.PRVDR_OSCAR_NUM
				,	cur.FAC_PRVDR_NPI_NUM
				,	cur.FAC_PRVDR_NAME_LAST
				,	cur.FAC_PRVDR_NAME_FIRST
				,	cur.FAC_PRVDR_NAME_ORG
				,	cur.BENE_PTNT_STUS
				,	cur.PRGRM
				,	cur.County
				,	cur.State
				,	cur.CLM_FROM_DT									as	EPSD_ID_FROM_DT
				,	cur.CLM_THRU_DT									as	EPSD_ID_THRU_DT
				,	cur.PRVDR_OSCAR_NUM								as	EPSD_ID_PRVDR_OSCAR_NUM
				,	1												as	EPSD_SEQ
				,	cast('Initial' as char(15))						as	EPSD_TYPE
				,	cur.CLM_THRU_DT									as	EPSD_THRU_DT
				,	cast(
						concat_ws(
							' - '
						,	date_format(cur.CLM_FROM_DT, '%Y-%m-%d')
						,	date_format(cur.CLM_THRU_DT, '%Y-%m-%d')
						)
					as	char(255)
					)												as	EPSD_SRVC_DATES
				,	cur.SRVC_DAYS									as	EPSD_SRVC_DAYS
				,	cur.CLM_PMT_AMT_ADJ								as	EPSD_PMT_AMT
				,	1												as	EPSD_CLM_CT
				,	cur.IP_FROM_DT
				,	cur.IP_INST_PMT_AMT
				,	cur.ED_FROM_DT
				,	cur.ED_INST_PMT_AMT
				,	cur.PPA_THRU_DT
				,	cur.PPA_INST_PMT_AMT
				from			claim_merge	as	cur
				where
					not exists	(
						select	1
						from	tmp_claim_merge_20230804_0828	as	prv
						where	prv.MR_MBI			=	cur.MR_MBI
							and	prv.PRVDR_OSCAR_NUM	=	cur.PRVDR_OSCAR_NUM
							and	prv.MR_MBI_SEQ		=	cur.MR_MBI_SEQ	-	1
							and	prv.CLM_THRU_DT		>=	date_add(cur.CLM_FROM_DT, interval -61 day)
						limit	1
					)
				
				union all
				-- HHA claims with corresponding HHA claim for same MBI/Provider within previous 60 days
				-- Subsequent episodes
				select
					cur.MR_MBI
				,	cur.CLM_FROM_DT
				,	cur.CLM_THRU_DT
				,	prev.YR
				,	prev.STAY_ID_FROM_DT
				,	prev.STAY_ID_THRU_DT
				,	prev.STAY_ID_PRVDR_OSCAR_NUM
				,	case	when	prev.EPSD_SRVC_DAYS + cur.SRVC_DAYS	>	60	then	prev.STAY_SEQ + 1							-- Recertification Episode
							else														prev.STAY_SEQ								-- Addition to Initial or Recertification Episode
					end												as	STAY_SEQ
				,	prev.STAY_FROM_DT
				,	cur.MR_MBI_SEQ
				,	cur.PRVDR_OSCAR_NUM
				,	cur.FAC_PRVDR_NPI_NUM
				,	cur.FAC_PRVDR_NAME_LAST
				,	cur.FAC_PRVDR_NAME_FIRST
				,	cur.FAC_PRVDR_NAME_ORG
				,	cur.BENE_PTNT_STUS
				,	cur.PRGRM
				,	cur.County
				,	cur.State
				,	case	when	prev.EPSD_SRVC_DAYS + cur.SRVC_DAYS	>	60	then	cur.CLM_FROM_DT								-- Recertification Episode
							else														prev.EPSD_ID_FROM_DT						-- Addition to Initial or Recertification Episode
					end												as	EPSD_ID_FROM_DT
				,	case	when	prev.EPSD_SRVC_DAYS + cur.SRVC_DAYS	>	60	then	cur.CLM_THRU_DT								-- Recertification Episode
							else														prev.EPSD_ID_THRU_DT						-- Addition to Initial or Recertification Episode
					end												as	EPSD_ID_THRU_DT
				,	case	when	prev.EPSD_SRVC_DAYS + cur.SRVC_DAYS	>	60	then	cur.PRVDR_OSCAR_NUM							-- Recertification Episode
							else														prev.EPSD_ID_PRVDR_OSCAR_NUM				-- Addition to Initial or Recertification Episode
					end												as	EPSD_ID_PRVDR_OSCAR_NUM
				,	case	when	prev.EPSD_SRVC_DAYS + cur.SRVC_DAYS	>	60	then	1											-- Recertification Episode
							else														prev.EPSD_SEQ + 1							-- Addition to Initial or Recertification Episode
					end												as	EPSD_SEQ
				,	case	when	prev.EPSD_SRVC_DAYS + cur.SRVC_DAYS	>	60	then	'Recertification'							-- Recertification Episode
							else														prev.EPSD_TYPE								-- Addition to Initial or Recertification Episode
					end												as	EPSD_TYPE
				,	cur.CLM_THRU_DT									as	EPSD_THRU_DT
				,	cast(
						case	when	prev.EPSD_SRVC_DAYS + cur.SRVC_DAYS	>	60	then		concat_ws(							-- Recertification Episode
																									' - '
																								,	date_format(cur.CLM_FROM_DT, '%Y-%m-%d')
																								,	date_format(cur.CLM_THRU_DT, '%Y-%m-%d')
																								)
								else														concat_ws(								-- Addition to Initial or Recertification Episode
																								concat(';', char(10))					-- Semi-colon, line-feed
																							,	prev.EPSD_SRVC_DATES
																							,	concat_ws(
																									' - '
																								,	date_format(cur.CLM_FROM_DT, '%Y-%m-%d')
																								,	date_format(cur.CLM_THRU_DT, '%Y-%m-%d')
																								)
																							)
						end
						as	char(255)
					)												as	EPSD_SRVC_DATES
				,	case	when	prev.EPSD_SRVC_DAYS + cur.SRVC_DAYS	>	60	then	cur.SRVC_DAYS								-- Recertification Episode
							else														prev.EPSD_SRVC_DAYS	+	cur.SRVC_DAYS		-- Addition to Initial or Recertification Episode
					end												as	EPSD_SRVC_DAYS
				,	case	when	prev.EPSD_SRVC_DAYS + cur.SRVC_DAYS	>	60	then	cur.CLM_PMT_AMT_ADJ							-- Recertification Episode
							else														prev.EPSD_PMT_AMT	+	cur.CLM_PMT_AMT_ADJ	-- Addition to Initial or Recertification Episode
					end												as	EPSD_PMT_AMT
				,	case	when	prev.EPSD_SRVC_DAYS + cur.SRVC_DAYS	>	60	then	1											-- Recertification Episode
							else														prev.EPSD_CLM_CT	+	1					-- Addition to Initial or Recertification Episode
					end												as	EPSD_PMT_AMT
				,	prev.IP_FROM_DT
				,	prev.IP_INST_PMT_AMT
				,	prev.ED_FROM_DT
				,	prev.ED_INST_PMT_AMT
				,	prev.PPA_THRU_DT
				,	prev.PPA_INST_PMT_AMT
				from			tmp_claim_merge_20230804_0828		as	cur
					inner join	episode_claims	as	prev	on	prev.MR_MBI				=	cur.MR_MBI
															and	prev.PRVDR_OSCAR_NUM	=	cur.PRVDR_OSCAR_NUM
															and	prev.MR_MBI_SEQ			=	cur.MR_MBI_SEQ	-	1
															and	prev.CLM_THRU_DT		>=	date_add(cur.CLM_FROM_DT, interval -61 day)
			)

		select	*
		from	episode_claims
		;


	--	No support for recursive CTEs (Databricks)
	--	A recursive CTE can be "unrolled" into a cascade of CTEs where each
	--		iteration is represented as a CTE and each CTE feeds into the next. 
	--		This technique, while admittedly inelegant, provides the same 
	--		functionality as recursion as long as the number of iterations can 
	--		be capped at a reasonable number. Testing each iteration to count 
	--		the number of rows returned will give a good indication of the number 
	--		of iterations required to complete the recursion. When successive 
	--		iterations return the same number of rows, it is likely that recursion 
	--		has completed. Including a few additional iterations for potential 
	--		growth might be prudent, depending on the application.

	--	Using WINDOW functions in place of self joins.
	--	Self joins can sometimes be avoided by using WINDOW functions to reference
	--		adjacent rows. The example below performed >100X better using WINDOW 
	--		functions in place of self-joins.
	--	Typically, a PARTITION clause specifies columns to be compared between the 
	--		current row and other rows. However, the PARTITION clause also 
	--		supports expressions that can be carefully crafted to evaluate to the 
	--		same value on the current row and other rows, even when the underlying
	--		values are not equal. In the example below, the current row has NULL 
	--		in the EPSD_ID column for the current row. The PARTITION clause uses 
	--		the IFNULL function to transform those NULL values into the value 
	--		expected for rows from the previous CTE. The result is effectively the 
	--		same as a self join.

		with
			..
			
		--^	The following cascade of hha_episode* CTEs are required to accurately group Claims into Episodes, because Claims with irregular number of 
		--		service days make it impossible to determine boundaries between Episodes using simple 60-day brackets. An episode can range in length 
		--		from 31-60 days. In the worst case, three 31-day Episodes would total to 93 days. Using 60-day brackets, that would only be two 60-day 
		--		Episodes. Even three 40-day Episodes would be bad enough to trigger the issue with using fixed brackets. The only way to accurately
		--		partition Claims with variable numbers of days into 60-day Episodes is to start with the first Claim and count forward to the first Claim
		--		that pushes the running total of service days over 60. That Claim would be the first in the next Episode, and the running total of service
		--		days would reset to zero.
		--	The cascade of CTEs below begin with hha_episode1 identifying the first Claim in the first Episode, which is easy because it is the first Claim 
		--		for the entire Stay. Each CTE updates EPSD_ID for all Claims in the Episode being identified, and for the first Claim in the following 
		--		Episode. Also, EPSD_END is upated to indicate the last Claim in the Episode, used to report each Episode on a single row in the main query. 
		--	Subsequent CTEs use a sliding window to capture the rows from the previous CTE that identify the first Claim for the Episode being identified. 
		--	hha_episode1 sets EPSD_ID = 2 for the first Claims in Episode 2. hha_episode2 uses the sliding window to capture the rows passed from hha_episode1 
		--		where EPSD_ID = 2. In the captured rows, STAY_SEQ identifies the first Claim for Episode 2 and EPSD_CT tells how many Claims are in Episode 2.
		--	Using sliding windows instead of more straight-forward self-joins results in a >100X performance improvement, allowing the query to execute in 30 seconds.
		,	hha_episode1	as	(
				select
						--	All claims in first episode
					case	when	a.STAY_SEQ	<=	b.EPSD_CT		then	1
						--	First claim in second episode
							when	a.STAY_SEQ	=	b.EPSD_CT + 1	then	2
						--	Claims for subsequenct episodes to be processed in subsequent iterations below
							else											null
					end	as	EPSD_ID
						--	Last claim of first episode
				,	case	when	a.STAY_SEQ	=	b.EPSD_CT		then	1
						--	Claims of first episode that are not last
							when	a.STAY_SEQ	<	b.EPSD_CT		then	0
						--	Claims for subsequent episodes to be processed in subsequenct iterations below
							else											null
					end	as	EPSD_END
				,	a.MR_MBI
				,	a.STAY_ID
				,	a.STAY_SEQ
				,	a.EPSD_CT
				from			hha_episode_claim_counts	as	a
			--	EPSD_ID on first episodes rows don't contain null, so the partition trick used on subsequent episodes below won't work here, thus the conventional (and slow) self-join here.
					inner join	hha_episode_claim_counts	as	b	on	a.MR_MBI	=	b.MR_MBI
																	and	a.STAY_ID	=	b.STAY_ID
																	and	b.STAY_SEQ	=	1
			)

		,	hha_episode2	as	(
				select
						--	Previous episodes
					case	when	EPSD_ID		is not null												then	EPSD_ID
						--	Current episode
							when	STAY_SEQ	<=		first_value(STAY_SEQ)	over	EpisodeID
													+	first_value(EPSD_CT)	over	EpisodeID - 1	then	2
						--	First claim for subsequent episode
							when	STAY_SEQ	=		first_value(STAY_SEQ)	over	EpisodeID
													+	first_value(EPSD_CT)	over	EpisodeID		then	3
						--	Claims for subsequent episodes to be processed in subsequenct iterations below
							else																				null
					end	as	EPSD_ID
						--	Previous episodes
				,	case	when	EPSD_END	is not null												then	EPSD_END
						--	Last claim of current episode
							when	STAY_SEQ	=		first_value(STAY_SEQ)	over	EpisodeID
													+	first_value(EPSD_CT)	over	EpisodeID - 1	then	1
						--	Claims of current episode that are not last
							when	STAY_SEQ	<		first_value(STAY_SEQ)	over	EpisodeID
													+	first_value(EPSD_CT)	over	EpisodeID - 1	then	0
						--	Claims for subsequent episodes to be processed in subsequenct iterations below
							else																				null
					end	as	EPSD_END
				,	MR_MBI
				,	STAY_ID
				,	STAY_SEQ
				,	EPSD_CT
				from			hha_episode1
			--	Partition expression is computed for ALL rows, and only rows where computed values match values computed for CURRENT ROW are included in window.
			--			The ISNULL function forces EPSD_ID in current row (which in this application will always contain null on rows benefitting from window functions) to be assigned to this episode.
			--			The result is the same as a self-join to return STAY_SEQ and EPSD_CT of first claim row for this episode without the overhead of joining large tables. It is verified as >100X faster than self-join.
				window	EpisodeID	as	(	partition by	MR_MBI	,	STAY_ID	,	(ifnull(EPSD_ID, 2) = 2)	order by	STAY_SEQ	)
			)

		,	hha_episode3	as	(
				select
					case	when	EPSD_ID		is not null												then	EPSD_ID
							when	STAY_SEQ	<=		first_value(STAY_SEQ)	over	EpisodeID
													+	first_value(EPSD_CT)	over	EpisodeID - 1	then	3
							when	STAY_SEQ	=		first_value(STAY_SEQ)	over	EpisodeID
													+	first_value(EPSD_CT)	over	EpisodeID		then	4
							else																				null
					end	as	EPSD_ID
				,	case	when	EPSD_END	is not null												then	EPSD_END
							when	STAY_SEQ	=		first_value(STAY_SEQ)	over	EpisodeID
													+	first_value(EPSD_CT)	over	EpisodeID - 1	then	1
							when	STAY_SEQ	<		first_value(STAY_SEQ)	over	EpisodeID
													+	first_value(EPSD_CT)	over	EpisodeID - 1	then	0
							else																				null
					end	as	EPSD_END
				,	MR_MBI
				,	STAY_ID
				,	STAY_SEQ
				,	EPSD_CT
				from			hha_episode2
				window	EpisodeID	as	(	partition by	MR_MBI	,	STAY_ID	,	(ifnull(EPSD_ID, 3) = 3)	order by	STAY_SEQ	)
			)

		,	hha_episode4	as	(
				select
					case	when	EPSD_ID		is not null												then	EPSD_ID
							when	STAY_SEQ	<=		first_value(STAY_SEQ)	over	EpisodeID
													+	first_value(EPSD_CT)	over	EpisodeID - 1	then	4
							when	STAY_SEQ	=		first_value(STAY_SEQ)	over	EpisodeID
													+	first_value(EPSD_CT)	over	EpisodeID		then	5
							else																				null
					end	as	EPSD_ID
				,	case	when	EPSD_END	is not null												then	EPSD_END
							when	STAY_SEQ	=		first_value(STAY_SEQ)	over	EpisodeID
													+	first_value(EPSD_CT)	over	EpisodeID - 1	then	1
							when	STAY_SEQ	<		first_value(STAY_SEQ)	over	EpisodeID
													+	first_value(EPSD_CT)	over	EpisodeID - 1	then	0
							else																				null
					end	as	EPSD_END
				,	MR_MBI
				,	STAY_ID
				,	STAY_SEQ
				,	EPSD_CT
				from			hha_episode3
				window	EpisodeID	as	(	partition by	MR_MBI	,	STAY_ID	,	(ifnull(EPSD_ID, 4) = 4)	order by	STAY_SEQ	)
			)

		..

		--^	HHA Stays
		,	hha_stays	as	(
				select
					e.MR_MBI
				,	e.STAY_ID
				,	e.STAY_BEG_DT
				,	e.STAY_END_DT
				from			hha_episodes	as	e
				group by
					e.MR_MBI
				,	e.STAY_ID
				,	e.STAY_BEG_DT
				,	e.STAY_END_DT
			)

		--^	HHA Episode Inpatient Before Stay Begin
		,	ip_before_begin	as	(
				select
					s.MR_MBI
				,	s.STAY_ID
				from			hha_stays	as	s
					inner join	ip_claims	as	ip	on	s.MR_MBI							=	ip.MR_MBI
													and	s.STAY_BEG_DT						>=	ip.CLM_THRU_DT
													and	date_add(day, -30, s.STAY_BEG_DT)	<=	ip.CLM_THRU_DT
				group by
					s.MR_MBI
				,	s.STAY_ID
			)

		--^	HHA Episode Inpatient After Stay Begin
		,	ip_after_begin	as	(
				select
					s.MR_MBI
				,	s.STAY_ID
				,	sum(ip.CLM_PMT_AMT)	as	STAY_SUM
				from			hha_stays	as	s
					inner join	ip_claims	as	ip	on	s.MR_MBI							=	ip.MR_MBI
													and	s.STAY_BEG_DT						<=	ip.CLM_FROM_DT
													and	date_add(day, 60, s.STAY_BEG_DT)	>=	ip.CLM_FROM_DT
				group by
					s.MR_MBI
				,	s.STAY_ID
			)

		--^	HHA Episode Inpatient After Stay End
		,	ip_after_end	as	(
				select
					s.MR_MBI
				,	s.STAY_ID
				,	sum(ip.CLM_PMT_AMT)	as	STAY_SUM
				from			hha_stays	as	s
					inner join	ip_claims	as	ip	on	s.MR_MBI							=	ip.MR_MBI
													and	date_add(day, 2, s.STAY_END_DT)		<=	ip.CLM_FROM_DT
													and	date_add(day, 32, s.STAY_END_DT)	>=	ip.CLM_FROM_DT
				group by
					s.MR_MBI
				,	s.STAY_ID
			)

		--^	HHA Episode Emergency Department Use After Stay Begin
		,	ed_after_begin	as	(
				select
					s.MR_MBI
				,	s.STAY_ID
				,	sum(ed.CLM_PMT_AMT)	as	STAY_SUM
				from			hha_stays	as	s
					inner join	ed_claims	as	ed	on	s.MR_MBI							=	ed.MR_MBI
													and	s.STAY_BEG_DT						<=	ed.CLM_FROM_DT
													and	date_add(day, 60, s.STAY_BEG_DT)	>=	ed.CLM_FROM_DT
				group by
					s.MR_MBI
				,	s.STAY_ID
			)

		--^	HHA Episodes (not Claims)
		,	hha_ep_metrics	as	(
				select
					e.MR_MBI							as	`Most Recent MBI`
				,	e.`ACO Historical`
				,	e.`ACO Current`
				,	e.STAY_ID							as	`Stay ID`
				,	e.STAY_END							as	`Home Health Stay Discharge`
				,	e.STAY_BEG_DT						as	`Stay Begin`
				,	e.STAY_END_DT						as	`Stay End`
				,	e.EPSD_ID							as	`Episode ID`
				,	e.EPSD_CLM_CT						as	`Episode Claim Count`
				,	e.EPSD_BEG_DT						as	`Episode Begin`
				,	e.EPSD_END_DT						as	`Episode End`
				,	e.EPSD_SRVC_DATES					as	`Episode Service Dates`
				,	year(e.EPSD_BEG_DT)					as	`Episode Year`
				,	e.EPSD_SRVC_DAYS					as	`Episode Service Days`
				,	e.EPSD_TYPE							as	`Episode Type`
				,	e.DSCHRG_HOME						as	`Discharged Home`
				,	e.PRVDR_OSCAR_NUM					as	`CMS Certification Number`
				,	e.EPSD_PMT_AMT						as	`Episode Payment`
				,	e.FAC_PRVDR_NPI_NUM					as	`Provider NPI`
				,	e.FAC_PRVDR_LAST_NAME				as	`Provider Name Last`
				,	e.FAC_PRVDR_FIRST_NAME				as	`Provider Name First`
				,	e.FAC_PRVDR_ORG_NAME				as	`Provider Name Organization`
				,	e.PRVDR_STATE						as	`Provider State`
				,	e.PRVDR_CITY						as	`Provider City`
				,	e.`NPI`								as	`Contract NPI`
				,	e.`CCN`								as	`Contract CMS Certification Number`
				,	e.`TIN`								as	`Contract Tax ID`
				,	e.`Organization`					as	`Contract Organization`
				,	e.`Contracted State`
				,	e.`Contract ID`
				,	e.`Contract Name`
				,	e.`Contract Type ID`
				,	e.`Model Category`
				,	e.`Financial Model`
				,	e.`% of FFS Reduction`
				,	e.`Hospitalization Rate`
				,	e.`ED Utilization Rate`
				,	e.`Readmission Rate`
				,	e.`Hospitalization Rate Incentive`
				,	e.`ED Utilization Rate Incentive`
				,	e.`Readmission Rate Incentive`
				,	case	when	e.STAY_END			=	1	then	ipab.STAY_SUM
							else										0
					end								as	`Inpatient Cost <=60 Days After Stay Start`
				,	case	when	e.STAY_END			=	1
								and	ipab.MR_MBI		is not null	then	1
							else										0
					end								as	`Inpatient Admission <=60 Days After Stay Start`
				,	case	when	e.STAY_END			=	1	then	edab.STAY_SUM
									else								0
							end						as	`Emergency Department Cost <=60 Days After Stay Start`
				,	case	when	e.STAY_END			=	1
								and	edab.MR_MBI		is not null	then	1
							else										0
					end								as	`Emergency Department Use <=60 Days After Stay Start`
				,	case	when	e.STAY_END			=	1
								and	e.DSCHRG_HOME		=	1
								and	ipbb.MR_MBI		is not null	then	ipae.STAY_SUM
							else										0
					end								as	`Inpatient Readmission Cost 2-32 Days After Stay End`
				,	case	when	e.STAY_END			=	1
								and	ipbb.MR_MBI		is not null	then	1
							else										0
					end								as	`Inpatient Admission <=30 Days Before Stay Start`
				,	case	when	e.STAY_END			=	1
								and	e.DSCHRG_HOME		=	1
								and	ipae.MR_MBI		is not null	then	1
							else										0
					end								as	`Inpatient Readmission 2-32 Days After Stay End`
				from			hha_episodes		as	e
					left join	ip_before_begin	as	ipbb	on	e.MR_MBI	=	ipbb.MR_MBI	and	e.STAY_ID	=	ipbb.STAY_ID
					left join	ip_after_begin	as	ipab	on	e.MR_MBI	=	ipab.MR_MBI	and	e.STAY_ID	=	ipab.STAY_ID
					left join	ip_after_end	as	ipae	on	e.MR_MBI	=	ipae.MR_MBI	and	e.STAY_ID	=	ipae.STAY_ID
					left join	ed_after_begin	as	edab	on	e.MR_MBI	=	edab.MR_MBI	and	e.STAY_ID	=	edab.STAY_ID
		)

		select	*
		from	hha_episode99
		where	EPSD_END	=	1		--	Last Episode in Stay
		;
