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
      <img src="/image.png" alt="Map Legend" />
    </div>

    <!-- 功能按钮组 -->
    <div class="button-group">
      <el-select
        v-model="selectedYear"
        class="func-button"
        placeholder="选择SPEI年份"
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

    <!-- 透明度调节器 (替换为 SpiShow 的样式) -->
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
            选择蒸散发数据文件夹
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
            placeholder="已选蒸散发数据文件夹路径"
            readonly
          ></el-input>
        </div>

        <!-- 降水文件夹上传 -->
        <div class="upload-item">
          <el-button
            type="primary"
            @click="triggerFolderInput('precipitation')"
          >
            选择降水数据文件夹
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
            placeholder="已选降水数据文件夹路径"
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
    >
      <div class="image-grid">
        <el-row :gutter="20">
          <el-col :span="8" v-for="(item, layerId) in imageList" :key="layerId">
            <div class="image-container">
              <img
                :src="`/SPEI_analyze/${item.filename}`"
                class="analysis-image"
                @click="openImageDialog(item)"
              />
              <div class="region-name">{{ item.region }}</div>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-dialog>

    <!-- 放大图片的弹窗 -->
    <el-dialog
      title="放大查看"
      :visible.sync="imageDialogVisible"
      width="60%"
      @close="closeImageDialog"
    >
      <div class="zoomed-image-container">
        <!-- 放大后的图片 -->
        <img
          :src="`/SPEI_analyze/${currentImage.filename}`"
          class="zoomed-image"
        />
        <!-- 显示放大图片的流域名称 -->
        <div class="zoomed-region">{{ currentImage.region }}</div>
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
          :src="`/SPEI_mapping/SPEI12_${selectedYear}_Map.jpg`"
          class="zoomed-image"
        />
        <!-- 显示放大图片的流域名称 -->
        <div class="zoomed-region">{{ `${selectedYear}年` }}</div>
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
import { ARCGIS_BASE_URL } from '../config';

export default {
  data() {
    return {
      // 地图相关
      map: null,
      mapView: null,
      overviewView: null,
      layer: null,
      geojsonLayer: null,
      jiuduanLayer:null,
      isGeoJSONVisible: true,

      // 状态控制
      transparency: 0,
      selectedYear: "",
      uploadDialogVisible: false,

      chartDialogVisible: false,
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
        { filename: "SPEI12_Annual_Changes_东南诸河.png", region: "东南诸河" },
        { filename: "SPEI12_Annual_Changes_海河流域.png", region: "海河流域" },
        { filename: "SPEI12_Annual_Changes_长江流域.png", region: "长江流域" },
        { filename: "SPEI12_Annual_Changes_黄河流域.png", region: "黄河流域" },
        { filename: "SPEI12_Annual_Changes_淮河流域.png", region: "淮河流域" },
        { filename: "SPEI12_Annual_Changes_内陆河.png", region: "内陆河" },
        {
          filename: "SPEI12_Annual_Changes_松辽河流域.png",
          region: "松辽河流域",
        },
        { filename: "SPEI12_Annual_Changes_西南诸河.png", region: "西南诸河" },
        { filename: "SPEI12_Annual_Changes_珠江流域.png", region: "珠江流域" },
      ],
      // 新增区域选择相关
      selectedRegions: [],
      regionsOptions: [],
      // 从geojson中提取的流域列表
      mapServe: `${ARCGIS_BASE_URL}/SPEI/SPEI发布/MapServer`,
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
      }
    };
  },

  mounted() {
    this.initializeMap();
    this.loadGeoJSONData(); // 加载时读取geojson数据
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
            color: [0, 0, 0, 0],
            outline: {
              color: [0, 0, 0],
              width: 1.5,
            },
          }),
        }),
      });

      const lineSymbol = new SimpleLineSymbol({
        color: [255, 0, 0],  // 设置颜色为红色
        width: 1
      });

      this.jiuduanLayer = new GeoJSONLayer({
        url: "./jiuduan.geojson",
        visible: true,
        renderer: new SimpleRenderer({
          symbol: lineSymbol
        }),
      });

      this.map = new Map({
        basemap: "satellite",
        layers: [this.geojsonLayer, this.jiuduanLayer],
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
      const imageUrl = `/SPEI_mapping/SPEI12_${this.selectedYear}_Map.jpg`;  // 获取图片 URL
      const link = document.createElement("a");  // 创建一个 <a> 元素
      link.href = imageUrl;  // 设置图片的 URL
      link.download = `${this.selectedYear}_image.png`;  // 设置下载的文件名
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
      // 仅当 layer 存在时调整透明度
      if (this.layer) {
        this.layer.opacity = 1 - value;
      }
    },

    handleYearChange(year) {
      if (year) {
        this.isLegendVisible = true; // 显示图例
        const selectedYearData = this.years.find((item) => item.year === year);
        if (selectedYearData) {
          this.selectedYear = year; // 更新 selectedYear
          this.updateLayer(selectedYearData.layerId); // 加载图层
        } else {
          console.error("未找到对应年份的图层ID");
          // 如果找不到数据，也应该移除旧图层并隐藏图例
          if (this.layer) {
            this.map.remove(this.layer);
            this.layer = null;
          }
          this.isLegendVisible = false;
        }
      } else {
        // 如果年份被清空
        this.isLegendVisible = false; // 隐藏图例
        this.selectedYear = ""; // 清空 selectedYear
        // 移除当前图层（如果存在）
        if (this.layer) {
          this.map.remove(this.layer);
          this.layer = null; // 将 layer 设回 null
        }
      }
    },

    updateLayer(layerId) {
      // 移除旧图层（如果存在）
      if (this.layer) {
        this.map.remove(this.layer);
        // 不需要将 this.layer 设为 null，因为马上会赋新值
      }

      // 创建新的 MapImageLayer
      this.layer = new MapImageLayer({
        url: this.mapServe,
        sublayers: [{ id: layerId }],
        opacity: 1 - this.transparency, // 应用当前透明度设置
      });

      // 将新图层添加到地图的最底层 (index 0)
      this.map.add(this.layer, 0);

      // 确保透明度被应用到新图层
      // this.adjustTransparency(this.transparency); // adjustTransparency 会在新图层加载后自动处理，这里调用可能过早

      // 可以添加一个 loaded 监听器来确保透明度在图层加载后设置，或者依赖于初始 opacity
      this.layer.when(() => {
         console.log(`Layer ${layerId} loaded.`);
         // 可以在这里再次确认透明度，但通常初始 opacity 足够
         // this.layer.opacity = 1 - this.transparency;
       }).catch(error => {
         console.error(`Layer ${layerId} failed to load:`, error);
       });
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
    }
  },

  watch: {},
};
</script>

<style>
/* 小圆角弹出窗口设计 */
.el-dialog {
  border-radius: 8px !important;
  overflow: hidden;
}

.el-dialog__header {
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}

.el-dialog__body {
  padding: 20px;
}

.el-dialog__footer {
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
}

/* 按钮、输入框等组件的圆角 */
.el-input, 
.el-button,
.el-select,
.el-progress,
.el-select-dropdown {
  border-radius: 5px !important;
}

/* 弹出窗口中的图片圆角 */
.analysis-image,
.zoomed-image {
  border-radius: 8px;
}

/* 下拉菜单圆角 */
.el-select-dropdown {
  border-radius: 6px !important;
  overflow: hidden;
}
</style>

<style scoped>
/* 图例位置上移 */
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
  width: 100px;       /* 图例图片宽度 */
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

/* 鸟瞰图位置上移 */
.overview-map {
  position: absolute;
  bottom: 100px;      /* 由原来的20px上移到100px */
  right: 20px;
  width: 300px;
  height: 200px;
  border: 2px solid #f9d423; /* 清新的黄色边框 */
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  z-index: 100;       /* 修正z-index属性名称 */
}

/* 按钮组 */
.button-group {
  position: absolute;
  top: 20px;
  right: 20px;
  z-layerId: 100;
  display: flex;
  flex-direction: row;
  gap: 10px;
}

/* 功能按钮 */
.func-button {
  width: 140px;
  background-color: #ffd37b;
  color: rgb(99, 96, 96);
  border-radius: 5px;
  border: none;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.func-button:before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.5s ease, height 0.5s ease;
  z-index: 0;
}

.func-button:hover:before {
  width: 250%;
  height: 250%;
}

.func-button:active {
  transform: scale(0.95);
}

.func-button:hover {
  background-color: #f7b800;
  color: rgb(0, 0, 0);
  box-shadow: 0 4px 10px rgba(249, 212, 35, 0.4);
}

/* 透明度调节器 */
.slider-container {
  position: absolute;
  top: 40%; /* 保持和 SpiShow 一致的位置 */
  left: 20px;
  transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.9);
  padding: 15px 10px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 110px; /* 保持和 SpiShow 一致的宽度 */
  z-index: 100;
}

.slider-header {
  width: 100%;
  text-align: center;
  margin-bottom: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.slider-title {
  font-size: 14px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.slider-value {
  font-size: 16px;
  color: #f7b800;
  font-weight: bold;
}

.slider-footer {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 10px;
}

.slider-label {
  font-size: 12px;
  color: #606266;
  margin: 3px 0;
}

.top-label {
  color: #f7b800;
}

.bottom-label {
  color: #909399;
}

/* 自定义滑动条样式 */
.el-slider {
  width: auto; /* 让滑块宽度自适应 */
  margin: 5px 0; /* 调整上下间距 */
}

.el-slider__button {
  width: 14px;
  height: 14px;
  background-color: #f7b800;
  border: 2px solid #fff;
}

.el-slider__runway {
  background-color: #f0f0f0;
  width: 8px; /* 保持轨道宽度 */
}

.el-slider__bar {
  background-color: #f9d423;
  width: 8px; /* 保持滑块条宽度 */
}

/* 隐藏 Element UI Slider 自带的 Tooltip */
.el-slider >>> .el-tooltip {
  display: none !important;
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

/* 图片展示容器 */
.image-container {
  text-align: center;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 15px;
}

.analysis-image {
  width: 100%;
  height: auto;
  max-height: 120px;
  object-fit: cover;
  border: 2px solid #f9d423;
  border-radius: 8px;
  cursor: pointer !important;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  position: relative;
  z-index: 2;
}

.analysis-image:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(249, 212, 35, 0.4);
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
  max-height: 80vh;
  overflow: hidden;
}

.zoomed-image {
  max-width: 100%;
  max-height: 70vh;
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
</style>
