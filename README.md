# 🐍 PdkBot Python版 - 电商客服聚合接待工具
核心亮点：
全平台覆盖：深度整合拼多多、抖店、快手、京东等主流电商平台，无论客户来自何处，您都能轻松应对。
无限账号登录：灵活支持无限数量的店铺或客服账号同时登录，满足您多店铺、多团队的复杂管理需求，实现真正的无缝切换。
高效聚合接待：将所有平台的客户消息汇聚于一处，告别多窗口切换的困扰，显著提升客服响应速度和工作效率。
使用PyQt6框架开发。
> **注意**: 这是独立的Python实现版本，与主目录的C#版本完全分离。

## 📋 项目特性

✅ **已实现功能**
- 支持拼多多、抖店、快手、京东等平台
- 无限客服账号登录
- 实时新消息监控和提醒
- 现代化用户界面
- 系统托盘支持
- 弹窗通知系统
- 独立WebView配置文件管理

🚧 **开发中功能**
- 发送文字/图片/视频消息
- 催付卡片功能
- 核对卡片功能
- 客服转接
- 买家订单获取
- 店铺商品获取
- 知识库集成
- 转接人工客服功能

## 🔧 技术栈

- **Python 3.8+**
- **PyQt6** - 现代化GUI框架
- **PyQt6-WebEngine** - 网页嵌入支持
- **Requests** - HTTP请求库
- **BeautifulSoup4** - HTML解析
- **Plyer** - 跨平台通知

## 📦 安装说明

### 1. 环境要求
- Python 3.8或更高版本
- 支持的操作系统：Windows、macOS、Linux

### 2. 进入Python版本目录
```bash
cd pdkbot-python
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 运行应用
```bash
python main.py
```

## 🎯 使用指南

### 基本使用
1. 启动应用程序
2. 从左侧导航栏选择要使用的电商平台
3. 点击"添加新店铺"或选择已有店铺
4. 在弹出的WebView中登录对应平台的客服系统
5. 系统会自动监控新消息并显示通知

### 界面布局
- **左侧导航栏**：平台选择和功能导航
- **右侧主区域**：店铺选择和WebView标签页
- **状态栏**：显示当前状态和操作信息
- **系统托盘**：后台运行和快捷操作

### 多账号管理
- 每个平台支持添加多个客服账号
- 每个账号使用独立的WebView实例和配置文件
- 账号信息自动保存，下次启动时恢复

### 消息提醒
- 实时监控各平台的新消息
- 桌面弹窗通知
- 导航栏消息徽章提示
- 点击通知快速跳转到对应平台

## 📁 项目结构

```
pdkbot-python/
├── main.py                    # 应用程序入口
├── requirements.txt           # 依赖包列表
├── README.md                 # 本说明文档
├── src/                      # 源代码目录
│   ├── core/                 # 核心应用模块
│   │   ├── application.py    # 应用程序主类
│   │   └── __init__.py
│   ├── windows/              # 窗口模块
│   │   ├── main_window.py    # 主窗口
│   │   ├── tray_notification.py # 托盘通知
│   │   └── __init__.py
│   ├── pages/                # 页面模块
│   │   ├── platform_page.py  # 平台页面
│   │   └── __init__.py
│   ├── controls/             # 控件模块
│   │   ├── webview_widget.py # WebView控件
│   │   ├── shop_list_widget.py # 店铺列表控件
│   │   └── __init__.py
│   ├── db/                   # 数据管理模块
│   │   ├── entities.py       # 数据实体
│   │   ├── shop_manager.py   # 店铺管理器
│   │   └── __init__.py
│   ├── platform/             # 平台脚本
│   │   ├── pdd.js           # 拼多多脚本
│   │   ├── doudian.js       # 抖店脚本
│   │   ├── jd.js            # 京东脚本
│   │   ├── kuaishou.js      # 快手脚本
│   │   └── __init__.py
│   └── __init__.py
├── data/                     # 数据目录(自动创建)
│   ├── config.json          # 应用配置
│   └── shops.json           # 店铺数据
├── webview_profiles/         # WebView配置文件(自动创建)
└── assets/                   # 资源文件
    └── pdkbot.ico           # 应用图标
```

## ⚙️ 配置说明

### 应用配置 (data/config.json)
```json
{
  "auto_reply": false,
  "notification": true,
  "theme": "light",
  "platforms": {
    "pdd": {"enabled": true, "name": "拼多多"},
    "doudian": {"enabled": true, "name": "抖店"},
    "kuaishou": {"enabled": true, "name": "快手"},
    "jd": {"enabled": true, "name": "京东"}
  }
}
```

### 平台URL配置
- **拼多多**: `https://mms.pinduoduo.com/chat-merchant/index.html#/`
- **抖店**: `https://fxg.jinritemai.com/ffa/mshop/shopIndex`
- **快手**: `https://s.kwaixiaodian.com/zone/settles/chat`  
- **京东**: `https://dongdong.jd.com/`

## 🔧 开发说明

### 添加新平台支持
1. 在`src/platform/`目录下创建新的JavaScript脚本
2. 在`src/windows/main_window.py`中添加平台配置
3. 更新导航栏图标和名称

### JavaScript脚本开发
- 使用`window.pywebview.api.post_message()`与Python通信
- 支持的消息类型：`currentuser`、`newmessage`、`receiveMessage`
- 需要定期监控页面状态变化

### 自定义样式
- 使用Qt样式表(QSS)进行界面美化
- 支持深色主题和自定义主题
- 响应式布局设计

## 🐛 故障排除

### 常见问题

1. **WebView无法加载页面**
   - 检查网络连接
   - 确认平台URL是否正确
   - 检查WebEngine是否正确安装

2. **JavaScript脚本不执行**
   - 确认脚本文件存在
   - 检查控制台错误信息
   - 验证平台页面结构是否变化

3. **通知不显示**
   - 检查系统通知权限
   - 确认通知服务是否启用

4. **数据丢失**
   - 检查data目录权限
   - 确认JSON文件格式正确

5. **导入错误**
   - 确认在`pdkbot-python`目录中运行
   - 检查Python版本是否符合要求
   - 重新安装依赖：`pip install -r requirements.txt`


## 🛡 注意事项

⚠️ **重要提醒**
- 本项目仅供学习与交流使用
- 请遵守各平台的使用条款
- 鉴于项目特殊性，开发团队可能随时停止更新或删除项目

## 🤝 贡献

欢迎提交Issue和Pull Request来帮助改进！

---

**Made with ❤️ and Python** 
