from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
import a2s
import json
import os
import re

# 注册插件
@register(name="SourceServerBot", description="V社服务器状态查询机器人", version="0.1", author="SLAR_Edge")
class MyPlugin(BasePlugin):

    # 插件加载时触发
    def __init__(self, host: APIHost):
        self.ap = host
        self.servers = {}  # 存储服务器信息 {名称: {"ip": ip, "port": port}}
        self.config_path = "servers_config.json"
        self.admin_ids = ["管理员QQ号1", "管理员QQ号2"]  # 将这里的QQ号替换为实际的管理员QQ号

    # 异步初始化
    async def initialize(self):
        # 加载服务器配置
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.servers = json.load(f)
                self.ap.logger.info(f"已加载 {len(self.servers)} 个服务器配置")
            except Exception as e:
                self.ap.logger.error(f"加载服务器配置失败: {e}")
        else:
            self.ap.logger.info("未找到服务器配置文件，将创建新配置")

    # 保存服务器配置
    def save_config(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.servers, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self.ap.logger.error(f"保存服务器配置失败: {e}")
            return False

    # 当收到个人消息时触发
    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message  # 这里的 event 即为 PersonNormalMessageReceived 的对象
        if msg == "hello":  # 如果消息为hello
            # 输出调试信息
            self.ap.logger.debug("hello, {}".format(ctx.event.sender_id))
            # 回复消息 "hello, <发送者id>!"
            ctx.add_return("reply", ["hello, {}!".format(ctx.event.sender_id)])
            # 阻止该事件默认行为（向接口获取回复）
            ctx.prevent_default()

    # 当收到群消息时触发
    @handler(GroupNormalMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message
        sender_id = ctx.event.sender_id
        
        # 处理添加服务器命令 (!add IP:端口 名称)
        add_match = re.match(r'^!add\s+([\w\.]+):(\d+)\s+(.+)$', msg)
        if add_match and sender_id in self.admin_ids:
            ip, port, name = add_match.groups()
            port = int(port)
            
            # 保存服务器信息
            self.servers[name] = {"ip": ip, "port": port}
            
            # 保存配置到文件
            if self.save_config():
                reply_msg = f"服务器 {name} ({ip}:{port}) 已添加成功！"
            else:
                reply_msg = "服务器添加失败，无法保存配置。"
                
            ctx.add_return("reply", [reply_msg])
            ctx.prevent_default()
            return
        
        # 处理查询服务器命令 (!cx 名称)
        if msg.startswith("!cx "):
            server_name = msg[4:].strip()
            
            if server_name not in self.servers:
                ctx.add_return("reply", [f"未找到名为 {server_name} 的服务器配置"])
                ctx.prevent_default()
                return
                
            server_info = self.servers[server_name]
            server_addr = (server_info["ip"], server_info["port"])
            
            try:
                info = a2s.info(server_addr)
                players = a2s.players(server_addr)
                
                # 构建回复信息
                reply_lines = [
                    f"✅ 服务器: {info.server_name}",
                    f"🗺️ 地图: {info.map_name}",
                    f"👥 玩家: {info.player_count}/{info.max_players}",
                    f"🎮 游戏: {info.game}"
                ]
                
                # 添加玩家列表
                if players:
                    reply_lines.append("\n🔹 在线玩家:")
                    # 按游戏时间排序
                    sorted_players = sorted(players, key=lambda p: p.duration, reverse=True)
                    for i, player in enumerate(sorted_players, 1):
                        if i > 10:  # 最多显示10名玩家
                            remaining = len(sorted_players) - 10
                            reply_lines.append(f"...以及其他 {remaining} 名玩家")
                            break
                        reply_lines.append(f"{i}. {player.name} - {int(player.duration//60)}分钟")
                
                ctx.add_return("reply", ["\n".join(reply_lines)])
            except Exception as e:
                ctx.add_return("reply", [f"查询服务器 {server_name} 失败: {str(e)}"])
            
            ctx.prevent_default()
            return
        


    # 插件卸载时触发
    def __del__(self):
        pass