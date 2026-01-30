# app.py
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import geopandas as gpd  # 用于空间分析
from shapely.geometry import Point  # 用于创建点
import numpy as np
import os
import traceback  # 用于打印详细错误

app = Flask(__name__)
# 允许所有来源的跨域请求，生产环境中应配置更严格的规则
CORS(app, resources={r"/api/*": {"origins": "*"}})

# --- 配置常量 ---
# 1. CSV 数据文件路径
DATA_FILE_PATH = r'C:\Users\lenovo\Desktop\mysql.csv'
# 2. 流域边界矢量文件路径 (Shapefile 或 GeoJSON)
BASIN_VECTOR_FILE_PATH = r'F:\DATA\复合高温干旱事件识别系统-数据处理成果\1982-2022干旱指数预处理后数据及输出结果\九大流域\China_nine_basin.shp'  # <--- 修改这里
# 3. 流域矢量文件中包含流域名称的列名
BASIN_NAME_COLUMN = 'name'  # <--- 修改这里 (例如 'name', 'Basin_Name', '流域名'等)

# 全局变量存储加载的数据
data_df = None
basins_gdf = None  # 流域 GeoDataFrame


# --- 数据加载和空间关联函数 ---
def load_data():
    """加载 CSV 数据，加载流域边界，并执行空间关联以添加准确的流域信息"""
    global data_df, basins_gdf
    print(f"开始加载数据...")

    # 1. 加载流域边界矢量数据
    print(f"加载流域边界文件: '{BASIN_VECTOR_FILE_PATH}'...")
    if not os.path.exists(BASIN_VECTOR_FILE_PATH):
        print(f"错误: 流域边界文件 '{BASIN_VECTOR_FILE_PATH}' 未找到。无法进行流域关联。")
        basins_gdf = None
    else:
        try:
            basins_gdf = gpd.read_file(BASIN_VECTOR_FILE_PATH)
            print(f"流域边界加载成功。共 {len(basins_gdf)} 个特征。")

            if BASIN_NAME_COLUMN not in basins_gdf.columns:
                print(f"错误: 流域边界文件中未找到指定的流域名称列 '{BASIN_NAME_COLUMN}'。")
                print(f"可用列: {basins_gdf.columns.tolist()}")
                basins_gdf = None  # 标记为不可用
            else:
                print(f"流域边界数据的 CRS: {basins_gdf.crs}")
                # 可选检查几何类型
                # if not all(basins_gdf.geometry.geom_type.isin(['Polygon', 'MultiPolygon'])):
                #     print("警告：流域边界文件包含非多边形几何对象。")
                # 预处理流域名称，去除可能的空格
                basins_gdf[BASIN_NAME_COLUMN] = basins_gdf[BASIN_NAME_COLUMN].str.strip()


        except Exception as e:
            print(f"加载流域边界文件 '{BASIN_VECTOR_FILE_PATH}' 时出错: {e}")
            traceback.print_exc()
            basins_gdf = None

    # 2. 加载 CSV 数据
    print(f"加载 CSV 数据文件: '{DATA_FILE_PATH}'...")
    if not os.path.exists(DATA_FILE_PATH):
        print(f"错误: CSV 数据文件 '{DATA_FILE_PATH}' 未找到。")
        data_df = pd.DataFrame()
        return

    try:
        # 尝试使用UTF-8编码读取CSV文件
        temp_df = pd.read_csv(DATA_FILE_PATH, encoding='utf-8', low_memory=False)
        print(f"CSV 文件加载成功。原始列名: {temp_df.columns.tolist()}")

        required_cols = {'year', 'coordinates', 'count'}
        current_cols_lower = {col.lower() for col in temp_df.columns}
        missing_cols = required_cols - current_cols_lower
        if missing_cols:
            print(f"错误: CSV 文件缺少必要的列: {missing_cols}")
            data_df = pd.DataFrame()
            return

        print("预处理 CSV 数据...")
        temp_df['year'] = pd.to_numeric(temp_df['year'], errors='coerce')
        temp_df['count'] = pd.to_numeric(temp_df['count'], errors='coerce')
        original_rows = len(temp_df)
        temp_df.dropna(subset=['year', 'count', 'coordinates'], inplace=True)
        cleaned_rows = len(temp_df)
        if original_rows > cleaned_rows:
            print(f"移除了 {original_rows - cleaned_rows} 行，因为 'year', 'count' 或 'coordinates' 包含无效/空值。")
        if cleaned_rows == 0:
            print("错误：预处理后没有有效的数值数据行。")
            data_df = pd.DataFrame()
            return
        temp_df['year'] = temp_df['year'].astype(int)

        # 3. 执行空间关联 (如果流域数据加载成功)
        if basins_gdf is not None:
            print("开始执行空间关联以分配流域...")
            try:
                # !!! 确认坐标格式 "纬度,经度" !!! Point(经度, 纬度)
                def parse_coords(coord_str):
                    try:
                        # 移除可能的额外字符并分割
                        parts = str(coord_str).strip().split(',')
                        if len(parts) == 2:
                            lat, lon = map(float, parts)
                            return Point(lon, lat)
                        else:
                            # print(f"无法解析坐标: {coord_str}") # 太多日志会刷屏
                            return None
                    except (ValueError, TypeError):
                        # print(f"无法解析坐标: {coord_str}") # 太多日志会刷屏
                        return None

                geometry = temp_df['coordinates'].apply(parse_coords)
                # 创建点 GeoDataFrame，假设原始坐标是 WGS84
                points_gdf = gpd.GeoDataFrame(temp_df, geometry=geometry, crs="EPSG:4326")
                points_gdf = points_gdf[points_gdf.geometry.notna()]  # 移除无效点

                if len(points_gdf) == 0:
                    print("错误：所有坐标都无法解析为有效的点几何对象。")
                    temp_df['basin'] = '解析错误'
                else:
                    print(f"成功创建 {len(points_gdf)} 个点几何对象。CRS: {points_gdf.crs}")

                    # 统一 CRS
                    if points_gdf.crs != basins_gdf.crs:
                        print(f"转换坐标点 CRS 以匹配流域边界 CRS ({basins_gdf.crs})...")
                        try:
                            points_gdf = points_gdf.to_crs(basins_gdf.crs)
                            print(f"坐标点 CRS 已转换为: {points_gdf.crs}")
                        except Exception as crs_e:
                            print(f"错误：转换 CRS 失败: {crs_e}")
                            temp_df['basin'] = 'CRS错误'
                            # 标记错误，但不中断，后续流程会处理'basin'列不存在的情况

                    # 只有在 CRS 成功转换（或原本就一致）的情况下才执行 sjoin
                    if 'basin' not in temp_df.columns or temp_df['basin'].iloc[0] != 'CRS错误':
                        print("执行空间连接 (point in polygon)...")
                        # 使用 'intersects' 可能比 'within' 更稳健，可以捕获边界上的点
                        joined_gdf = gpd.sjoin(points_gdf, basins_gdf[[BASIN_NAME_COLUMN, 'geometry']],
                                               how='left', predicate='intersects')
                        print("空间连接完成。")

                        # 处理重复匹配 (如果一个点落在多个多边形边界上)
                        joined_gdf = joined_gdf[~joined_gdf.index.duplicated(keep='first')]

                        # 获取空间连接结果中的流域列名 (可能是 'NAME_right')
                        basin_col_in_joined = BASIN_NAME_COLUMN
                        if f"{BASIN_NAME_COLUMN}_right" in joined_gdf.columns:
                            basin_col_in_joined = f"{BASIN_NAME_COLUMN}_right"
                        elif BASIN_NAME_COLUMN not in joined_gdf.columns:
                            print(f"警告：空间连接结果中未找到流域名称列 '{BASIN_NAME_COLUMN}' 或 '{BASIN_NAME_COLUMN}_right'。")
                            temp_df['basin'] = '关联失败'
                        else:
                            # 合并流域名称到原 DataFrame
                            temp_df['basin'] = temp_df.index.map(joined_gdf[basin_col_in_joined])
                            temp_df['basin'].fillna('未知流域', inplace=True)  # 处理未匹配到的点
                            print("流域名称已成功合并。")


            except Exception as sj_e:
                print(f"空间关联过程中发生错误: {sj_e}")
                traceback.print_exc()
                temp_df['basin'] = '关联错误'

        else:
            print("警告: 未加载流域边界数据，无法执行空间关联。")
            temp_df['basin'] = '未知流域'

        # 最终赋值给全局变量
        data_df = temp_df
        if 'basin' in data_df.columns:
            print("最终流域分布统计:\n", data_df['basin'].value_counts())
        print(f"数据加载和处理完成，共 {len(data_df)} 条有效记录。")
        print("数据预览 (含流域信息):\n", data_df[['year', 'coordinates', 'count', 'basin']].head())


    except Exception as e:
        print(f"加载或处理 CSV 文件 '{DATA_FILE_PATH}' 时发生严重错误: {e}")
        traceback.print_exc()
        data_df = pd.DataFrame()


# --- ECDF 计算函数 ---
def calculate_ecdf_data(values_series):
    """计算给定 Pandas Series 的 ECDF"""
    # ... (与之前版本相同) ...
    if values_series is None or values_series.empty: return []
    values = pd.Series(values_series).dropna()
    if values.empty: return []
    values_np = values.sort_values().to_numpy()
    n = len(values_np)
    if n == 0: return []
    ecdf_points = []
    unique_values, indices, counts = np.unique(values_np, return_index=True, return_counts=True)
    cumulative_counts = np.cumsum(counts)
    for i, val in enumerate(unique_values):
        ecdf_value = cumulative_counts[i] / n
        ecdf_points.append([float(val), ecdf_value])
    if not ecdf_points or ecdf_points[0][0] > 0:
        ecdf_points.insert(0, [0.0, 0.0])
    elif ecdf_points[0][0] == 0 and ecdf_points[0][1] > (1e-9):
        ecdf_points.insert(0, [0.0, 0.0])
    return ecdf_points


# --- API 端点: ECDF 分析 ---
@app.route('/api/ecdf_analysis', methods=['GET'])
def get_ecdf_analysis():
    global data_df
    # 检查数据加载和必要列
    if data_df is None:
        print("ECDF API: 数据尚未加载，尝试加载...")
        load_data()
        if data_df is None or data_df.empty:
            print("ECDF API: 数据加载失败。")
            return jsonify({"error": "数据未加载或加载失败，请检查后端日志"}), 500
    if data_df.empty:
        return jsonify({"error": "数据为空，无法进行分析"}), 400
    required_cols = {'year', 'count', 'basin'}
    if not required_cols.issubset(data_df.columns):
        missing = required_cols - set(data_df.columns)
        print(f"错误: DataFrame 缺少进行分析所需的列: {missing}")
        return jsonify({"error": f"数据缺少必要列: {missing}"}), 400

    # 获取请求参数
    basin_name = request.args.get('basin')  # 可能为 None
    try:
        interval = int(request.args.get('interval', 0))
    except ValueError:
        interval = 0

    print(f"收到 ECDF 分析请求，流域: {basin_name if basin_name else '所有流域汇总'}, 间隔: {interval}")

    # 1. 筛选流域数据
    if basin_name:
        # 前端发送过来的流域名称可能需要与矢量数据中的名称严格匹配
        # 可以考虑做一些标准化处理，例如去除空格
        basin_name_clean = basin_name.strip()
        filtered_df = data_df[data_df['basin'] == basin_name_clean].copy()
        if filtered_df.empty:
            print(f"警告: 在流域 '{basin_name_clean}' 未找到数据。")
            # 返回空结果和空年份字符串
            return jsonify({"period1_ecdf": [], "period2_ecdf": [], "period1_years": "", "period2_years": ""})
    else:
        filtered_df = data_df.copy()
    current_basin_display = basin_name if basin_name else "所有流域汇总"

    if filtered_df.empty:  # 再次检查，即使是所有流域也可能为空
        print(f"警告: 没有用于分析的数据 ({current_basin_display})。")
        return jsonify({"period1_ecdf": [], "period2_ecdf": [], "period1_years": "", "period2_years": ""})

    # 确定总的年份范围 (基于筛选后的数据)
    try:
        min_year_data = int(filtered_df['year'].min())
        max_year_data = int(filtered_df['year'].max())
    except ValueError:
        print("错误：无法确定筛选后数据的年份范围。")
        return jsonify({"error": "无法确定年份范围"}), 500

    year_range_total = max_year_data - min_year_data + 1

    # 2. 根据 interval 确定时间段
    period1_years_str = ""
    period2_years_str = ""
    start1, end1, start2, end2 = 0, 0, 0, 0

    # 确保 interval 值有效
    valid_intervals = {5, 10, 15, 20}
    use_half_split = (interval == 0 or interval not in valid_intervals or year_range_total < 2 * interval)

    if use_half_split:
        # 按前后半段分 (确保至少有两年数据)
        if year_range_total < 2:
            print("警告：数据年份范围不足两年，无法按前后半段分割。")
            start1, end1 = min_year_data, max_year_data
            start2, end2 = min_year_data, max_year_data  # 让两个时段相同
        else:
            mid_point_year = min_year_data + year_range_total // 2 - 1
            start1, end1 = min_year_data, mid_point_year
            start2, end2 = mid_point_year + 1, max_year_data
        period1_years_str = f"{start1}-{end1}年"
        period2_years_str = f"{start2}-{end2}年"
        print(f"使用时间段分割: {period1_years_str} vs {period2_years_str}")

    else:  # interval 在 {5, 10, 15, 20} 且数据范围足够
        start1, end1 = min_year_data, min_year_data + interval - 1
        start2, end2 = max_year_data - interval + 1, max_year_data
        # 确保 end1 和 start2 不越界（虽然理论上在检查 year_range_total 后不会）
        end1 = min(end1, max_year_data)
        start2 = max(start2, min_year_data)

        period1_years_str = f"{start1}-{end1}年 (前{interval}年)"
        period2_years_str = f"{start2}-{end2}年 (后{interval}年)"
        print(f"使用时间段分割: {period1_years_str} vs {period2_years_str}")

    # 3. 筛选时间段数据
    try:
        period1_df = filtered_df[(filtered_df['year'] >= start1) & (filtered_df['year'] <= end1)]
        period2_df = filtered_df[(filtered_df['year'] >= start2) & (filtered_df['year'] <= end2)]
    except Exception as e:
        print(f"筛选时间段时出错: {e}")
        return jsonify(
            {"error": f"筛选时间段时出错: {e}", "period1_years": period1_years_str, "period2_years": period2_years_str}), 500

    print(f"时间段 1 ({period1_years_str}) 条数: {len(period1_df)}")
    print(f"时间段 2 ({period2_years_str}) 条数: {len(period2_df)}")

    # 4. 计算 ECDF
    ecdf_data1 = calculate_ecdf_data(period1_df['count'])
    ecdf_data2 = calculate_ecdf_data(period2_df['count'])
    print(f"时间段 1 ECDF 点数: {len(ecdf_data1)}")
    print(f"时间段 2 ECDF 点数: {len(ecdf_data2)}")

    # 5. 返回结果
    return jsonify({
        "period1_ecdf": ecdf_data1,
        "period2_ecdf": ecdf_data2,
        "period1_years": period1_years_str,  # 返回给前端
        "period2_years": period2_years_str  # 返回给前端
    })


# --- 可选：API 端点，用于前端获取原始数据 ---
@app.route('/api/data', methods=['GET'])
def get_data():
    # ... (与之前版本类似，现在返回的 data_df 包含准确的 'basin' 列) ...
    global data_df
    if data_df is None: load_data()
    if data_df is None or data_df.empty: return jsonify({"error": "数据未加载或加载失败"}), 500
    if data_df.empty: return jsonify([])
    try:
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=0, type=int)
        if page < 1: page = 1
        if limit < 0: limit = 0
        if limit > 0:
            start_index = (page - 1) * limit
            end_index = start_index + limit
            paginated_df = data_df.iloc[start_index:end_index]
        else:
            paginated_df = data_df
        data_to_return = paginated_df.replace({np.nan: None}).to_dict(orient='records')
        total_count = len(data_df)
        return jsonify(data_to_return)  # 或者封装 {"data": ..., "total": ...}
    except Exception as e:
        print(f"获取数据 /api/data 时出错: {e}")
        traceback.print_exc()
        return jsonify({"error": f"获取数据时出错: {e}"}), 500


# --- 主程序入口 ---
if __name__ == '__main__':
    load_data()  # 应用启动时加载数据和执行空间关联
    app.run(host='0.0.0.0', port=5001, debug=True)