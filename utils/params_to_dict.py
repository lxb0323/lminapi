def get_params_dict_inlist(data, inList: list) -> dict:
    '''
    整理传入字段，紧包含在inList中的并传入值的字段
    '''
    try:
        adata = data.dict()
    except:
        adata = data
    paramDict = {}
    for i in inList:
        if i in adata.keys():
            if data[i] != "":
                paramDict[i] = adata[i]
            else:
                continue
        else:
            continue
    return paramDict