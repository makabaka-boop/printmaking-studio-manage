# 手工版画工作室管理平台

## 项目简介

这是一个为手工版画工作室设计的套色版次与纸张耗材管理平台，帮助工作室管理作品档案、版次信息、纸张库存和印制批次。

## 技术栈

### 后端
- FastAPI - 高性能Web框架
- SQLAlchemy - ORM框架
- SQLite - 轻量级数据库
- OpenPyXL - Excel文件处理

### 前端
- Vue 3 - 渐进式JavaScript框架
- Ant Design Vue - UI组件库
- ECharts - 数据可视化图表库
- Vite - 下一代前端构建工具

## 功能模块

### 1. 作品管理
- 维护作品档案：作品名、版种（木刻/铜版/丝网/石版）、成品尺寸、计划版数、签名规则
- 自动计算已印制版数和剩余可售版数
- 支持导出版次台账Excel

### 2. 版次管理
- 维护套色版次信息：色版序号、油墨配比备注、是否定稿
- 按作品筛选版次

### 3. 纸张库存
- 维护纸张信息：名称、克重、幅面、库存张数、单张成本
- 设置低库存预警阈值
- 低于阈值自动告警

### 4. 印制批次
- 记录每次印制信息：作品、日期、使用版次、试印/正印/废张数、纸张消耗
- 自动扣减纸张库存
- 自动计算废张率

### 5. 仪表盘
- 各版种作品数饼图
- 近三个月印制批次折线图
- 废张率排行柱状图
- 库存不足纸张预警列表

## 项目结构

```
printmaking-studio-manage/
├── backend/                 # 后端代码
│   ├── backend/
│   │   ├── database/        # 数据库配置
│   │   ├── models/          # 数据模型
│   │   ├── schemas/         # Pydantic模式
│   │   ├── routers/         # API路由
│   │   └── main.py          # 应用入口
│   ├── requirements.txt     # Python依赖
│   └── start.sh             # 后端启动脚本
├── frontend/                # 前端代码
│   ├── src/
│   │   ├── views/           # 页面组件
│   │   ├── components/      # 公共组件
│   │   ├── api/             # API调用
│   │   ├── router/          # 路由配置
│   │   └── main.js          # 入口文件
│   ├── package.json         # 前端依赖
│   └── vite.config.js       # Vite配置
└── README.md
```

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+

### 启动后端

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8031 --reload
```

后端API文档：http://localhost:8031/docs

### 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端访问地址：http://localhost:8831

### Windows用户

双击运行：
- `start-backend.bat` - 启动后端
- `start-frontend.bat` - 启动前端

## 使用说明

1. **创建作品**：在「作品管理」页面点击「新建作品」，填写作品信息
2. **添加版次**：在「版次管理」页面为作品添加各个色版
3. **录入纸张**：在「纸张库存」页面添加纸张种类和库存
4. **记录印制**：在「印制批次」页面记录每次印制的详细信息
5. **查看统计**：在「仪表盘」查看各项统计数据和图表

## 端口说明

- 后端服务：8031
- 前端服务：8831

## API接口

- `GET /api/artworks` - 获取作品列表
- `POST /api/artworks` - 创建作品
- `PUT /api/artworks/{id}` - 更新作品
- `DELETE /api/artworks/{id}` - 删除作品
- `GET /api/plates` - 获取版次列表
- `POST /api/plates` - 创建版次
- `GET /api/papers` - 获取纸张列表
- `POST /api/papers` - 添加纸张
- `GET /api/batches` - 获取批次列表
- `POST /api/batches` - 创建批次
- `GET /api/dashboard/stats` - 获取统计数据
- `GET /api/export/artwork/{id}` - 导出版次台账
