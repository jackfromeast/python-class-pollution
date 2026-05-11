from fastapi import FastAPI, Request
from docarray import BaseDoc
from docarray.data import MultiModalDataset
import uvicorn

app = FastAPI()

class MyDoc(BaseDoc):
  text: str = ""

docs = [MyDoc(text="stored")]

@app.post("/docs")
async def update_docs(request: Request):
  data = await request.json()
  # Simulates applying user-provided preprocessing paths to documents
  # The MultiModalDataset.__getitem__ splits field paths on "." and
  # traverses via getattr/setattr
  for item in data.get("data", []):
    for key, value in item.items():
      if key == "text":
        continue
      # Apply attribute path update (vulnerable pattern)
      parts = key.split(".")
      obj = docs[0]
      for part in parts[:-1]:
        obj = getattr(obj, part)
      setattr(obj, parts[-1], value)
  return {"status": "updated"}

if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=8080)
