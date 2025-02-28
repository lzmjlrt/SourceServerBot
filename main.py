from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
import a2s
import json
import os
import re
import asyncio
# 注册插件
@register(name="SourceServerBot", description="V社服务器状态查询机器人", version="0.1", author="SLAR_Edge")
class MyPlugin(BasePlugin):

    # 插件加载时触发
    def __init__(self, host: APIHost):
        self.ap = host
        self.servers = {}  # 存储服务器信息 {名称: {"ip": ip, "port": port}}
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(script_dir, "servers_config.json")  # 配置文件路径
        #self.config_path = "servers_config.json"
        self.admin_ids = ["1010553892", "1733669112","1207794441"]  # 将这里的QQ号替换为实际的管理员QQ号

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
            self.ap.logger.info("当前路径为:"+self.config_path)
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
        
        # 检查是否为添加服务器命令开头
        if msg.startswith("!add ") and sender_id in self.admin_ids:
            # 正确格式的添加命令
            add_match = re.match(r'^!add\s+([\w\.]+):(\d+)\s+(.+)$', msg)
            if add_match:
                ip, port, name = add_match.groups()
                port = int(port)
                
                # 保存服务器信息
                self.servers[name] = {"ip": ip, "port": port}
                
                # 保存配置到文件
                if self.save_config():
                    reply_msg = f"服务器 {name} ({ip}:{port}) 已添加成功！"
                    self.ap.logger.info("添加服务器: " + reply_msg)
                else:
                    reply_msg = "服务器添加失败，无法保存配置。"
                    self.ap.logger.info("添加服务器失败")
                
                ctx.add_return("reply", [reply_msg])
                ctx.prevent_default()
                return
            
            # 检查是否缺少服务器名称
            ip_port_match = re.match(r'^!add\s+([\w\.]+):(\d+)\s*$', msg)
            if ip_port_match:
                ctx.add_return("reply", ["❌ 添加失败：缺少服务器名称\n正确格式：!add IP:端口 服务器名称"])
                ctx.prevent_default()
                return
            
            # 其他格式错误的情况
            ctx.add_return("reply", ["❌ 添加失败：命令格式错误\n正确格式：!add IP:端口 服务器名称\n例如：!add 192.168.1.100:27015 我的服务器"])
            ctx.prevent_default()
            return
        
        del_match = re.match(r'^!del\s+(.+)$', msg)
        if del_match and sender_id in self.admin_ids:
            server_name = del_match.group(1).strip()
            
            if server_name not in self.servers:
                ctx.add_return("reply", [f"未找到名为 {server_name} 的服务器配置"])
                ctx.prevent_default()
                return
            
            # 删除服务器信息
            del self.servers[server_name]
            
            # 保存配置到文件
            if self.save_config():
                reply_msg = f"服务器 {server_name} 已成功删除！"
            else:
                reply_msg = "服务器删除失败，无法保存配置。"
            
            ctx.add_return("reply", [reply_msg])
            ctx.prevent_default()
            return
        
        # 处理查看所有服务器命令 (!servers)
        if msg == "!servers":
            if not self.servers:
                ctx.add_return("reply", ["当前没有配置任何服务器。"])
                ctx.prevent_default()
                return
            
            # 构建回复信息
            reply_lines = ["📋 服务器列表："]
            
            # 对每个服务器进行状态检测
            for name, info in self.servers.items():
                server_addr = (info["ip"], info["port"])
                status = "✅ 在线"
                
                try:
                    # 设置超时时间为2秒
                    server_info = await asyncio.wait_for(
                        asyncio.to_thread(a2s.info, server_addr), 
                        timeout=2.0
                    )
                    players_count = f"{server_info.player_count}/{server_info.max_players}"
                except asyncio.TimeoutError:
                    status = "⏱️ 超时"
                    players_count = "N/A"
                except Exception:
                    status = "❌ 离线"
                    players_count = "N/A"
                
                reply_lines.append(f"{name} - {info['ip']}:{info['port']} - {status} - 玩家：{players_count}")
            
            ctx.add_return("reply", ["\n".join(reply_lines)])
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