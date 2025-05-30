import boto3 # this is for talking to aws service
from botocore.config import Config # this is for setting timeout and retry setings for downloding big files
import json
import pandas as pd # this is for organizing data into tables
import shutil # for deleting folders and files
import matplotlib.pyplot as plt  # this is for creating chart!
import os

# in case it takes too long to down load all files from S3 bucket
s3_config = Config(read_timeout=120, retries={'max_attempts':10}) # if AWS is slow, wait longer (120 seconds), and retry up to 10 times

# the bucket where there are all output files are stored
bucket_name = "sugarscape-100-jobs"

model_folders = [
    "altruistBinary", "altruistTop", "benthamBinary", "benthamTop",
    "egoistBinary", "egoistTop", "negativeBentham", "none", "rawSugarscape"
]

# local folder where we store files
local_folder = "results_from_s3"

# createing local folder to store all files
if os.path.exists(local_folder):
    shutil.rmtree(local_folder)
os.makedirs(local_folder)


# connect to S3 in the us-east-1 region
s3 = boto3.client("s3", region_name="us-east-1", config=s3_config)

# this is where we store all the simulation data that we donload!
all_records = []


# download files from s3 bucket
for model in model_folders:
    print(f"we are downloding output files from model folder: {model}")
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=f"{model}/") # this is asking AWS what files there are in this model folder?
    for object in response.get("Contents", []):
        key = object["Key"]
        if not key.endswith(".json"):
            continue
        object_data = s3.get_object(Bucket=bucket_name, Key=key)
        content = object_data["Body"].read()

        # Save JSON to local disk
        model_dir = os.path.join(local_folder, model)
        os.makedirs(model_dir, exist_ok=True)
        filename = os.path.basename(key)
        local_path = os.path.join(model_dir, filename)
        with open(local_path, "wb") as f:
            f.write(content)

        
        records = json.loads(content)
        # each record states which model it belongs to
        for r in records:
            r["model"] = model
        all_records.extend(records)

# convert json to table
df = pd.DataFrame(all_records) # this has all the simulation data!

# turn records list into csv file
df.to_csv("all_records.csv", index=False)
print(f"we loaded {len(df)} rows from s3 bucket!")







# ----- this is analyzing part! -----




# we keep only the last timestep of each simulation
# because we are just interested in how it ended 
final_timesteps = (
    df.sort_values("timestep")
    .groupby(["model", "seed"])
    .tail(1)
    .reset_index(drop=True)
)

# we want simulations to be soretd by model and seed
final_timesteps = final_timesteps.sort_values(by=["model", "seed"]).reset_index(drop=True)

# this is where we save all the analysis results!
output_dir = "analysis_outputs"
os.makedirs(output_dir, exist_ok=True)

# we save it to CSV
final_csv_path = os.path.join(output_dir, "summary_final_timesteps.csv")
final_timesteps.to_csv(final_csv_path, index=False)
print("we saved final timestep summary to csv file for you!")





# Boxplot: Gini Coefficient by model ----------


# this starts a new chart with the size of 12 inches wide and 6 inches tall
plt.figure(figsize=(12, 6))

# this makes a boxplot t
# each box will show the range of Gini values from 100 different sumulation runs per model
final_timesteps.boxplot(column="giniCoefficient", by="model")

# this is a title
plt.title("Final Gini Coefficient by Model")
plt.suptitle("") # this is for removing the subtitle

# this label the x and y axis
plt.xlabel("Model")
plt.ylabel("Gini Coefficient")

# i needed to totate the name or each name will overlap with the one next to it
plt.xticks(rotation=45)
plt.tight_layout()

# this saves the chart as a png image file in the folder that we created!
gini_plot_path = os.path.join(output_dir, "gini_by_model.png")
plt.savefig(gini_plot_path)
print("Saved boxplot to gini_by_model.png")





# Boxplot: Final Wealth by model ----------


# this starts a new chart with the size of 12 inches wide and 6 inches tall
plt.figure(figsize=(12, 6))

# this makes a boxplot using the average wealth of agents at the end
final_timesteps.boxplot(column="meanWealth", by="model")

# label the chart
plt.title("Final Mean Wealth by Model")
plt.suptitle("")
plt.xlabel("Model")
plt.ylabel("Mean Wealth")
plt.xticks(rotation=45)
plt.tight_layout()

# save the wealth boxplot to a PNG file
wealth_plot_path = os.path.join(output_dir, "wealth_by_model.png")
plt.savefig(wealth_plot_path)   
print("Saved boxplot to wealth_by_model.png")





# Line Plot: Average Gini over time per model ---------


# this starts a new blank chart for the line plot
plt.figure(figsize=(12, 6))

# this loops throught each unique model name in the data
for model in df["model"].unique():
    model_df = df[df["model"] == model] # picls out all rows taht belong to only this model (one at a time!)
    # this group by timestep and calculate the average Gini score across all 100 runs at each step
    gini_over_time = model_df.groupby("timestep")["giniCoefficient"].mean() 
    # this draw a line on the chart
    plt.plot(gini_over_time.index, gini_over_time.values, label=model)

# this adds title and labels
plt.title("Average Gini Coefficient Over Time")
plt.xlabel("Timestep")
plt.ylabel("Average Gini Coefficient")
plt.legend()
plt.tight_layout()

# save the line polot as png
gini_lineplot_path = os.path.join(output_dir, "gini_over_time.png")
plt.savefig(gini_lineplot_path) 
print("Saved line plot to gini_over_time.png")