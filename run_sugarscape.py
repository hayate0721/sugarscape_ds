# Hayate Saito
import os
import json


# this is the list of models that we will be using
# each modell will get 100 jobs
models = [
    "altruistBinary", "altruistTop", "benthamBinary", "benthamTop",
    "egoistBinary", "egoistTop", "negativeBentham", "none", "rawSugarscape"
]

# Job index (this is needed to identify each job)
# default is set to 0 (for local testing purpose)
index = int(os.environ.get("AWS_BATCH_JOB_ARRAY_INDEX", "0"))


# divide the index by 100 to choose which model to use
# we divide it by 100 because we submit 100 jobs to one model
model = models[index // 100]


# it takes the remainder as a seed (we will get 0-99)
seed = index % 100


# we load our existing config file for each job
with open("new_config.json") as f:
    config = json.load(f)


# we modify our config file for each job
config["sugarscapeOptions"]["agentDecisionModels"] = [model]
config["sugarscapeOptions"]["seed"] = seed
config["sugarscapeOptions"]["logfile"] = f"output_{model}_seed_{seed}.json"



# we save new config file
with open("config.json", "w") as f:
    json.dump(config, f)


# run the program
os.system("python3 sugarscape.py --conf config.json")
