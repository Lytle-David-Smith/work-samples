# Define the SQL statements
comment = "\n".join([
    "# National Plan and Provider Enumeration System  (NPPES) NPI",
    "- https://download.cms.gov/nppes/NPI_Files.html"
])
sql_statement1 = f"""
	create or replace view test.analytics_schema.dim_nppes_view_npi
	comment '{comment}'
	as (
		SELECT
			NPI,
			Entity_Type_Code,
			Replacement_NPI,
			Employer_Identification_Number_EIN AS EIN,
			Is_Sole_Proprietor,
			Is_Organization_Subpart,
			Parent_Organization_LBN AS Parent_Organization_Legal_Business_Name,
			Parent_Organization_TIN,
			Provider_Gender_Code AS Gender_Code,
			Provider_Enumeration_Date AS Enumeration_Date,
			Certification_Date,
			NPI_Deactivation_Reason_Code AS Deactivation_Reason_Code,
			NPI_Deactivation_Date AS Deactivation_Date,
			NPI_Reactivation_Date AS Reactivation_Date,
			Last_Update_Date
		FROM
			test.analytics_schema.dim_nppes_npidata
		ORDER BY
			NPI
	)
"""

comment = "\n".join([
    "# National Plan and Provider Enumeration System  (NPPES) Name",
    "- https://download.cms.gov/nppes/NPI_Files.html"
])
sql_statement2 = f"""
	create or replace view test.analytics_schema.dim_nppes_view_name
	comment '{comment}'
	as (
					select
						NPI
					,	'Primary'										as	Address_Type
					,	null											as	Other_Type_Code
					,	Provider_Organization_Name_Legal_Business_Name	as	Organization_Name
					,	Provider_Last_Name_Legal_Name					as	Last_Name
					,	Provider_First_Name								as	First_Name
					,	Provider_Middle_Name							as	Middle_Name
					,	Provider_Name_Prefix_Text						as	Name_Prefix
					,	Provider_Name_Suffix_Text						as	Name_Suffix
					,	Provider_Credential_Text						as	Credential
					from	test.analytics_schema.dim_nppes_npidata
					where
						Provider_Organization_Name_Legal_Business_Name	is not null
					or	Provider_Last_Name_Legal_Name					is not null
					or	Provider_First_Name								is not null
					or	Provider_Middle_Name							is not null
					or	Provider_Name_Prefix_Text						is not null
					or	Provider_Name_Suffix_Text						is not null
					or	Provider_Credential_Text						is not null

		union all	select
						NPI
					,	'Other'											as	Address_Type
					,	coalesce(
							Provider_Other_Organization_Name_Type_Code
						,	Provider_Other_Last_Name_Type_Code
						)												as	Other_Type_Code
					,	Provider_Other_Organization_Name				as	Organization_Name
					,	Provider_Other_Last_Name						as	Last_Name
					,	Provider_Other_First_Name						as	First_Name
					,	Provider_Other_Middle_Name						as	Middle_Name
					,	Provider_Other_Name_Prefix_Text					as	Name_Prefix
					,	Provider_Other_Name_Suffix_Text					as	Name_Suffix
					,	Provider_Other_Credential_Text					as	Credential
					from	test.analytics_schema.dim_nppes_npidata
					where
						Provider_Other_Organization_Name_Type_Code		is not null
					or	Provider_Other_Last_Name_Type_Code				is not null
					or	Provider_Other_Organization_Name				is not null
					or	Provider_Other_Last_Name						is not null
					or	Provider_Other_First_Name						is not null
					or	Provider_Other_Middle_Name						is not null
					or	Provider_Other_Name_Prefix_Text					is not null
					or	Provider_Other_Name_Suffix_Text					is not null
					or	Provider_Other_Credential_Text					is not null

		union all	select
						NPI
					,	'Authorized'									as	Address_Type
					,	null											as	Other_Type_Code
					,	Provider_Organization_Name_Legal_Business_Name	as	Organization_Name
					,	Authorized_Official_Last_Name					as	Last_Name
					,	Authorized_Official_First_Name					as	First_Name
					,	Authorized_Official_Middle_Name					as	Middle_Name
					,	Authorized_Official_Name_Prefix_Text			as	Name_Prefix
					,	Authorized_Official_Name_Suffix_Text			as	Name_Suffix
					,	Authorized_Official_Credential_Text				as	Credential
					from	test.analytics_schema.dim_nppes_npidata
					where
						Provider_Organization_Name_Legal_Business_Name	is not null
					or	Authorized_Official_Last_Name					is not null
					or	Authorized_Official_First_Name					is not null
					or	Authorized_Official_Middle_Name					is not null
					or	Authorized_Official_Name_Prefix_Text			is not null
					or	Authorized_Official_Name_Suffix_Text			is not null
					or	Authorized_Official_Credential_Text				is not null

		order by
			NPI
		,	Address_Type
		,	Other_Type_Code
	)
"""

comment = "\n".join([
    "# National Plan and Provider Enumeration System  (NPPES) Address",
    "- https://download.cms.gov/nppes/NPI_Files.html"
])
sql_statement3 = f"""
	create or replace view test.analytics_schema.dim_nppes_view_address
	comment '{comment}'
	as (
					select
						NPI
					,	'Mailing'														as	Purpose
					,	Provider_First_Line_Business_Mailing_Address					as	Address1
					,	Provider_Second_Line_Business_Mailing_Address					as	Address2
					,	Provider_Business_Mailing_Address_City_Name						as	City
					,	Provider_Business_Mailing_Address_State_Name					as	State
					,	Provider_Business_Mailing_Address_Postal_Code					as	Postal_Code
					,	Provider_Business_Mailing_Address_Country_Code_If_outside_US	as	CountryCode
					,	case	when	Provider_Business_Mailing_Address_Country_Code_If_outside_US	=	'US'	then	'Domestic'
								when	Provider_Business_Mailing_Address_Country_Code_If_outside_US	is null		then	'Domestic'
								else																						'Foreign'
						end																as	Type
					,	Provider_Business_Mailing_Address_Telephone_Number				as	Phone
					,	null															as	Phone_Ext
					,	Provider_Business_Mailing_Address_Fax_Number					as	Fax
					from	test.analytics_schema.dim_nppes_npidata
					where
						Provider_First_Line_Business_Mailing_Address					is not null
					or	Provider_Second_Line_Business_Mailing_Address					is not null
					or	Provider_Business_Mailing_Address_City_Name						is not null
					or	Provider_Business_Mailing_Address_State_Name					is not null
					or	Provider_Business_Mailing_Address_Postal_Code					is not null
					or	Provider_Business_Mailing_Address_Country_Code_If_outside_US	is not null
					or	Provider_Business_Mailing_Address_Telephone_Number				is not null
					or	Provider_Business_Mailing_Address_Fax_Number					is not null

		union all	select
						NPI
					,	'Primary Location'														as	Purpose
					,	Provider_First_Line_Business_Practice_Location_Address					as	Address1
					,	Provider_Second_Line_Business_Practice_Location_Address					as	Address2
					,	Provider_Business_Practice_Location_Address_City_Name					as	City
					,	Provider_Business_Practice_Location_Address_State_Name					as	State
					,	Provider_Business_Practice_Location_Address_Postal_Code					as	Postal_Code
					,	Provider_Business_Practice_Location_Address_Country_Code_If_outside_US	as	Country_Code
					,	case	when	Provider_Business_Practice_Location_Address_Country_Code_If_outside_US	=	'US'	then	'Domestic'
								when	Provider_Business_Practice_Location_Address_Country_Code_If_outside_US	is null		then	'Domestic'
								else																								'Foreign'
						end																		as	Type
					,	Provider_Business_Practice_Location_Address_Telephone_Number			as	Phone
					,	null																	as	Phone_Ext
					,	Provider_Business_Practice_Location_Address_Fax_Number					as	Fax
					from	test.analytics_schema.dim_nppes_npidata
					where
						Provider_First_Line_Business_Practice_Location_Address					is not null
					or	Provider_Second_Line_Business_Practice_Location_Address					is not null
					or	Provider_Business_Practice_Location_Address_City_Name					is not null
					or	Provider_Business_Practice_Location_Address_State_Name					is not null
					or	Provider_Business_Practice_Location_Address_Postal_Code					is not null
					or	Provider_Business_Practice_Location_Address_Country_Code_If_outside_US	is not null
					or	Provider_Business_Practice_Location_Address_Telephone_Number			is not null
					or	Provider_Business_Practice_Location_Address_Fax_Number					is not null

		union all	select
						NPI
					,	'Secondary Location'													as	Purpose
					,	Provider_Secondary_Practice_Location_Address_Address_Line_1				as	Address1
					,	Provider_Secondary_Practice_Location_Address_Address_Line_2				as	Address2
					,	Provider_Secondary_Practice_Location_Address_City_Name					as	City
					,	Provider_Secondary_Practice_Location_Address_State_Name					as	State
					,	Provider_Secondary_Practice_Location_Address_Postal_Code				as	Postal_Code
					,	Provider_Secondary_Practice_Location_Address_Country_Code_If_outside_US	as	Country_Code
					,	case	when	Provider_Secondary_Practice_Location_Address_Country_Code_If_outside_US	=	'US'	then	'Domestic'
								when	Provider_Secondary_Practice_Location_Address_Country_Code_If_outside_US	is null		then	'Domestic'
								else																								'Foreign'
						end																		as	Type
					,	Provider_Secondary_Practice_Location_Address_Telephone_Number			as	Phone
					,	Provider_Secondary_Practice_Location_Address_Telephone_Extension		as	Phone_Ext
					,	Provider_Practice_Location_Address_Fax_Number							as	Fax
					from	test.analytics_schema.dim_nppes_pl
					where
						Provider_Secondary_Practice_Location_Address_Address_Line_1				is not null
					or	Provider_Secondary_Practice_Location_Address_Address_Line_1				is not null
					or	Provider_Secondary_Practice_Location_Address_City_Name					is not null
					or	Provider_Secondary_Practice_Location_Address_State_Name					is not null
					or	Provider_Secondary_Practice_Location_Address_Postal_Code				is not null
					or	Provider_Secondary_Practice_Location_Address_Country_Code_If_outside_US	is not null
					or	Provider_Secondary_Practice_Location_Address_Telephone_Number			is not null
					or	Provider_Secondary_Practice_Location_Address_Telephone_Extension		is not null
					or	Provider_Practice_Location_Address_Fax_Number							is not null

		order by
			NPI
		,	Purpose
	);
"""

comment = "\n".join([
    "# National Plan and Provider Enumeration System  (NPPES) Identifier",
    "- https://download.cms.gov/nppes/NPI_Files.html"
])
sql_statement4 = f"""
	create or replace view test.analytics_schema.dim_nppes_view_identifier
	comment '{comment}'
	as (
					select
						NPI
					,	Other_Provider_Identifier_1					as	Identifier
					,	1											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_1		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_1			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_1			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_1				is not null
					or	Other_Provider_Identifier_Type_Code_1	is not null
					or	Other_Provider_Identifier_State_1		is not null
					or	Other_Provider_Identifier_Issuer_1		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_2					as	Identifier
					,	2											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_2		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_2			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_2			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_2				is not null
					or	Other_Provider_Identifier_Type_Code_2	is not null
					or	Other_Provider_Identifier_State_2		is not null
					or	Other_Provider_Identifier_Issuer_2		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_3					as	Identifier
					,	3											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_3		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_3			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_3			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_3				is not null
					or	Other_Provider_Identifier_Type_Code_3	is not null
					or	Other_Provider_Identifier_State_3		is not null
					or	Other_Provider_Identifier_Issuer_3		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_4					as	Identifier
					,	4											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_4		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_4			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_4			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_4				is not null
					or	Other_Provider_Identifier_Type_Code_4	is not null
					or	Other_Provider_Identifier_State_4		is not null
					or	Other_Provider_Identifier_Issuer_4		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_5					as	Identifier
					,	5											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_5		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_5			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_5			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_5				is not null
					or	Other_Provider_Identifier_Type_Code_5	is not null
					or	Other_Provider_Identifier_State_5		is not null
					or	Other_Provider_Identifier_Issuer_5		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_6					as	Identifier
					,	6											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_6		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_6			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_6			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_6				is not null
					or	Other_Provider_Identifier_Type_Code_6	is not null
					or	Other_Provider_Identifier_State_6		is not null
					or	Other_Provider_Identifier_Issuer_6		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_7					as	Identifier
					,	7											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_7		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_7			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_7			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_7				is not null
					or	Other_Provider_Identifier_Type_Code_7	is not null
					or	Other_Provider_Identifier_State_7		is not null
					or	Other_Provider_Identifier_Issuer_7		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_8					as	Identifier
					,	8											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_8		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_8			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_8			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_8				is not null
					or	Other_Provider_Identifier_Type_Code_8	is not null
					or	Other_Provider_Identifier_State_8		is not null
					or	Other_Provider_Identifier_Issuer_8		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_9					as	Identifier
					,	9											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_9		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_9			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_9			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_9				is not null
					or	Other_Provider_Identifier_Type_Code_9	is not null
					or	Other_Provider_Identifier_State_9		is not null
					or	Other_Provider_Identifier_Issuer_9		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_10				as	Identifier
					,	10											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_10		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_10			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_10			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_10			is not null
					or	Other_Provider_Identifier_Type_Code_10	is not null
					or	Other_Provider_Identifier_State_10		is not null
					or	Other_Provider_Identifier_Issuer_10		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_11				as	Identifier
					,	11											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_11		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_11			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_11			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_11			is not null
					or	Other_Provider_Identifier_Type_Code_11	is not null
					or	Other_Provider_Identifier_State_11		is not null
					or	Other_Provider_Identifier_Issuer_11		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_12				as	Identifier
					,	12											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_12		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_12			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_12			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_12			is not null
					or	Other_Provider_Identifier_Type_Code_12	is not null
					or	Other_Provider_Identifier_State_12		is not null
					or	Other_Provider_Identifier_Issuer_12		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_13				as	Identifier
					,	13											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_13		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_13			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_13			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_13			is not null
					or	Other_Provider_Identifier_Type_Code_13	is not null
					or	Other_Provider_Identifier_State_13		is not null
					or	Other_Provider_Identifier_Issuer_13		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_14				as	Identifier
					,	14											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_14		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_14			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_14			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_14			is not null
					or	Other_Provider_Identifier_Type_Code_14	is not null
					or	Other_Provider_Identifier_State_14		is not null
					or	Other_Provider_Identifier_Issuer_14		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_15				as	Identifier
					,	15											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_15		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_15			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_15			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_15			is not null
					or	Other_Provider_Identifier_Type_Code_15	is not null
					or	Other_Provider_Identifier_State_15		is not null
					or	Other_Provider_Identifier_Issuer_15		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_16				as	Identifier
					,	16											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_16		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_16			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_16			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_16			is not null
					or	Other_Provider_Identifier_Type_Code_16	is not null
					or	Other_Provider_Identifier_State_16		is not null
					or	Other_Provider_Identifier_Issuer_16		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_17				as	Identifier
					,	17											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_17		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_17			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_17			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_17			is not null
					or	Other_Provider_Identifier_Type_Code_17	is not null
					or	Other_Provider_Identifier_State_17		is not null
					or	Other_Provider_Identifier_Issuer_17		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_18				as	Identifier
					,	18											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_18		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_18			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_18			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_18			is not null
					or	Other_Provider_Identifier_Type_Code_18	is not null
					or	Other_Provider_Identifier_State_18		is not null
					or	Other_Provider_Identifier_Issuer_18		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_19				as	Identifier
					,	19											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_19		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_19			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_19			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_19			is not null
					or	Other_Provider_Identifier_Type_Code_19	is not null
					or	Other_Provider_Identifier_State_19		is not null
					or	Other_Provider_Identifier_Issuer_19		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_20				as	Identifier
					,	20											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_20		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_20			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_20			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_20			is not null
					or	Other_Provider_Identifier_Type_Code_20	is not null
					or	Other_Provider_Identifier_State_20		is not null
					or	Other_Provider_Identifier_Issuer_20		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_21				as	Identifier
					,	21											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_21		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_21			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_21			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_21			is not null
					or	Other_Provider_Identifier_Type_Code_21	is not null
					or	Other_Provider_Identifier_State_21		is not null
					or	Other_Provider_Identifier_Issuer_21		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_22				as	Identifier
					,	22											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_22		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_22			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_22			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_22			is not null
					or	Other_Provider_Identifier_Type_Code_22	is not null
					or	Other_Provider_Identifier_State_22		is not null
					or	Other_Provider_Identifier_Issuer_22		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_23				as	Identifier
					,	23											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_23		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_23			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_23			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_23			is not null
					or	Other_Provider_Identifier_Type_Code_23	is not null
					or	Other_Provider_Identifier_State_23		is not null
					or	Other_Provider_Identifier_Issuer_23		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_24				as	Identifier
					,	24											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_24		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_24			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_24			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_24			is not null
					or	Other_Provider_Identifier_Type_Code_24	is not null
					or	Other_Provider_Identifier_State_24		is not null
					or	Other_Provider_Identifier_Issuer_24		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_25				as	Identifier
					,	25											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_25		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_25			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_25			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_25			is not null
					or	Other_Provider_Identifier_Type_Code_25	is not null
					or	Other_Provider_Identifier_State_25		is not null
					or	Other_Provider_Identifier_Issuer_25		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_26				as	Identifier
					,	26											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_26		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_26			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_26			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_26			is not null
					or	Other_Provider_Identifier_Type_Code_26	is not null
					or	Other_Provider_Identifier_State_26		is not null
					or	Other_Provider_Identifier_Issuer_26		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_27				as	Identifier
					,	27											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_27		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_27			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_27			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_27			is not null
					or	Other_Provider_Identifier_Type_Code_27	is not null
					or	Other_Provider_Identifier_State_27		is not null
					or	Other_Provider_Identifier_Issuer_27		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_28				as	Identifier
					,	28											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_28		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_28			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_28			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_28			is not null
					or	Other_Provider_Identifier_Type_Code_28	is not null
					or	Other_Provider_Identifier_State_28		is not null
					or	Other_Provider_Identifier_Issuer_28		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_29				as	Identifier
					,	29											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_29		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_29			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_29			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_29			is not null
					or	Other_Provider_Identifier_Type_Code_29	is not null
					or	Other_Provider_Identifier_State_29		is not null
					or	Other_Provider_Identifier_Issuer_29		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_30				as	Identifier
					,	30											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_30		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_30			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_30			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_30			is not null
					or	Other_Provider_Identifier_Type_Code_30	is not null
					or	Other_Provider_Identifier_State_30		is not null
					or	Other_Provider_Identifier_Issuer_30		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_31				as	Identifier
					,	31											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_31		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_31			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_31			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_31			is not null
					or	Other_Provider_Identifier_Type_Code_31	is not null
					or	Other_Provider_Identifier_State_31		is not null
					or	Other_Provider_Identifier_Issuer_31		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_32				as	Identifier
					,	32											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_32		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_32			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_32			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_32			is not null
					or	Other_Provider_Identifier_Type_Code_32	is not null
					or	Other_Provider_Identifier_State_32		is not null
					or	Other_Provider_Identifier_Issuer_32		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_33				as	Identifier
					,	33											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_33		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_33			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_33			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_33			is not null
					or	Other_Provider_Identifier_Type_Code_33	is not null
					or	Other_Provider_Identifier_State_33		is not null
					or	Other_Provider_Identifier_Issuer_33		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_34				as	Identifier
					,	34											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_34		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_34			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_34			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_34			is not null
					or	Other_Provider_Identifier_Type_Code_34	is not null
					or	Other_Provider_Identifier_State_34		is not null
					or	Other_Provider_Identifier_Issuer_34		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_35				as	Identifier
					,	35											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_35		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_35			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_35			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_35			is not null
					or	Other_Provider_Identifier_Type_Code_35	is not null
					or	Other_Provider_Identifier_State_35		is not null
					or	Other_Provider_Identifier_Issuer_35		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_36				as	Identifier
					,	36											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_36		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_36			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_36			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_36			is not null
					or	Other_Provider_Identifier_Type_Code_36	is not null
					or	Other_Provider_Identifier_State_36		is not null
					or	Other_Provider_Identifier_Issuer_36		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_37				as	Identifier
					,	37											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_37		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_37			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_37			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_37			is not null
					or	Other_Provider_Identifier_Type_Code_37	is not null
					or	Other_Provider_Identifier_State_37		is not null
					or	Other_Provider_Identifier_Issuer_37		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_38				as	Identifier
					,	38											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_38		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_38			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_38			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_38			is not null
					or	Other_Provider_Identifier_Type_Code_38	is not null
					or	Other_Provider_Identifier_State_38		is not null
					or	Other_Provider_Identifier_Issuer_38		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_39				as	Identifier
					,	39											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_39		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_39			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_39			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_39			is not null
					or	Other_Provider_Identifier_Type_Code_39	is not null
					or	Other_Provider_Identifier_State_39		is not null
					or	Other_Provider_Identifier_Issuer_39		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_40				as	Identifier
					,	40											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_40		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_40			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_40			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_40			is not null
					or	Other_Provider_Identifier_Type_Code_40	is not null
					or	Other_Provider_Identifier_State_40		is not null
					or	Other_Provider_Identifier_Issuer_40		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_41				as	Identifier
					,	41											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_41		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_41			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_41			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_41			is not null
					or	Other_Provider_Identifier_Type_Code_41	is not null
					or	Other_Provider_Identifier_State_41		is not null
					or	Other_Provider_Identifier_Issuer_41		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_42				as	Identifier
					,	42											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_42		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_42			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_42			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_42			is not null
					or	Other_Provider_Identifier_Type_Code_42	is not null
					or	Other_Provider_Identifier_State_42		is not null
					or	Other_Provider_Identifier_Issuer_42		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_43				as	Identifier
					,	43											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_43		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_43			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_43			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_43			is not null
					or	Other_Provider_Identifier_Type_Code_43	is not null
					or	Other_Provider_Identifier_State_43		is not null
					or	Other_Provider_Identifier_Issuer_43		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_44				as	Identifier
					,	44											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_44		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_44			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_44			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_44			is not null
					or	Other_Provider_Identifier_Type_Code_44	is not null
					or	Other_Provider_Identifier_State_44		is not null
					or	Other_Provider_Identifier_Issuer_44		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_45				as	Identifier
					,	45											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_45		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_45			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_45			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_45			is not null
					or	Other_Provider_Identifier_Type_Code_45	is not null
					or	Other_Provider_Identifier_State_45		is not null
					or	Other_Provider_Identifier_Issuer_45		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_46				as	Identifier
					,	46											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_46		
					,	Other_Provider_Identifier_State_46			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_46			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_46			is not null
					or	Other_Provider_Identifier_Type_Code_46	is not null
					or	Other_Provider_Identifier_State_46		is not null
					or	Other_Provider_Identifier_Issuer_46		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_47				as	Identifier
					,	47											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_47		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_47			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_47			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_47			is not null
					or	Other_Provider_Identifier_Type_Code_47	is not null
					or	Other_Provider_Identifier_State_47		is not null
					or	Other_Provider_Identifier_Issuer_47		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_48				as	Identifier
					,	48											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_48		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_48			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_48			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_48			is not null
					or	Other_Provider_Identifier_Type_Code_48	is not null
					or	Other_Provider_Identifier_State_48		is not null
					or	Other_Provider_Identifier_Issuer_48		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_49				as	Identifier
					,	49											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_49		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_49			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_49			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_49			is not null
					or	Other_Provider_Identifier_Type_Code_49	is not null
					or	Other_Provider_Identifier_State_49		is not null
					or	Other_Provider_Identifier_Issuer_49		is not null

		union all	select
						NPI
					,	Other_Provider_Identifier_50				as	Identifier
					,	50											as	Identifier_Number
					,	Other_Provider_Identifier_Type_Code_50		as	Identifier_Type_Code
					,	Other_Provider_Identifier_State_50			as	Identifier_State
					,	Other_Provider_Identifier_Issuer_50			as	Identifier_Issuer
					from	test.analytics_schema.dim_nppes_npidata
					where
						Other_Provider_Identifier_50			is not null
					or	Other_Provider_Identifier_Type_Code_50	 is not null
					or	Other_Provider_Identifier_State_50		 is not null
					or	Other_Provider_Identifier_Issuer_50		 is not null

		order by
			NPI
		,	Identifier_Number
	)
"""

comment = "\n".join([
    "# National Plan and Provider Enumeration System  (NPPES) Taxonomy",
    "- https://download.cms.gov/nppes/NPI_Files.html"
])
sql_statement5 = f"""
	create or replace view test.analytics_schema.dim_nppes_view_taxonomy
	comment '{comment}'
	as (
					select
						NPI
					,	'1'												as	Taxonomy_Number
					,	Healthcare_Provider_Taxonomy_Code_1				as	Taxonomy_Code
					,	Healthcare_Provider_Taxonomy_Group_1			as	Taxonomy_Group
					,	Provider_License_Number_1						as	License_Number
					,	Provider_License_Number_State_Code_1			as	License_Number_State_Code
					,	Healthcare_Provider_Primary_Taxonomy_Switch_1	as	Primary_Taxonomy_Switch
					from test.analytics_schema.dim_nppes_npidata
					where
						Healthcare_Provider_Taxonomy_Code_1				is not null
					or	Healthcare_Provider_Taxonomy_Group_1			is not null
					or	Provider_License_Number_1						is not null
					or	Provider_License_Number_State_Code_1			is not null
					or	Healthcare_Provider_Primary_Taxonomy_Switch_1	is not null
		union all
					select
						NPI
					,	'2'												as	Taxonomy_Number
					,	Healthcare_Provider_Taxonomy_Code_2				as	Taxonomy_Code
					,	Healthcare_Provider_Taxonomy_Group_2			as	Taxonomy_Group
					,	Provider_License_Number_2						as	License_Number
					,	Provider_License_Number_State_Code_2			as	License_Number_State_Code
					,	Healthcare_Provider_Primary_Taxonomy_Switch_2	as	Primary_Taxonomy_Switch
					from test.analytics_schema.dim_nppes_npidata
					where
						Healthcare_Provider_Taxonomy_Code_2				is not null
					or	Healthcare_Provider_Taxonomy_Group_1			is not null
					or	Provider_License_Number_2						is not null
					or	Provider_License_Number_State_Code_2			is not null
					or	Healthcare_Provider_Primary_Taxonomy_Switch_2	is not null
		union all
					select
						NPI
					,	'3'												as	Taxonomy_Number
					,	Healthcare_Provider_Taxonomy_Code_3				as	Taxonomy_Code
					,	Healthcare_Provider_Taxonomy_Group_3			as	Taxonomy_Group
					,	Provider_License_Number_3						as	License_Number
					,	Provider_License_Number_State_Code_3			as	License_Number_State_Code
					,	Healthcare_Provider_Primary_Taxonomy_Switch_3	as	Primary_Taxonomy_Switch
					from test.analytics_schema.dim_nppes_npidata
					where
						Healthcare_Provider_Taxonomy_Code_3				is not null
					or	Healthcare_Provider_Taxonomy_Group_1			is not null
					or	Provider_License_Number_3						is not null
					or	Provider_License_Number_State_Code_3			is not null
					or	Healthcare_Provider_Primary_Taxonomy_Switch_3	is not null
		union all
					select
						NPI
					,	'4'												as	Taxonomy_Number
					,	Healthcare_Provider_Taxonomy_Code_4				as	Taxonomy_Code
					,	Healthcare_Provider_Taxonomy_Group_4			as	Taxonomy_Group
					,	Provider_License_Number_4						as	License_Number
					,	Provider_License_Number_State_Code_4			as	License_Number_State_Code
					,	Healthcare_Provider_Primary_Taxonomy_Switch_4	as	Primary_Taxonomy_Switch
					from test.analytics_schema.dim_nppes_npidata
					where
						Healthcare_Provider_Taxonomy_Code_4				is not null
					or	Healthcare_Provider_Taxonomy_Group_1			is not null
					or	Provider_License_Number_4						is not null
					or	Provider_License_Number_State_Code_4			is not null
					or	Healthcare_Provider_Primary_Taxonomy_Switch_4	is not null
		union all
					select
						NPI
					,	'5'												as	Taxonomy_Number
					,	Healthcare_Provider_Taxonomy_Code_5				as	Taxonomy_Code
					,	Healthcare_Provider_Taxonomy_Group_5			as	Taxonomy_Group
					,	Provider_License_Number_5						as	License_Number
					,	Provider_License_Number_State_Code_5			as	License_Number_State_Code
					,	Healthcare_Provider_Primary_Taxonomy_Switch_5	as	Primary_Taxonomy_Switch
					from test.analytics_schema.dim_nppes_npidata
					where
						Healthcare_Provider_Taxonomy_Code_5				is not null
					or	Healthcare_Provider_Taxonomy_Group_1			is not null
					or	Provider_License_Number_5						is not null
					or	Provider_License_Number_State_Code_5			is not null
					or	Healthcare_Provider_Primary_Taxonomy_Switch_5	is not null
		union all
					select
						NPI
					,	'6'												as	Taxonomy_Number
					,	Healthcare_Provider_Taxonomy_Code_6				as	Taxonomy_Code
					,	Healthcare_Provider_Taxonomy_Group_6			as	Taxonomy_Group
					,	Provider_License_Number_6						as	License_Number
					,	Provider_License_Number_State_Code_6			as	License_Number_State_Code
					,	Healthcare_Provider_Primary_Taxonomy_Switch_6	as	Primary_Taxonomy_Switch
					from test.analytics_schema.dim_nppes_npidata
					where
						Healthcare_Provider_Taxonomy_Code_6				is not null
					or	Healthcare_Provider_Taxonomy_Group_1			is not null
					or	Provider_License_Number_6						is not null
					or	Provider_License_Number_State_Code_6			is not null
					or	Healthcare_Provider_Primary_Taxonomy_Switch_6	is not null
		union all
					select
						NPI
					,	'7'												as	Taxonomy_Number
					,	Healthcare_Provider_Taxonomy_Code_7				as	Taxonomy_Code
					,	Healthcare_Provider_Taxonomy_Group_7			as	Taxonomy_Group
					,	Provider_License_Number_7						as	License_Number
					,	Provider_License_Number_State_Code_7			as	License_Number_State_Code
					,	Healthcare_Provider_Primary_Taxonomy_Switch_7	as	Primary_Taxonomy_Switch
					from test.analytics_schema.dim_nppes_npidata
					where
						Healthcare_Provider_Taxonomy_Code_7				is not null
					or	Healthcare_Provider_Taxonomy_Group_1			is not null
					or	Provider_License_Number_7						is not null
					or	Provider_License_Number_State_Code_7			is not null
					or	Healthcare_Provider_Primary_Taxonomy_Switch_7	is not null
		union all
					select
						NPI
					,	'8'												as	Taxonomy_Number
					,	Healthcare_Provider_Taxonomy_Code_8				as	Taxonomy_Code
					,	Healthcare_Provider_Taxonomy_Group_8			as	Taxonomy_Group
					,	Provider_License_Number_8						as	License_Number
					,	Provider_License_Number_State_Code_8			as	License_Number_State_Code
					,	Healthcare_Provider_Primary_Taxonomy_Switch_8	as	Primary_Taxonomy_Switch
					from test.analytics_schema.dim_nppes_npidata
					where
						Healthcare_Provider_Taxonomy_Code_8				is not null
					or	Healthcare_Provider_Taxonomy_Group_1			is not null
					or	Provider_License_Number_8						is not null
					or	Provider_License_Number_State_Code_8			is not null
					or	Healthcare_Provider_Primary_Taxonomy_Switch_8	is not null
		union all
					select
						NPI
					,	'9'												as	Taxonomy_Number
					,	Healthcare_Provider_Taxonomy_Code_9				as	Taxonomy_Code
					,	Healthcare_Provider_Taxonomy_Group_9			as	Taxonomy_Group
					,	Provider_License_Number_9						as	License_Number
					,	Provider_License_Number_State_Code_9			as	License_Number_State_Code
					,	Healthcare_Provider_Primary_Taxonomy_Switch_9	as	Primary_Taxonomy_Switch
					from test.analytics_schema.dim_nppes_npidata
					where
						Healthcare_Provider_Taxonomy_Code_9			is not null
					or	Healthcare_Provider_Taxonomy_Group_9			is not null
					or	Provider_License_Number_9						is not null
					or	Provider_License_Number_State_Code_9			is not null
					or	Healthcare_Provider_Primary_Taxonomy_Switch_9	is not null
		union all
					select
						NPI
					,	'10'											as	Taxonomy_Number
					,	Healthcare_Provider_Taxonomy_Code_10			as	Taxonomy_Code
					,	Healthcare_Provider_Taxonomy_Group_10			as	Taxonomy_Group
					,	Provider_License_Number_10						as	License_Number
					,	Provider_License_Number_State_Code_10			as	License_Number_State_Code
					,	Healthcare_Provider_Primary_Taxonomy_Switch_10	as	Primary_Taxonomy_Switch
					from test.analytics_schema.dim_nppes_npidata
					where
						Healthcare_Provider_Taxonomy_Code_10			is not null
					or	Healthcare_Provider_Taxonomy_Group_10			is not null
					or	Provider_License_Number_10						is not null
					or	Provider_License_Number_State_Code_10			is not null
					or	Healthcare_Provider_Primary_Taxonomy_Switch_10	is not null
		union all
					select
						NPI
					,	'11'											as	Taxonomy_Number
					,	Healthcare_Provider_Taxonomy_Code_11			as	Taxonomy_Code
					,	Healthcare_Provider_Taxonomy_Group_11			as	Taxonomy_Group
					,	Provider_License_Number_11						as	License_Number
					,	Provider_License_Number_State_Code_11			as	License_Number_State_Code
					,	Healthcare_Provider_Primary_Taxonomy_Switch_11	as	Primary_Taxonomy_Switch
					from test.analytics_schema.dim_nppes_npidata
					where
						Healthcare_Provider_Taxonomy_Code_11			is not null
					or	Healthcare_Provider_Taxonomy_Group_11			is not null
					or	Provider_License_Number_11						is not null
					or	Provider_License_Number_State_Code_11			is not null
					or	Healthcare_Provider_Primary_Taxonomy_Switch_11	is not null
		union all
					select
						NPI
					,	'12'											as	Taxonomy_Number
					,	Healthcare_Provider_Taxonomy_Code_12			as	Taxonomy_Code
					,	Healthcare_Provider_Taxonomy_Group_12			as	Taxonomy_Group
					,	Provider_License_Number_12						as	License_Number
					,	Provider_License_Number_State_Code_12			as	License_Number_State_Code
					,	Healthcare_Provider_Primary_Taxonomy_Switch_12	as	Primary_Taxonomy_Switch
					from test.analytics_schema.dim_nppes_npidata
					where
						Healthcare_Provider_Taxonomy_Code_12			is not null
					or	Healthcare_Provider_Taxonomy_Group_12			is not null
					or	Provider_License_Number_12						is not null
					or	Provider_License_Number_State_Code_12			is not null
					or	Healthcare_Provider_Primary_Taxonomy_Switch_12	is not null
		union all
					select
						NPI
					,	'13'											as	Taxonomy_Number
					,	Healthcare_Provider_Taxonomy_Code_13			as	Taxonomy_Code
					,	Healthcare_Provider_Taxonomy_Group_13			as	Taxonomy_Group
					,	Provider_License_Number_13						as	License_Number
					,	Provider_License_Number_State_Code_13			as	License_Number_State_Code
					,	Healthcare_Provider_Primary_Taxonomy_Switch_13	as	Primary_Taxonomy_Switch
					from test.analytics_schema.dim_nppes_npidata
					where
						Healthcare_Provider_Taxonomy_Code_13			is not null
					or	Healthcare_Provider_Taxonomy_Group_13			is not null
					or	Provider_License_Number_13						is not null
					or	Provider_License_Number_State_Code_13			is not null
					or	Healthcare_Provider_Primary_Taxonomy_Switch_13	is not null
		union all
					select
						NPI
					,	'14'											as	Taxonomy_Number
					,	Healthcare_Provider_Taxonomy_Code_14			as	Taxonomy_Code
					,	Healthcare_Provider_Taxonomy_Group_14			as	Taxonomy_Group
					,	Provider_License_Number_14						as	License_Number
					,	Provider_License_Number_State_Code_14			as	License_Number_State_Code
					,	Healthcare_Provider_Primary_Taxonomy_Switch_14	as	Primary_Taxonomy_Switch
					from test.analytics_schema.dim_nppes_npidata
					where
						Healthcare_Provider_Taxonomy_Code_14			is not null
					or	Healthcare_Provider_Taxonomy_Group_14			is not null
					or	Provider_License_Number_14						is not null
					or	Provider_License_Number_State_Code_14			is not null
					or	Healthcare_Provider_Primary_Taxonomy_Switch_14	is not null
		union all
					select
						NPI
					,	'15'											as	Taxonomy_Number
					,	Healthcare_Provider_Taxonomy_Code_15			as	Taxonomy_Code
					,	Healthcare_Provider_Taxonomy_Group_15			as	Taxonomy_Group
					,	Provider_License_Number_15						as	License_Number
					,	Provider_License_Number_State_Code_15			as	License_Number_State_Code
					,	Healthcare_Provider_Primary_Taxonomy_Switch_15	as	Primary_Taxonomy_Switch
					from test.analytics_schema.dim_nppes_npidata
					where
						Healthcare_Provider_Taxonomy_Code_15			is not null
					or	Healthcare_Provider_Taxonomy_Group_15			is not null
					or	Provider_License_Number_15						is not null
					or	Provider_License_Number_State_Code_15			is not null
					or	Healthcare_Provider_Primary_Taxonomy_Switch_15	is not null
		order by
			NPI
		,	Taxonomy_Number
	)
"""

# Execute the SQL statements
spark.sql(sql_statement1)
spark.sql(sql_statement2)
spark.sql(sql_statement3)
spark.sql(sql_statement4)
spark.sql(sql_statement5)
