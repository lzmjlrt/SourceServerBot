# SourceServerBot

<!--
## 插件开发者详阅

### 开始

此仓库是 LangBot 插件模板，您可以直接在 GitHub 仓库中点击右上角的 "Use this template" 以创建你的插件。  
接下来按照以下步骤修改模板代码：

#### 修改模板代码

- 修改此文档顶部插件名称信息
- 将此文档下方的`<插件发布仓库地址>`改为你的插件在 GitHub· 上的地址
- 补充下方的`使用`章节内容
- 修改`main.py`中的`@register`中的插件 名称、描述、版本、作者 等信息
- 修改`main.py`中的`MyPlugin`类名为你的插件类名
- 将插件所需依赖库写到`requirements.txt`中
- 根据[插件开发教程](https://docs.langbot.app/plugin/dev/tutor.html)编写插件代码
- 删除 README.md 中的注释内容


#### 发布插件

推荐将插件上传到 GitHub 代码仓库，以便用户通过下方方式安装。   
欢迎[提issue](https://github.com/RockChinQ/LangBot/issues/new?assignees=&labels=%E7%8B%AC%E7%AB%8B%E6%8F%92%E4%BB%B6&projects=&template=submit-plugin.yml&title=%5BPlugin%5D%3A+%E8%AF%B7%E6%B1%82%E7%99%BB%E8%AE%B0%E6%96%B0%E6%8F%92%E4%BB%B6)，将您的插件提交到[插件列表](https://github.com/stars/RockChinQ/lists/qchatgpt-%E6%8F%92%E4%BB%B6)

下方是给用户看的内容，按需修改
-->

## 安装

配置完成 [LangBot](https://github.com/RockChinQ/LangBot) 主程序后使用管理员账号向机器人发送命令即可安装：

```
!plugin get <你的插件发布仓库地址>
```
或查看详细的[插件安装说明](https://docs.langbot.app/plugin/plugin-intro.html#%E6%8F%92%E4%BB%B6%E7%94%A8%E6%B3%95)

## 使用

<!-- 插件开发者自行填写插件使用说明 -->
### 插件简介
SourceServerBot 是一个用于查询和监控 Valve Source 引擎游戏服务器(如 CS:GO、GMOD、TF2 等)状态的机器人插件。它可以显示服务器基本信息、当前地图、在线人数以及详细的玩家列表。

### 配置
main.py中的self.admin_ids列表中填入你的QQ号，以便使用管理员命令。例如
```python
self.admin_ids = [123456789] #将里面的123456789改为你的QQ号
```

## 命令说明
### 管理员命令
* 添加服务器
格式：`!add <服务器名称> <服务器地址>:<服务器端口> <名称>`
例如：`!add 192.168.31.111:27015 Sandbox服务器`

* 删除服务器
格式：`!del <服务器名称>`
例如：`!del Sandbox服务器`

### 用户命令
* 查询服务器列表
格式：`!servers`

## 数据存储
所有服务器信息将存储在`severs_config.json`文件中，如果需要备份或迁移数据，请将此文件一并拷贝。


## 注意事项
1. 本插件依赖python-a2s库，可能存在一些小bug，如果有问题请提交issue。
2. 本插件仅支持Valve Source引擎游戏服务器，不支持其他类型的服务器。
3. 本插件不支持查询非公网IP的服务器，如果需要查询请使用公网IP。
4. 目前只会显示前十名玩家的信息，剩余玩家会显示为`...以及其他 xx`。

## Todo List
* 后续加入服务器管理功能，如重启服务器、踢出玩家
