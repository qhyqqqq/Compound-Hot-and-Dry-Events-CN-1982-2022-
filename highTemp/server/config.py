import os

DATA_FILE_PATH = os.getenv(
    "HIGHTEMP_DATA_FILE_PATH",
    r"C:\Users\lenovo\Desktop\mysql.csv",
)
BASIN_VECTOR_FILE_PATH = os.getenv(
    "HIGHTEMP_BASIN_VECTOR_FILE_PATH",
    r"F:\DATA\复合高温干旱事件识别系统-数据处理成果\1982-2022干旱指数预处理后数据及输出结果\九大流域\China_nine_basin.shp",
)
BASIN_NAME_COLUMN = os.getenv("HIGHTEMP_BASIN_NAME_COLUMN", "name")

RASTER_DATA_PATH = os.getenv(
    "HIGHTEMP_RASTER_DATA_PATH",
    r"F:\DATA\复合高温干旱事件识别系统-数据处理成果\复合高温干旱事件统计结果\复合高温事件_tif",
)
BASIN_SHP_PATH = os.getenv(
    "HIGHTEMP_BASIN_SHP_PATH",
    r"F:\DATA\复合高温干旱事件识别系统-数据处理成果\1982-2022干旱指数预处理后数据及输出结果\九大流域\China_nine_basin.shp",
)

HWMID_COUNT_PATH = os.getenv(
    "HIGHTEMP_HWMID_COUNT_PATH",
    r"F:\DATA\复合高温干旱事件识别系统-数据处理成果\热浪事件统计结果\HWMID_tif_次数\HWMID_results",
)
HWMID_DAYS_PATH = os.getenv(
    "HIGHTEMP_HWMID_DAYS_PATH",
    r"F:\DATA\复合高温干旱事件识别系统-数据处理成果\热浪事件统计结果\HWMID_results_tif日数",
)

API_HOST = os.getenv("HIGHTEMP_API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("HIGHTEMP_API_PORT", "5001"))
