# 个人云盘项目

这是一个基于 FastAPI 和 SQLite 的简单个人云盘项目，提供用户认证和基本的文件上传、下载、查看和删除功能。

## 主要特性

- **用户认证**: 使用 JWT Bearer Token 进行安全的用户注册和登录。
- **文件管理**:
  - 上传文件到服务器安全目录。
  - 查看已上传文件的列表。
  - 下载文件。
  - 删除不再需要的文件。
- **异步后端**: 基于 FastAPI 构建，性能高效。
- **数据库**: 使用 SQLAlchemy 和 SQLite，轻量且易于设置。
- **前端界面**: 提供一个简单的 HTML/CSS/JavaScript 界面与后端 API 进行交互。
- **配置管理**: 使用 Pydantic 和 `.env` 文件轻松管理应用配置。
- **日志记录**: 集成 Loguru 进行详细的日志记录，便于调试和监控。

## 技术栈

- **后端**:
  - FastAPI
  - SQLAlchemy
  - Pydantic (用于配置管理和数据验证)
  - Uvicorn (ASGI 服务器)
  - python-jose 和 passlib (用于 JWT 和密码哈希)
  - Loguru (用于日志记录)
- **数据库**:
  - SQLite
- **前端**:
  - HTML
  - CSS
  - JavaScript

## 项目结构

```
Disk/
├── app/                  # 后端 FastAPI 应用
│   ├── routers/          # API 路由 (files.py, users.py)
│   ├── __init__.py
│   ├── config.py         # 配置管理
│   ├── crud.py           # 数据库操作
│   ├── database.py       # 数据库连接和会话
│   ├── logging_config.py # 日志配置
│   ├── main.py           # 应用入口
│   ├── models.py         # SQLAlchemy 模型
│   ├── schemas.py        # Pydantic 模型
│   └── security.py       # 安全相关 (密码, JWT)
├── frontend/             # 前端文件
│   ├── css/
│   ├── js/
│   ├── index.html
│   └── login.html
├── safe_uploads/         # 上传文件存储目录
├── .env                  # 环境变量文件 (需自行创建)
└── requirements.txt      # Python 依赖
```

## 安装与设置

1.  **克隆仓库**
    ```bash
    git clone <repository-url>
    cd Disk
    ```

2.  **创建并激活虚拟环境**
    ```bash
    # Windows
    python -m venv .venv
    .venv\Scripts\activate

    # macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```

4.  **创建 `.env` 文件**

    在项目根目录下创建一个名为 `.env` 的文件，并添加以下内容。`SECRET_KEY` 可以是一个随机的字符串。

    ```env
    SECRET_KEY="YOUR_SUPER_SECRET_KEY"
    ALGORITHM="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```

## 运行项目

在项目根目录下运行以下命令来启动应用：

```bash
uvicorn app.main:app --reload
```

应用将在 `http://127.0.0.1:8000` 上可用。

## 如何使用

1.  **访问登录/注册页面**:
    在浏览器中打开 `http://127.0.0.1:8000/`。

2.  **注册新用户**:
    在登录页面，你可以找到注册的链接或表单来创建一个新账户。

3.  **登录**:
    使用你注册的用户名和密码登录。成功后，你将被重定向到文件管理页面。

4.  **文件管理**:
    - **上传**: 点击“选择文件”并“上传”来添加新文件。
    - **查看**: 页面会显示你所有文件的列表。
    - **下载/删除**: 点击相应文件旁边的按钮进行操作。

## API 端点

应用启动后，你可以在 `http://127.0.0.1:8000/docs` 访问自动生成的 Swagger UI 文档，其中包含了所有 API 端点的详细信息和交互式测试工具。

### 主要端点

- `POST /users/register`: 注册新用户。
- `POST /users/token`: 用户登录，获取 access token。
- `POST /files/upload`: (需认证) 上传文件。
- `GET /files/`: (需认证) 获取当前用户的文件列表。
- `DELETE /files/{file_unique_id}`: (需认证) 删除指定的文件。
- `GET /files/download/{file_unique_id}`: 下载文件。
- `GET /files/view/{file_unique_id}`: 查看文件的元数据。
