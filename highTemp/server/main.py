#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
整合后的主程序，将栅格数据统计分析(raster_statistics.py)和ECDF分析(app.py)
整合到同一个Flask服务中
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, shape
import numpy as np
import rasterio
import rasterio.features
import os
import time
import statistics
import traceback

os.environ["PYTHONIOENCODING"] = "utf-8"

app = Flask(__name__)
CORS(app)

# --- 配置常量 ---
# ECDF分析相关路径
DATA_FILE_PATH = r'C:\Users\lenovo\Desktop\mysql.csv'
BASIN_VECTOR_FILE_PATH = r'F:\DATA\复合高温干旱事件识别系统-数据处理成果\1982-2022干旱指数预处理后数据及输出结果\九大流域\China_nine_basin.shp'
BASIN_NAME_COLUMN = 'name'

# 栅格数据统计相关路径
RASTER_DATA_PATH = r"F:\DATA\复合高温干旱事件识别系统-数据处理成果\复合高温干旱事件统计结果\复合高温事件_tif"
BASIN_SHP_PATH = r"F:\DATA\复合高温干旱事件识别系统-数据处理成果\1982-2022干旱指数预处理后数据及输出结果\九大流域\China_nine_basin.shp"

# HWMID数据路径
HWMID_COUNT_PATH = r"F:\DATA\复合高温干旱事件识别系统-数据处理成果\热浪事件统计结果\HWMID_tif_次数\HWMID_results"
HWMID_DAYS_PATH = r"F:\DATA\复合高温干旱事件识别系统-数据处理成果\热浪事件统计结果\HWMID_results_tif日数"

# 全局变量
data_df = None  # ECDF分析数据
basins_gdf = None  # ECDF分析流域数据
raster_basins = None  # 栅格统计流域数据

# --- 数据加载和处理函数 ---
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
            basins_gdf = gpd.read_file(BASIN_VECTOR_FILE_PATH, encoding='utf-8')  # 使用UTF-8编码
            print(f"流域边界加载成功。共 {len(basins_gdf)} 个特征。")

            if BASIN_NAME_COLUMN not in basins_gdf.columns:
                print(f"错误: 流域边界文件中未找到指定的流域名称列 '{BASIN_NAME_COLUMN}'。")
                print(f"可用列: {basins_gdf.columns.tolist()}")
                basins_gdf = None  # 标记为不可用
            else:
                print(f"流域边界数据的 CRS: {basins_gdf.crs}")
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
    except Exception as e:
        print(f"加载数据文件时出错: {e}")
        data_df = pd.DataFrame()
        return

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
            def parse_coords(coord_str):
                try:
                    # 移除可能的额外字符并分割
                    parts = str(coord_str).strip().split(',')
                    if len(parts) == 2:
                        lat, lon = map(float, parts)
                        return Point(lon, lat)
                    else:
                        return None
                except (ValueError, TypeError):
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

def load_basins():
    """加载栅格统计分析所需的流域边界数据"""
    global raster_basins
    if raster_basins is None:
        print(f"加载栅格统计流域数据: {BASIN_SHP_PATH}")
        raster_basins = gpd.read_file(BASIN_SHP_PATH)
        print(f"成功加载 {len(raster_basins)} 个流域")
    return raster_basins

def get_raster_files(data_type="compound"):
    """获取栅格文件列表
    
    参数:
        data_type: 数据类型，可选值包括 "compound"(复合高温干旱), "hwmid_count"(HWMID次数), "hwmid_days"(HWMID日数)
    """
    if data_type == "compound":
        data_path = RASTER_DATA_PATH
        file_prefix = "Compound_"
    elif data_type == "hwmid_count":
        data_path = HWMID_COUNT_PATH  
        file_prefix = "HWMID_"
    elif data_type == "hwmid_days":
        data_path = HWMID_DAYS_PATH
        file_prefix = "HWMID_"
    else:
        print(f"错误: 未知的数据类型: {data_type}")
        return []
    
    files = []
    print(f"尝试读取栅格目录: {data_path}")
    if not os.path.exists(data_path):
        print(f"错误: 栅格数据路径不存在: {data_path}")
        # 尝试检查父目录
        parent_dir = os.path.dirname(data_path)
        if os.path.exists(parent_dir):
            print(f"父目录存在: {parent_dir}")
            print(f"父目录内容: {os.listdir(parent_dir)}")
        return files
    
    try:
        # 打印目录内容便于调试
        print(f"目录内容: {os.listdir(data_path)[:10]}..." if len(os.listdir(data_path)) > 10 else os.listdir(data_path))
        
        for file in os.listdir(data_path):
            # 检查是否为TIF文件，并且是否包含指定前缀
            if file.lower().endswith('.tif') and file.startswith(file_prefix):
                try:
                    # 提取年份，更灵活地处理文件名
                    parts = file.split('_')
                    if len(parts) >= 2:
                        # 从第二部分中提取数字部分
                        year_part = ''.join(c for c in parts[1] if c.isdigit())
                        if year_part and 1982 <= int(year_part) <= 2022:
                            file_path = os.path.join(data_path, file)
                            print(f"找到有效栅格文件: {file}, 年份: {year_part}")
                            files.append((int(year_part), file_path))
                except (IndexError, ValueError) as e:
                    print(f"警告: 跳过文件 {file}, 原因: {e}")
        
        if not files:
            print(f"警告: 未找到任何符合格式的栅格文件")
            # 尝试其他可能的格式
            for file in os.listdir(data_path):
                if file.lower().endswith('.tif'):
                    print(f"发现其他TIF文件: {file}")
        else:
            print(f"共找到 {len(files)} 个栅格文件")
        
        files.sort(key=lambda x: x[0])  # 按年份排序
    except Exception as e:
        print(f"读取栅格文件列表时出错: {str(e)}")
        traceback.print_exc()
    
    return files

def calculate_statistics_for_basin(basin_geom, raster_path):
    """计算特定流域范围内栅格数据的统计值"""
    try:
        print(f"正在处理栅格文件: {os.path.basename(raster_path)}")
        with rasterio.open(raster_path) as src:
            # 打印栅格和几何的坐标系统信息
            print(f"栅格坐标系: {src.crs}")
            if hasattr(raster_basins, 'crs'):
                print(f"流域坐标系: {raster_basins.crs}")
            else:
                print("无法获取流域坐标系信息")
                
            # 读取栅格数据
            data = src.read(1)  # 读取第一个波段
            
            # 检查数据是否有效
            valid_count = np.sum(~np.isnan(data))
            if valid_count == 0:
                print(f"警告: 栅格文件不包含有效数据")
                return None
                
            print(f"栅格大小: {data.shape}, 有效数据比例: {valid_count/data.size*100:.2f}%")
            
            # 获取栅格的地理变换信息
            transform = src.transform
            
            # 尝试坐标系转换
            try:
                from rasterio.warp import transform_geom
                from shapely.geometry import mapping, shape
                
                # 检查并转换坐标系
                if hasattr(raster_basins, 'crs') and raster_basins.crs != src.crs and src.crs:
                    print(f"执行坐标系转换: {raster_basins.crs} -> {src.crs}")
                    basin_geom_dict = mapping(basin_geom)
                    basin_geom_dict_transformed = transform_geom(
                        raster_basins.crs.to_string(), 
                        src.crs.to_string(), 
                        basin_geom_dict
                    )
                    basin_geom = shape(basin_geom_dict_transformed)
                    print("坐标系转换完成")
            except Exception as e:
                print(f"坐标系转换出错 (继续使用原始几何): {e}")
                traceback.print_exc()
            
            # 创建一个掩码数组，表示哪些像素位于流域内
            try:
                mask = rasterio.features.geometry_mask(
                    [basin_geom],
                    out_shape=data.shape,
                    transform=transform,
                    invert=True
                )
                
                # 检查掩码是否有效
                mask_pixels = np.sum(mask)
                print(f"掩码像素数: {mask_pixels}, 占比: {mask_pixels/data.size*100:.2f}%")
                
                if mask_pixels == 0:
                    print("警告: 掩码未覆盖任何像素，将使用全图计算")
                    mask = np.ones_like(data, dtype=bool)
                    mask_pixels = np.sum(mask)
                
                # 应用掩码提取流域内的数据
                masked_data = data[mask]
                
                # 过滤掉无效值
                valid_data = masked_data[~np.isnan(masked_data)]
                if src.nodata is not None:
                    valid_data = valid_data[valid_data != src.nodata]
                
                print(f"掩码内有效值数量: {len(valid_data)}")
                
                if len(valid_data) == 0:
                    print(f"警告: 未提取到任何有效数据")
                    return None
                
                # 计算统计值
                stats = {
                    'mean': float(np.mean(valid_data)),
                    'max': float(np.max(valid_data)),
                    'min': float(np.min(valid_data)),
                    'median': float(np.median(valid_data)),
                    'std': float(np.std(valid_data)),
                    'count': int(len(valid_data))
                }
                
                print(f"统计结果: 均值={stats['mean']:.2f}, 最大值={stats['max']:.2f}, 最小值={stats['min']:.2f}")
                return stats
            except Exception as mask_error:
                print(f"创建或应用掩码时出错: {mask_error}")
                traceback.print_exc()
                return None
    except Exception as e:
        print(f"处理栅格文件 {raster_path} 时出错: {e}")
        traceback.print_exc()
        return None

# --- ECDF 计算函数 ---
def calculate_ecdf_data(values_series):
    """计算给定 Pandas Series 的 ECDF"""
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

# --- API 端点: 栅格数据统计分析 ---
@app.route('/api/raster_statistics', methods=['GET'])
def get_raster_statistics():
    """API端点: 获取栅格统计数据"""
    try:
        start_time = time.time()
        
        # 获取查询参数
        region = request.args.get('region')
        data_type = request.args.get('data_type', 'compound')  # 默认为复合高温干旱数据
        
        if not region:
            return jsonify({"error": "请提供流域名称参数"}), 400
        
        print(f"收到栅格统计请求，流域: {region}, 数据类型: {data_type}")
        
        # 加载流域数据
        try:
            all_basins = load_basins()
            if all_basins is None:
                print("错误: 流域数据加载失败")
                return jsonify({"error": "流域数据加载失败，请检查流域数据文件"}), 500
        except Exception as e:
            print(f"加载流域数据失败: {str(e)}")
            traceback.print_exc()
            return jsonify({"error": f"加载流域数据失败: {str(e)}"}), 500
        
        # 查找请求的流域
        try:
            basin_row = all_basins[all_basins['name'] == region]
            if len(basin_row) == 0:
                # 尝试查找相似名称
                all_names = all_basins['name'].tolist()
                print(f"可用流域名称: {all_names}")
                return jsonify({"error": f"未找到名为 '{region}' 的流域", "available_basins": all_names}), 404
            
            basin_geom = basin_row.iloc[0].geometry
            if basin_geom is None:
                print(f"错误: 流域 '{region}' 的几何对象为空")
                return jsonify({"error": f"流域 '{region}' 的几何对象为空"}), 500
            
            print(f"流域 '{region}' 几何类型: {basin_geom.geom_type}")
        except Exception as e:
            print(f"查找流域 '{region}' 时出错: {str(e)}")
            traceback.print_exc()
            return jsonify({"error": f"查找流域时出错: {str(e)}"}), 500
        
        # 获取栅格文件列表
        try:
            raster_files = get_raster_files(data_type)
            if not raster_files:
                print(f"错误: 未找到有效的栅格文件，数据类型: {data_type}")
                return jsonify({"error": f"未找到有效的栅格文件，请检查路径和文件名格式。数据类型: {data_type}"}), 500
            
            print(f"找到 {len(raster_files)} 个栅格文件")
        except Exception as e:
            print(f"获取栅格文件列表时出错: {str(e)}")
            traceback.print_exc()
            return jsonify({"error": f"获取栅格文件列表时出错: {str(e)}"}), 500
        
        # 计算每个年份的统计值
        result = {region: {}}
        stats_keys = ['mean', 'max', 'min', 'median', 'std', 'count']
        
        for stat_key in stats_keys:
            result[region][stat_key] = {}
        
        success_count = 0
        try:
            for year, file_path in raster_files:
                print(f"\n正在处理年份: {year}, 文件: {os.path.basename(file_path)}")
                try:
                    stats = calculate_statistics_for_basin(basin_geom, file_path)
                    
                    if stats:
                        success_count += 1
                        for stat_key in stats_keys:
                            if stat_key in stats:
                                result[region][stat_key][str(year)] = stats[stat_key]
                    else:
                        print(f"警告: 年份 {year} 未能获取有效统计结果")
                except Exception as year_error:
                    print(f"处理年份 {year} 时出错: {str(year_error)}")
                    traceback.print_exc()
                    # 继续处理下一个年份，不中断整个过程
        except Exception as e:
            print(f"处理栅格统计时出错: {str(e)}")
            traceback.print_exc()
            return jsonify({"error": f"处理栅格统计时出错: {str(e)}"}), 500
        
        # 检查是否有成功处理的数据
        if success_count == 0:
            print("错误: 所有栅格文件处理后均未获得有效统计结果")
            return jsonify({"error": "没有获取到任何有效的统计数据，请检查栅格文件内容和坐标系统"}), 500
        
        # 添加处理时间和成功率信息
        process_time = time.time() - start_time
        result["process_time"] = f"{process_time:.2f}秒"
        result["success_rate"] = f"{success_count}/{len(raster_files)}"
        result["data_type"] = data_type
        
        print(f"栅格统计分析完成，处理了 {len(raster_files)} 个文件，成功 {success_count} 个")
        return jsonify(result)
    
    except Exception as e:
        print(f"API处理过程中发生意外错误: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"服务器内部错误: {str(e)}"}), 500

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
        "period1_years": period1_years_str,
        "period2_years": period2_years_str
    })

# --- API 端点: 获取原始数据 ---
@app.route('/api/data', methods=['GET'])
def get_data():
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
        return jsonify(data_to_return)
    except Exception as e:
        print(f"获取数据 /api/data 时出错: {e}")
        traceback.print_exc()
        return jsonify({"error": f"获取数据时出错: {e}"}), 500

# --- 主程序入口 ---
if __name__ == '__main__':
    print("开始加载所有服务所需的数据...")
    try:
        load_data()  # 加载ECDF分析数据
    except Exception as e:
        print(f"加载ECDF数据出错: {str(e)}")
        traceback.print_exc()
        
    try:
        load_basins()  # 加载栅格统计流域数据
    except Exception as e:
        print(f"加载流域数据出错: {str(e)}")
        traceback.print_exc()
        
    print("数据加载完成，正在启动API服务...")
    
    # 打印当前工作目录和数据路径
    print(f"当前工作目录: {os.getcwd()}")
    print(f"栅格数据路径: {RASTER_DATA_PATH}")
    print(f"流域边界路径: {BASIN_SHP_PATH}")
    
    # 启动整合后的API服务
    app.run(host='0.0.0.0', port=5001, debug=True) 