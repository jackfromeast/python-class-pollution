module ClassPollutionMessage {
  predicate outputMsg(string vulnType, string msg) {
    (
      (
        vulnType = "SetBoth-GetBoth" and 
        msg = "Type:" + vulnType + " Class pollution function: $@, with key source: $@, and object source: $@. Set attribute key: $@, Set item op key: $@. Get attribute op: $@. Get item op: $@."
      )
      or
      (
        vulnType = "SetBoth-GetAttr" and 
        msg = "Type:" + vulnType + " Class pollution function: $@, with key source: $@, and object source: $@. Set attribute key: $@, Set item op key: $@. Get attribute op: $@."
      )
      or 
      (
        vulnType = "SetAttr-GetBoth" and 
        msg = "Type:" + vulnType + " Class pollution function: $@, with key source: $@, and object source: $@. Set attribute key: $@. Get attribute op: $@. Get attribute op: $@. Get item op: $@."
      )
      or
      (
        vulnType = "SetAttr-GetAttr" and 
        msg = "Type:" + vulnType + " Class pollution function: $@, with key source: $@, and object source: $@. Set attribute key: $@. Get attribute op: $@."
      ) 
      or
      (
        vulnType = "SetItem-GetBoth" and 
        msg = "Type:" + vulnType + " Class pollution function: $@, with key source: $@, and object source: $@. Set item key: $@. Get attribute op: $@. Get item op: $@."
      )
      or
      (
        vulnType = "SetItem-GetAttr" and 
        msg = "Type:" + vulnType + " Class pollution function: $@, with key source: $@, and object source: $@. Set item key: $@. Get attribute op: $@."
      )
    )
  }
}