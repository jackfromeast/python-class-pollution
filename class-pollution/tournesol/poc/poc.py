from solidago.generative_model import GenerativeModel
from solidago.pipeline import Pipeline
import json



def set_attr(x_parameter: str, x: float, generative_model, pipeline):
    x_list = x_parameter.split(".")
    
    if x_list[0] == "generative_model": 
        obj = generative_model
    elif x_list[0] == "pipeline":
        obj = pipeline
    else: 
        raise ValueError(f"No match for {x_parameter[0]}")
        
    for attr in x_list[1:-1]:
        try:    obj = getattr(obj, attr)
        except: 
            try: obj = obj[attr]
            except: obj = obj[int(attr)]
    try:
        setattr(obj, x_list[-1], x)
    except:
        obj[x_list[-1]] = x


with open("hyperparameters.json") as json_file:
    hps = json.load(json_file)
generative_model = GenerativeModel.from_json(hps["generative_model"])
pipeline = Pipeline.from_json(hps["pipeline"])
set_attr("generative_model.__init__.__globals__.GenerativeModel.__name__", "polluted", generative_model, pipeline)
print(GenerativeModel.__name__)