# askMe
匿名提问箱

### 准备工作

准备一个 Mastodon/Pleroma 上的bot帐号, 创建应用

+ 权限范围:`read:accounts` `read:statuses` `write:statuses`

+ 重定向 URI: \<WORK\_URL\>/askMe/auth

### 部署

0. (可选) 创建venv环境

  ```console
  $ python -m venv venv
  $ source venv/bin/activate
  ```

1. 安装依赖

   `pip install -r requirements.txt`

2. 创建config.py, 可参考config.example\*.py

3. 第一次运行前的准备工作

   `python prepare.py`

   会创建数据库,以及根据config.py生成index.html

4. 运行

  + 开发环境:

    `python ask.py`

  + 生产环境

    建议使用uwsgi

    `$ uwsgi --touch-reload=ask.ini ask.ini &`, 或使用emperor管理

    uwsgi 与 nginx 配置可参考 example\_dist
