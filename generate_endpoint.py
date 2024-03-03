from fastapi import FastAPI
from pydantic import BaseModel
from typing import List


app = FastAPI()

class BaseFramework(BaseModel):
    name: str
    llm: str

class NewFramework(BaseFramework):
    file: str
    topk: int
    header: str = "default header"

    def invoke(self) -> str:
        return f"Chat completion completed {self.header=}"

class ChatCompletionRequest(BaseModel):
    stream: bool
    message: List = []


# in the yaml
#
# newusecase:
#   session:
#     llm:
#       type: str
#       required: false
#       default: "AzureGPT3"
#     topk:
#       type: int
#       required: false
#       default: "Loaded Header"

usecase1_yaml_load_dict = {
    "llm": "AzureGPT3",  # Default value is None, so the field is optional
    "header": "loaded header",
    "topk": 3,
    "message": [{"role": "system", "message": "hello human!"}]
}

@app.get("/usecase/{usecase}/schema")
async def read_item(usecase: str):
    """gets the schema of the usecase"""

    def model_class_to_dict(model_class):
        model_dict = {}
        for name, model_field in model_class.__fields__.items():
            print("model field", model_field)
            model_dict[name] = str(model_field).split(" ")
        return model_dict

    # rparam is all the params necessary to create chatcompletion with a newframework usecase
    rparam = model_class_to_dict(NewFramework)
    rparam.update(model_class_to_dict(ChatCompletionRequest)) 

    # remove param keys from yaml session dict that prefilled some values 
    rparam = {key: rparam[key] for key in rparam if key not in usecase1_yaml_load_dict}

    return rparam


@app.post("/generate/{usecase}")
async def read_item(usecase: str, session: dict):
    """invoke usecase -> create session + chatcompletion"""
    
    tmp_dict = session.copy()
    tmp_dict.update(usecase1_yaml_load_dict)
    
    # all these value can create the newframework
    framework = NewFramework(**tmp_dict)

    return framework.invoke()

# {
#   "name": "new usecase",
#   "file": "this is file",
#   "stream": true
# }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5678)
