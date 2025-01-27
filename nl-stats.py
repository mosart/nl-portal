import requests
import pandas as pd
import yaml
import datetime

# Load configuration
def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Authenticate and retrieve access token
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
def fetch_api_data(url, token, params=None):
    print(f"Fetching data from {url} with params {params}...")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        print("Data fetched successfully.")
        return response.json()
    else:
        raise Exception(f"API request failed: {response.status_code}, {response.text}")

# Process the institutions data
def process_institutions(file_path):
    print(f"Loading institutions data from {file_path}...")
    return pd.read_csv(file_path)

# Main script
def main():
    print("Loading configuration...")
    config = load_config('config.yaml')

    client_id = config['OpenAIRE_Client_ID']
    client_secret = config['OpenAIRE_Client_Secret']
    org_data_file = config['Org_data_file']

    access_token = get_access_token(client_id, client_secret)
    institutions = process_institutions(org_data_file)

    results = []

    for index, row in institutions.iterrows():
        print(f"Processing institution {index + 1}/{len(institutions)}: {row['full_name_in_English']}...")
        ror_link = row['ROR_LINK']
        org_name = row['full_name_in_English']

        # Step 3: Get OpenAIRE Organization ID
        org_response = fetch_api_data(
            f"{config['OpenAIRE_API']}organizations",
            access_token,
            params={'pid': ror_link}
        )
        openorg_ids = [org['id'] for org in org_response['results'] if org['id'].startswith('openorgs')]

        for openorg_id in openorg_ids:
            print(f"Processing OpenAIRE Org ID: {openorg_id}...")

            # Step 4: Get research products count
            research_products_response = fetch_api_data(
                f"{config['OpenAIRE_API']}researchProducts",
                access_token,
                params={'relOrganizationId': openorg_id}
            )
            num_found_research_products = research_products_response['header']['numFound']
            print(f"Research products count: {num_found_research_products}")

            # Step 5: Get projects count
            projects_response = fetch_api_data(
                f"{config['OpenAIRE_API']}projects",
                access_token,
                params={'relOrganizationId': openorg_id}
            )
            num_found_projects = projects_response['header']['numFound']
            print(f"Projects count: {num_found_projects}")

            # Step 6: Get data sources
            data_sources_response = fetch_api_data(
                f"{config['OpenAIRE_API']}dataSources",
                access_token,
                params={'relOrganizationId': openorg_id}
            )
            for ds in data_sources_response['results']:
                ds_id = ds['id']
                ds_name = ds.get('officialName', '')
                ds_compatibility = ds.get('openaireCompatibility', '')
                ds_last_validated = ds.get('dateOfValidation', '')
                ds_url = ds.get('websiteUrl', '')

                print(f"Processing Data Source: {ds_name} (ID: {ds_id})...")

                # Step 7: Get research products in data source
                ds_research_products_response = fetch_api_data(
                    f"{config['OpenAIRE_API']}researchProducts",
                    access_token,
                    params={'relCollectedFromDatasourceId': ds_id}
                )
                num_found_research_products_ds = ds_research_products_response['header']['numFound']
                print(f"Research products in data source: {num_found_research_products_ds}")

                # Step 8: Get research products in data source associated with organization
                ds_org_research_products_response = fetch_api_data(
                    f"{config['OpenAIRE_API']}researchProducts",
                    access_token,
                    params={
                        'relOrganizationId': openorg_id,
                        'relCollectedFromDatasourceId': ds_id
                    }
                )
                num_found_research_products_ds_org = ds_org_research_products_response['header']['numFound']
                print(f"Research products in data source associated with organization: {num_found_research_products_ds_org}")

                # Step 9: Calculate missing research products in data source
                num_missing_ds = num_found_research_products_ds - num_found_research_products_ds_org
                print(f"Missing research products in data source: {num_missing_ds}")

                # Step 10: Calculate missing research products in organization
                num_missing_org = num_found_research_products - num_found_research_products_ds_org
                print(f"Missing research products in organization: {num_missing_org}")

                results.append({
                    'Institution': org_name,
                    'OpenAIRE_Org_ID': openorg_id,
                    'DataSource_ID': ds_id,
                    'DataSource_Name': ds_name,
                    'DataSource_Compatibility': ds_compatibility,
                    'DataSource_LastValidated': ds_last_validated,
                    'DataSource_URL': ds_url,
                    'Num_Research_Products_Org': num_found_research_products,
                    'Num_Research_Products_DS': num_found_research_products_ds,
                    'Num_Research_Products_DS_Org': num_found_research_products_ds_org,
                    'Num_Missing_DS': num_missing_ds,
                    'Num_Missing_Org': num_missing_org,
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
