前端：

主要包含了3个组件：
1.coze的chatsdk内置的嵌入聊天框（需要用后端指定的user和conversation初始化）
2.制作一个Bug信息表单，表单会显示ai整理的bug内容，用户可以手动调整内容，手动发起提交。
3.一个工具箱，可以手动提取本地日志，服务器远端日志，截屏，录像等功能。

后端：
使用Coze API SDK for Python框架， 通过OAuth JWT 方式实现授权与 OpenAPI 鉴权
通过Access Token的直接获取会话信心


远端服务：
通过OpenAPI提供的各类接口，LLM的agent实际运行在此