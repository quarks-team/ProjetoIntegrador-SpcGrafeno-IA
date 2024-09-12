import pandas as pd
import PostgresConnection as conn



asset_parts = pd.read_csv('asset_parts.csv', low_memory=False)

print(asset_parts)



# Example usage:

#db = conn(dbname='postgres', user='postgres', password='123')
#db.connect()

#for(row in asset_parts):
#    db.execute_query("INSERT INTO asset_parts (name) VALUES (%s);", (row[''],))

#print(results)
#db.close()
#results = db.fetch_query("SELECT * FROM asset_parts;")
#print(results)
#db.close()



# Create a connection object
db = PostgresConnection(dbname='your_dbname', user='your_username', password='your_password')

# Connect to the database
db.connect()

# Insert a new paymaster record
db.insert_paymaster(
    id='1234567890abcdef1234567890abcdef',  # Example UUID
    kind='employee',
    name='John Doe',
    document='ID123456789',
    email_primary='john.doe@example.com',
    email_secondary='john.doe.secondary@example.com',
    deleted_at=None,  # or '2024-09-11 12:00:00' if it's a timestamp
    created_at='2024-09-11 12:00:00',
    updated_at='2024-09-11 12:00:00'
)

# Close the connection
db.close()
