import torch
from docarray import DocList, BaseDoc
from docarray.data import MultiModalDataset
from docarray.documents import TextDoc
from docarray.base_doc import DocArrayResponse
from fastapi import FastAPI
from typing import Dict, List
import uvicorn


class Thesis(BaseDoc):
    title: TextDoc


class Student(BaseDoc):
    thesis: Thesis


class ProcessingRequest(BaseDoc):
    student: Student
    preprocessing_paths: Dict[str, List[str]] = {}


def embed_title(title: TextDoc):
    """Generate embeddings for the thesis title."""
    title.embedding = torch.ones(4)


def normalize_embedding(thesis: Thesis):
    """Normalize the thesis title embeddings."""
    if hasattr(thesis.title, "embedding") and thesis.title.embedding is not None:
        thesis.title.embedding = thesis.title.embedding / thesis.title.embedding.norm()


def prepend_number(text: str):
    """Prepend 'Number ' to the title text."""
    return f"Number {text}"


AVAILABLE_PROCESSORS = {
    "embed_title": embed_title,
    "normalize_embedding": normalize_embedding,
    "prepend_number": prepend_number,
}


app = FastAPI(title="Thesis Processing API")


@app.post("/process_thesis/", response_model=Student, response_class=DocArrayResponse)
async def process_thesis(request: ProcessingRequest) -> Student:
    """
    Process a student's thesis using MultiModalDataset with user-specified preprocessing paths.

    Example request:
    {
        "student": {
            "thesis": {
                "title": {
                    "text": "5"
                }
            }
        },
        "preprocessing_paths": {
            "thesis.title.text": ["prepend_number"]
        }
    }
    """
    preprocessing_config = {}

    for path, processors in request.preprocessing_paths.items():
        for processor_name in processors:
            if processor_name in AVAILABLE_PROCESSORS:
                if path not in preprocessing_config:
                    preprocessing_config[path] = AVAILABLE_PROCESSORS[processor_name]

    single_doc = DocList[Student]([request.student])

    if preprocessing_config:
        ds = MultiModalDataset[Student](
            single_doc,
            preprocessing=preprocessing_config,
        )
        processed_student = ds[0]
    else:
        processed_student = request.student

    return processed_student


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
