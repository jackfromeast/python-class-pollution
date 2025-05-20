#11 dict[key]
def item_get(d, k):
    return d[k]

#12 dict.get(key) 
def item_get_method(d, k):
    return d.get(k)

#13 dict.pop(key) 
def item_pop(d, k):
    return d.pop(k)

#14 dict.__getitem__(key) 
def getitem_dunder(d, k):
    return d.__getitem__(k)

#15 operator.getitem(dict, key) 
import operator
def getitem_operator(d, k):
    return operator.getitem(d, k)

#16 operator.__getitem__(dict, key)
import operator
def getitem_dunder_operator(d, k):
    return operator.__getitem__(d, k)

#17 operator.itemgetter(key)(dict) 
import operator
def itemgetter_operator(k, d):
    return operator.itemgetter(k)(d)

def itemgetter_operator_2(k, d):
    getter_func = operator.itemgetter(k)
    return getter_func(d)
