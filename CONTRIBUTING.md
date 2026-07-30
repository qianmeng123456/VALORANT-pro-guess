# 贡献指南

感谢你对「无畏契约选手猜一猜」的关注！欢迎各种形式的贡献——数据纠错、新功能、Bug 修复、文档改进等。

## 🐛 报告问题

发现 Bug 或数据错误？请通过以下方式报告：

1. 在游戏中点击 **📝 反馈** 按钮（会自动跳转到 GitHub Issues）
2. 或直接到 [Issues 页面](https://github.com/qianmeng123456/VALORANT-pro-guess/issues/new) 新建 Issue

请尽量包含：
- 选手 ID 和具体错误字段
- 正确的信息及来源（截图/链接）
- 操作复现步骤（如果是 Bug）

## 🔧 本地开发

### 环境要求

- 任意现代浏览器（Chrome / Firefox / Edge）
- Python 3.x（用于本地服务器）或 Node.js（用于 `npx serve`）

### 快速开始

```bash
# 克隆项目
git clone https://github.com/qianmeng123456/VALORANT-pro-guess.git
cd VALORANT-pro-guess

# 启动本地服务器
python server.py
# 打开 http://localhost:8000
```

由于使用了 `fetch()` 加载选手数据，必须通过 HTTP 服务器访问，不能直接用 `file://` 协议。

### 项目结构

```
src/
├── index.html        # 主页面
├── css/style.css     # 样式（暗色主题、响应式）
├── js/
│   ├── data.js       # 数据加载
│   ├── game.js       # 游戏逻辑（比较、反馈）
│   ├── ui.js         # UI 渲染与交互
│   ├── stats.js      # 战绩统计（localStorage）
│   └── main.js       # 入口
├── data/players.json # 选手数据
└── assets/agents/    # 英雄头像
```

### 更新选手数据

```bash
# 构建选手数据集（需在项目根目录运行）
python data/scripts/build_dataset.py

# 更新英雄头像
python data/scripts/download_agents.py

# 从 VLR.gg 爬取最新数据
python data/scripts/scrape_vlr.py
```

构建完成后，将生成的 `data/processed/players.json` 复制到 `src/data/players.json`。

## 📝 代码风格

- **JavaScript**：ES6+，无框架依赖，无构建步骤
- **CSS**：使用 CSS 自定义属性（variables），保持暗色主题风格
- **数据**：遵守 `build_dataset.py` 中的数据结构模式
- 保持现有命名规范和注释风格

## 🔄 提交 PR

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feat/your-feature`
3. 提交改动：`git commit -m "feat: add xxx"`
4. 推送到你的仓库：`git push origin feat/your-feature`
5. 创建 Pull Request

PR 合并前请确保：
- [ ] 功能在本地测试通过
- [ ] 无控制台报错
- [ ] 截图已附上（如果是 UI 改动）
- [ ] 相关 Issue 已关联

## 📋 Issue 标签说明

| 标签 | 用途 |
|------|------|
| `bug` | 功能异常 |
| `data` | 选手数据错误 |
| `enhancement` | 功能建议 |
| `good first issue` | 适合新手的任务 |

## 🙏 致谢

每一位贡献者都会出现在 [README](./README.md) 的致谢列表中！

---

*本项目不隶属于 Riot Games 或 VLR.gg。所有数据仅供娱乐参考。*
