# PIM-fraud-analytics
## Architecture
This workload runs on two LPARs (IBM i and Linux)


### Linux
The Linux LPAR is where the REST API is running (in RHEL). This LPAR does inference with 7 transactions (current + 6 previous) to determine if the current transaction is fraud.

### IBM i
The IBM i LPAR hosts the database with the credit card transactions. The schema has the following database elements:

- **UDF:** grabs the previous 6 transaction for a given user and card. This UDF will be called in the trigger
- **Trigger:** Upon insert, the trigger creates a JSON document with the current transaction, as well as the previous 6 transactions for that user/card (this is done by calling the UDF). The JSON document is then sent to the REST API on the linux lpar to determine if the current transaction is fraud. The result is sent back to IBM i, which inserts the transaction into the database with the `is_fraud` value set.

## Setup Steps
### Linux
### IBM i

## Running the Workload Using JMeter
