
def is_list_of(l : list, classe : object)-> bool:
    if(l==None or classe == None or len(l) == 0 ):
        return False
    i : int = 0
    is_type : bool = True
    length : int = len(l)
    while is_type and i<length:
        if type(l[i])!=classe: is_type = False
        i += 1
    return is_type


