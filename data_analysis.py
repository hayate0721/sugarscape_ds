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




# ----- this is analyzing part! -----

# we get only the last entries per seed per model
final_timesteps = (
    df.sort_values("timestep")
    .groupby(["model", "seed"])
    .tail(1)
    .reset_index(drop=True)
)

final_timesteps = final_timesteps.sort_values(by=["model", "seed"]).reset_index(drop=True)

output_dir = "analysis_outputs"
os.makedirs(output_dir, exist_ok=True)


# we save it to CSV
final_csv_path = os.path.join(output_dir, "summary_final_timesteps.csv")
final_timesteps.to_csv(final_csv_path, index=False)
print("we saved final timestep summary to csv file for you!")

# Boxplot: Gini Coefficient by model
plt.figure(figsize=(12, 6))
final_timesteps.boxplot(column="giniCoefficient", by="model")
plt.title("Final Gini Coefficient by Model")
plt.suptitle("")
plt.xlabel("Model")
plt.ylabel("Gini Coefficient")
plt.xticks(rotation=45)
plt.tight_layout()
gini_plot_path = os.path.join(output_dir, "gini_by_model.png")
plt.savefig(gini_plot_path)
print("Saved boxplot to gini_by_model.png")

# Boxplot: Final Wealth by model
plt.figure(figsize=(12, 6))
final_timesteps.boxplot(column="meanWealth", by="model")
plt.title("Final Mean Wealth by Model")
plt.suptitle("")
plt.xlabel("Model")
plt.ylabel("Mean Wealth")
plt.xticks(rotation=45)
plt.tight_layout()
wealth_plot_path = os.path.join(output_dir, "wealth_by_model.png")
plt.savefig(wealth_plot_path)   
print("Saved boxplot to wealth_by_model.png")

# Line Plot: Average Gini over time per model
plt.figure(figsize=(12, 6))
for model in df["model"].unique():
    model_df = df[df["model"] == model]
    gini_over_time = model_df.groupby("timestep")["giniCoefficient"].mean()
    plt.plot(gini_over_time.index, gini_over_time.values, label=model)

plt.title("Average Gini Coefficient Over Time")
plt.xlabel("Timestep")
plt.ylabel("Average Gini Coefficient")
plt.legend()
plt.tight_layout()
gini_lineplot_path = os.path.join(output_dir, "gini_over_time.png")
plt.savefig(gini_lineplot_path) 
print("Saved line plot to gini_over_time.png")