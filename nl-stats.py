import requests
import pandas as pd
import yaml
import datetime

# Load configuration
def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Authenticate and retrieve access_token
def get_access_token(client_id, client_secret):
    print("Requesting access token...")
    url = "https://aai.openaire.eu/oidc/token"
    response = requests.post(
        url,
        auth=(client_id, client_secret),
        data={'grant_type': 'client_credentials'}
    )
    if response.status_code == 200:
        print("Access token retrieved successfully.")
        return response.json().get('access_token')
    else:
        raise Exception(f"Failed to retrieve access token: {response.status_code}, {response.text}")

# Fetch data from API
def fetch_api_data(api_url, access_token, params=None):
    print(f"Fetching data from {api_url} with params {params}...")
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(api_url, headers=headers, params=params)
    if response.status_code == 200:
        print("Data fetched successfully.")
        return response.json()
    else:
        raise Exception(f"API request failed: {response.status_code}, {response.text}")

# Process the data file with all the Dutch institutions
def process_institutions(data_file):
    print(f"Loading data file from {data_file}...")
    return pd.read_csv(data_file)

# Main script
def main():
    print("Loading configuration...")
    config = load_config('config.yaml')

    client_id = config['CLIENT_ID']
    client_secret = config['CLIENT_SECRET']
    data_file = config['Org_data_file']

    access_token = get_access_token(client_id, client_secret)
    institutions = process_institutions(data_file)

    results = []

    for index, row in institutions.iterrows():
        print(f"Processing institution {index + 1}/{len(institutions)}: {row['full_name_in_English']}...")
        ror_link = row['ROR_LINK']
        institution_name = row['full_name_in_English']

        # Step 3: Get OpenAIRE Organization ID
        org_response = fetch_api_data(
            f"{config['OpenAIRE_API']}organizations",
            access_token,
            params={'pid': ror_link}
        )
        openorg_ids = [org['id'] for org in org_response['results'] if org['id'].startswith('openorgs')]

        for openorg_id in openorg_ids:
            print(f"Processing {openorg_id}...")

            # Step 4: Get number of research products
            research_products_response = fetch_api_data(
                f"{config['OpenAIRE_API']}researchProducts",
                access_token,
                params={'relOrganizationId': openorg_id}
            )
            num_found_research_products_openorgs = research_products_response['header']['numFound']
            print(f"Research products count: {num_found_research_products_openorgs}")

            # Step 5: Get number of projects
            projects_response = fetch_api_data(
                f"{config['OpenAIRE_API']}projects",
                access_token,
                params={'relOrganizationId': openorg_id}
            )
            num_found_research_projects_openorgs = projects_response['header']['numFound']
            print(f"Projects count: {num_found_research_projects_openorgs}")

            # Step 6: Get data sources
            data_sources_response = fetch_api_data(
                f"{config['OpenAIRE_API']}dataSources",
                access_token,
                params={'relOrganizationId': openorg_id}
            )
            for ds in data_sources_response['results']:
                datasource_id = ds['id']
                datasource_name = ds.get('officialName', '')
                datasource_compatibility = ds.get('openaireCompatibility', '')
                datasource_last_validated = ds.get('dateOfValidation', '')
                datasource_url = ds.get('websiteUrl', '')

                print(f"Processing Data Source: {datasource_name} (ID: {datasource_id})...")

                # Step 7: Get number of research products in data source
                ds_research_products_response = fetch_api_data(
                    f"{config['OpenAIRE_API']}researchProducts",
                    access_token,
                    params={'relCollectedFromDatasourceId': datasource_id}
                )
                num_found_research_products_datasource = ds_research_products_response['header']['numFound']
                print(f"Research products in data source: {num_found_research_products_datasource}")

                # Step 8: Get research products in data source associated with organization
                ds_org_research_products_response = fetch_api_data(
                    f"{config['OpenAIRE_API']}researchProducts",
                    access_token,
                    params={
                        'relOrganizationId': openorg_id,
                        'relCollectedFromDatasourceId': datasource_id
                    }
                )
                num_found_research_products_datasource_and_openorgs = ds_org_research_products_response['header']['numFound']
                print(f"Research products in data source associated with organization: {num_found_research_products_datasource_and_openorgs}")

                # Step 9: Calculate missing research products in data source
                num_missing_research_products_in_datasource = num_found_research_products_datasource - num_found_research_products_datasource_and_openorgs
                print(f"Missing research products in data source: {num_missing_research_products_in_datasource}")

                # Step 10: Calculate missing research products in organization
                num_missing_research_products_in_openorgs = num_found_research_products_openorgs - num_found_research_products_datasource_and_openorgs
                print(f"Missing research products in organization: {num_missing_research_products_in_openorgs}")

                results.append({
                    'Institution': institution_name,
                    'OpenOrg_ID': openorg_id,
                    'DataSource_ID': datasource_id,
                    'DataSource_Name': datasource_name,
                    'DataSource_Compatibility': datasource_compatibility,
                    'DataSource_LastValidated': datasource_last_validated,
                    'DataSource_URL': datasource_url,
                    'Num_Found_ResearchProducts_for_OpenOrg': num_found_research_products_openorgs,
                    'Num_Found_ResearchProducts_for_DataSource': num_found_research_products_datasource,
                    'Num_Found_ResearchProducts_for_OpenOrg_AND_DataSource': num_found_research_products_datasource_and_openorgs,
                    'Num_Missing_ResearchProducts_in_DataSource': num_missing_research_products_in_datasource,
                    'Num_Missing_ResearchProducts_in_OpenOrg': num_missing_research_products_in_openorgs,
                })

    # Save results to CSV
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    output_file = f"{timestamp}_nl-stats.csv"
    df = pd.DataFrame(results)
    df['Retrieved_On'] = datetime.datetime.now()
    df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()
