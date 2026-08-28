# Databricks notebook source
# DBTITLE 1,Display Contents of dbfs:/tmp/david.smith/NPPES and /local_disk0/tmp
from dir import dir
display(dir("dbfs:/tmp/david.smith/NPPES", "EST"))
display(dir("/local_disk0/tmp/", "EST"))


# COMMAND ----------

# DBTITLE 1,Download most current NPPES ZIP file from CMS website to /local_disk0/tmp.
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
import zipfile
from pyspark.sql.functions import col

def download_large_file(url, local_path):
	response = requests.get(url, stream=True)
	response.raise_for_status()	 # Ensure we got an OK response

	# Parse filename from URL
	url_path = urlparse(url).path
	filename = os.path.basename(url_path)

	# Open a stream to local path in binary mode
	with open(local_path + '/' + filename, 'wb') as fd:
		for chunk in response.iter_content(chunk_size=8192):
			if chunk:	 # filter out keep-alive new chunks
				fd.write(chunk)
	return filename	 # Return the filename for later use

# Remove contents of destination folder.
folder_path = 'dbfs:/tmp/david.smith/NPPES'
for item in dbutils.fs.ls(folder_path):
		dbutils.fs.rm(item.path, recurse=True)

# Send a GET request to the webpage.
url = "https://download.cms.gov/nppes/NPI_Files.html"
response = requests.get(url)

# Parse the webpage.
soup = BeautifulSoup(response.text, 'html.parser')

# Find the specific anchor and get the link.
anchor = soup.find('a', id=re.compile(r'DDSMTH\.ZIP\..*'))
relative_link = anchor['href']

# Combine the base URL with the relative URL to get the absolute URL.
#absolute_link = urlparse.urljoin(url, relative_link)
absolute_link = urljoin(url, relative_link)

# Download the ZIP file to a local path.
local_path = "/local_disk0/tmp"	 # Local path on Databricks cluster node
filename = download_large_file(absolute_link, local_path)


# COMMAND ----------

# DBTITLE 1,Extract NPPES ZIP file, then load extracted CSV files into test.analytics_schema.dim_nppes_* tables.
def extract_zip_file(zip_file, local_dir_path, dbfs_dir_path):
	# Copy the zip file from DBFS to local file system
	local_zip_path = os.path.join(local_dir_path, zip_file)

	# Extract the zip file on local file system
	with zipfile.ZipFile(local_zip_path, 'r') as zip_ref:
			zip_ref.extractall(local_dir_path)

	# Move the extracted files back to DBFS
	for filename in os.listdir(local_dir_path):
		if not (filename == zip_file or filename.endswith('.r') or os.path.isdir(os.path.join(local_dir_path, filename)) or '_fileheader' in filename):
			local_file_path = os.path.join(local_dir_path, filename)
			dbfs_file_path = os.path.join(dbfs_dir_path, filename)
			dbutils.fs.cp("file:" + local_file_path, dbfs_file_path, recurse=True)
			dbutils.fs.rm("file:" + local_file_path)

# Define a function to clean column names
def clean_column_name(column_name):
	column_name = re.sub(r'[- _]+', '_', column_name)	# Replace any number of adjacent spaces/dashes/underscores with underscore
	column_name = re.sub(r'[().]', '', column_name)	 # Remove periods and parentheses
	column_name = re.sub(r'\W+', '', column_name)	 # Remove all other non-word characters
	return column_name

# Extract ZIP file to destination folder.
local_dir_path = "/local_disk0/tmp/"	# Replace with your local directory path
dbfs_dir_path = "dbfs:/tmp/david.smith/NPPES"	 # Replace with your DBFS directory path
try:
	extract_zip_file(filename, local_dir_path, dbfs_dir_path)
except:
	pass

# Iterate over the files.
for file in dbutils.fs.ls(dbfs_dir_path):

		# Get the filename
		filename = file.name

		# Check if the filename includes the substring '_pfile_'.
		if '_pfile_' in filename:

				# Get the portion of the filename that precedes '_pfile_'.
				table_suffix = filename.split('_pfile_')[0]

				# Specify the table name.
				table_name = 'test.analytics_schema.dim_nppes_' + table_suffix

				# Specify the file path.
				file_path = os.path.join(dbfs_dir_path, filename)

				# Load the CSV file into a DataFrame.
				df = spark.read.format("csv").option("header", "true").load(file_path)

				# First, create a list of new column names
				new_columns = [clean_column_name(c) for c in df.columns]

				# Then, rename the columns in the DataFrame
				for old_c, new_c in zip(df.columns, new_columns):
					df = df.withColumnRenamed(old_c, new_c)
    			
				# Drop existing table, if exists.
				spark.sql("DROP TABLE IF EXISTS " + table_name)

				# Save the DataFrame as a permanent table.
				df.write.format("delta").saveAsTable(table_name)


# COMMAND ----------

# DBTITLE 1,Create NPPES code tables.
# MAGIC %sql
# MAGIC create or replace table test.analytics_schema.dim_nppes_entity_type as (
# MAGIC 	select	*
# MAGIC 	from	(	values
# MAGIC 					(	'1',	'Individual'	)
# MAGIC 				,	(	'2',	'Organization'	)
# MAGIC 			)	as	a(entity_type_code, entity_type)
# MAGIC );
# MAGIC
# MAGIC create or replace table test.analytics_schema.dim_nppes_sole_proprietor as (
# MAGIC 	select	*
# MAGIC 	from	(	values
# MAGIC 					(	'X',	'Not Answered'	)
# MAGIC 				,	(	'Y',	'Yes, Entity Type 1 Provider (Individual) is a Sole Proprietor'	)
# MAGIC 				,	(	'N',	'No, Entity Type 1 Provider (Individual) is not a Sole Proprietor'	)
# MAGIC 			)	as	a(sole_proprietor_code, sole_proprietor)
# MAGIC );
# MAGIC
# MAGIC create or replace table test.analytics_schema.dim_nppes_subpart as (
# MAGIC 	select	*
# MAGIC 	from	(	values
# MAGIC 					(	'X',	'Not Answered'	)
# MAGIC 				,	(	'Y',	'Yes, Entity Type 2 Provider (Organization) is a Subpart'	)
# MAGIC 				,	(	'N',	'No, Entity Type 2 Provider (Organization) is not a Subpart'	)
# MAGIC 			)	as	a(subpart_code, subpart_description)
# MAGIC );
# MAGIC
# MAGIC create or replace table test.analytics_schema.dim_nppes_gender as (
# MAGIC 	select	*
# MAGIC 	from	(	values
# MAGIC 					(	'M',	'Male'	)
# MAGIC 				,	(	'F',	'Female'	)
# MAGIC 			)	as	a(gender_code, gender)
# MAGIC );
# MAGIC
# MAGIC create or replace table test.analytics_schema.dim_nppes_other_provider_name_type as (
# MAGIC 	select	*
# MAGIC 	from	(	values
# MAGIC 					(	'1',	'Former Name'                   ,	'Individual'	)
# MAGIC 				,	(	'2',	'Professional Name'             ,	'Individual'	)
# MAGIC 				,	(	'3',	'Doing Business As'             ,	'Organization'	)
# MAGIC 				,	(	'4',	'Former Legal Business Name'	,	'Organization'	)
# MAGIC 				,	(	'5',	'Other Name'					,	'Both'	)
# MAGIC 			)	as	a(name_type_code, name_type, entity_name_type_code)
# MAGIC );
# MAGIC
# MAGIC create or replace table test.analytics_schema.dim_nppes_name_suffix as (
# MAGIC 	select	*
# MAGIC 	from	(	values
# MAGIC 					(	'Jr.',	'Jr.'	)
# MAGIC 				,	(	'Sr.',	'Sr.'	)
# MAGIC 				,	(	'I',	'I'	)
# MAGIC 				,	(	'II',	'II'	)
# MAGIC 				,	(	'III',	'III'	)
# MAGIC 				,	(	'IV',	'IV'	)
# MAGIC 				,	(	'V',	'V'	)
# MAGIC 				,	(	'VI',	'VI'	)
# MAGIC 				,	(	'VII',	'VII'	)
# MAGIC 				,	(	'VIII', 'VIII'	)
# MAGIC 				,	(	'IX',	'IX'	)
# MAGIC 				,	(	'X',	'X'	)
# MAGIC 			)	as	a(name_suffix_code, name_suffix)
# MAGIC );
# MAGIC
# MAGIC create or replace table test.analytics_schema.dim_nppes_state as (
# MAGIC 	select	*
# MAGIC 	from	(	values
# MAGIC 					(	'AK',	'ALASKA'							,	'State'	)
# MAGIC 				,	(	'AL',	'ALABAMA'							,	'State'	)
# MAGIC 				,	(	'AR',	'ARKANSAS'							,	'State'	)
# MAGIC 				,	(	'AS',	'AMERICAN SAMOA'					,	'Territory'	)
# MAGIC 				,	(	'AZ',	'ARIZONA'							,	'State'	)
# MAGIC 				,	(	'CA',	'CALIFORNIA'						,	'State'	)
# MAGIC 				,	(	'CO',	'COLORADO'							,	'State'	)
# MAGIC 				,	(	'CT',	'CONNECTICUT'						,	'State'	)
# MAGIC 				,	(	'DC',	'DISTRICT OF COLUMBIA'				,	'Territory'	)
# MAGIC 				,	(	'DE',	'DELAWARE'							,	'State'	)
# MAGIC 				,	(	'FL',	'FLORIDA'							,	'State'	)
# MAGIC 				,	(	'FM',	'MICRONESIA, FEDERATED STATES OF'	,	'Territory'	)
# MAGIC 				,	(	'GA',	'GEORGIA'							,	'State'	)
# MAGIC 				,	(	'GU',	'GUAM'								,	'Territory'	)
# MAGIC 				,	(	'HI',	'HAWAII'							,	'State'	)
# MAGIC 				,	(	'IA',	'IOWA'								,	'State'	)
# MAGIC 				,	(	'ID',	'IDAHO'								,	'State'	)
# MAGIC 				,	(	'IL',	'ILLINOIS'							,	'State'	)
# MAGIC 				,	(	'IN',	'INDIANA'							,	'State'	)
# MAGIC 				,	(	'KS',	'KANSAS'							,	'State'	)
# MAGIC 				,	(	'KY',	'KENTUCKY'							,	'State'	)
# MAGIC 				,	(	'LA',	'LOUISIANA'							,	'State'	)
# MAGIC 				,	(	'MA',	'MASSACHUSETTS'						,	'State'	)
# MAGIC 				,	(	'MD',	'MARYLAND'							,	'State'	)
# MAGIC 				,	(	'ME',	'MAINE'								,	'State'	)
# MAGIC 				,	(	'MH',	'MARSHALL ISLANDS'					,	'Territory'	)
# MAGIC 				,	(	'MI',	'MICHIGAN'							,	'State'	)
# MAGIC 				,	(	'MN',	'MINNESOTA'							,	'State'	)
# MAGIC 				,	(	'MO',	'MISSOURI'							,	'State'	)
# MAGIC 				,	(	'MP',	'MARIANA ISLANDS, NORTHERN'			,	'Territory'	)
# MAGIC 				,	(	'MS',	'MISSISSIPPI'						,	'State'	)
# MAGIC 				,	(	'MT',	'MONTANA'							,	'State'	)
# MAGIC 				,	(	'NC',	'NORTH CAROLINA'					,	'State'	)
# MAGIC 				,	(	'ND',	'NORTH DAKOTA'						,	'State'	)
# MAGIC 				,	(	'NE',	'NEBRASKA'							,	'State'	)
# MAGIC 				,	(	'NH',	'NEW HAMPSHIRE'						,	'State'	)
# MAGIC 				,	(	'NJ',	'NEW JERSEY'						,	'State'	)
# MAGIC 				,	(	'NM',	'NEW MEXICO'						,	'State'	)
# MAGIC 				,	(	'NV',	'NEVADA'							,	'State'	)
# MAGIC 				,	(	'NY',	'NEW YORK'							,	'State'	)
# MAGIC 				,	(	'OH',	'OHIO'								,	'State'	)
# MAGIC 				,	(	'OK',	'OKLAHOMA'							,	'State'	)
# MAGIC 				,	(	'OR',	'OREGON'							,	'State'	)
# MAGIC 				,	(	'PA',	'PENNSYLVANIA'						,	'State'	)
# MAGIC 				,	(	'PR',	'PUERTO RICO'						,	'Territory'	)
# MAGIC 				,	(	'PW',	'PALAU'								,	'Territory'	)
# MAGIC 				,	(	'RI',	'RHODE ISLAND'						,	'State'	)
# MAGIC 				,	(	'SC',	'SOUTH CAROLINA'					,	'State'	)
# MAGIC 				,	(	'SD',	'SOUTH DAKOTA'						,	'State'	)
# MAGIC 				,	(	'TN',	'TENNESSEE'							,	'State'	)
# MAGIC 				,	(	'TX',	'TEXAS'								,	'State'	)
# MAGIC 				,	(	'UT',	'UTAH'								,	'State'	)
# MAGIC 				,	(	'VA',	'VIRGINIA'							,	'State'	)
# MAGIC 				,	(	'VI',	'VIRGIN ISLANDS'					,	'Territory'	)
# MAGIC 				,	(	'VT',	'VERMONT'							,	'State'	)
# MAGIC 				,	(	'WA',	'WASHINGTON'						,	'State'	)
# MAGIC 				,	(	'WI',	'WISCONSIN'							,	'State'	)
# MAGIC 				,	(	'WV',	'WEST VIRGINIA'						,	'State'	)
# MAGIC 				,	(	'WY',	'WYOMING'							,	'State'	)
# MAGIC 				,	(	'ZZ',	'Foreign Country'					,	'Territory'	)
# MAGIC 			)	as	a(state_code, state, state_type)
# MAGIC );
# MAGIC
# MAGIC create or replace table test.analytics_schema.dim_nppes_country as (
# MAGIC 	select	*
# MAGIC 	from	(	values
# MAGIC 					(	'AD',	'ANDORRA'	)
# MAGIC 				,	(	'AE',	'UNITED ARAB EMIRATES'	)
# MAGIC 				,	(	'AF',	'AFGHANISTAN'	)
# MAGIC 				,	(	'AG',	'ANTIGUA AND BARBUDA'	)
# MAGIC 				,	(	'AI',	'ANGUILLA'	)
# MAGIC 				,	(	'AL',	'ALBANIA'	)
# MAGIC 				,	(	'AM',	'ARMENIA'	)
# MAGIC 				,	(	'AN',	'NETHERLANDS ANTILLES'	)
# MAGIC 				,	(	'AO',	'ANGOLA'	)
# MAGIC 				,	(	'AQ',	'ANTARCTICA'	)
# MAGIC 				,	(	'AR',	'ARGENTINA'	)
# MAGIC 				,	(	'AT',	'AUSTRIA'	)
# MAGIC 				,	(	'AU',	'AUSTRALIA'	)
# MAGIC 				,	(	'AW',	'ARUBA'	)
# MAGIC 				,	(	'AX',	'ALAND ISLANDS'	)
# MAGIC 				,	(	'AZ',	'AZERBAIJAN'	)
# MAGIC 				,	(	'BA',	'BOSNIA AND HERZEGOVINA'	)
# MAGIC 				,	(	'BB',	'BARBADOS'	)
# MAGIC 				,	(	'BD',	'BANGLADESH'	)
# MAGIC 				,	(	'BE',	'BELGIUM'	)
# MAGIC 				,	(	'BF',	'BURKINA FASO'	)
# MAGIC 				,	(	'BG',	'BULGARIA'	)
# MAGIC 				,	(	'BH',	'BAHRAIN'	)
# MAGIC 				,	(	'BI',	'BURUNDI'	)
# MAGIC 				,	(	'BJ',	'BENIN'	)
# MAGIC 				,	(	'BM',	'BERMUDA'	)
# MAGIC 				,	(	'BN',	'BRUNEI DARUSSALAM'	)
# MAGIC 				,	(	'BO',	'BOLIVIA'	)
# MAGIC 				,	(	'BR',	'BRAZIL'	)
# MAGIC 				,	(	'BS',	'BAHAMAS'	)
# MAGIC 				,	(	'BT',	'BHUTAN'	)
# MAGIC 				,	(	'BV',	'BOUVET ISLAND'	)
# MAGIC 				,	(	'BW',	'BOTSWANA'	)
# MAGIC 				,	(	'BY',	'BELARUS'	)
# MAGIC 				,	(	'BZ',	'BELIZE'	)
# MAGIC 				,	(	'CA',	'CANADA'	)
# MAGIC 				,	(	'CC',	'COCOS (KEELING) ISLANDS'	)
# MAGIC 				,	(	'CD',	'CONGO, THE DEMOCRATIC REPUBLIC OF THE'	)
# MAGIC 				,	(	'CF',	'CENTRAL AFRICAN REPUBLIC'	)
# MAGIC 				,	(	'CG',	'CONGO'	)
# MAGIC 				,	(	'CH',	'SWITZERLAND'	)
# MAGIC 				,	(	'CI',	"COTE D'IVOIRE"	)
# MAGIC 				,	(	'CK',	'COOK ISLANDS'	)
# MAGIC 				,	(	'CL',	'CHILE'	)
# MAGIC 				,	(	'CM',	'CAMEROON'	)
# MAGIC 				,	(	'CN',	'CHINA'	)
# MAGIC 				,	(	'CO',	'COLOMBIA'	)
# MAGIC 				,	(	'CR',	'COSTA RICA'	)
# MAGIC 				,	(	'CS',	'SERBIA AND MONTENEGRO'	)
# MAGIC 				,	(	'CU',	'CUBA'	)
# MAGIC 				,	(	'CV',	'CAPE VERDE'	)
# MAGIC 				,	(	'CX',	'CHRISTMAS ISLAND'	)
# MAGIC 				,	(	'CY',	'CYPRUS'	)
# MAGIC 				,	(	'CZ',	'CZECH REPUBLIC'	)
# MAGIC 				,	(	'DE',	'GERMANY'	)
# MAGIC 				,	(	'DJ',	'DJIBOUTI'	)
# MAGIC 				,	(	'DK',	'DENMARK'	)
# MAGIC 				,	(	'DM',	'DOMINICA'	)
# MAGIC 				,	(	'DO',	'DOMINICAN REPUBLIC'	)
# MAGIC 				,	(	'DZ',	'ALGERIA'	)
# MAGIC 				,	(	'EC',	'ECUADOR'	)
# MAGIC 				,	(	'EE',	'ESTONIA'	)
# MAGIC 				,	(	'EG',	'EGYPT'	)
# MAGIC 				,	(	'EH',	'WESTERN SAHARA'	)
# MAGIC 				,	(	'ER',	'ERITREA'	)
# MAGIC 				,	(	'ES',	'SPAIN'	)
# MAGIC 				,	(	'ET',	'ETHIOPIA'	)
# MAGIC 				,	(	'FI',	'FINLAND'	)
# MAGIC 				,	(	'FJ',	'FIJI'	)
# MAGIC 				,	(	'FK',	'FALKLAND ISLANDS (MALVINAS)'	)
# MAGIC 				,	(	'FO',	'FAROE ISLANDS'	)
# MAGIC 				,	(	'FR',	'FRANCE'	)
# MAGIC 				,	(	'GA',	'GABON'	)
# MAGIC 				,	(	'GB',	'Great Britain (UK)'	)
# MAGIC 				,	(	'GD',	'GRENADA'	)
# MAGIC 				,	(	'GE',	'GEORGIA'	)
# MAGIC 				,	(	'GF',	'FRENCH GUIANA'	)
# MAGIC 				,	(	'GG',	'GUERNSEY'	)
# MAGIC 				,	(	'GH',	'GHANA'	)
# MAGIC 				,	(	'GI',	'GIBRALTAR'	)
# MAGIC 				,	(	'GL',	'GREENLAND'	)
# MAGIC 				,	(	'GM',	'GAMBIA'	)
# MAGIC 				,	(	'GN',	'GUINEA'	)
# MAGIC 				,	(	'GP',	'GUADELOUPE'	)
# MAGIC 				,	(	'GQ',	'EQUATORIAL GUINEA'	)
# MAGIC 				,	(	'GR',	'GREECE'	)
# MAGIC 				,	(	'GS',	'SOUTH GEORGIA AND THE SOUTH SANDWICH ISLANDS'	)
# MAGIC 				,	(	'GT',	'GUATEMALA'	)
# MAGIC 				,	(	'GW',	'GUINEA-BISSAU'	)
# MAGIC 				,	(	'GY',	'GUYANA'	)
# MAGIC 				,	(	'HK',	'HONG KONG'	)
# MAGIC 				,	(	'HM',	'HEARD ISLAND AND MCDONALD ISLANDS'	)
# MAGIC 				,	(	'HN',	'HONDURAS'	)
# MAGIC 				,	(	'HR',	'CROATIA'	)
# MAGIC 				,	(	'HT',	'HAITI'	)
# MAGIC 				,	(	'HU',	'HUNGARY'	)
# MAGIC 				,	(	'ID',	'INDONESIA'	)
# MAGIC 				,	(	'IE',	'IRELAND'	)
# MAGIC 				,	(	'IL',	'ISRAEL'	)
# MAGIC 				,	(	'IM',	'ISLE OF MAN'	)
# MAGIC 				,	(	'IN',	'INDIA'	)
# MAGIC 				,	(	'IO',	'BRITISH INDIAN OCEAN TERRITORY'	)
# MAGIC 				,	(	'IQ',	'IRAQ'	)
# MAGIC 				,	(	'IR',	'IRAN, ISLAMIC REPUBLIC OF'	)
# MAGIC 				,	(	'IS',	'ICELAND'	)
# MAGIC 				,	(	'IT',	'ITALY'	)
# MAGIC 				,	(	'JE',	'JERSEY'	)
# MAGIC 				,	(	'JM',	'JAMAICA'	)
# MAGIC 				,	(	'JO',	'JORDAN'	)
# MAGIC 				,	(	'JP',	'JAPAN'	)
# MAGIC 				,	(	'KE',	'KENYA'	)
# MAGIC 				,	(	'KG',	'KYRGYZSTAN'	)
# MAGIC 				,	(	'KH',	'CAMBODIA'	)
# MAGIC 				,	(	'KI',	'KIRIBATI'	)
# MAGIC 				,	(	'KM',	'COMOROS'	)
# MAGIC 				,	(	'KN',	'SAINT KITTS AND NEVIS'	)
# MAGIC 				,	(	'KP',	"KOREA, DEMOCRATIC PEOPLE'S REPUBLIC OF"	)
# MAGIC 				,	(	'KR',	'KOREA, REPUBLIC OF'	)
# MAGIC 				,	(	'KW',	'KUWAIT'	)
# MAGIC 				,	(	'KY',	'CAYMAN ISLANDS'	)
# MAGIC 				,	(	'KZ',	'KAZAKHSTAN'	)
# MAGIC 				,	(	'LA',	"LAO PEOPLE'S DEMOCRATIC REPUBLIC"	)
# MAGIC 				,	(	'LB',	'LEBANON'	)
# MAGIC 				,	(	'LC',	'SAINT LUCIA'	)
# MAGIC 				,	(	'LI',	'LIECHTENSTEIN'	)
# MAGIC 				,	(	'LK',	'SRI LANKA'	)
# MAGIC 				,	(	'LR',	'LIBERIA'	)
# MAGIC 				,	(	'LS',	'LESOTHO'	)
# MAGIC 				,	(	'LT',	'LITHUANIA'	)
# MAGIC 				,	(	'LU',	'LUXEMBOURG'	)
# MAGIC 				,	(	'LV',	'LATVIA'	)
# MAGIC 				,	(	'LY',	'LIBYAN ARAB JAMAHIRIYA'	)
# MAGIC 				,	(	'MA',	'MOROCCO'	)
# MAGIC 				,	(	'MC',	'MONACO'	)
# MAGIC 				,	(	'MD',	'MOLDOVA, REPUBLIC OF'	)
# MAGIC 				,	(	'MG',	'MADAGASCAR'	)
# MAGIC 				,	(	'MK',	'MACEDONIA, THE FORMER YUGOSLAV REPUBLIC OF'	)
# MAGIC 				,	(	'ML',	'MALI'	)
# MAGIC 				,	(	'MM',	'MYANMAR'	)
# MAGIC 				,	(	'MN',	'MONGOLIA'	)
# MAGIC 				,	(	'MO',	'MACAO'	)
# MAGIC 				,	(	'MQ',	'MARTINIQUE'	)
# MAGIC 				,	(	'MR',	'MAURITANIA'	)
# MAGIC 				,	(	'MS',	'MONTSERRAT'	)
# MAGIC 				,	(	'MT',	'MALTA'	)
# MAGIC 				,	(	'MU',	'MAURITIUS'	)
# MAGIC 				,	(	'MV',	'MALDIVES'	)
# MAGIC 				,	(	'MW',	'MALAWI'	)
# MAGIC 				,	(	'MX',	'MEXICO'	)
# MAGIC 				,	(	'MY',	'MALAYSIA'	)
# MAGIC 				,	(	'MZ',	'MOZAMBIQUE'	)
# MAGIC 				,	(	'NA',	'NAMIBIA'	)
# MAGIC 				,	(	'NC',	'NEW CALEDONIA'	)
# MAGIC 				,	(	'NE',	'NIGER'	)
# MAGIC 				,	(	'NF',	'NORFOLK ISLAND'	)
# MAGIC 				,	(	'NG',	'NIGERIA'	)
# MAGIC 				,	(	'NI',	'NICARAGUA'	)
# MAGIC 				,	(	'NL',	'NETHERLANDS'	)
# MAGIC 				,	(	'NO',	'NORWAY'	)
# MAGIC 				,	(	'NP',	'NEPAL'	)
# MAGIC 				,	(	'NR',	'NAURU'	)
# MAGIC 				,	(	'NU',	'NIUE'	)
# MAGIC 				,	(	'NZ',	'NEW ZEALAND'	)
# MAGIC 				,	(	'OM',	'OMAN'	)
# MAGIC 				,	(	'PA',	'PANAMA'	)
# MAGIC 				,	(	'PE',	'PERU'	)
# MAGIC 				,	(	'PF',	'FRENCH POLYNESIA'	)
# MAGIC 				,	(	'PG',	'PAPUA NEW GUINEA'	)
# MAGIC 				,	(	'PH',	'PHILIPPINES'	)
# MAGIC 				,	(	'PK',	'PAKISTAN'	)
# MAGIC 				,	(	'PL',	'POLAND'	)
# MAGIC 				,	(	'PM',	'SAINT PIERRE AND MIQUELON'	)
# MAGIC 				,	(	'PN',	'PITCAIRN'	)
# MAGIC 				,	(	'PS',	'PALESTINIAN TERRITORY, OCCUPIED'	)
# MAGIC 				,	(	'PT',	'PORTUGAL'	)
# MAGIC 				,	(	'PY',	'PARAGUAY'	)
# MAGIC 				,	(	'QA',	'QATAR'	)
# MAGIC 				,	(	'RE',	'REUNION'	)
# MAGIC 				,	(	'RO',	'ROMANIA'	)
# MAGIC 				,	(	'RU',	'RUSSIAN FEDERATION'	)
# MAGIC 				,	(	'RW',	'RWANDA'	)
# MAGIC 				,	(	'SA',	'SAUDI ARABIA'	)
# MAGIC 				,	(	'SB',	'SOLOMON ISLANDS'	)
# MAGIC 				,	(	'SC',	'SEYCHELLES'	)
# MAGIC 				,	(	'SD',	'SUDAN'	)
# MAGIC 				,	(	'SE',	'SWEDEN'	)
# MAGIC 				,	(	'SG',	'SINGAPORE'	)
# MAGIC 				,	(	'SH',	'SAINT HELENA'	)
# MAGIC 				,	(	'SI',	'SLOVENIA'	)
# MAGIC 				,	(	'SJ',	'SVALBARD AND JAN MAYEN'	)
# MAGIC 				,	(	'SK',	'SLOVAKIA'	)
# MAGIC 				,	(	'SL',	'SIERRA LEONE'	)
# MAGIC 				,	(	'SM',	'SAN MARINO'	)
# MAGIC 				,	(	'SN',	'SENEGAL'	)
# MAGIC 				,	(	'SO',	'SOMALIA'	)
# MAGIC 				,	(	'SR',	'SURINAME'	)
# MAGIC 				,	(	'ST',	'SAO TOME AND PRINCIPE'	)
# MAGIC 				,	(	'SV',	'EL SALVADOR'	)
# MAGIC 				,	(	'SY',	'SYRIAN ARAB REPUBLIC'	)
# MAGIC 				,	(	'SZ',	'SWAZILAND'	)
# MAGIC 				,	(	'TC',	'TURKS AND CAICOS ISLANDS'	)
# MAGIC 				,	(	'TD',	'CHAD'	)
# MAGIC 				,	(	'TF',	'FRENCH SOUTHERN TERRITORIES'	)
# MAGIC 				,	(	'TG',	'TOGO'	)
# MAGIC 				,	(	'TH',	'THAILAND'	)
# MAGIC 				,	(	'TJ',	'TAJIKISTAN'	)
# MAGIC 				,	(	'TK',	'TOKELAU'	)
# MAGIC 				,	(	'TL',	'TIMOR-LESTE'	)
# MAGIC 				,	(	'TM',	'TURKMENISTAN'	)
# MAGIC 				,	(	'TN',	'TUNISIA'	)
# MAGIC 				,	(	'TO',	'TONGA'	)
# MAGIC 				,	(	'TR',	'TURKEY'	)
# MAGIC 				,	(	'TT',	'TRINIDAD AND TOBAGO'	)
# MAGIC 				,	(	'TV',	'TUVALU'	)
# MAGIC 				,	(	'TW',	'TAIWAN '	)
# MAGIC 				,	(	'TZ',	'TANZANIA, UNITED REPUBLIC OF'	)
# MAGIC 				,	(	'UA',	'UKRAINE'	)
# MAGIC 				,	(	'UG',	'UGANDA'	)
# MAGIC 				,	(	'UM',	'UNITED STATES MINOR OUTLYING ISLANDS'	)
# MAGIC 				,	(	'US',	'UNITED STATES'	)
# MAGIC 				,	(	'UY',	'URUGUAY'	)
# MAGIC 				,	(	'UZ',	'UZBEKISTAN'	)
# MAGIC 				,	(	'VA',	'HOLY SEE (VATICAN CITY STATE)'	)
# MAGIC 				,	(	'VC',	'SAINT VINCENT AND THE GRENADINES'	)
# MAGIC 				,	(	'VE',	'VENEZUELA'	)
# MAGIC 				,	(	'VG',	'VIRGIN ISLANDS, BRITISH'	)
# MAGIC 				,	(	'VN',	'VIET NAM'	)
# MAGIC 				,	(	'VU',	'VANUATU'	)
# MAGIC 				,	(	'WF',	'WALLIS AND FUTUNA'	)
# MAGIC 				,	(	'WS',	'SAMOA'	)
# MAGIC 				,	(	'XK',	'KOSOVO'	)
# MAGIC 				,	(	'YE',	'YEMEN'	)
# MAGIC 				,	(	'YT',	'MAYOTTE'	)
# MAGIC 				,	(	'ZA',	'SOUTH AFRICA'	)
# MAGIC 				,	(	'ZM',	'ZAMBIA'	)
# MAGIC 				,	(	'ZW',	'ZIMBABWE'	)
# MAGIC 			)	as	a(country_code, country)
# MAGIC );
# MAGIC
# MAGIC create or replace table test.analytics_schema.dim_nppes_other_provider_identifier_issuer as (
# MAGIC 	select	*
# MAGIC 	from	(	values
# MAGIC 					(	'01',	'OTHER'	)
# MAGIC 				,	(	'05',	'MEDICAID'	)
# MAGIC 			)	as	a(other_provider_type_code, other_provider_type)
# MAGIC );
# MAGIC
# MAGIC create or replace table test.analytics_schema.dim_nppes_primary_taxonomy as (
# MAGIC 	select	*
# MAGIC 	from	(	values
# MAGIC 					(	'X',	'Not Answered'	)
# MAGIC 				,	(	'Y',	'Yes'	)
# MAGIC 				,	(	'N',	'No'	)
# MAGIC 			)	as	a(primary_taxonomy_switch_code, primary_taxonomy_switch)
# MAGIC );
# MAGIC
# MAGIC create or replace table test.analytics_schema.dim_nppes_group_taxonomy as (
# MAGIC 	select	*
# MAGIC 	from	(	values
# MAGIC 					(	'193200000X',	'Multi-Specialty Group'	)
# MAGIC 				,	(	'193400000X',	'Single Specialty Group'	)
# MAGIC 			)	as	a(group_taxonomy_code, group_taxonomy)
# MAGIC );
# MAGIC
# MAGIC create or replace table test.analytics_schema.dim_nppes_endpoint_type as (
# MAGIC 	select	*
# MAGIC 	from	(	values
# MAGIC 					(	'SOAP',	'SOAP WS URL'	)
# MAGIC 				,	(	'CONNECT',	'Connect URL'	)
# MAGIC 				,	(	'FHIR',	'FHIR URL'	)
# MAGIC 				,	(	'DIRECT',	'Direct Address'	)
# MAGIC 				,	(	'REST',	'RESTful WS URL'	)
# MAGIC 				,	(	'WEB',	'Website URL'	)
# MAGIC 				,	(	'OTHERS',	'Other URL'	)
# MAGIC 			)	as	a(endpoint_type_code, endpoint_type)
# MAGIC );
# MAGIC
# MAGIC create or replace table test.analytics_schema.dim_nppes_endpoint_affiliation as (
# MAGIC 	select	*
# MAGIC 	from	(	values
# MAGIC 					(	'Y',	'Yes, Endpoint is affiliated with an NPI or EIN'	)
# MAGIC 				,	(	'N',	'No, Endpoint is not affiliated with an NPI or EIN'	)
# MAGIC 			)	as	a(endpoint_affiliation_code, endpoint_affiliation)
# MAGIC );
# MAGIC
