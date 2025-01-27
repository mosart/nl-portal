# nl-portal

## nl-stats.py

The `nl-stats.py` script retrieves the latest number of research outputs from OpenAIRE related to Dutch institutions and their associated data source systems. It uses the [beta graph API](https://graph.openaire.eu/docs/apis/graph-api/).

### Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/mosart/nl-portal
cd nl-portal
```

#### 2. Set Up Python Environment
1. Ensure you have Python 3.8 or newer installed on your machine.
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

#### 3. Get your API credentials as registered service
[https://graph.openaire.eu/docs/apis/authentication#registered-services](https://graph.openaire.eu/docs/apis/authentication#registered-services)

#### 4. Configure `config.yaml`
1. Rename `config-example.yaml` to `config.yaml`.
2. Add the following details to `config.yaml`:
   - `CLIENT_ID`: Your OpenAIRE client ID.
   - `CLIENT_SECRET`: Your OpenAIRE client secret.
   - `Org_data_file`: Path to the CSV file containing the list of Dutch institutions (e.g., `rpo_nl_list_test_20240201.csv`).

Example `config.yaml`:
```yaml
CLIENT_ID: "your_client_id"
CLIENT_SECRET: "your_client_secret"
OpenAIRE_API: "https://api-beta.openaire.eu/graph/"
Org_data_file: "rpo_nl_list_test_20240201.csv"
```

#### 5. Download Institution Data File
- For testing: Download `rpo_nl_list_test_20240201.csv`.
- to get the latest visit: [https://doi.org/10.5281/zenodo.11360571](https://doi.org/10.5281/zenodo.11360571)
- Place the file in the same directory or update the path in `config.yaml`.

### Usage

1. Run the script:
   ```bash
   python nl-stats.py
   ```
2. The script will:
   - Fetch an access token using the client ID and secret.
   - Process the institution data file.
   - Retrieve data from OpenAIRE APIs.
   - Perform calculations for research products and data sources.
   - Save results to a timestamped CSV file.

### Output
- The results are saved in a CSV file named in the format: `yyyy-mm-dd_HH-MM_nl-stats.csv`.
- Each row includes details about:
  - Institutions.
  - OpenAIRE organization IDs.
  - Data sources.
  - Counts and calculations of research products and missing data.

### Example Output

| Institution       | OpenAIRE_Org_ID  | DataSource_ID | DataSource_Name | Num_Research_Products_Org | Num_Research_Products_DS | Num_Missing_DS | Num_Missing_Org |
|-------------------|------------------|---------------|-----------------|---------------------------|--------------------------|----------------|-----------------|
| Example University | openorgs-123456 | ds-987654     | Example Source  | 1000                      | 800                      | 200            | 50              |

### Notes
- Ensure your client ID and secret are valid.
- Confirm that the data file (`rpo_nl_list_test_20240201.csv`) is updated and matches the required format.

If you encounter issues, check the API documentation [here](https://graph.openaire.eu/docs/apis/graph-api/).

### Who it works

#### For you to do: 
a. add client id and secret in the config.yaml file (rename config-example.yaml first. config.yaml is in gitignore.)
b. download the latest list of dutch research institutions. Kramer, B. (2024). Coverage and quality of open metadata for Dutch research output - dataset (1.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.11360572
latest: rpo_nl_list_long_20240201.csv
for testing: rpo_nl_list_test_20240201.csv

#### What the script does: 
1. fetch the {ACCESS_TOKEN} by using the {CLIENT_ID} and {CLIENT_SECRET} in the config.yaml
2. get the data file with all the Dutch institutions
    load: rpo_nl_list_test_20240201.csv
3. use the {ROR_LINK} of the institutions to get the OpenAIRE Organisation ID {OpenORG_ID}
    request: https://api-beta.openaire.eu/graph/organizations?pid={ROR_LINK}
    result: OpenORGS_ID=$.results[].id (keep only id's that do have a prefix containing "openorgs")
4. use the {OpenOrgs_ID} to get the number of Research products associated to the organisation
    request: https://api-beta.openaire.eu/graph/researchProducts?relOrganizationId={OpenOrgs_ID}
    result: numFound_ResearchProducts_OpenOrgs=$.header.numFound
5. use the {OpenOrgs_ID} to get the number of Projects associated to the organisation
    request: https://api-beta.openaire.eu/graph/projects?relOrganizationId={OpenOrgs_ID}
    result: numFound_ResearchProjects_OpenOrgs=$.header.numFound
6. use the {OpenOrgs_ID} to get the Data sources related to Organisation
    https://api-beta.openaire.eu/graph/dataSources?relOrganizationId={OpenOrgs_ID}
    results: for each $.results DataSource_ID=$.results[].id , DataSource_Name=$.results[].officialName , DataSource_Compatibility=.results[].openaireCompatibility , DataSource_LastValidated=$.results[].dateOfValidation , DataSource_URL=$.results[].websiteUrl
7. use the {DataSource_ID} to get the number of Research products associated to the organisation
    request: https://api-beta.openaire.eu/graph/researchProducts?relCollectedFromDatasourceId={DataSource_ID}
    result: numFound_ResearchProducts_DataSource=$.header.numFound
8. use the {OpenOrgs_ID} and the {DataSource_ID} to get the number of Research products in the Data Source that is associated to its Organisation
    request: https://api-beta.openaire.eu/graph/researchProducts?relOrganizationId={OpenOrgs_ID}&relCollectedFromDatasourceId={DataSource_ID}
    result: numFound_ResearchProducts_DataSource_AND_OpenOrgs=$.header.numFound
9. calculate the missing number of Research products in the Data source
    result: numMissing_ResearchProducts_in_DataSource={numFound_ResearchProducts_DataSource}-{numFound_ResearchProducts_DataSource_AND_OpenOrgs}
10. calculate the the missing number of Research products that should be associated to the Organisation.
    result: numMissing_ResearchProducts_in_OpenOrgs={numFound_ResearchProducts_OpenOrgs}-{numFound_ResearchProducts_DataSource_AND_OpenOrgs}
11. write a timestamped csv file (a column 'retrieved on' with the timestamp, and the timestamp on the filename yyyy-mm-dd_HH-MM_nl-stats.csv)
