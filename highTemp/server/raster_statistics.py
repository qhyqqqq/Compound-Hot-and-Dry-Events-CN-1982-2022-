#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import rasterio
import geopandas as gpd
from flask import Flask, request, jsonify
from flask_cors import CORS
from shapely.geometry import shape, mapping
import time
import statistics
import traceback  # 添加traceback模块
from rasterio.warp import transform_geom

app = Flask(__name__)
CORS(app)

# 数据路径配置
RASTER_DATA_PATH = r"F:\DATA\复合高温干旱事件识别系统-数据处理成果\复合高温干旱事件统计结果\复合高温事件_tif"
BASIN_SHP_PATH = r"F:\DATA\复合高温干旱事件识别系统-数据处理成果\1982-2022干旱指数预处理后数据及输出结果\九大流域\China_nine_basin.shp"

# 加载流域数据
basins = None

def load_basins():
    """加载流域边界数据"""
    global basins
    if basins is None:
        print(f"加载流域数据: {BASIN_SHP_PATH}")
        try:
            if not os.path.exists(BASIN_SHP_PATH):
                print(f"错误: 流域文件不存在: {BASIN_SHP_PATH}")
                return None
                
            basins = gpd.read_file(BASIN_SHP_PATH)
            print(f"成功加载 {len(basins)} 个流域")
            print(f"流域坐标系: {basins.crs}")
            
            # 验证流域数据是否包含name字段
            if 'name' not in basins.columns:
                available_columns = list(basins.columns)
                print(f"警告: 流域数据缺少'name'字段，可用字段: {available_columns}")
            else:
                # 打印所有流域名称以供参考
                print(f"可用流域名称: {basins['name'].tolist()}")
        except Exception as e:
            print(f"加载流域数据出错: {str(e)}")
            traceback.print_exc()
            return None
    return basins

def get_raster_files():
    """获取栅格文件列表"""
    files = []
    if not os.path.exists(RASTER_DATA_PATH):
        print(f"错误: 栅格数据路径不存在: {RASTER_DATA_PATH}")
        return files
    
    try:
        all_files = os.listdir(RASTER_DATA_PATH)
        
        # 打印目录中的所有文件以进行调试
        print(f"目录中的文件: {all_files[:10]}..." if len(all_files) > 10 else f"目录中的文件: {all_files}")
        
        for file in all_files:
            # 检查是否为TIF文件，并且是Compound_{年份}格式
            if file.lower().endswith('.tif') and file.startswith('Compound_'):
                try:
                    year = file.split('_')[1].split('.')[0]
                    if year.isdigit() and 1982 <= int(year) <= 2022:
                        file_path = os.path.join(RASTER_DATA_PATH, file)
                        # 检查文件是否真实存在且可读
                        if os.path.isfile(file_path) and os.access(file_path, os.R_OK):
                            files.append((int(year), file_path))
                        else:
                            print(f"警告: 文件不存在或不可读: {file_path}")
                except (IndexError, ValueError) as e:
                    print(f"警告: 跳过文件 {file}, 原因: {e}")
        
        if not files:
            print(f"警告: 未找到任何符合格式的栅格文件")
        else:
            print(f"找到 {len(files)} 个栅格文件")
            
        files.sort(key=lambda x: x[0])  # 按年份排序
    except Exception as e:
        print(f"获取栅格文件列表时出错: {str(e)}")
        traceback.print_exc()
        
    return files

def calculate_statistics_for_basin(basin_geom, raster_path):
    """
    计算特定流域范围内栅格数据的统计值
    """
    try:
        with rasterio.open(raster_path) as src:
            print(f"处理栅格文件: {os.path.basename(raster_path)}")
            print(f"栅格坐标系: {src.crs}")
            print(f"栅格大小: {src.width}x{src.height}, 波段数: {src.count}")
            
            # 读取第一个波段
            data = src.read(1)  
            
            # 数据验证
            valid_mask = ~np.isnan(data)
            if src.nodata is not None:
                valid_mask &= (data != src.nodata)
                
            valid_count = np.sum(valid_mask)
            print(f"栅格统计: 大小={data.shape}, 有效像素数={valid_count} ({valid_count/(data.size)*100:.2f}%)")
            
            if valid_count == 0:
                print(f"警告: 栅格文件不包含有效数据")
                return None
                
            print(f"栅格值范围: [{np.min(data[valid_mask]):.2f}, {np.max(data[valid_mask]):.2f}]")
            
            # 获取栅格的地理变换信息
            transform = src.transform
            
            # 由于坐标系可能不匹配，需要将流域几何转换为栅格的坐标系
            try:
                # 检查坐标系是否需要转换
                basin_geom_raster_crs = basin_geom
                if hasattr(basins, 'crs') and basins.crs != src.crs:
                    print(f"坐标系不匹配，尝试转换流域几何到栅格坐标系")
                    print(f"流域坐标系: {basins.crs} -> 栅格坐标系: {src.crs}")
                    
                    # 使用rasterio的transform_geom来转换几何
                    basin_geom_dict = mapping(basin_geom)
                    basin_geom_dict_transformed = transform_geom(
                        basins.crs, 
                        src.crs, 
                        basin_geom_dict
                    )
                    basin_geom_raster_crs = shape(basin_geom_dict_transformed)
                
                # 创建一个掩码数组，表示哪些像素位于流域内
                mask = rasterio.features.geometry_mask(
                    [basin_geom_raster_crs],
                    out_shape=data.shape,
                    transform=transform,
                    invert=True
                )
                
                mask_pixels = np.sum(mask)
                print(f"掩码内像素数: {mask_pixels} ({mask_pixels/(data.size)*100:.2f}%)")
                
                if mask_pixels == 0:
                    print(f"警告: 流域掩码未覆盖任何像素，可能是坐标系转换问题")
                    # 尝试使用原始几何，不进行坐标转换
                    print(f"尝试使用原始流域几何（不转换坐标系）")
                    mask = rasterio.features.geometry_mask(
                        [basin_geom],
                        out_shape=data.shape,
                        transform=transform,
                        invert=True
                    )
                    mask_pixels = np.sum(mask)
                    print(f"原始几何掩码内像素数: {mask_pixels} ({mask_pixels/(data.size)*100:.2f}%)")
                    
                    if mask_pixels == 0:
                        # 坐标系仍然不匹配，可能需要手动投影或查看几何范围
                        print(f"警告: 使用原始几何仍然无法获取任何像素")
                        return None
                
                # 应用掩码提取流域内的数据
                masked_data = data[mask]
                
                # 过滤掉无效值
                valid_data = masked_data[~np.isnan(masked_data)]
                if src.nodata is not None:
                    valid_data = valid_data[valid_data != src.nodata]
                
                print(f"掩码内有效值数: {len(valid_data)} ({len(valid_data)/mask_pixels*100 if mask_pixels > 0 else 0:.2f}%)")
                
                if len(valid_data) == 0:
                    print(f"警告: 流域内没有有效数据")
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
                
            except Exception as geom_error:
                print(f"处理流域几何时出错: {str(geom_error)}")
                traceback.print_exc()
                return None
    except Exception as e:
        print(f"处理栅格文件 {raster_path} 时出错: {str(e)}")
        traceback.print_exc()
        return None

@app.route('/api/raster_statistics', methods=['GET'])
def get_raster_statistics():
    """API端点: 获取栅格统计数据"""
    start_time = time.time()
    
    # 获取查询参数
    region = request.args.get('region')
    if not region:
        return jsonify({"error": "请提供流域名称参数"}), 400
    
    print(f"收到请求，流域: {region}")
    
    # 加载流域数据
    try:
        all_basins = load_basins()
        if all_basins is None:
            return jsonify({"error": "无法加载流域数据"}), 500
    except Exception as e:
        print(f"加载流域数据失败: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"加载流域数据失败: {str(e)}"}), 500
    
    # 查找请求的流域
    basin_row = all_basins[all_basins['name'] == region]
    if len(basin_row) == 0:
        # 尝试查找相似名称
        similar_basins = all_basins[all_basins['name'].str.contains(region, case=False, na=False)]
        if len(similar_basins) > 0:
            similar_names = similar_basins['name'].tolist()
            return jsonify({"error": f"未找到名为 '{region}' 的流域，但找到类似名称: {similar_names}"}), 404
        else:
            return jsonify({"error": f"未找到名为 '{region}' 的流域，可用流域: {all_basins['name'].tolist()}"}), 404
    
    basin_geom = basin_row.iloc[0].geometry
    print(f"流域几何类型: {basin_geom.geom_type}, 面积: {basin_geom.area}")
    
    # 获取栅格文件列表
    raster_files = get_raster_files()
    if not raster_files:
        return jsonify({"error": "未找到有效的栅格文件"}), 500
    
    # 计算每个年份的统计值
    result = {region: {}}
    stats_keys = ['mean', 'max', 'min', 'median', 'std', 'count']
    
    for stat_key in stats_keys:
        result[region][stat_key] = {}
    
    success_count = 0
    for year, file_path in raster_files:
        print(f"\n处理年份: {year}")
        stats = calculate_statistics_for_basin(basin_geom, file_path)
        
        if stats:
            success_count += 1
            for stat_key in stats_keys:
                result[region][stat_key][str(year)] = stats[stat_key]
    
    if success_count == 0:
        print(f"警告: 所有栅格文件处理后均未获得有效统计结果")
        return jsonify({"error": f"无法获取流域 '{region}' 的任何有效栅格统计数据，请检查数据路径和坐标系统"}), 500
    
    # 添加处理时间和成功率信息
    process_time = time.time() - start_time
    result["process_time"] = f"{process_time:.2f}秒"
    result["success_rate"] = f"{success_count}/{len(raster_files)}"
    
    print(f"统计完成，处理了 {len(raster_files)} 个文件，成功 {success_count} 个")
    return jsonify(result)

if __name__ == '__main__':
    # 加载流域数据
    load_basins()
    
    # 打印工作目录和数据路径信息
    print(f"当前工作目录: {os.getcwd()}")
    print(f"栅格数据路径: {RASTER_DATA_PATH}")
    print(f"流域边界路径: {BASIN_SHP_PATH}")
    
    # 启动API服务
    app.run(host='0.0.0.0', port=5001, debug=True) 