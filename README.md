# HoshinoAuthorizeSystem
用于HoshinoV2的授权系统

当前授权系统仅能管理用咖啡佬的服务层的功能

下载后覆盖原来的hoshino文件夹，然后安装requirements.txt中的依赖就行了

## 更新
支持yobot缝合板管理,将nonebot_plugin.py替换yobot/src/client下的文件即可

## 网页端使用方法
1.从<https://github.com/wdvxdr1123/pcr-auth-vue/releases>下载编译好的前端

2.将前端放入auth/vue文件夹中

3.按照注释，修改__init__.py和web_server.py

4.打开机器人公网访问

####每次修改完网页端密码后必须清理浏览器缓存！！！

## 使用方法
所有指令与参数之间必须有<空格>(nonebot.on_command的特性...)
> 超级用户权限(私聊机器人)
1. 添加注册码 30 : 添加一个时长为30天的授权码
2. 查看注册码 : 查看当前所有授权码
3. 授权列表  : 查看当前授权情况

> 用户在群内注册方法
1. @机器人  注册  <注册码> <群号>
2.访问网页端注册
