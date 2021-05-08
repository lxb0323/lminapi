'''
    return Json models
'''

import functools
from datetime import datetime
from rest_framework.response import Response
from django.db.utils import IntegrityError


class ReCode(object):

    def error_func(self, status, error,message = None):
        
        data = {
            "status": status,  # 状态
            "code": 0,
            "error": error,  # 错误提示
            "message": message if message else error,  # 信息
            "timestamp": datetime.now().strftime('%Y/%m/%d %H:%M:%S'),  # 时间
        }
        return data

    def success_func(self,data: dict):

        re_data = {
            "status": 200,
            "code": 1,
            "message": "操作成功",
            "data": data,
            "timestamp": datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        }
        return re_data


def get_error_handler_return(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except AssertionError as a:
            re_data = ReCode().error_func(status=a.args[0][0], error=a.args[0][1])
            
            return Response(re_data)
        except IntegrityError as t:
            re_data = ReCode().error_func(status=1002, error="内容已存在")
            return Response(re_data)
        except Exception as e:
            re_data = ReCode().error_func(status=5000, error=str(e))
            
            return Response(re_data)
    return wrapper
