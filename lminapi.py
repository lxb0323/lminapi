from rest_framework.response import Response
from rest_framework.views import APIView
from itertools import chain
from datetime import datetime


from utils import recode, get_error_handler_return
from utils.params_to_dict import get_params_dict_inlist
from utils.comfunc import paginationfunc, exam_old, file_save_addr
from utils.params_verify import validator_function

class LminApiView(APIView):

    modelObj: object  # 查询数据库对象
    list_display: tuple or list
    get_list_filter: list # 列表筛选字段  [{"field": , "rule": "field__in"}]
    post_files: dict # post上传文件
    put_files: dict # post上传文件
    unique_param: list # 需要查重的字段
    delete_rule: dict # 删除时传入的字段规则
    post_rule: dict # 新增时传入的字段规则
    put_rule: dict # 编辑时传入的字段规则
    put_where_params = [] # put请求修改时的条件参数
    post_inlist: list # 新增时创建model对象需要的字段
    put_inlist: list # 编辑时修改model对象需要的字段
    file_first_path: str
    delete_where_params = [] # delete请求删除时的条件参数

    def _get_list_values(self, instance):
        opts = instance._meta
        data = {}
        fields = self.list_display
        for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
            if not getattr(f, 'editable', False):
                continue
            if fields and f.name not in fields:
                continue
            if type(f.value_from_object(instance)) == datetime:
                data[f.name] = datetime.strftime(f.value_from_object(instance), "%Y-%m-%d %H:%M:%S")
            else:
                data[f.name] = f.value_from_object(instance)
        return data

    def _get_list_filter_kwargs(self, data):
        try:
            adata = data.dict()
        except:
            adata = data
        filterDict = {}
        for i in self.get_list_filter:
            key = i["rule"]
            value = adata[i["field"]]
            filterDict[key] = value
        return filterDict

    def _get_post_params(self, data):
        return get_params_dict_inlist(data, self.post_inlist)
    
    def _get_put_params(self, data):
        return get_params_dict_inlist(data, self.put_inlist)

    @get_error_handler_return
    def get(self, request, *args, **kwargs):
        '''
        APIView视图get请求
        param page: 页码
        param size: 每页条数
        return: 返回分两种情况，传入page时进行分页返回data为对象，不传时返回所有结果data为list
        '''
        page = request.GET.get("page", None)
        size = request.GET.get("size", 20)
        se_dict = self._get_list_filter_kwargs(data=request.GET)
        res = self.modelObj.objects.filter(**se_dict)
        resList = []
        for i in res:
            resList.append(self._get_list_values(i))
        if page:
            rList = paginationfunc(resList=resList, pg=page, size=size)
        else:
            rList = resList
        return Response(recode.success_func(data=rList))

    @get_error_handler_return
    def post(self, request, *args, **kwargs):
        '''
        APIView视图post请求
        '''
        ok = validator_function(rules=self.post_rule,request=request)
        if ok != True:
            return ok
        cr_dict = self._get_post_params(data=request.data)
        for unparam in self.unique_param_list:
            val = request.data.get(unparam)
            assert exam_old(obj=self.obj, paramDict={unparam:val}, excludeDict=None),(1001, "该【{}】内容已存在".format(unparam))
        
        for param in self.post_file_params_dict.keys():
            if request.data.get(param):
                file = request.data.get(param)
                ok, fileaddr = file_save_addr(file=file, firstPath=self.file_first_path, pathList=self.post_file_params_dict[param]["path"])
                if ok != True:
                    return Response(recode.error_func(status=5003, error=ok))
                cr_dict[param] = fileaddr
        self.modelObj.objects.create(**cr_dict)
        return Response(recode.success_func(data={}))

    @get_error_handler_return
    def put(self, request, *args, **kwargs):
        '''
        APIView视图put请求
        '''
        assert self.put_where_params, ("update_find where error", "请传入修改条件")
        ok = validator_function(rules=self.put_rule,request=request)
        if ok != True:
            return ok
        up_dict = self._get_put_params(data=request.data)
        for unparam in self.unique_param_list:
            val = request.data.get(unparam)
            assert exam_old(obj=self.obj, paramDict={unparam:val}, excludeDict=None),(1001, "该【{}】内容已存在".format(unparam))
        
        for param in self.post_file_params_dict.keys():
            if request.data.get(param):
                file = request.data.get(param)
                ok, fileaddr = file_save_addr(file=file, firstPath=self.file_first_path, pathList=self.post_file_params_dict[param]["path"])
                if ok != True:
                    return Response(recode.error_func(status=5003, error=ok))
                up_dict[param] = fileaddr
        if up_dict != {}:
            f_dict = get_params_dict_inlist(data=request.data, inList=self.put_where_params)
            ups = self.modelObj.objects.filter(**f_dict)
            for i in ups:
                i.__dict__.update(**up_dict)
                i.save()
        return Response(recode.success_func(data={}))

    @get_error_handler_return
    def delete(self, request, *args, **kwargs):
        '''
        APIView视图delete请求
        '''
        assert self.delete_where_params, ("delete_find where error", "请传入修改条件")
        ok = validator_function(rules=self.delete_rule,request=request)
        if ok != True:
            return ok
        f_dict = get_params_dict_inlist(data=request.data, inList=self.delete_where_params)
        dels = self.modelObj.objects.filter(**f_dict)
        for i in dels:
            i.delete()
        return Response(recode.success_func(data={}))


class TestView(LminApiView):

    modelObj = UsersModels  # 查询数据库对象
    list_display = ("id", "name")
    get_list_filter = [] # 列表筛选字段  [{"field": , "rule": "field__in"}] "rule"根据django orm 的**kwargs查询方式条件来写
    post_files = {} # post上传文件 {"file_field": {"path": ["folder_name", "child_folder_name"]}}
    put_files = {} # post上传文件 {"file_field": {"path": ["folder_name", "child_folder_name"]}}
    unique_param = [] # 需要查重的字段 ["field"]
    delete_rule = {} # 删除时传入的字段规则 {"id": [Required,],}
    post_rule = {} # 新增时传入的字段规则  {"field": [Required, Length(32), InstanceOf(str)],}
    put_rule = {} # 编辑时传入的字段规则  {"field": [Required, Length(32), InstanceOf(str)],}
    put_where_params = [] # put请求修改时的条件参数  [{"field": , "rule": "field__in"}]
    post_inlist = [] # 新增时创建model对象需要的字段 ["field1","field2"]
    put_inlist = [] # 编辑时修改model对象需要的字段 ["field1","field2"]
    file_first_path = "/usr/myfolder/" # 文件保存的初始地址
    delete_where_params = [] # delete请求删除时的条件参数 [{"field": , "rule": "field"}]