import influxdb_client
from sqlalchemy import create_engine
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import pandas as pd
import os
# InfluxDB settings
token = os.environ.get("INFLUXDB_TOKEN")
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

# Connect to the MySQL database using SQLAlchemy
with engine.connect() as connection:
    result = connection.execute(query)

    for row in result:
        customer_id = row['customer_id']  # Extracting the customer_id
        num_rentals = row['num_rentals']  # Extracting the num_rentals

        # Create a point and write it to InfluxDB
        point = (
            Point("Top_Renting_Customers")
            .tag("customer_id", str(customer_id))  # Storing customer_id as a tag
            .field("num_rentals", num_rentals)  # Storing num_rentals as a field
        )
        write_api.write(bucket=bucket, org=org, record=point)
