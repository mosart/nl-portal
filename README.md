# nl-portal

This repository is a collection of a bush of scripts that relate to the Netherlands Research Portal project.

## nl-stats.py
This script gets the latest number of research output from OpenAIRE that are related to Dutch institutions, and the Data Source systems from those institutions.

Currently using the [beta graph API](https://graph.openaire.eu/docs/apis/graph-api/)

### For you to do: 
a. add client id and secret in the config.yaml file (rename config-example.yaml first. config.yaml is in gitignore.)
b. download the latest list of dutch research institutions. Kramer, B. (2024). Coverage and quality of open metadata for Dutch research output - dataset (1.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.11360572
latest: rpo_nl_list_long_20240201.csv
for testing: rpo_nl_list_test_20240201.csv

### What the script does: 
1. fetch the {ACCESS_TOKEN} by using the {CLIENT_ID} and {CLIENT_SECRET}
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