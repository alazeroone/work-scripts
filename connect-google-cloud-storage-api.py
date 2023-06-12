from google.cloud import bigquery
from google.cloud import bigquery_storage_v1beta1
from google.oauth2 import service_account

# Path to your service account key JSON file
credentials_path = '/path/to/service-account-key.json'

# Create credentials object from the service account key file
credentials = service_account.Credentials.from_service_account_file(credentials_path)

# Create a BigQuery client with the credentials
client = bigquery.Client(credentials=credentials)

# Create a BigQuery Storage client with the credentials
storage_client = bigquery_storage_v1beta1.BigQueryStorageClient(credentials=credentials)

# Define the table reference
table_reference = bigquery.TableReference.from_string("your-project-id.your-dataset-id.your-table-id")

# Create a read session
read_session = bigquery_storage_v1beta1.types.ReadSession(table=table_reference)

# Start the read session
created_session = storage_client.create_read_session(request={"read_session": read_session})

# Get the read session ID
session_id = created_session.name

# Create a read stream
read_stream = bigquery_storage_v1beta1.types.StreamPosition(stream=session_id)

# Create a read request
read_request = bigquery_storage_v1beta1.types.ReadRowsRequest(read_stream=read_stream)

# Read rows from the session
response = storage_client.read_rows(request=read_request)

# Process the read rows response
for row in response:
    # TODO: Add your logic here to handle the read rows response
    print(row)

# Optionally, close the read session
storage_client.close_read_session(request={"name": session_id})
