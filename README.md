# AI HOT 日报飞书推送机器人

自动获取 AI HOT 日报并推送到飞书群。

## 功能

- 每天 8:00（北京时间）自动推送
- 支持 GitHub Actions 云端运行（无需本地电脑开机）
- 支持手动触发推送

## 文件结构

```
aihot-feishu-bot/
├── fetch_and_push.py      # 主推送脚本
├── .github/
│   └── workflows/
│       └── daily_push.yml # GitHub Actions 配置
└── README.md              # 说明文档
```

## 使用方法

### 1. 创建 GitHub 仓库

1. 登录 GitHub
2. 创建新仓库（名称如 `aihot-feishu-bot`）
3. 上传本项目文件

### 2. 配置飞书 Webhook Secret

1. 进入仓库 Settings → Secrets and variables → Actions
2. 点击 "New repository secret"
3. Name: `FEISHU_WEBHOOK`
4. Value: 您的飞书机器人 Webhook 地址
5. 点击 "Add secret"

### 3. 启用 GitHub Actions

1. 进入仓库 Actions 页面
2. 如果需要启用，点击 "I understand my workflows, go ahead and enable them"

### 4. 手动测试

1. 进入 Actions → AI HOT Daily Push
2. 点击 "Run workflow" → "Run workflow"
3. 查看飞书群是否收到消息

## 注意事项

- 飞书机器人 Webhook 地址需要保密
- 推送时间为北京时间 8:00（AI HOT 日报生成时间）
- 如果日报未生成，会推送精选动态作为替代

## 数据来源

- [AI HOT](https://aihot.virxact.com) - AI 资讯情报站
