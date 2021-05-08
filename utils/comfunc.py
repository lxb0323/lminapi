'''
常用方法
'''
import os
from django.core.paginator import Paginator

def paginationfunc(self, resList, pg, size):
    '''
    分页方法
    param resList: 需要进行分页的列表
    param pg: 页码
    param size: 每页条数
    return:
        count: 总条数
        num_pages: 总页数
        next_page: 下一页
        previous_page：上一页
        ret：当前页结果列表
    '''
    p = Paginator(resList, size)
    next_page = None
    previous_page = None
    page1 = p.page(pg)
    if page1.has_next():
        next_page = page1.next_page_number()
    if  page1.has_previous():
        previous_page = page1.previous_page_number()
    data = {"count":p.count,"num_pages":p.num_pages,"next_page":next_page,"previous_page":previous_page,
        "ret":page1.object_list}
    return data

def exam_old(modelObj, paramDict: dict, excludeDict: dict = None) -> bool:
    '''
    检查对象是否已存在 配合post新增时进行也有查重
    param modelObj: django models 对象
    param paramDict: 查重的字段以及值，{"field": field_value,}
    param excludeDict: 需要排除的条件，{"field": field_value,}
    return:
        返回bool值, 存在时返回true
    '''
    if excludeDict == None:
        old = modelObj.objects.filter(**paramDict).first()
    else:
        old = modelObj.objects.filter(**paramDict).exclude(**excludeDict).first()
    if not old:
        return False
    return True


def make_path(fpath: str):
    '''
    检查文件夹是否存在，不存在则创建
    return:
        True or err
    '''
    try:
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        return True
    except Exception as e:
        return str(e)

def add_file(filePath, file):
    '''
    写入文件
    param filePath:文件写入地址
    param file: 文件对象
    return:
        True or err
    '''
    try:
        with open(filePath,'wb') as f:
            for fimg in file.chunks():
                f.write(fimg)
        return True
    except Exception as e:
        return str(e)

def file_save_addr(file, firstPath: str, pathList: list):
    '''
    对文件进行写入并返回路劲
    param file: 文件对象
    param firstPath: 初始文件夹路径
    param pathList: 文件写入的具体路径分级列表,["floder","child floder"]
    return:
        bool
        路径str
    '''
    filepath = firstPath
    filestr = ""
    for i in pathList:
        filepath = os.path.join(filepath, i)
        filestr = filestr + "/" + i
    make_path(filepath)
    lastfilePath = os.path.join(filepath, file.name)
    ok = add_file(filePath=lastfilePath, file=file)
    if ok != True:
        return ok, ""
    return True, filestr + "/" + file.name