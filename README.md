# HoshinoAuthorizeSystem
用于HoshinoV2的授权系统

当前授权系统仅能管理用咖啡佬的服务层的功能

下载后覆盖原来的hoshino文件夹，然后安装requirements.txt中的依赖就行了

##更新
支持yobot缝合板管理,将nonebot_plugin.py替换yobot/src/client下的文件即可

### 使用方法
> 超级用户权限(私聊机器人)
1. 添加注册码 30 : 添加一个时长为30天的授权码
2. 查看注册码 : 查看当前所有授权码
3. 授权列表  : 查看当前授权情况

> 用户在群内注册方法
1. @机器人  注册  <注册码>
2. @机器人  查看授权状态
