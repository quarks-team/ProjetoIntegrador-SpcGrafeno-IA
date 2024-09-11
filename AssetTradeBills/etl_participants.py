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