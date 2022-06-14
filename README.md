# askMe
匿名提问箱

## 准备工作

准备一个 Mastodon/Pleroma 上的bot帐号, 创建应用

+ 权限范围:`read:accounts` `read:statuses` `write:statuses`

+ 重定向 URI: \<WORK\_URL\>/askMe/auth

## 部署

`python3 -m pip install -r requirement.txt`

创建config.py

`python3 prepare.py`

+ 开发环境: 
   
   `python3 ask.py`

+ 生产环境

  建议使用uwsgi
    
  建议 `$ uwsgi --touch-reload=ask.ini ask.ini &`, 或使用emperor管理
