from setuptools import setup, find_packages
 
setup(
    name='lminapi',  # 打包后的包文件名
    version='0.0.1',    #版本号
    keywords=("APIView", "Validator", "api"),    # 关键字
    description='整合简化drf APIView视图类常用方法, 简化传入参数已验证方法',  # 说明
    long_description="整合简化drf APIView视图类常用方法, 简化传入参数已验证方法",  #详细说明
    license="MIT Licence",  # 许可
    url='112',# 一般是GitHub项目路径
    author='bing0323',
    author_email='ltjlxb@163.com',
    packages= find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=['django','djangorestframework'],
)