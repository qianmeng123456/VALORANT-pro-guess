# 🎯 无畏契约选手猜一猜

Valorant Pro Player Guessing Game

受 [guessassin.xyz](https://www.guessassin.xyz/) 和 LoLdle 启发制作的"猜选手"网页游戏。每天一个目标选手，根据多维度反馈提示缩小范围。

## 游戏玩法

1. 输入无畏契约职业选手 ID（如 `ZmjjKK`、`TenZ`、`f0rsakeN`）
2. 系统对比 6 个字段并给出颜色反馈：
   - 🟩 **绿色** = 完全匹配
   - 🟨 **黄色** = 部分匹配（代表英雄）
   - ⬛ **黑色** = 不匹配
   - 🔺 **蓝色** = 目标更大/更多
   - 🔻 **橙色** = 目标更小/更少
3. 根据提示不断缩小范围，直到猜中！

### 六大赛博字段

| 字段 | 说明 | 反馈 |
|------|------|------|
| ID | 选手游戏名 | 🟩/⬛ |
| 年龄 | 选手年龄 | 🟩/🔺/🔻 |
| 赛区 | Americas / EMEA / Pacific / China | 🟩/⬛ |
| 战队 | 当前所属战队 | 🟩/⬛ |
| 冠军数 | Masters + Champions 冠军总数 | 🟩/🔺/🔻 |
| 代表英雄 | 使用场次最多的 3 个英雄 | 🟩/🟨/⬛ |

## 数据说明

- **选手数量**：157 名（VCT 国际联赛 + 挑战者赛知名选手）
- **数据来源**：手动编译自 VLR.gg、Liquipedia 等公开数据源
- **更新时间**：2026 年 7 月
- **年龄数据**：手动维护，覆盖主流选手

## 项目结构

```
fuyiba/
├── data/
│   ├── processed/players.json   # 清洗后的选手数据
│   ├── processed/players.csv    # CSV 格式
│   └── scripts/
│       ├── build_dataset.py     # 数据集构建脚本
│       ├── scrape_vlr.py        # VLR.gg 爬虫脚本
│       └── download_agents.py   # 英雄头像下载脚本
├── src/
│   ├── index.html               # 主页面
│   ├── css/style.css            # 样式（暗色主题、响应式）
│   ├── js/
│   │   ├── data.js              # 数据加载
│   │   ├── game.js              # 游戏逻辑（比较、反馈）
│   │   ├── ui.js                # UI 渲染与交互
│   │   └── main.js              # 入口
│   ├── data/players.json        # 前端用选手数据
│   └── assets/agents/           # 27 个英雄头像
├── server.py                    # 本地测试服务器
└── README.md
```

## 本地运行

```bash
# 方法 1：使用 Python 服务器
python server.py
# 打开 http://localhost:8000

# 方法 2：使用任意 HTTP 服务器
cd src
python -m http.server 8000
# 或
npx serve .
```

> ⚠️ 由于使用了 `fetch()` 加载 JSON，必须通过 HTTP 服务器打开，不能直接用 `file://` 协议。

## 数据更新

```bash
# 重新构建选手数据集
python data/scripts/build_dataset.py

# 更新英雄头像
python data/scripts/download_agents.py

# 从 VLR.gg 爬取最新数据（需要网络）
python data/scripts/scrape_vlr.py
```

## 技术栈

- **纯前端**：HTML + CSS + JavaScript（无框架依赖）
- **数据**：从 Valorant API 获取英雄图标，从 VLR.gg 获取选手数据
- **设计**：暗色主题，适配桌面端和移动端

## 开发计划

- [x] 选手数据库（157 名主流选手）
- [x] 核心游戏逻辑（6 字段比较反馈）
- [x] 暗色主题 UI（自适应布局）
- [x] 英雄头像（27 个英雄齐全）
- [x] 每日挑战（日期种子）
- [x] 自动补全输入
- [x] 分享结果（Wordle 风格 emoji 格子）
- [ ] 更多选手数据
- [ ] 统计追踪
- [ ] PvP 对战模式

---

*本项目不隶属于 Riot Games 或 VLR.gg。所有数据仅供娱乐参考。*
