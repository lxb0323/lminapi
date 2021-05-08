import re
import time
from functools import wraps
from django.http import JsonResponse
from abc import ABCMeta, abstractmethod
from utils import recode

class Validator(object):
    """
    Abstract class that advanced
    validators can inherit from in order
    to set custom error messages and such.

    """

    __metaclass__ = ABCMeta

    err_message = "failed validation"
    not_message = "failed validation"

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError

class NotNull(Validator):
    """
    非空验证
    # NotNull(True)
    """

    def __init__(self, base_class):
        self.base_class = base_class
        self.err_message = "参数不为空"
    def __call__(self, value):
        return True if value else False

class PhoneVerif(Validator):
    """
    手机号规范验证
    """
    def __init__(self, base_class):
        self.base_class = base_class
        self.err_message = "手机号不规范"
    def __call__(self, value):
        if value:
            if re.match(r"^1[356789]\d{9}$", value):
                return True
            return False
        return True

class DateTimeVerif(Validator):
    """
    时间格式验证
    """
    def __init__(self, base_class):
        self.base_class = base_class
        self.err_message = "时间格式不正确'YYYY-mm-dd HH:MM:SS'"
    def __call__(self, value):
        if value:
            if datetime_verify(value):
                return True
            return False
        else:
            return True

def datetime_verify(date):
    """判断是否是一个有效的日期字符串"""
    try:
        if ":" in date:
            time.strptime(date, "%Y-%m-%d %H:%M:%S")
            
        else:
            time.strptime(date, "%Y-%m-%d")
        return True
    except Exception as e:
        print(e)
        return False


class InStr(Validator):
    """
    枚举验证 字符串
    # 示例:In([1, 2, 3])
    """

    def __init__(self, collection):
        self.collection = collection
        self.err_message = "必须是 %r 其中之一" % collection

    def __call__(self, value):
        if not value:
            return True
        return (value.lower() in self.collection)


class InInt(Validator):
    """
    枚举验证 整形
    # 示例:In([1, 2, 3])
    """

    def __init__(self, collection):
        self.collection = collection
        self.err_message = "必须是 %r 其中之一" % collection

    def __call__(self, value):
        if not value:
            return True
        return (int(value) in self.collection)


class Length(Validator):
    '''
    字符长度验证
    # 示例：Length(255)
    '''
    def __init__(self, collection):
        self.collection = collection
        self.err_message = "最大长度为 %r" % collection

    def __call__(self, value):
        if value:
            return len(value) <= self.collection
        return True

class InstanceOf(Validator):
    """
    参数类型验证
    # 示例: InstanceOf(basestring)
    """

    def __init__(self, base_class):
        self.base_class = base_class
        self.err_message = "必须为 %s 类型" % base_class.__name__

    def __call__(self, value):
        if value:
            return isinstance(value, self.base_class)
        return True

class YearMonthStr(Validator):
    """
    年-月  传入验证
    # 示例: YearMonthStr(str)
    """

    def __init__(self, base_class):
        self.base_class = base_class
        self.err_message = "必须为 '年-月' 格式，如：2020-3"

    def __call__(self, value):
        s = value.split('-')
        year_len = len(s[0])
        month = int(s[1])
        return year_len == 4 and 0 < month <= 12

def Required(field, dictionary):
    if field in dictionary.keys():
        return True if dictionary[field] else False
    else:
        return False


class ValVerify(object):

    def __init__(self):
        self.error = {}

    def _validate_list_helper(self, rules, args_dict, key):
        '''
        验证:
        param(rules): 传入规则，规则的类型为字典(dict), 示例：
                      {验证字段：[规则方法1, 规则方法2]}
        param(args_dict): 需要验证的参数字典(dict), 示例：
                          {"字段1": 值,}
        param(key): 需要验证的字段
        param(err): 错误信息
        '''
        elist = []
        for vfunc in rules[key]: # 遍历这个参数所有验证方法
            if key in args_dict.keys(): # 判断这个参数有没有传入
                if vfunc != Required: # 如果验证方法不为Required
                    valid = vfunc(args_dict[key])
                    if not valid:
                        msg = getattr(vfunc, "err_message", "failed validation")
                        elist.append(msg)
        if elist != []:
            self.error[key] = elist


    def validate(self, rules, args_dict):
        '''
        验证
        param(rules): 传入规则，规则的类型为字典(dict), 示例：
                      {验证字段：[规则方法1, 规则方法2]}
        param(args_dict): 需要验证的参数字典(dict), 示例：
                          {"字段1": 值,}
        '''
        for key in rules:
            if Required in rules[key]:
                if Required(key, args_dict) != True:
                    self.error[key] = ["参数必传, 并不能为空"]
                    continue
            self._validate_list_helper(rules, args_dict, key)
        ok = True
        if self.error != {}:
            ok = False
        return ok, self.error

def validator_wrap(rules):
    """装饰器: 检测传入参数是否符合规则
    :param rules:参数的校验规则,map
    :param strip:对字段进行前后空格检测
    """

    def decorator(f):
        @wraps(f)
        def decorated_func(request, *args, **kwargs):
            try:
                if request.request.data:
                    args_dict = request.request.data
                elif request.request.GET:
                    args_dict = request.request.GET
                else:
                    args_dict = {}
                if rules:
                    result, err = ValVerify().validate(rules, args_dict)
                    if not result:
                        re_data = recode.error_func(status=22, error=err, message="验证失败")
                        return JsonResponse(re_data)
            except Exception as e:
                re_data = recode.error_func(status=33, error=str(e))
                return JsonResponse(re_data)
            return f(request, *args, **kwargs)

        return decorated_func

    return decorator

def validator_function(rules, request):
    """方法调用: 检测传入参数是否符合规则
    :param rules:参数的校验规则,map
    :param strip:对字段进行前后空格检测
    """

    try:
        if request.data:
            args_dict = request.data
        elif request.GET:
            args_dict = request.GET
        else:
            args_dict = {}
        if rules:
            result, err = ValVerify().validate(rules, args_dict)
            if not result:
                re_data = recode.error_func(status=22, error=err, message="验证失败")
                return JsonResponse(re_data)
    except Exception as e:
        re_data = recode.error_func(status=33, error=str(e))
        return JsonResponse(re_data)
    return True