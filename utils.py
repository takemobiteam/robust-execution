# Utilities:

def index_in_rangep(i, min_i: int, max_i: int):
    # Returns True if index i is an integer within the range from min_i to max_i.
    return type(i) is int and min_i <= i <= max_i

def list2string(list1: list) -> str:
    #Returns a string denoting a list of objects,
    # while ensuring that the string method for each object is invoked.
    st = "["
    first = True
    for l1 in list1:
        if first:
            st = st + str(l1)
            first = False
        else:
            st = st + "," + str(l1)
    return st + "]"