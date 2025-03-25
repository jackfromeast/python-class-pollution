def test1(obj, key): 				# Source: Key, SourceKeyFlowState
	for _ in range(2):
		obj = obj.get(key)			# if key has SourceKeyFlowState, obj.get(key) -> ObjectLayerOneFlowState 
														# if key has SourceKeyFlowState and obj has ObjectLayerOneFlowState, obj.get(key) -> ObjectLayerTwoFlowState

	return obj 								# Sink: obj, ObjectLayerTwoFlowState

def test2(obj, key): 				# Source: Key, SourceKeyFlowState
	for _ in range(1):
		obj = obj.get(key)			# if key has SourceKeyFlowState, obj.get(key) -> ObjectLayerOneFlowState 
														# if key has SourceKeyFlowState and obj has ObjectLayerOneFlowState, obj.get(key) -> ObjectLayerTwoFlowState

	return obj 								# Sink: obj, ObjectLayerOneFlowState

def test3(obj, key): 				# Source: Key, SourceKeyFlowState
	key2 = "x"								# Not Source Key
	for _ in range(2):
		obj = obj.get(key)			# if key has SourceKeyFlowState, obj.get(key) -> ObjectLayerOneFlowState 
														# if key has SourceKeyFlowState and obj has ObjectLayerOneFlowState, obj.get(key) -> ObjectLayerTwoFlowState
		obj = obj.get(key2)			# Should not propagate the taint flow as key2 is not tainted with SourceKeyFlowState

	return obj 								# Sink: obj, ObjectLayerOneFlowState
