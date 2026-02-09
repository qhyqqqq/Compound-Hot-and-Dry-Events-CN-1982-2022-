<template>
  <div class="map-container">
    <!-- 主地图 -->
    <div class="map-jl" id="map-jl"></div>

    <!-- 鸟瞰图 -->
    <div class="overview-map" id="overviewMap"></div>

  <!-- 经纬度 -->
    <div id="coordinates" style="position: absolute; top: 30px; left: 10px; background-color: rgba(255, 255, 255, 0.7); padding: 5px; border-radius: 3px;">
  坐标: <span id="lat">纬度: 0</span>, <span id="lon">经度: 0</span>
</div>

<div v-if="isLegendVisible" id="map-legend">
      <img src="/image1.png" alt="Map Legend" />
    </div>

    <!-- 功能按钮组 -->
    <div class="button-group">
      <el-select
        v-model="selectedYear"
        class="func-button"
        placeholder="选择年份"
        @change="handleYearChange"
      >
        <el-option
          v-for="item in years"
          :key="item.year"
          :label="item.year"
          :value="item.year"
        />
      </el-select>
      <el-button
        class="func-button"
        type="primary"
        @click="uploadDialogVisible = true"
      >
        数据上传
      </el-button>

      <el-button
        class="func-button"
        type="primary"
        @click="analysisDialogVisible = true"
      >
        统计分析
      </el-button>

      <el-button class="func-button" type="primary" @click="showAnalyze">
        专题绘图
      </el-button>

      <el-button class="func-button" type="primary" @click="change">
        变化率分析
      </el-button>

            <el-button class="func-button" type="primary" @click="toggleBaseMap">
        底图切换
      </el-button>

      <!-- 区域多选 -->
      <el-select
        v-model="selectedRegions"
        class="func-button regions-select"
        multiple
        collapse-tags
        placeholder="选择流域"
        @change="handleRegionChange"
      >
        <el-option
          v-for="region in regionsOptions"
          :key="region"
          :label="region"
          :value="region"
        />
      </el-select>
    </div>

    <!-- 透明度滑块 -->
    <div class="slider-container">
      <div class="slider-header">
        <span class="slider-title">透明度调节</span>
        <span class="slider-value">{{ Math.round(transparency * 100) }}%</span>
      </div>
      <el-slider
        v-model="transparency"
        @input="adjustTransparency"
        vertical
        :min="0"
        :max="1"
        :step="0.05"  
        height="160px" 
        :format-tooltip="formatTooltip"
        :marks="sliderMarks"
      />
      <div class="slider-footer">
        <div class="slider-label top-label">不透明</div>
        <div class="slider-label bottom-label">透明</div>
      </div>
    </div>

    <!-- 数据上传弹窗 -->
    <el-dialog title="数据上传" :visible.sync="uploadDialogVisible">
      <div class="upload-container">
        <div class="upload-item">
          <el-button type="primary" @click="triggerFolderInput('temperature')">
            选择温度数据文件夹
          </el-button>
          <input
            type="file"
            webkitdirectory
            hidden
            ref="temperatureInput"
            @change="handleFolderSelect($event, 'temperature')"
          />
          <el-input
            v-model="selectedTemperaturePath"
            placeholder="已选温度数据文件夹路径"
            readonly
          ></el-input>
        </div>

   
        <div class="upload-item">
          <el-button
            type="primary"
            @click="triggerFolderInput('precipitation')"
          >
            选择SPI或SPEI文件夹
          </el-button>
          <input
            type="file"
            webkitdirectory
            hidden
            ref="precipitationInput"
            @change="handleFolderSelect($event, 'precipitation')"
          />
          <el-input
            v-model="selectedPrecipitationPath"
            placeholder="已选SPI路径"
            readonly
          ></el-input>
        </div> 
      </div>

      <div slot="footer">
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpload">开始处理</el-button>
      </div>
    </el-dialog>

    <!-- 统计分析弹窗 -->
    <el-dialog
      title="统计分析"
      :visible.sync="analysisDialogVisible"
      width="80%"
      @open="loadStatisticalData"
    >
      <!-- 选择分析指标 -->
      <div class="analysis-controls">
        <el-select v-model="selectedRegion" placeholder="选择流域" style="width: 150px; margin-right: 10px;">
          <el-option v-for="region in regionsOptions" :key="region" :label="region" :value="region"></el-option>
        </el-select>
        
        <el-select v-model="selectedMetric" placeholder="选择统计指标" style="width: 150px; margin-right: 10px;">
          <el-option label="平均值" value="mean"></el-option>
          <el-option label="最大值" value="max"></el-option>
          <el-option label="中位数" value="median"></el-option>
          <el-option label="最小值" value="min"></el-option>
          <el-option label="标准差" value="std"></el-option>
        </el-select>

        <el-button type="primary" @click="refreshStatisticalData">刷新分析</el-button>
      </div>

      <!-- 统计图表 -->
      <div class="chart-container" v-loading="chartLoading">
        <div id="statisticalChart" style="width: 100%; height: 400px;"></div>
      </div>
      
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="downloadChartImage">导出图表</el-button>
      </div>
    </el-dialog>

    <!-- 绘图弹窗 -->
    <el-dialog
      title="数据绘图"
      :visible.sync="chartDialogVisible"
      @close="closeImageDialog"
      width="50%"
    >
      <div class="zoomed-image-container">
        <!-- 放大后的图片 -->
        <img
          :src="`/Compound_mapping/Compound_${selectedYear}.png`"
          class="zoomed-image"
        />
        <!-- 显示放大图片的流域名称 -->
        <div class="zoomed-region">{{ `${selectedYear}年` }}</div>
      </div>
      <!-- 右下角下载按钮 -->
    <div class="download-button-container">
      <el-button
        type="primary"
        icon="el-icon-download"
        @click="downloadImage"
        size="small"
      >
        下载
      </el-button>
    </div>
    </el-dialog>

    <!-- 变化率分析弹窗 -->
    <el-dialog
      title="变化率分析"
      :visible.sync="chartDialogVisible1"
      width="60%"
    >
      <div class="dialog-content">
        <div class="image-description">
          根据变化趋势，将研究期分成两个时段：1982—2002年与 2002—2022年进行分析，计算复合高温干旱事件的频率变化。频率变定义为两时段复合高温干旱事件日数之差除以前一时段复合高温干旱事件日数，用百分比表示。
        </div>
        <div class="zoomed-image-container">
          <img
            :src="frequencyChangeImage"
            class="zoomed-image"
            alt="变化率分析图"
          />
        </div>
        <div class="download-button-container">
          <el-button
            type="primary"
            icon="el-icon-download"
            @click="downloadImage"
            size="small"
          >
            下载
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 上传加载效果 -->
    <el-dialog :visible.sync="uploadLoading" width="30%" :show-close="false">
      <el-progress
        type="circle"
        :percentage="uploadProgress"
        :status="uploadStatus"
      ></el-progress>
    </el-dialog>
  </div>
</template>

<script>
/* eslint-disable */
import Map from "@arcgis/core/Map";
import MapView from "@arcgis/core/views/MapView";
import MapImageLayer from "@arcgis/core/layers/MapImageLayer";
import GeoJSONLayer from "@arcgis/core/layers/GeoJSONLayer";
import SimpleFillSymbol from "@arcgis/core/symbols/SimpleFillSymbol";
import SimpleLineSymbol from "@arcgis/core/symbols/SimpleLineSymbol";
import SimpleRenderer from "@arcgis/core/renderers/SimpleRenderer";
import Basemap from '@arcgis/core/Basemap';
import TileLayer from '@arcgis/core/layers/TileLayer';
// 引入ECharts
import * as echarts from 'echarts';
import { API_BASE_URL, ARCGIS_BASE_URL } from '../config';

export default {
  data() {
    return {
      // 地图相关
      map: null,
      mapView: null,
      overviewView: null,
      layer: null,
      geojsonLayer: null,
      jiuduanLayer: null,
      isGeoJSONVisible: true,

      // 状态控制
      transparency: 0,
      selectedYear: "",
      uploadDialogVisible: false,

      chartDialogVisible: false,
      chartDialogVisible1: false,
      uploadLoading: false,
      uploadStatus: "",
       isLegendVisible: false,
      // 数据路径
      selectedTemperaturePath: "",
      selectedPrecipitationPath: "",
      // 新增上传相关状态
      uploadProgress: 0,
      uploadInterval: null,
      //数据控制
      isShow: false,
      analysisDialogVisible: false, // 控制原始图片弹窗显示
      imageDialogVisible: false, // 控制放大图片弹窗显示
      currentImage: {}, // 当前选中的图片
        currentBasemap: 'satellite',
      imageList: [
        { filename: "复合高温干旱事件年变化趋势_东南诸河.png", region: "东南诸河" },
        { filename: "复合高温干旱事件年变化趋势_海河流域.png", region: "海河流域" },
        { filename: "复合高温干旱事件年变化趋势_长江流域.png", region: "长江流域" },
        { filename: "复合高温干旱事件年变化趋势_黄河流域.png", region: "黄河流域" },
        { filename: "复合高温干旱事件年变化趋势_淮河流域.png", region: "淮河流域" },
        { filename: "复合高温干旱事件年变化趋势_内陆河.png", region: "内陆河" },
        {
          filename: "复合高温干旱事件年变化趋势_松辽河流域.png",
          region: "松辽河流域",
        },
        { filename: "复合高温干旱事件年变化趋势_西南诸河.png", region: "西南诸河" },
        { filename: "复合高温干旱事件年变化趋势_珠江流域.png", region: "珠江流域" },
      ],
      // 新增区域选择相关
      selectedRegions: [],
      regionsOptions: [],
      // 从geojson中提取的流域列表
      mapServe: `${ARCGIS_BASE_URL}/复合/复合事件发布/MapServer`,
      // 数据配置
     years: [
    { year: "1982", url: "", layerId: "0" },
    { year: "1983", url: "", layerId: "1" },
    { year: "1984", url: "", layerId: "2" },
    { year: "1985", url: "", layerId: "3" },
    { year: "1986", url: "", layerId: "4" },
    { year: "1987", url: "", layerId: "5" },
    { year: "1988", url: "", layerId: "6" },
    { year: "1989", url: "", layerId: "7" },
    { year: "1990", url: "", layerId: "8" },
    { year: "1991", url: "", layerId: "9" },
    { year: "1992", url: "", layerId: "10" },
    { year: "1993", url: "", layerId: "11" },
    { year: "1994", url: "", layerId: "12" },
    { year: "1995", url: "", layerId: "13" },
    { year: "1996", url: "", layerId: "14" },
    { year: "1997", url: "", layerId: "15" },
    { year: "1998", url: "", layerId: "16" },
    { year: "1999", url: "", layerId: "17" },
    { year: "2000", url: "", layerId: "18" },
    { year: "2001", url: "", layerId: "19" },
    { year: "2002", url: "", layerId: "20" },
    { year: "2003", url: "", layerId: "21" },
    { year: "2004", url: "", layerId: "22" },
    { year: "2005", url: "", layerId: "23" },
    { year: "2006", url: "", layerId: "24" },
    { year: "2007", url: "", layerId: "25" },
    { year: "2008", url: "", layerId: "26" },
    { year: "2009", url: "", layerId: "27" },
    { year: "2010", url: "", layerId: "28" },
    { year: "2011", url: "", layerId: "29" },
    { year: "2012", url: "", layerId: "30" },
    { year: "2013", url: "", layerId: "31" },
    { year: "2014", url: "", layerId: "32" },
    { year: "2015", url: "", layerId: "33" },
    { year: "2016", url: "", layerId: "34" },
    { year: "2017", url: "", layerId: "35" },
    { year: "2018", url: "", layerId: "36" },
    { year: "2019", url: "", layerId: "37" },
    { year: "2020", url: "", layerId: "38" },
    { year: "2021", url: "", layerId: "39" },
    { year: "2022", url: "", layerId: "40" }
],
      // 新增 sliderMarks
      sliderMarks: {
        0: '0%',
        0.5: '50%',
        1: '100%'
      },
      selectedRegion: "",
      selectedMetric: "mean",
      chartLoading: false,
      showImageGrid: false,
      frequencyChangeImage: '/compound_mapping/Frequency_Change_Map.png',
    };
  },

  mounted() {
    this.initializeMap();
    this.loadGeoJSONData(); // 加载时读取geojson数据
    // 确保在图层存在后设置初始透明度
    this.$nextTick(() => {
      this.adjustTransparency(this.transparency); // 使用 this.transparency 确保与 v-model 一致
    });
  },

  methods: {
    initializeMap() {
   
     // 初始化主地图
  this.geojsonLayer = new GeoJSONLayer({
  url: "./china_nine1.geojson",
  outFields: ["*"],
  visible: true,
  renderer: new SimpleRenderer({
    symbol: new SimpleFillSymbol({
      color: [0, 0, 0, 0], // 透明填充
      outline: {
        color: [0, 0, 0], // 线条颜色改为黑色
        width: 1.5, // 线条加粗
      },
    }),
  }),
});

const lineSymbol = new SimpleLineSymbol({
  color: [255, 0, 0], // 线条颜色改为黑色
  width: 1, // 线条加粗
});

this.jiuduanLayer = new GeoJSONLayer({
  url: "./jiuduan.geojson",
  visible: true,
  renderer: new SimpleRenderer({
    symbol: lineSymbol,
  }),
});

  

  this.layer = new MapImageLayer({
    url: this.years[0].url,
    opacity: 1 - this.transparency,
  });

  this.map = new Map({
    basemap: "satellite",
    layers: [this.geojsonLayer, this.jiuduanLayer, this.layer],
  });

  this.mapView = new MapView({
    container: "map-jl",
    map: this.map,
    center: [104.1954, 35.8617],
    zoom: 4,
    constraints: {
      rotationEnabled: false,
      minZoom: 4,
      maxZoom: 10,
    },
  });

  // 初始化鸟瞰图
  this.overviewView = new MapView({
    container: "overviewMap",
    map: this.map,
    constraints: {
      rotationEnabled: false,
      minZoom: 3,
      maxZoom: 7,
    },
    viewpoint: this.mapView.viewpoint,
  });

  // 监听鼠标位置并显示经纬度
  this.mapView.on("pointer-move", (event) => {
    // 获取屏幕坐标并转换为地图坐标
    const mapPoint = this.mapView.toMap({ x: event.x, y: event.y });

    if (mapPoint) {
      const { longitude, latitude } = mapPoint;

      // 更新显示的坐标
      document.getElementById("lat").innerText = "纬度: " + latitude.toFixed(4);
      document.getElementById("lon").innerText = "经度: " + longitude.toFixed(4);
    }
  });


      let timeoutId = null; // 用来存储延迟函数的ID

      this.mapView.watch("extent", (extent) => {
        // 清除之前的延迟任务
        if (timeoutId) clearTimeout(timeoutId);

        // 设置延迟，避免频繁调用goTo()
        timeoutId = setTimeout(() => {
          this.overviewView.goTo({ target: extent }).catch((error) => {
            console.error("Error synchronizing views:", error);
          });
        }, 10); // 延迟300毫秒进行同步
      });
      this.mapView.on("click", (event) => {
        this.handleBasinClick(event);
      });
      //  this.mapView.on("click", async (event) => {
      //   try {
      //     const hitResponse = await this.mapView.hitTest(event);
      //     const geoJSONGraphic = hitResponse.results.find(
      //       (result) => result.graphic.layer === this.geojsonLayer
      //     );

      //     if (geoJSONGraphic) {
      //       const attributes = geoJSONGraphic.graphic.attributes;

      //       // 调试输出所有属性
      //       console.log("所有属性字段:", Object.keys(attributes));
      //       console.log("完整属性:", attributes);

      //       // 尝试获取可能的名称字段（按优先级）
      //       const nameKeys = ["quyu", "NAME", "name", "流域名称", "Region"];
      //       const foundKey = nameKeys.find(key => attributes.hasOwnProperty(key));

      //       if (foundKey) {
      //         this.$message.success(`当前流域：${attributes[foundKey]}`);
      //       } else {
      //         // 使用OBJECTID作为备用方案
      //         this.$message.warning(`未找到名称字段，区域ID：${attributes.__OBJECTID}`);
      //       }
      //     } else {
      //       this.$message.warning("未选中任何流域区域");
      //     }
      //   } catch (error) {
      //     console.error("点击查询失败:", error);
      //     this.$message.error("数据查询失败");
      //   }
      // });
    },
    // 功能方法
        toggleBaseMap() {
   
      const newBasemap = this.currentBasemap === 'satellite' ? 'streets' : 'satellite';
      const newBasemapInstance = newBasemap === 'satellite'
        ? new Basemap({
            baseLayers: [new TileLayer({ url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer' })],
            title: 'Satellite',
            id: 'satellite',
          })
        : new Basemap({
            baseLayers: [new TileLayer({ url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer' })],
            title: 'Streets',
            id: 'streets',
          });

      this.map.basemap = newBasemapInstance;
      this.currentBasemap = newBasemap;
    },

      downloadImage() {
  if (!this.selectedYear) {
    alert("请选择年份！");
    return;
  }

  const imageUrl = `/Compound_mapping/Compound_${this.selectedYear}.png`;  // 获取图片 URL
  const link = document.createElement("a");  // 创建一个 <a> 元素
  link.href = imageUrl;  // 设置图片的 URL
  link.download = `${this.selectedYear}_image.png`;  // 设置下载的文件名
  link.click();  // 触发下载
},


    downloadImage1() {
      const imageUrl = `/Compound_mapping/Frequency_Change_Map.png`;  // 获取图片 URL
      const link = document.createElement("a");  // 创建一个 <a> 元素
      link.href = imageUrl;  // 设置图片的 URL
      link.download = `1982-2022change.png`;  // 设置下载的文件名
      link.click();  // 触发下载
    },

    handleBasinClick(event) {
      const screenPoint = event.screenPoint;
      this.mapView.hitTest(screenPoint).then((response) => {
        // Find the clicked feature (basin)
        const clickedFeature = response.results.find(
          (result) => result.graphic.layer === this.geojsonLayer
        )?.graphic;

        if (clickedFeature) {
          console.log("clickedFeature:", clickedFeature.attributes);
          // 获取属性值
          const basinName = clickedFeature.attributes?.name; // 使用可选链防止属性不存在时报错
          console.log("当前选中流域名称:", basinName);

          // 确保 basinName 存在
          if (basinName) {
            // 设置为当前选中的流域并刷新统计数据
            this.selectedRegion = basinName;
            if (this.analysisDialogVisible && !this.showImageGrid) {
              this.refreshStatisticalData();
            } else {
              // 查找对应的统计图
              const selectedImage = this.imageList.find(
                (item) => item.region === basinName
              );

              if (selectedImage) {
                this.currentImage = selectedImage;
                this.imageDialogVisible = true;
              } else {
                alert("未找到该流域的统计图像");
              }
            }
          } else {
            alert("该流域没有名称信息");
          }
        }
      });
    },
    toggleGeoJSONLayer() {
      this.isGeoJSONVisible = !this.isGeoJSONVisible;
      this.geojsonLayer.visible = this.isGeoJSONVisible;
    },

    adjustTransparency(value) {
      // 添加对 layer 是否存在的检查
      if (this.layer) {
        this.layer.opacity = 1 - value;
      } else {
        console.warn("尝试调整透明度时，图层对象尚未初始化。");
      }
    },

handleYearChange(year) {
  // 选择年份后显示图例
  if (year) {
    this.isLegendVisible = true;  // 设置为显示图例
  } else {
    this.isLegendVisible = false; // 没有选择年份时隐藏图例
  }

  // 查找对应年份的数据
  const selectedYearData = this.years.find((item) => item.year === year);
  if (selectedYearData) {
    // 更新 selectedYear
    this.selectedYear = year;
    // 更新图层ID，加载相应的图层
    this.updateLayer(selectedYearData.layerId);
  } else {
    console.error("未找到对应年份的图层ID");
  }
},

    updateLayer(layerId) {
      // 移除现有的图层
      if (this.layer) {
        this.map.layers.remove(this.layer);
      }

      // 创建新的 MapImageLayer
      this.layer = new MapImageLayer({
        url: this.mapServe, // 使用固定的 MapServer
        sublayers: [
          {
            id: layerId, // 根据年份选择的图层ID
          },
        ],
        opacity: 1 - this.transparency,
      });

      // 将新图层添加到地图
      this.map.add(this.layer);
      this.map.add(this.geojsonLayer);

    },
    // 打开放大图片弹窗
    openImageDialog(item) {
      console.log("点击图片:", item); // 添加调试日志
      this.currentImage = item;
      this.imageDialogVisible = true;
    },

    // 关闭放大图片弹窗
    closeImageDialog() {
      this.imageDialogVisible = false;
      this.currentImage = {};
    },
    // 触发文件夹选择
    triggerFolderInput(type) {
      const inputRef =
        type === "temperature"
          ? this.$refs.temperatureInput
          : this.$refs.precipitationInput;
      inputRef.value = "";
      inputRef.click();
    },

    // 处理文件夹选择
    handleFolderSelect(event, type) {
      const files = event.target.files;
      if (files.length > 0) {
        // 获取文件夹名称（浏览器安全限制无法获取完整路径）
        const folderName = files[0].webkitRelativePath.split("/")[0];
        if (type === "temperature") {
          this.selectedTemperaturePath = folderName;
        } else {
          this.selectedPrecipitationPath = folderName;
        }
      }
      return false;
    },

    showAnalyze() {
      if (this.selectedYear == "") {
        alert("请选择年份");
        return;
      }
      this.chartDialogVisible = !this.chartDialogVisible;
    },

    change() {
      console.log("变化率分析按钮被点击"); // 添加调试输出
      this.frequencyChangeImage = '/compound_mapping/Frequency_Change_Map.png'; // 使用相对路径
      this.chartDialogVisible1 = !this.chartDialogVisible1; // 切换对话框显示状态
    },

    // 模拟上传过程
    async handleUpload() {
      if (
        this.selectedPrecipitationPath == "" ||
        this.selectedTemperaturePath == ""
      ) {
        alert("请先上传文件夹");
        return;
      }
      this.uploadLoading = true;
      this.uploadStatus = "";
      this.uploadProgress = 0;

      // 模拟进度更新
      this.uploadInterval = setInterval(() => {
        if (this.uploadProgress < 95) {
          this.uploadProgress += Math.floor(Math.random() * 10) + 1;
        }
      }, 500);

      // 模拟上传请求
      try {
        await new Promise((resolve) => setTimeout(resolve, 5000));
        clearInterval(this.uploadInterval);
        this.uploadProgress = 100;
        this.uploadStatus = "success";

        // 2秒后自动关闭
        setTimeout(() => {
          this.uploadLoading = false;
          this.uploadDialogVisible = false;
        }, 5000);
      } catch (error) {
        clearInterval(this.uploadInterval);
        this.uploadStatus = "exception";
      }
    },
    async loadGeoJSONData() {
      try {
        const response = await fetch("./china_nine1.geojson");
        const geojson = await response.json();

        // 提取所有唯一的name值
        const names = new Set();
        geojson.features.forEach((feature) => {
          // 跳过name为null的要素
          if (feature.properties.name !== null) {
            names.add(feature.properties.name);
          }
        });

        this.regionsOptions = Array.from(names);
        this.selectedRegions = Array.from(names); // 默认全选

        // 初始化图层过滤
        this.updateGeoJSONFilter();
      } catch (error) {
        console.error("加载GeoJSON失败:", error);
      }
    },
    updateGeoJSONFilter() {
      if (this.selectedRegions.length === 0) {
        this.geojsonLayer.definitionExpression = "1=0"; // 不显示任何要素
      } else {
        // 构建过滤表达式，例如："name IN ('黄河流域', '长江流域')"
        const filter = this.selectedRegions
          .map((name) => `'${name}'`)
          .join(",");
        this.geojsonLayer.definitionExpression = `name IN (${filter})`;
      }
    },
    handleRegionChange() {
      this.updateGeoJSONFilter();
    },
    // 新增 formatTooltip 方法
    formatTooltip(val) {
      return Math.round(val * 100) + '%';
    },
    loadStatisticalData() {
      // 如果没有选择流域，则默认选择第一个
      if (!this.selectedRegion && this.regionsOptions.length > 0) {
        this.selectedRegion = this.regionsOptions[0];
      }
      this.refreshStatisticalData();
    },
    async refreshStatisticalData() {
      if (!this.selectedRegion) {
        this.$message.warning("请选择一个流域进行分析");
        return;
      }

      this.chartLoading = true;
      try {
        // 调用后端API获取统计数据
        const response = await fetch(`${API_BASE_URL}/api/raster_statistics?region=${this.selectedRegion}`);
        
        if (!response.ok) {
          throw new Error(`API请求失败: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        this.statisticalData = data;
        
        // 渲染图表
        this.renderChart();
      } catch (error) {
        console.error("获取统计数据失败:", error);
        this.$message.error(`获取统计数据失败: ${error.message}`);
      } finally {
        this.chartLoading = false;
      }
    },
    renderChart() {
      // 销毁已有的图表实例
      if (this.chartInstance) {
        this.chartInstance.dispose();
      }

      // 初始化图表
      const chartDom = document.getElementById('statisticalChart');
      this.chartInstance = echarts.init(chartDom);
      
      // 从statisticalData中提取数据
      const years = this.years.map(y => y.year);
      const data = this.statisticalData[this.selectedRegion] || {};
      
      // 根据选择的指标获取数据序列
      let seriesData = [];
      const metricLabels = {
        mean: "平均值",
        max: "最大值",
        median: "中位数",
        min: "最小值",
        std: "标准差"
      };
      
      if (data[this.selectedMetric]) {
        seriesData = years.map(year => data[this.selectedMetric][year] || null);
      } else {
        // 如果没有所选指标的数据，则显示所有可用指标
        const availableMetrics = Object.keys(data).filter(key => 
          ["mean", "max", "median", "min", "std"].includes(key)
        );
        
        const series = availableMetrics.map(metric => ({
          name: metricLabels[metric] || metric,
          type: 'line',
          data: years.map(year => (data[metric] && data[metric][year]) || null),
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
          emphasis: {
            focus: 'series'
          }
        }));
        
        // 设置图表选项
        const option = {
          title: {
            text: `${this.selectedRegion} - 复合高温干旱事件统计`,
            left: 'center'
          },
          tooltip: {
            trigger: 'axis',
            formatter: function(params) {
              let result = params[0].axisValue + '年<br/>';
              params.forEach(param => {
                result += param.marker + ' ' + param.seriesName + ': ' + (param.value !== null && param.value !== undefined ? param.value.toFixed(2) : '无数据') + '<br/>';
              });
              return result;
            }
          },
          legend: {
            data: availableMetrics.map(metric => metricLabels[metric] || metric),
            bottom: 0
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '10%',
            top: '15%',
            containLabel: true
          },
          toolbox: {
            feature: {
              saveAsImage: {}
            }
          },
          xAxis: {
            type: 'category',
            boundaryGap: false,
            data: years,
            name: '年份',
            nameLocation: 'end',
            nameGap: 5
          },
          yAxis: {
            type: 'value',
            name: '日数',
            nameLocation: 'end',
            nameGap: 15
          },
          dataZoom: [
            {
              type: 'inside',
              start: 0,
              end: 100
            },
            {
              start: 0,
              end: 100
            }
          ],
          series: series
        };
        
        this.chartInstance.setOption(option);
        return;
      }
      
      // 单指标图表
      const option = {
        title: {
          text: `${this.selectedRegion} - ${metricLabels[this.selectedMetric] || this.selectedMetric}`,
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          formatter: function(params) {
            return params[0].axisValue + '年<br/>' + 
                   params[0].marker + ' ' + params[0].seriesName + ': ' + 
                   (params[0].value !== null && params[0].value !== undefined ? params[0].value.toFixed(2) : '无数据');
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '10%',
          top: '15%',
          containLabel: true
        },
        toolbox: {
          feature: {
            saveAsImage: {}
          }
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: years,
          name: '年份',
          nameLocation: 'end',
          nameGap: 5
        },
        yAxis: {
          type: 'value',
          name: '日数',
          nameLocation: 'end',
          nameGap: 15
        },
        dataZoom: [
          {
            type: 'inside',
            start: 0,
            end: 100
          },
          {
            start: 0,
            end: 100
          }
        ],
        series: [{
          name: metricLabels[this.selectedMetric] || this.selectedMetric,
          type: 'line',
          data: seriesData,
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
          lineStyle: {
            width: 3
          },
          emphasis: {
            focus: 'series'
          },
          markPoint: {
            data: [
              { type: 'max', name: '最大值' },
              { type: 'min', name: '最小值' }
            ]
          },
          markLine: {
            data: [
              { type: 'average', name: '平均值' }
            ]
          }
        }]
      };
      
      this.chartInstance.setOption(option);
    },
    downloadChartImage() {
      if (this.chartInstance) {
        const url = this.chartInstance.getDataURL({
          type: 'png',
          pixelRatio: 2,
          backgroundColor: '#fff'
        });
        
        const link = document.createElement('a');
        link.download = `${this.selectedRegion}_${this.selectedMetric}_统计图.png`;
        link.href = url;
        link.click();
      }
    },
    downloadImage() {
      const link = document.createElement("a");
      link.href = this.frequencyChangeImage; // 使用设置的图片路径
      link.download = "Frequency_Change_Map.png"; // 设置下载文件名
      link.click(); // 触发下载
    },
  },

  watch: {
    // 监听selectedRegion变化，更新图表
    selectedRegion(newVal, oldVal) {
      if (newVal !== oldVal && this.analysisDialogVisible) {
        this.refreshStatisticalData();
      }
    },
    // 监听selectedMetric变化，更新图表
    selectedMetric(newVal, oldVal) {
      if (newVal !== oldVal && this.analysisDialogVisible && this.chartInstance) {
        this.renderChart();
      }
    }
  },
  
  // 组件销毁前清理图表实例
  beforeDestroy() {
    if (this.chartInstance) {
      this.chartInstance.dispose();
      this.chartInstance = null;
    }
  }
};
</script>

<style scoped>
/* 新增的统计分析相关样式 */
.analysis-controls {
  display: flex;
  margin-bottom: 20px;
  align-items: center;
  justify-content: flex-start;
  flex-wrap: wrap;
}

.chart-container {
  width: 100%;
  height: 450px;
  margin-bottom: 20px;
  border: 1px solid #eaeaea;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  background-color: #fff;
}

/* 保留原有样式 */
#map-legend {
  position: absolute;
  bottom: 120px;       /* 由原来的40px上移到120px */
  left: 20px;         /* 保持不变 */
  background-color: white;
  padding: 10px;
  border: 1px solid #ccc;
  z-index: 10;        /* 确保图例在地图之上 */
}

#map-legend img {
  width: 300px;       /* 图例图片宽度 */
  height: auto;       /* 自动调整高度 */
}

/* 地图容器 */
.map-container {
  position: relative;
  height: 100vh;
  width: 100%;
  background-color: #fdf6e3; /* 清新的浅黄色背景 */
}

/* 主地图 */
.map-jl {
  height: 100%;
  width: 100%;
}

/* 鸟瞰图 */
.overview-map {
  position: absolute;
  bottom: 100px;      /* 由原来的20px上移到100px */
  right: 20px;
  width: 300px;
  height: 200px;
  border: 2px solid #f9d423; /* 保持原样式不变 */
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

/* 按钮组 */
.button-group {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 100;
  display: flex;
  flex-direction: row;
  gap: 10px;
}


/* 功能按钮 */
.func-button {
  width: 140px;
  background-color: #ffd37b; /* 清新的黄色 */
  color: rgb(99, 96, 96);
  border-radius: 5px;
  border: none;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.func-button:active {
  background-color: #f9d423 !important;
  border-color: #f9d423 !important;
  color: rgb(0, 0, 0);
}

.func-button:focus {
  outline: none;
  background-color: #f9d423;
  color: rgb(0, 0, 0);
}

.func-button:hover {
  background-color: #f7b800; /* 略深的黄色 */
  color: rgb(0, 0, 0);
}

/* 透明度调节器 - 更新样式 */
.slider-container {
  position: absolute;
  top: 40%;
  left: 20px; /* 从 30px 改为 20px */
  transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.9); /* 更新背景透明度 */
  padding: 15px 10px; /* 更新内边距 */
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15); /* 更新阴影 */
  display: flex; /* 新增 */
  flex-direction: column; /* 新增 */
  align-items: center; /* 新增 */
  width: 110px; /* 新增宽度 */
  z-index: 100; /* 新增层级 */
}

/* 新增 slider header 样式 */
.slider-header {
  width: 100%;
  text-align: center;
  margin-bottom: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 新增 slider title 样式 */
.slider-title {
  font-size: 14px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

/* 新增 slider value 样式 */
.slider-value {
  font-size: 16px;
  color: #f7b800;
  font-weight: bold;
}

/* 新增 slider footer 样式 */
.slider-footer {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 10px;
}

/* 新增 slider label 样式 */
.slider-label {
  font-size: 12px;
  color: #606266;
  margin: 3px 0;
}

/* 新增 top label 样式 */
.top-label {
  color: #f7b800;
}

/* 新增 bottom label 样式 */
.bottom-label {
  color: #909399;
}

/* 自定义滑动条样式 - 更新 */
.el-slider {
  width: auto; /* 移除背景色和圆角，设为auto */
}

.el-slider__button {
  width: 14px; /* 新增 */
  height: 14px; /* 新增 */
  background-color: #f7b800; /* 更新颜色 */
  border: 2px solid #fff; /* 新增边框 */
}

.el-slider__runway {
  background-color: #f0f0f0; /* 更新颜色 */
  width: 8px; /* 新增宽度 */
}

/* 新增 slider bar 样式 */
.el-slider__bar {
  background-color: #f9d423;
  width: 8px;
}

/* 数据上传 */
.upload-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.upload-item {
  margin-bottom: 20px;
}

.upload-container .el-input {
  width: 100%;
  background-color: #fff8e5;
  border: 1px solid #f9d423;
  border-radius: 5px;
}

.upload-container .el-button {
  background-color: #f9d423;
  color: white;
  border-radius: 5px;
  border: none;
  margin-bottom: 5px;
}

.upload-container .el-button:hover {
  background-color: #f7b800;
}

/* 数据上传弹窗的按钮 */
.el-dialog__footer .el-button {
  background-color: #f9d423;
  color: white;
  border-radius: 5px;
}

.el-dialog__footer .el-button:hover {
  background-color: #f7b800;
}

/* 上传进度容器 */
.upload-progress {
  text-align: center;
  position: relative;
}

/* 上传成功的提示 */
.upload-success {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.upload-success i {
  font-size: 60px;
  color: #67c23a;
}

.upload-success p {
  margin-top: 10px;
  color: #606266;
}

.upload-item {
  margin-bottom: 20px;
}

/* 图片展示容器 */
.image-container {
  text-align: center;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 15px;
}

/* 修改分析图片样式 */
.analysis-image {
  width: 100%;
  height: auto;
  max-height: 120px;
  object-fit: cover;
  border: 2px solid #f9d423;
  border-radius: 8px;
  cursor: pointer !important; /* 确保鼠标指针变为手型 */
  transition: transform 0.3s ease, box-shadow 0.3s ease; /* 添加过渡效果 */
  position: relative;
  z-index: 2; /* 确保图片在上层 */
}

.analysis-image:hover {
  transform: scale(1.05); /* 鼠标悬停时放大 */
  box-shadow: 0 4px 12px rgba(249, 212, 35, 0.4); /* 添加阴影效果 */
}

.region-name {
  margin-top: 10px;
  font-size: 16px;
  font-weight: bold;
  color: #f7b800;
}

/* 放大弹窗样式 */
.zoomed-image-container {
  text-align: center;
}

.zoomed-image {
  width: 100%;
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
  border: 2px solid #f9d423;
  border-radius: 8px;
}

.zoomed-region {
  margin-top: 10px;
  font-size: 18px;
  font-weight: bold;
  color: #f9d423;
}

/* 选择框样式 */
.el-select {
  margin-right: 8px;
}
.regions-select {
  width: 240px !important;
}

/* 调整多选标签样式 */
.el-select__tags {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
}
.download-button-container {
  position: absolute;
  bottom: 20px;
  right: 20px;
  display: flex;
  justify-content: flex-end;
}
.download-button-container1 {
  position: absolute;
  bottom: 60px;
  right: 40px;
  display: flex;
  justify-content: flex-end;
}

/* 新增：隐藏 Element UI Slider 自带的 Tooltip */
.el-slider >>> .el-tooltip {
  display: none !important;
}

/* 对话框底部按钮容器样式 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.dialog-content {
  display: flex;
  flex-direction: column;
  align-items: center; /* 居中对齐 */
}

.image-description {
  margin-bottom: 15px; /* 图片与文字之间的间距 */
  font-size: 14px; /* 文字大小 */
  color: #333; /* 文字颜色 */
  text-align: center; /* 文字居中 */
  padding: 0 10px; /* 左右内边距 */
}

.zoomed-image-container {
  text-align: center;
  margin-bottom: 20px; /* 图片与下载按钮之间的间距 */
}

.zoomed-image {
  width: 100%;
  max-width: 100%; /* 确保图片自适应 */
  max-height: 80vh; /* 限制最大高度 */
  object-fit: contain; /* 保持图片比例 */
  border: 2px solid #f9d423; /* 图片边框 */
  border-radius: 8px; /* 圆角 */
}

.download-button-container {
  margin-top: 10px; /* 按钮与图片之间的间距 */
  display: flex;
  justify-content: center; /* 按钮居中对齐 */
}
</style>
