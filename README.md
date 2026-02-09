# highTemp - ERA5-Land 数据驱动的复合高温干旱事件识别系统

## 项目简介

本系统基于 **ERA5-Land** 再分析数据集，面向中国九大流域，针对 1982–2022 年复合高温干旱灾害，提供从数据管理、指数计算到可视化分析的一整套功能。  
系统采用前后端分离架构，支持浏览器端交互式分析和后端批量栅格统计。

### 核心功能

- **SPI 指数分析**：标准化降水指数（SPI）的空间分布与时间序列统计。
- **SPEI 指数分析**：标准化降水蒸散指数（SPEI）的空间分布与时间序列统计。
- **HWMId 指数分析**：热浪指数（Heat Wave Magnitude Index daily）的空间分布与频次、日数统计。
- **复合灾害识别**：复合高温干旱事件的识别、强度统计及多年变化趋势分析。
- **灾害事件管理**：基于 CSV 的灾害事件数据的增删改查、筛选查询以及 ECDF（经验累积分布）分析。

### 技术架构

- **前端**：Vue.js 2.x、Vue Router、Vuex、Element UI、ECharts、`@arcgis/core`。
- **后端**：Flask、Flask-CORS、Pandas、GeoPandas、Shapely、Rasterio、NumPy。
- **数据格式**：CSV、Shapefile/GeoJSON、GeoTIFF。

---

## 环境要求

### 前端环境

- **Node.js**: v14.0.0 或更高版本
- **npm**: v6.0.0 或更高版本（或使用 yarn）

### 后端环境

- **Python**: 3.7 或更高版本（推荐 3.8+）
- **操作系统**: Windows / Linux / macOS

### Python 依赖包

| 包名 | 版本要求 | 说明 |
|------|---------|------|
| flask | >= 2.0.0 | Web框架 |
| flask-cors | >= 3.0.0 | 跨域支持 |
| pandas | >= 1.3.0 | 数据处理 |
| geopandas | >= 0.10.0 | 地理空间数据处理 |
| shapely | >= 1.8.0 | 几何对象操作 |
| numpy | >= 1.20.0 | 数值计算 |
| rasterio | >= 1.2.0 | 栅格数据处理 |

---

## 📦 安装步骤

### 1. 克隆或下载项目

```bash
# 如果使用 Git
git clone <repository-url>
cd highTemp

# 或直接解压项目压缩包到指定目录
```

### 2. 安装前端依赖

**重要提示**：项目实际位于 `highTemp` 子目录中，请先进入该目录。

```bash
# Windows PowerShell
cd highTemp
npm install

# Linux/macOS
cd highTemp
npm install
```

如果安装速度较慢，可以使用国内镜像：

```bash
npm install --registry=https://registry.npmmirror.com
```

### 3. 安装后端依赖

#### 方式一：使用 pip（推荐简单环境）

```bash
pip install flask flask-cors pandas geopandas shapely numpy rasterio
```

#### 方式二：使用 conda（推荐，特别是 Windows 系统）

```bash
# 创建 conda 环境（可选）
conda create -n hightemp python=3.8
conda activate hightemp

# 安装依赖
conda install -c conda-forge flask flask-cors pandas geopandas shapely numpy rasterio
```

**注意事项**：

- `geopandas` 和 `rasterio` 依赖 GDAL 库，在 Windows 上使用 conda 安装更稳定
- 如果使用 pip 安装遇到 GDAL 相关错误，请先安装 GDAL：
  ```bash
  # Windows (使用 conda)
  conda install -c conda-forge gdal
  
  # Linux
  sudo apt-get install gdal-bin libgdal-dev
  pip install GDAL
  ```

### 4. 配置数据路径

在运行系统前，需要配置后端的数据文件路径。推荐通过环境变量设置（`highTemp/server/config.py` 会读取并提供默认值）：

```bash
# ECDF分析相关路径
export HIGHTEMP_DATA_FILE_PATH="/path/to/mysql.csv"
export HIGHTEMP_BASIN_VECTOR_FILE_PATH="/path/to/China_nine_basin.shp"
export HIGHTEMP_BASIN_NAME_COLUMN="name"

# 栅格数据统计相关路径
export HIGHTEMP_RASTER_DATA_PATH="/path/to/compound_tif"
export HIGHTEMP_BASIN_SHP_PATH="/path/to/China_nine_basin.shp"

# HWMID数据路径
export HIGHTEMP_HWMID_COUNT_PATH="/path/to/hwmid_count"
export HIGHTEMP_HWMID_DAYS_PATH="/path/to/hwmid_days"

# 后端服务端口（可选）
export HIGHTEMP_API_PORT=5001
```

**配置说明**：

1. **HIGHTEMP_DATA_FILE_PATH**: CSV数据文件，应包含以下列：
   - `year`: 年份
   - `latitude`: 纬度
   - `longitude`: 经度
   - `count`: 事件计数
   - 其他相关字段

2. **HIGHTEMP_BASIN_VECTOR_FILE_PATH**: 流域边界矢量文件（Shapefile或GeoJSON），用于空间关联和统计分析

3. **HIGHTEMP_RASTER_DATA_PATH**: 复合高温干旱事件栅格数据目录，包含按年份命名的GeoTIFF文件，格式如：`Compound_1982.tif`

4. **HIGHTEMP_HWMID_COUNT_PATH**: HWMID次数栅格数据目录，文件格式如：`HWMID_1982.tif`

5. **HIGHTEMP_HWMID_DAYS_PATH**: HWMID日数栅格数据目录，文件格式如：`HWMID_1982.tif`

**数据文件要求**：

- CSV文件编码：UTF-8
- 栅格文件格式：GeoTIFF (.tif)
- 栅格文件命名：`前缀_年份.tif`（如 `Compound_1982.tif`）
- 年份范围：1982-2022
- 坐标系统：建议使用 WGS84 (EPSG:4326) 或 Albers等面积投影

---

## 🚀 运行项目

### 方式一：分别启动前后端（推荐开发环境）

#### 步骤 1：启动后端服务

打开第一个终端窗口：

```bash
# Windows PowerShell
cd highTemp\server
python main.py

# Linux/macOS
cd highTemp/server
python3 main.py
```

**成功启动标志**：
```
开始加载所有服务所需的数据...
数据加载完成，正在启动API服务...
 * Running on http://0.0.0.0:5001
```

后端服务将在 `http://0.0.0.0:5001` 启动。

#### 步骤 2：启动前端服务

打开第二个终端窗口：

```bash
# Windows PowerShell
cd highTemp
npm run serve

# Linux/macOS
cd highTemp
npm run serve
```

**成功启动标志**：
```
  App running at:
  - Local:   http://localhost:8080/
  - Network: http://192.168.x.x:8080/
```

前端开发服务器通常在 `http://localhost:8080` 启动（具体端口请查看终端输出）。

#### 步骤 3：访问应用

在浏览器中打开前端地址（通常是 `http://localhost:8080`），系统将自动跳转到登录页面。

**默认登录信息**（根据实际配置）：
- 用户名：根据系统配置
- 密码：根据系统配置

### 方式二：使用 app.py（备用方式）

如果项目中有独立的 `app.py` 文件，也可以使用：

```bash
cd highTemp/server
python app.py
```

---

## 📖 系统使用说明

### 主要功能模块

#### 1. SPI指数模块 (`/spi`)

- **功能**：展示标准化降水指数的空间分布和时间序列
- **操作**：选择年份和流域，查看SPI指数的空间分布图和统计图表

#### 2. SPEI指数模块 (`/spei`)

- **功能**：展示标准化降水蒸散指数的空间分布和时间序列
- **操作**：选择年份和流域，查看SPEI指数的空间分布图和统计图表

#### 3. HWMId指数模块 (`/hwmid`)

- **功能**：展示热浪指数的空间分布和统计分析
- **数据类型**：
  - HWMID次数：热浪事件发生次数
  - HWMID日数：热浪事件持续天数
- **操作**：选择流域和数据类型，查看统计图表和趋势分析

#### 4. 复合灾害识别模块 (`/high`)

- **功能**：复合高温干旱事件的识别和统计分析
- **操作**：
  - 选择流域进行统计分析
  - 查看多年统计趋势图（均值、最大值、最小值、中位数、标准差等）
  - 查看空间分布图

#### 5. 灾害事件管理模块 (`/data`)

- **功能**：事件数据的增删改查和高级分析
- **主要功能**：
  - **数据查询**：按年份、坐标、事件计数等条件查询
  - **数据管理**：新增、编辑、删除事件记录
  - **ECDF分析**：经验累积分布函数分析，支持：
    - 按流域筛选
    - 时间段对比（前后半段或指定年份区间）
    - 可视化展示
  - **数据导出**：导出为Excel或CSV格式

---

## 🔧 配置说明

### 后端配置

#### 修改服务端口

编辑 `highTemp/server/main.py`：

```python
# 修改端口号（默认5001）
app.run(host='0.0.0.0', port=5001, debug=True)
```

#### 修改CORS配置

如果需要限制跨域访问：

```python
from flask_cors import CORS

# 允许所有来源（开发环境）
CORS(app)

# 或限制特定来源（生产环境）
CORS(app, resources={r"/api/*": {"origins": "http://localhost:8080"}})
```

### 前端配置

#### 修改API地址

如果后端运行在不同地址或端口，请通过环境变量统一配置：

```bash
export VUE_APP_API_BASE_URL="http://your-backend-host:5001"
export VUE_APP_ARCGIS_BASE_URL="http://your-arcgis-host:6080/arcgis/rest/services"
```

然后重新启动前端服务即可生效。

#### 修改前端端口

编辑 `vue.config.js`（如需要）：

```javascript
const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 8080  // 修改为其他端口
  }
})
```

---

## 📊 API接口说明

### 1. 栅格数据统计接口

**端点**：`GET /api/raster_statistics`

**参数**：
- `region` (必需): 流域名称，如 "长江流域"、"黄河流域" 等
- `data_type` (可选): 数据类型
  - `compound`: 复合高温干旱事件（默认）
  - `hwmid_count`: HWMID次数
  - `hwmid_days`: HWMID日数

**示例**：
```
GET http://localhost:5001/api/raster_statistics?region=长江流域&data_type=compound
```

**响应**：
```json
{
  "长江流域": {
    "mean": {"1982": 1.23, "1983": 1.45, ...},
    "max": {"1982": 5.67, "1983": 6.12, ...},
    "min": {"1982": 0.01, "1983": 0.02, ...},
    "median": {...},
    "std": {...},
    "count": {...}
  },
  "process_time": "12.34秒",
  "success_rate": "41/41",
  "data_type": "compound"
}
```

### 2. ECDF分析接口

**端点**：`GET /api/ecdf_analysis`

**参数**：
- `basin` (可选): 流域名称，不提供则分析所有流域
- `interval` (可选): 时间段间隔（5/10/15/20年），0或不提供则按前后半段分割

**示例**：
```
GET http://localhost:5001/api/ecdf_analysis?basin=长江流域&interval=10
```

**响应**：
```json
{
  "period1_ecdf": [[0, 0.1], [1, 0.3], ...],
  "period2_ecdf": [[0, 0.05], [1, 0.25], ...],
  "period1_years": "1982-1991年 (前10年)",
  "period2_years": "2013-2022年 (后10年)"
}
```

### 3. 数据查询接口

**端点**：`GET /api/data`

**参数**：
- `page` (可选): 页码，默认1
- `limit` (可选): 每页数量，0表示返回全部

**示例**：
```
GET http://localhost:5001/api/data?page=1&limit=100
```

**响应**：
```json
[
  {
    "year": 1982,
    "latitude": 30.5,
    "longitude": 120.3,
    "count": 3,
    "basin": "长江流域",
    ...
  },
  ...
]
```

---

## 🐛 常见问题

### 1. 前端启动失败

**问题**：`npm run serve` 报错 "Missing script: serve"

**解决**：确保在正确的目录下运行命令：
```bash
# 检查当前目录是否有 package.json 和 src 文件夹
# 如果没有，需要进入 highTemp 子目录
cd highTemp
npm run serve
```

### 2. 后端启动失败 - 数据文件未找到

**问题**：`FileNotFoundError` 或数据加载失败

**解决**：
1. 检查 `main.py` 中的数据路径配置是否正确
2. 确认所有数据文件存在且路径正确
3. 检查文件权限

### 3. 后端启动失败 - 依赖包缺失

**问题**：`ModuleNotFoundError: No module named 'xxx'`

**解决**：
```bash
# 重新安装缺失的包
pip install <package-name>

# 或使用 conda
conda install -c conda-forge <package-name>
```

### 4. 栅格数据读取失败

**问题**：栅格统计返回空结果或错误

**解决**：
1. 检查栅格文件格式和命名规范
2. 确认栅格文件与流域边界文件的坐标系统一致
3. 检查栅格文件是否包含有效数据（非全NaN值）

### 5. 跨域问题

**问题**：前端无法访问后端API

**解决**：
1. 确认后端CORS配置正确
2. 检查后端服务是否正常运行
3. 确认前端API地址配置正确

### 6. 端口被占用

**问题**：端口5001或8080已被占用

**解决**：
- **后端**：修改 `main.py` 中的端口号
- **前端**：修改 `vue.config.js` 中的端口配置，或使用：
  ```bash
  npm run serve -- --port 8081
  ```

---

## 📝 开发说明

### 项目结构

```
highTemp/
├── public/                 # 静态资源文件
│   ├── index.html         # HTML模板
│   ├── *.geojson          # GeoJSON数据文件
│   └── *.png              # 图片资源
├── server/                 # 后端服务
│   ├── main.py            # 主程序（整合版）
│   ├── app.py             # ECDF分析服务
│   └── raster_statistics.py  # 栅格统计服务
├── src/                    # 前端源码
│   ├── components/        # Vue组件
│   │   ├── HomePage.vue   # 主页组件
│   │   ├── SpiShow.vue    # SPI指数组件
│   │   ├── SpeiShow.vue   # SPEI指数组件
│   │   ├── HwmidShow.vue  # HWMID指数组件
│   │   ├── HighShow.vue   # 复合灾害组件
│   │   ├── DataManage.vue # 数据管理组件
│   │   └── UserLogin.vue  # 登录组件
│   ├── router/            # 路由配置
│   ├── utils/             # 工具函数
│   ├── assets/            # 资源文件
│   ├── App.vue            # 根组件
│   └── main.js            # 入口文件
├── package.json           # 前端依赖配置
├── vue.config.js          # Vue CLI配置
└── README.md              # 项目说明文档
```

### 构建生产版本

#### 前端构建

```bash
cd highTemp
npm run build
```

构建产物将输出到 `dist/` 目录。

#### 部署建议

1. **前端部署**：
   - 将 `dist/` 目录部署到 Nginx、Apache 等 Web 服务器
   - 配置反向代理指向后端API

2. **后端部署**：
   - 使用 Gunicorn 或 uWSGI 作为 WSGI 服务器
   - 使用 Nginx 作为反向代理
   - 配置进程管理工具（如 Supervisor 或 systemd）

---



---

## 🔄 更新日志

### v0.1.0 (2024)
- 初始版本发布
- 实现SPI、SPEI、HWMID指数可视化
- 实现复合高温干旱事件识别
- 实现数据管理和ECDF分析功能

---

**最后更新**：2024年
