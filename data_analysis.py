import boto3
from botocore.config import Config
import json
import pandas as pd
import shutil
import matplotlib.pyplot as plt  # this is for creating chart!
import os

# in case it takes too long to down load all files from S3 bucket
s3_config = Config(read_timeout=120, retries={'max_attempts':10})

# the bucket where there are all output files are stored
bucket_name = "sugarscape-100-jobs"
model_folders = [
    "altruistBinary", "altruistTop", "benthamBinary", "benthamTop",
    "egoistBinary", "egoistTop", "negativeBentham", "none", "rawSugarscape"
]

local_folder = "results_from_s3"

# createing local folder to store all files
if os.path.exists(local_folder):
    shutil.rmtree(local_folder)
os.makedirs(local_folder)

# connect to S3
s3 = boto3.client("s3", region_name="us-east-1", config=s3_config)
all_records = []


# download files from s3 bucket
for model in model_folders:
    print(f"we are downloding output files from model folder: {model}")
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=f"{model}/")
    for object in response.get("Contents", []):
        key = object["Key"]
        if not key.endswith(".json"):
            continue
        object_data = s3.get_object(Bucket=bucket_name, Key=key)
        content = object_data["Body"].read()
        records = json.loads(content)
        # each record states which model it belongs to
        for r in records:
            r["model"] = model
        all_records.extend(records)

# convert json to table
df = pd.DataFrame(all_records)

# turn records list into csv file
df.to_csv("all_records.csv", index=False)
print(f"we loaded {len(df)} rows from s3 bucket!")



