import influxdb_client
from sqlalchemy import create_engine
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import pandas as pd
import os
# InfluxDB settings
token = "UU4QPxIjcwcDOFVMMv0zfq5dIYGJC-vFFT1oSBEEQ7tUYNlXehU_F9EnBKQn4w3zYaQ17zv7X0JJjYVIRUORQQ=="
org = "ieuni"
url = "http://localhost:8086"
bucket = "diana"


# Initialize InfluxDB client
client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Initialize SQLAlchemy engine for MySQL
engine = create_engine('mysql://root:Forzaforza3@localhost/sakila')

# Your SQL query
query = """
SELECT customer_id, count(*) as num_rentals 
FROM rental 
GROUP BY customer_id 
ORDER BY num_rentals desc 
LIMIT 5; 
"""

data = pd.read_sql(query, engine)

points = []
# Create a point for each data row
for row in data.itertuples(index=False):
    point = Point("rental").tag("customer_id", row.customer_id).field("num_rentals", row.num_rentals)
    points.append(point)

# Write points to InfluxDB
write_api.write(bucket=bucket, record=points, write_precision=WritePrecision.NS)

# Close the client
client.close()
