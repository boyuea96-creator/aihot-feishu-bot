#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI HOT 日报自动推送到飞书机器人
每天定时运行，获取 AI HOT 日报并推送到飞书群
"""

import os
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta

# 配置
AIHOT_API_BASE = "https://aihot.virxact.com/api/public"
FEISHU_WEBHOOK = os.environ.get("FEISHU_WEBHOOK", "")
UA = "aihot-skill/0.3.4 (+https://aihot.virxact.com/aihot-skill/)"

def get_aihot_daily():
    """获取 AI HOT 日报"""
    url = f"{AIHOT_API_BASE}/daily"
    
    req = urllib.request.Request(url)
    req.add_header("User-Agent", UA)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"error": "当天日报尚未生成"}
        raise
    except Exception as e:
        return {"error": str(e)}

def get_aihot_items(since_days=1, mode="selected", category=None, query=None):
    """获取 AI HOT 动态列表"""
    params = [f"mode={mode}"]
    
    # 时间窗
    since = (datetime.utcnow() - timedelta(days=since_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    params.append(f"since={since}")
    
    if category:
        params.append(f"category={category}")
    if query:
        params.append(f"q={query}")
    
    url = f"{AIHOT_API_BASE}/items?{'&'.join(params)}"
    
    req = urllib.request.Request(url)
    req.add_header("User-Agent", UA)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except Exception as e:
        return {"error": str(e)}

def format_daily_message(daily_data):
    """格式化日报消息为飞书卡片"""
    if "error" in daily_data:
        return format_error_message(daily_data["error"])
    
    date = daily_data.get("date", "未知日期")
    sections = daily_data.get("sections", [])
    
    if not sections:
        return format_error_message("日报内容为空")
    
    # 构建卡片内容
    elements = []
    
    # 日期标题
    elements.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": f"**📅 {date} AI HOT 日报**\n共 {sum(len(s.get('items', [])) for s in sections)} 条精选内容"
        }
    })
    
    elements.append({"tag": "hr"})
    
    # 遍历各分类
    for section in sections[:5]:  # 最多显示5个分类
        category_name = section.get("category", "其他")
        items = section.get("items", [])
        
        if not items:
            continue
        
        # 分类标题
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**{category_name}** ({len(items)}条)"
            }
        })
        
        # 显示前3条
        for item in items[:3]:
            title = item.get("title", "无标题")
            source = item.get("source", "")
            url = item.get("url", "")
            
            content = f"• [{title}]({url})"
            if source:
                content += f" _{source}_"
            
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": content
                }
            })
        
        if len(items) > 3:
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"_...还有 {len(items)-3} 条_"
                }
            })
        
        elements.append({"tag": "hr"})
    
    # 底部按钮
    elements.append({
        "tag": "action",
        "actions": [
            {
                "tag": "button",
                "text": {
                    "tag": "plain_text",
                    "content": "查看完整日报"
                },
                "url": f"https://aihot.virxact.com/daily/{date}",
                "type": "primary"
            },
            {
                "tag": "button",
                "text": {
                    "tag": "plain_text",
                    "content": "AI HOT 官网"
                },
                "url": "https://aihot.virxact.com",
                "type": "default"
            }
        ]
    })
    
    return {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "📰 AI HOT 日报"
                },
                "template": "blue"
            },
            "elements": elements
        }
    }

def format_items_message(items_data, title="AI HOT 动态"):
    """格式化动态列表消息"""
    if "error" in items_data:
        return format_error_message(items_data["error"])
    
    items = items_data.get("items", [])
    count = items_data.get("count", 0)
    
    if not items:
        return format_error_message("暂无动态")
    
    elements = []
    
    # 标题
    elements.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": f"**{title}**\n共 {count} 条动态"
        }
    })
    
    elements.append({"tag": "hr"})
    
    # 显示前10条
    for item in items[:10]:
        title_text = item.get("title", "无标题")
        source = item.get("source", "")
        url = item.get("url", "")
        summary = item.get("summary", "")
        
        content = f"**[{title_text}]({url})**"
        if source:
            content += f" _{source}_"
        if summary:
            # 截取摘要前100字
            summary_short = summary[:100] + "..." if len(summary) > 100 else summary
            content += f"\n{summary_short}"
        
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": content
            }
        })
        
        elements.append({"tag": "hr"})
    
    if count > 10:
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"_...还有 {count-10} 条_"
            }
        })
    
    # 底部按钮
    elements.append({
        "tag": "action",
        "actions": [
            {
                "tag": "button",
                "text": {
                    "tag": "plain_text",
                    "content": "查看完整内容"
                },
                "url": "https://aihot.virxact.com/all",
                "type": "primary"
            }
        ]
    })
    
    return {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "🔥 AI HOT 动态"
                },
                "template": "orange"
            },
            "elements": elements
        }
    }

def format_error_message(error_msg):
    """格式化错误消息"""
    return {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "⚠️ AI HOT 推送"
                },
                "template": "red"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**获取失败**\n{error_msg}\n\n可能是日报尚未生成（北京时间8点后生成），请稍后再试。"
                    }
                },
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "tag": "plain_text",
                                "content": "访问 AI HOT"
                            },
                            "url": "https://aihot.virxact.com",
                            "type": "default"
                        }
                    ]
                }
            ]
        }
    }

def send_to_feishu(message):
    """发送消息到飞书"""
    if not FEISHU_WEBHOOK:
        print("错误：未配置 FEISHU_WEBHOOK 环境变量")
        return False
    
    data = json.dumps(message).encode('utf-8')
    
    req = urllib.request.Request(
        FEISHU_WEBHOOK,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get("StatusCode") == 0:
                print("✓ 消息发送成功")
                return True
            else:
                print(f"✗ 发送失败: {result}")
                return False
    except Exception as e:
        print(f"✗ 发送异常: {e}")
        return False

def main():
    """主函数"""
    print(f"开始执行 AI HOT 日报推送 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 先尝试获取日报
    print("正在获取 AI HOT 日报...")
    daily_data = get_aihot_daily()
    
    if "error" in daily_data:
        print(f"日报获取失败: {daily_data['error']}，尝试获取精选动态...")
        # 如果日报没有，获取精选动态
        items_data = get_aihot_items(since_days=1, mode="selected")
        message = format_items_message(items_data, "今日 AI 圈精选动态")
    else:
        print("日报获取成功，正在格式化...")
        message = format_daily_message(daily_data)
    
    # 发送到飞书
    print("正在推送到飞书...")
    success = send_to_feishu(message)
    
    if success:
        print("推送完成！")
    else:
        print("推送失败，请检查配置")
    
    return success

if __name__ == "__main__":
    main()
