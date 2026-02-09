<template>
  <el-container class="data-management">
    <el-main class="scrollable-main">
      <!-- 标题和介绍 -->
      <div class="page-header">
        <h1 class="page-title">复合高温干旱事件管理</h1>
        <p class="page-description">在此页面中您可以查询、添加、编辑和删除复合高温干旱事件数据</p>
      </div>
      
      <!-- 查询框 -->
      <el-card shadow="hover" class="query-card">
        <div slot="header" class="card-header">
          <span><i class="el-icon-search"></i> 复合高温干旱事件查询</span>
        </div>
        <el-form :inline="true" class="query-form">
          <el-form-item label="年份">
            <el-input
              v-model="queryYear"
              placeholder="请输入年份（如：1982）"
              clearable
              prefix-icon="el-icon-date"
            />
          </el-form-item>
          <el-form-item label="经纬度">
            <el-input
              v-model="queryCoordinates"
              placeholder="请输入经纬度（如：45.12,120.56）"
              clearable
              prefix-icon="el-icon-location"
              class="coordinates-input"
            />
          </el-form-item>
          <el-form-item label="发生次数">
            <el-input
              v-model="queryCount"
              placeholder="请输入发生次数（如：2）"
              clearable
              prefix-icon="el-icon-sort"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="el-icon-search" @click="filterData">
              查询
            </el-button>
            <el-button icon="el-icon-refresh" @click="clearQuery">
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 新增数据 -->
      <el-card shadow="hover" class="add-card">
        <div slot="header" class="card-header">
          <span><i class="el-icon-plus"></i> 新增复合高温干旱事件</span>
          <el-button type="text" icon="el-icon-arrow-up" @click="toggleAddForm">
            {{ showAddForm ? '收起' : '展开' }}
          </el-button>
        </div>
        
        <el-collapse-transition>
          <div v-show="showAddForm">
            <el-form :model="newData" ref="form" label-width="100px" class="add-form">
              <el-row :gutter="20">
                <el-col :md="12" :sm="24">
                  <el-form-item label="年份" required>
                    <el-input v-model="newData.year" placeholder="请输入年份（如：1982）">
                      <i slot="prefix" class="el-icon-date"></i>
                    </el-input>
                  </el-form-item>
                </el-col>
                <el-col :md="12" :sm="24">
                  <el-form-item label="像元位置" required>
                    <el-input v-model="newData.location" placeholder="请输入像元位置（如：4x186）">
                      <i slot="prefix" class="el-icon-position"></i>
                    </el-input>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :md="12" :sm="24">
                  <el-form-item label="经纬度" required>
                    <el-input v-model="newData.coordinates" placeholder="请输入经纬度（如：52.625,120.125）">
                      <i slot="prefix" class="el-icon-location"></i>
                    </el-input>
                  </el-form-item>
                </el-col>
                <el-col :md="12" :sm="24">
                  <el-form-item label="发生次数" required>
                    <div class="horizontal-number-input">
                      <el-button size="small" icon="el-icon-minus" @click="decreaseCount"></el-button>
                      <el-input v-model="newData.count" type="number" min="1" max="10" class="count-input"></el-input>
                      <el-button size="small" icon="el-icon-plus" @click="increaseCount"></el-button>
                    </div>
                  </el-form-item>
                </el-col>
              </el-row>

              <!-- 发生时间 -->
              <el-form-item label="发生时间" required>
                <div class="time-input-container">
                  <div class="time-tags-container" v-if="newData.timeList.length > 0">
                    <el-tag
                      v-for="(time, index) in newData.timeList"
                      :key="index"
                      closable
                      type="success"
                      effect="dark"
                      @close="removeTime(index)"
                      class="time-tag"
                    >
                      {{ time }}
                    </el-tag>
                  </div>
                  <div class="time-status" v-if="newData.count">
                    <span :class="{'status-complete': newData.timeList.length === parseInt(newData.count), 'status-incomplete': newData.timeList.length < parseInt(newData.count)}">
                      已添加 {{ newData.timeList.length }}/{{ newData.count }} 组
                    </span>
                  </div>
                  <div class="time-input">
                    <el-input
                      v-model="newTime"
                      placeholder="输入时间后回车添加（如：06-13到06-15）"
                      @keyup.enter.native="addTime"
                    >
                      <i slot="prefix" class="el-icon-time"></i>
                      <el-button slot="append" icon="el-icon-plus" @click="addTime">添加</el-button>
                    </el-input>
                  </div>
                </div>
              </el-form-item>

              <el-form-item>
                <el-button type="primary" icon="el-icon-check" @click="submitData">提交数据</el-button>
                <el-button icon="el-icon-refresh" @click="clearNewData">清空</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-collapse-transition>
      </el-card>

      <!-- 数据表格 -->
      <el-card shadow="hover" class="data-table-card">
        <div slot="header" class="card-header">
          <span><i class="el-icon-document"></i> 复合高温干旱事件统计列表</span>
          <div class="card-actions">
            <el-button type="success" size="small" icon="el-icon-data-line" @click="openEcdfDialog">
              ECDF 分析
            </el-button>
            
            <el-dropdown @command="handleExportCommand" trigger="click">
              <el-button type="primary" size="small">
                <i class="el-icon-download"></i> 导出数据 <i class="el-icon-arrow-down el-icon--right"></i>
              </el-button>
              <el-dropdown-menu slot="dropdown">
                <el-dropdown-item command="current">导出当前页数据</el-dropdown-item>
                <el-dropdown-item command="search">导出搜索结果</el-dropdown-item>
                <el-dropdown-item command="byYear">按年份导出</el-dropdown-item>
                <el-dropdown-item command="all">导出全部数据</el-dropdown-item>
              </el-dropdown-menu>
            </el-dropdown>
            <el-button size="small" icon="el-icon-refresh" @click="fetchData">刷新</el-button>
          </div>
        </div>
        
        <div class="table-operations">
          <el-select v-model="pageSize" placeholder="每页显示" @change="handleSizeChange" style="width: 120px;">
            <el-option v-for="item in [10, 20, 50, 100]" :key="item" :label="`${item}条/页`" :value="item"></el-option>
          </el-select>
          <span class="data-count">共 {{ filteredData.length }} 条记录</span>
        </div>
        
        <div class="table-container">
          <el-table
            ref="dataTable"
            :data="paginatedData"
            border
            stripe
            highlight-current-row
            style="width: 100%"
            height="400"
            v-loading="tableLoading"
            :header-cell-style="{backgroundColor: '#f5f7fa', color: '#606266', fontWeight: 'bold'}"
          >
            <el-table-column prop="year" label="年份" min-width="80" sortable>
              <template slot-scope="scope">
                <span class="cell-highlight">{{ scope.row.year }}</span>
              </template>
            </el-table-column>
            
            <el-table-column prop="location" label="像元位置" min-width="120" sortable>
              <template slot-scope="scope">
                <el-tag size="medium" effect="plain">{{ scope.row.location }}</el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="coordinates" label="经纬度" min-width="220" show-overflow-tooltip>
              <template slot-scope="scope">
                <el-tooltip :content="scope.row.coordinates" placement="top">
                  <span>{{ scope.row.coordinates }}</span>
                </el-tooltip>
              </template>
            </el-table-column>
            
            <el-table-column prop="count" label="发生次数" min-width="100" sortable>
              <template slot-scope="scope">
                <el-tag type="warning" effect="dark" size="medium">{{ scope.row.count }}</el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="time" label="发生时间" min-width="250" show-overflow-tooltip>
              <template slot-scope="scope">
                <div class="time-display">
                  <el-tag
                    v-for="(time, index) in scope.row.time ? scope.row.time.split(';') : []"
                    :key="index"
                    size="small"
                    effect="plain"
                    type="success"
                    class="time-item-tag"
                  >
                    {{ time }}
                  </el-tag>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="120" fixed="right">
              <template slot-scope="scope">
                <el-button
                  size="mini"
                  type="primary"
                  icon="el-icon-edit"
                  circle
                  @click="openEditDialog(scope.$index)"
                  title="编辑"
                ></el-button>
                <el-button
                  size="mini"
                  type="danger"
                  icon="el-icon-delete"
                  circle
                  @click="deleteData(scope.$index)"
                  title="删除"
                ></el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 空数据显示 -->
          <div class="empty-data" v-if="paginatedData.length === 0 && !tableLoading">
            <i class="el-icon-document"></i>
            <p>暂无数据</p>
          </div>
        </div>

        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            background
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
            :current-page="currentPage"
            :page-sizes="[10, 20, 50, 100]"
            :page-size="pageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredData.length"
          ></el-pagination>
        </div>
      </el-card>
    </el-main>

    <!-- ECDF 分析对话框 -->
    <el-dialog 
      :title="'发生次数 ECDF 分析 - ' + (selectedBasin === 'all_basins' ? '所有流域' : selectedBasin)"
      :visible.sync="ecdfDialogVisible"
      width="70%"
      top="5vh"
      center
      :show-close="false"
      @opened="initEcdfChart"
      @closed="disposeEcdfChart"
      custom-class="ecdf-dialog"
    >
      <div class="basin-select-container">
        <span>选择流域：</span>
        <el-select v-model="selectedBasin" @change="handleBasinChange" placeholder="请选择流域">
          <el-option label="所有流域汇总" value="all_basins"></el-option>
          <el-option v-for="basin in basinOptions" :key="basin" :label="basin" :value="basin"></el-option>
        </el-select>
      </div>

      <div ref="ecdfChart" style="width: 100%; height: 450px; margin-bottom: 15px;"></div>
      
      <div class="analysis-text-container" v-html="currentBasinAnalysisText" transition="fade"></div>
      
      <span slot="footer" class="dialog-footer">
        <el-button @click="ecdfDialogVisible = false">关闭</el-button>
      </span>
    </el-dialog>

    <!-- 添加年份选择对话框 -->
    <el-dialog title="选择导出年份" :visible.sync="exportYearDialogVisible" width="30%" center>
      <el-form>
        <el-form-item label="选择年份">
          <el-select v-model="selectedExportYear" placeholder="请选择年份" style="width: 100%">
            <el-option
              v-for="year in availableYears"
              :key="year"
              :label="year"
              :value="year"
            ></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="exportYearDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="exportDataByYear">确定导出</el-button>
      </span>
    </el-dialog>

    <!-- 添加编辑数据对话框 -->
    <el-dialog 
      title="编辑复合高温干旱事件" 
      :visible.sync="editDialogVisible" 
      width="50%"
      center
    >
      <el-form :model="editForm" ref="editForm" label-width="100px">
        <el-row :gutter="20">
          <el-col :md="12" :sm="24">
            <el-form-item label="年份" required>
              <el-input v-model="editForm.year" placeholder="请输入年份（如：1982）">
                <i slot="prefix" class="el-icon-date"></i>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :md="12" :sm="24">
            <el-form-item label="像元位置" required>
              <el-input v-model="editForm.location" placeholder="请输入像元位置（如：4x186）">
                <i slot="prefix" class="el-icon-position"></i>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :md="12" :sm="24">
            <el-form-item label="经纬度" required>
              <el-input v-model="editForm.coordinates" placeholder="请输入经纬度（如：52.625,120.125）">
                <i slot="prefix" class="el-icon-location"></i>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :md="12" :sm="24">
            <el-form-item label="发生次数" required>
              <div class="horizontal-number-input">
                <el-button size="small" icon="el-icon-minus" @click="decreaseEditCount"></el-button>
                <el-input v-model="editForm.count" type="number" min="1" max="10" class="count-input"></el-input>
                <el-button size="small" icon="el-icon-plus" @click="increaseEditCount"></el-button>
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 发生时间 -->
        <el-form-item label="发生时间" required>
          <div class="time-input-container">
            <div class="time-tags-container" v-if="editForm.timeList.length > 0">
              <el-tag
                v-for="(time, index) in editForm.timeList"
                :key="index"
                closable
                type="success"
                effect="dark"
                @close="removeEditTime(index)"
                class="time-tag"
              >
                {{ time }}
              </el-tag>
            </div>
            <div class="time-status" v-if="editForm.count">
              <span :class="{'status-complete': editForm.timeList.length === parseInt(editForm.count), 'status-incomplete': editForm.timeList.length < parseInt(editForm.count)}">
                已添加 {{ editForm.timeList.length }}/{{ editForm.count }} 组
              </span>
            </div>
            <div class="time-input">
              <el-input
                v-model="editTime"
                placeholder="输入时间后回车添加（如：06-13到06-15）"
                @keyup.enter.native="addEditTime"
              >
                <i slot="prefix" class="el-icon-time"></i>
                <el-button slot="append" icon="el-icon-plus" @click="addEditTime">添加</el-button>
              </el-input>
            </div>
          </div>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="submitEditData">确定</el-button>
      </span>
    </el-dialog>
  </el-container>
</template>

<style scoped>
/* 修改数据管理页面的样式 */
.data-management {
  padding: 20px;
  min-height: calc(100vh - 70px);  /* 调整最小高度 */
}

.scrollable-main {
  height: calc(100vh - 70px); /* 调整高度，减去导航栏高度 */
  overflow-y: auto;
  padding: 20px;
  background-color: #f5f7fa;
}

/* 确保卡片有足够的上边距 */
.el-card {
  margin-bottom: 20px;
}

/* 表格容器样式 */
.table-container {
  margin-top: 10px;  /* 添加上边距 */
  width: 100%;
  position: relative;
}

/* 分页容器样式 */
.pagination-container {
  margin-top: 20px;
  margin-bottom: 20px;  /* 添加底部边距 */
  padding: 10px 0;
}

/* 美化滚动条 */
.scrollable-main::-webkit-scrollbar {
  width: 8px;
}

.scrollable-main::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.scrollable-main::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 4px;
}

.scrollable-main::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 页面标题 */
.page-header {
  margin-bottom: 20px;
  text-align: center;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 10px;
}

.page-description {
  font-size: 14px;
  color: #909399;
}

/* 查询表单 */
.query-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

/* 新增样式：加宽经纬度查询输入框 */
.query-form .coordinates-input {
  width: 280px; /* 您可以根据需要调整这个宽度值 */
}

/* 新增表单 */
.add-form {
  margin-top: 15px;
}

/* 时间输入样式 */
.time-input-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.time-tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 5px;
}

.time-tag {
  margin-right: 5px;
  margin-bottom: 5px;
}

.time-status {
  font-size: 12px;
  margin-bottom: 5px;
}

.status-complete {
  color: #67c23a;
  font-weight: bold;
}

.status-incomplete {
  color: #e6a23c;
  font-weight: bold;
}

/* 表格样式优化 */
.data-table-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05) !important;
}

/* 美化表格滚动条 */
.el-table__body-wrapper::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.el-table__body-wrapper::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.el-table__body-wrapper::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 4px;
}

.el-table__body-wrapper::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

.table-operations {
  margin-bottom: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.data-count {
  color: #606266;
  font-size: 14px;
}

.time-display {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  max-width: 100%;
}

.time-item-tag {
  margin: 2px;
  white-space: nowrap;
}

.cell-highlight {
  font-weight: bold;
}

/* 响应式适配 */
@media screen and (max-width: 768px) {
  .table-container {
    overflow-x: auto;
  }
}

/* 优化数字输入框样式，使控制按钮与输入框更加融合 */
.integrated-input-number {
  width: 100%;
}

.integrated-input-number .el-input-number__decrease,
.integrated-input-number .el-input-number__increase {
  border-radius: 0;
  border-left: 1px solid #DCDFE6;
  background-color: #F5F7FA;
  height: 100%;
  top: 0;
  margin-top: 0;
  line-height: 40px;
}

.integrated-input-number .el-input-number__decrease:hover,
.integrated-input-number .el-input-number__increase:hover {
  background-color: #E4E7ED;
  color: #409EFF;
}

.integrated-input-number .el-input__inner {
  padding-right: 50px !important; /* 确保文本不会被按钮遮挡 */
  text-align: center;
}

.integrated-input-number.is-controls-right .el-input__inner {
  text-align: center;
  padding-left: 15px;
  padding-right: 50px;
}

/* 确保按钮与输入框边缘对齐 */
.integrated-input-number.is-controls-right .el-input-number__decrease,
.integrated-input-number.is-controls-right .el-input-number__increase {
  right: 0;
  border-left: 1px solid #DCDFE6;
  border-radius: 0;
}

.integrated-input-number.is-controls-right .el-input-number__increase {
  border-bottom: 1px solid #DCDFE6;
}

/* 新增表单中的发生次数输入框 */
.horizontal-number-input {
  display: flex;
  align-items: center;
  width: 100%;
}

.horizontal-number-input .count-input {
  margin: 0 5px;
  text-align: center;
  flex: 1;
}

.horizontal-number-input .el-button {
  padding: 8px 12px;
  border-radius: 4px;
}

/* 卡片头部样式 */
.card-header {
  display: flex;
  justify-content: space-between; /* 让标题和按钮组分开 */
  align-items: center;
  width: 100%;
}

/* 定位在卡片头部的右侧按钮组 */
.card-actions {
  display: flex;           /* 使用 Flexbox 布局 */
  align-items: center;     /* 垂直居中对齐按钮 */
  gap: 10px;               /* 在按钮之间设置 10px 的间距 */
}

/* 表格操作区域样式（如果需要调整）*/
.table-operations {
  margin-bottom: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 新增：ECDF 分析文字容器样式 */
.analysis-text-container {
  margin-top: 20px;
  padding: 15px 20px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #dee2e6;
  font-size: 14px;
  line-height: 1.7;
  color: #495057;
}

.analysis-text-container h4 {
  margin-top: 10px;
  margin-bottom: 12px;
  font-size: 16px;
  font-weight: 600;
  color: #007bff;
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 5px;
}
/* 第一个 h4 不带上边距 */
.analysis-text-container h4:first-of-type {
    margin-top: 0;
}

.analysis-text-container ul, 
.analysis-text-container ol {
  padding-left: 25px; 
  margin-bottom: 12px;
}

.analysis-text-container li {
  margin-bottom: 6px; 
}

.analysis-text-container p {
    margin-bottom: 10px;
}

.analysis-text-container strong {
    color: #343a40;
}

.analysis-text-container i {
    color: #6c757d;
    font-size: 0.9em;
}

.analysis-text-container p:last-child {
  margin-bottom: 0; 
}

/* 定义过渡效果 */
.fade-enter-active, .fade-leave-active {
  transition: opacity .5s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}

/* ECDF 对话框样式调整 */
.ecdf-dialog {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.ecdf-dialog .el-dialog__header {
  padding: 15px 20px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  font-size: 16px;
  font-weight: bold;
}

.ecdf-dialog .el-dialog__body {
  padding: 20px;
}

.basin-select-container {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.basin-select-container span {
  font-size: 14px;
  color: #606266;
}

.basin-select-container .el-select {
  width: 200px;
}
</style>

<script>
import axios from 'axios';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';
import * as echarts from 'echarts'; // 引入 echarts
import { API_BASE_URL } from '../config';

export default {
  data() {
    return {
      // 查询条件
      queryYear: "",
      queryCoordinates: "",
      queryCount: "",
      // 新增数据相关
      newTime: "",
      newData: {
        year: "",
        location: "",
        coordinates: "",
        count: "",
        timeList: [] // 发生时间列表
      },
      // 数据列表
      dataList: [],
      filteredData: [],
      paginatedData: [],
      pageSize: 50,
      currentPage: 1,
      // 编辑数据相关
      editDialogVisible: false,
      editForm: {
        id: "",
        year: "",
        location: "",
        coordinates: "",
        count: "",
        timeList: []
      },
      editTime: "",
      showAddForm: true,     // 控制新增表单显示/隐藏
      tableLoading: false,   // 表格加载状态
      submitLoading: false,  // 提交按钮加载状态
      exportYearDialogVisible: false,
      selectedExportYear: null,
      exportLoading: false,
      ecdfDialogVisible: false,
      ecdfChartInstance: null,
      ecdfData1: [], 
      ecdfData2: [], 
      selectedBasin: '所有流域汇总', 
      ecdfLoading: false, 
      basinOptions: [
        "东南诸河", "海河流域", "长江流域", "黄河流域", 
        "淮河流域", "内陆河", "松辽河流域", "西南诸河", "珠江流域"
      ],
      basinAnalysisTexts: {
        'all_basins': `
          <h4>所有流域汇总分析：</h4>
          <p>通过对1982-2002年和2003-2022年两个时期的 ECDF 曲线对比分析,可以看出：</p>
          <ul>
            <li>两条曲线在0-6次区间内的明显分离,后期遭遇的相对较轻的复合高温干旱事件略多。</li>  
            <li>后期曲线达到中位数(ECDF=0.5)时对应的发生次数(约3次)高于前期(约2次),说明总体事件强度有所增加。</li>
            <li>曲线尾部的变化揭示,极端高发次数事件(如8次以上)的概率在后期有显著上升。</li>
          </ul>
          <p><i>综合来看,后期复合高温干旱事件的影响范围扩大,强度整体上升,极端事件概率增加。</i></p>
        `,
        '长江流域': `
          <h4>长江流域分析：</h4>
          <p>针对长江流域的数据分析显示：</p>
          <ul>
            <li>在0-3次区间内,后期曲线总体低于前期,说明在前期更广泛的地区遭遇了相对轻度的复合高温干旱事件。</li>
            <li>两条曲线在3-7次区间内的陡峭上升,反映中等强度事件的发生概率明显提高。</li>  
            <li>两条曲线在8次以上趋于一致,表明极端事件(如9次以上)在两个时期的发生概率变化不大。</li>
          </ul>
          <p><i>总的来说,长江流域在后期遭受轻度事件影响的范围扩大,中等强度事件概率显著上升,极端事件概率基本稳定。</i></p>
        `,
        '黄河流域': `
          <h4>黄河流域分析：</h4>  
          <p>针对黄河流域的数据分析显示：</p>
          <ul>
            <li>在发生1次的情况下,后期累积概率略高于前期,说明更多地区遭遇了单次事件。</li>
            <li>后期曲线达到ECDF=0.5时的发生次数(2次)高于前期(1次),反映总体事件强度有所增强。</li>
            <li>两条曲线最终在6次附近趋于一致,表明极端高发事件(如7次以上)的概率变化不明显。</li>
          </ul>  
          <p><i>综合来看,黄河流域在后期遭受单次事件影响的范围扩大,总体强度有所增强,但极端事件概率变化不大。</i></p>
        `,
        '淮河流域': `
          <h4>淮河流域分析：</h4>
          <p>针对淮河流域的数据分析显示：</p>  
          <ul>
            <li>后期曲线在1-5次处高于前期,表明轻中等强度事件的发生概率有所提高。</li>
            <li>两条曲线在5次以上基本重合,说明极端事件的发生概率变化不大。</li>
          </ul>
          <p><i>总的来说,淮河流域在后期中低强度事件的分布有所变化,中等强度事件概率上升,极端事件概率基本稳定。</i></p>
        `,
        '珠江流域': `  
          <h4>珠江流域分析：</h4>
          <p>针对珠江流域的数据分析显示：</p>
          <ul>  
            <li>在2-6次处,后期曲线明显低于前期,说明少量事件的影响范围略有减小。</li>
            <li>两条曲线在3次处的急剧上升,反映中等强度事件的发生概率显著提高。</li>
            <li>曲线尾部在7次以上重合,表明极端事件的概率变化不明显。</li>
          </ul>
          <p><i>综合来看,珠江流域在后期中低强度事件的分布略有变化,中等强度事件概率明显上升,极端事件概率基本稳定。</i></p>
        `,
        '松辽河流域': `
          <h4>松辽河流域分析：</h4>
          <p>针对松辽河流域的数据分析显示：</p>
          <ul>
            <li>在0-4次区间内,后期曲线整体高于前期,表明后期更多地区遭遇了相对轻度的复合高温干旱事件。</li>
            <li>两条曲线在5次以上逐渐重合,说明极端事件(如6次以上)的概率变化不大。</li>  
          </ul>
          <p><i>总的来说,松辽河流域在后期遭受轻度事件影响的范围扩大,中等强度事件概率上升,极端事件概率基本稳定。</i></p>  
        `,
        '西南诸河': `
          <h4>西南诸河分析：</h4>
          <p>针对西南诸河的数据分析显示：</p>
          <ul>
            <li>在0-10次区间内,后期曲线明显低于前期,说明轻度事件的影响范围有大幅下降。</li>
            <li>10次以上,两条曲线逐渐重合,表明高强度和极端事件的概率变化不明显。</li>
          </ul>  
          <p><i>综合来看,西南诸河流域在前期轻度事件影响范围较大,高强度和极端事件概率基本稳定。</i></p>
        `,
        '东南诸河': `  
          <h4>东南诸河分析：</h4>
          <p>针对东南诸河的数据分析显示：</p>
          <ul>
            <li>在0-5次区间内,后期曲线总体略低于前期,表明轻中度事件的影响范围有小幅缩减。</li>
            <li>5次以上,两条曲线基本重合,说明较强和极端事件的概率在两个时期没有明显变化。</li>
          </ul>
          <p><i>综合来看,东南诸河流域在后期轻中度事件的影响范围略有扩大,较强和极端事件概率基本稳定,总体变化趋势相对平缓。</i></p>
        `,
        '内陆河': `
          <h4>内陆河分析：</h4>  
          <p>针对内陆河的数据分析显示：</p>
          <ul>
            <li>在1-4次区间内,后期曲线高于前期且更加陡峭,反映中等强度事件的发生概率有所上升。</li>
            <li>4次以上,两条曲线逐渐重合,表明内陆河流域极端事件的概率变化不明显。</li>
          </ul>
          <p><i>综合来看,内陆河流域在后期遭受轻度事件影响的范围扩大,中等强度事件概率上升,极端事件概率基本稳定。</i></p>
        `,
        '海河流域': `  
          <h4>海河流域分析：</h4>
          <p>针对海河流域的数据分析显示：</p>
          <ul>  
            <li>在1-4次的大部分区间内,后期曲线总体高于前期,表明复合高温干旱事件的影响范围总体有所扩大。</li>
            <li>4次以上,两条曲线基本重合,说明海河流域极端事件的发生概率变化不大。</li>
          </ul>
          <p><i>总的来说,海河流域的变化主要体现在中低强度事件影响范围的扩张,极端事件概率基本稳定。</i></p>
        `
      },
      seriesVisibility: {
        period1: true,
        period2: true
      },
    };
  },
  computed: {
    availableYears() {
      if (!this.dataList || this.dataList.length === 0) return [];
      const yearsSet = new Set(this.dataList.map(item => item.year));
      return Array.from(yearsSet).sort();
    },
    currentBasinAnalysisText() {
      const key = this.selectedBasin === '所有流域汇总' ? 'all_basins' : this.selectedBasin;
      return this.basinAnalysisTexts[key] || '<p>暂无对该流域的分析</p>';
    }
  },
  methods: {
    async fetchData() {
      this.tableLoading = true;
      try {
        const response = await axios.get(`${API_BASE_URL}/api/data?limit=0`);
        this.dataList = response.data;
        this.filteredData = [...this.dataList];
        this.updatePagination();
      } catch (error) {
        this.$message.error("获取数据失败：" + error.message);
        this.dataList = [];
        this.filteredData = [];
        this.updatePagination();
      } finally {
        this.tableLoading = false;
      }
    },
    clearQuery() {
      this.queryYear = "";
      this.queryCoordinates = "";
      this.queryCount = "";
      this.filteredData = [...this.dataList];
      this.currentPage = 1;
      this.updatePagination();
      this.$message.success("查询条件已清空");
    },
    clearNewData() {
      this.newData = { year: "", location: "", coordinates: "", count: "", timeList: [] };
      this.newTime = "";
      this.$message.success("新增数据表单已清空");
    },
    filterData() {
      // 校验查询条件格式
      if (this.queryYear && !/^\d{4}$/.test(this.queryYear.trim())) {
        this.$message.error("年份格式错误，请输入4位数字，如：1982");
        return;
      }
      if (this.queryCoordinates && !/^\d+(\.\d+)?,\d+(\.\d+)?$/.test(this.queryCoordinates.trim())) {
        this.$message.error("经纬度格式错误，请输入如：45.12,120.56");
        return;
      }
      if (this.queryCount && !/^\d+$/.test(this.queryCount.trim())) {
        this.$message.error("发生次数格式错误，请输入纯数字");
        return;
      }

      this.filteredData = this.dataList.filter(item => {
        let match = true;
        if (this.queryYear) {
          match = match && String(item.year) === this.queryYear.trim();
        }
        if (this.queryCoordinates && item.coordinates) {
          const [qLat, qLon] = this.queryCoordinates.split(",").map(s => s.trim());
          const coords = item.coordinates.split(",").map(s => s.trim());
          if (coords.length >= 2) {
            const latMatch = coords[0].startsWith(qLat);
            const lonMatch = coords[1].startsWith(qLon);
            match = match && latMatch && lonMatch;
          } else {
            match = false;
          }
        }
        if (this.queryCount) {
          match = match && parseInt(item.count) === parseInt(this.queryCount.trim());
        }
        return match;
      });

      this.currentPage = 1;
      this.updatePagination();
      if (this.filteredData.length > 0) {
        this.$message.success(`查询成功，共找到 ${this.filteredData.length} 条数据`);
      } else {
        this.$message.error("查询失败：未找到满足条件的数据");
      }
    },
    addTime() {
      const singleTimePattern = /^\d{2}-\d{2}到\d{2}-\d{2}$/;
      const timeValue = this.newTime.trim();
      
      if (!timeValue) {
        this.$message.error("请输入时间");
        return;
      }
      
      // 验证时间格式
      if (!singleTimePattern.test(timeValue)) {
        this.$message.error("时间格式错误，请输入如：06-13到06-15");
        return;
      }
      
      // 获取期望的次数，确保是数字
      let expectedCount = 0;
      if (this.newData.count && /^\d+$/.test(this.newData.count.toString().trim())) {
        expectedCount = parseInt(this.newData.count.toString().trim());
      } else {
        this.$message.error("请先输入有效的发生次数");
        return;
      }
      
      // 检查是否已达到最大次数
      if (this.newData.timeList.length >= expectedCount) {
        this.$message.error(`最多只能输入 ${expectedCount} 组发生时间`);
        return;
      }
      
      // 添加时间到列表
      this.newData.timeList.push(timeValue);
      this.newTime = ""; // 清空输入框
      
      // 显示添加成功消息
      this.$message.success(`成功添加时间: ${timeValue}，当前已添加 ${this.newData.timeList.length}/${expectedCount} 组`);
    },
    removeTime(index) {
      this.newData.timeList.splice(index, 1);
    },
    submitData() {
      if (!/^\d{4}$/.test(String(this.newData.year))) {
        this.$message.error("年份格式错误，请输入4位数字，如：1982");
        return;
      }
      if (!/^\d+x\d+$/.test(String(this.newData.location))) {
        this.$message.error("像元位置格式错误，请输入如：4x186");
        return;
      }
      if (!/^\d+\.\d+,\d+\.\d+$/.test(String(this.newData.coordinates))) {
        this.$message.error("经纬度格式错误，请输入如：52.625240725535,120.12554948578496");
        return;
      }
      
      // 确保 count 是字符串，修复 trim 方法错误
      const countValue = String(this.newData.count);
      if (!/^\d+$/.test(countValue)) {
        this.$message.error("发生次数格式错误，请输入纯数字");
        return;
      }
      
      // 检查是否有足够的时间记录
      const expectedCount = parseInt(countValue);
      if (this.newData.timeList.length < expectedCount) {
        this.$message.warning(`请添加 ${expectedCount} 组发生时间，当前只有 ${this.newData.timeList.length} 组`);
        return;
      }
      
      const timePattern = /^\d{2}-\d{2}到\d{2}-\d{2}$/;
      const timeList = this.newData.timeList.map(time => String(time).trim()).filter(time => time);
      for (const time of timeList) {
        if (!timePattern.test(time)) {
          this.$message.error(`发生时间格式错误：${time}，请使用正确格式，如 06-13到06-15`);
          return;
        }
      }
      
      // 构造 payload，将 timeList 数组转换为字符串（以分号分隔）
      const payload = {
        year: this.newData.year,
        location: this.newData.location,
        coordinates: this.newData.coordinates,
        count: this.newData.count,
        time: this.newData.timeList.join(";")
      };
      
      console.log("提交新增数据:", payload);
      
      this.submitLoading = true; // 添加loading状态
      
      axios
        .post(`${API_BASE_URL}/api/data`, payload)
        .then(response => {
          console.log("提交成功响应:", response.data);
          
          // 确保时间字段存在并处理正确
          const newItem = response.data;
          if (!newItem.time && payload.time) {
            // 如果返回的数据中没有time字段，手动添加
            newItem.time = payload.time;
          }
          
          this.dataList.unshift(newItem); // 添加到数组开头，方便查看新数据
          this.filteredData = [...this.dataList]; // 更新过滤后的数据
          this.currentPage = 1; // 返回第一页以查看新数据
          this.updatePagination();
          
          // 重置新增数据表单
          this.newData = { year: "", location: "", coordinates: "", count: "", timeList: [] };
          this.newTime = "";
          this.$message.success("数据提交成功");
        })
        .catch(error => {
          console.error("提交失败详情:", error);
          this.$message.error("提交数据失败：" + (error.response?.data?.message || error.message));
        })
        .finally(() => {
          this.submitLoading = false;
        });
    },
    deleteData(index) {
      // 获取要删除的数据项
      const item = this.paginatedData[index];
      console.log("要删除的数据项:", item);
      
      if (!item) {
        this.$message.error("无法删除：未找到数据项");
        return;
      }
      
      // 检查id是否存在
      if (item.id === undefined || item.id === null) {
        this.$message.error("无法删除：数据项没有ID");
        console.error("数据项缺少ID:", item);
        return;
      }
      
      const idToDelete = item.id;
      console.log("要删除的ID:", idToDelete);
      
      this.$confirm('确认删除此条数据吗?', '提示', {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        const deleteUrl = `${API_BASE_URL}/api/data/${idToDelete}`;
        console.log("发送删除请求到:", deleteUrl);
        
        this.tableLoading = true;
        
        axios
          .delete(deleteUrl)
          .then(response => {
            console.log("删除成功:", response);
            
            // 从数据列表中移除项目
            this.dataList = this.dataList.filter(d => d.id !== idToDelete);
            this.filteredData = this.filteredData.filter(d => d.id !== idToDelete);
            this.updatePagination();
            
            this.$notify({
              title: '成功',
              message: '数据已成功删除',
              type: 'success',
              position: 'bottom-right'
            });
          })
          .catch(error => {
            console.error("删除失败详情:", error);
            
            this.$notify({
              title: '错误',
              message: '删除数据失败，请检查控制台获取详细信息',
              type: 'error',
              position: 'bottom-right'
            });
          })
          .finally(() => {
            this.tableLoading = false;
          });
      }).catch(() => {
        this.$message.info('已取消删除');
      });
    },
    handlePageChange(page) {
      this.currentPage = page;
      this.updatePagination();
    },
    updatePagination() {
      const start = (this.currentPage - 1) * this.pageSize;
      const end = start + this.pageSize;
      
      // 确保不超出数组范围
      this.paginatedData = this.filteredData.slice(start, Math.min(end, this.filteredData.length));
      
      // 检查时间字段格式
      this.paginatedData.forEach(item => {
        // 确保时间字段是字符串
        if (item.time && typeof item.time !== 'string') {
          item.time = String(item.time);
        }
      });
      
      // 表格重新布局
      this.$nextTick(() => {
        if (this.$refs.dataTable) {
          this.$refs.dataTable.doLayout();
        }
      });
    },
    // 点击编辑时弹出编辑对话框
    openEditDialog(index) {
      // 深拷贝选中的数据到 editForm 中
      const item = JSON.parse(JSON.stringify(this.paginatedData[index]));
      console.log("编辑原始数据:", item);
      
      this.editForm = {
        id: item.id,
        year: item.year,
        location: item.location,
        coordinates: item.coordinates,
        count: item.count,
        timeList: []
      };
      
      // 将后端返回的 time 字符串转换为数组
      if (item.time) {
        // 处理可能的不同分隔符情况
        if (item.time.includes(";")) {
          this.editForm.timeList = item.time.split(";");
        } else if (item.time.includes(",")) {
          this.editForm.timeList = item.time.split(",");
        } else {
          // 如果只有一个时间段，直接添加
          this.editForm.timeList = [item.time];
        }
        
        console.log("解析后的时间列表:", this.editForm.timeList);
      }
      
      // 清空新增时间的输入框
      this.editTime = "";
      this.editDialogVisible = true;
    },
    addEditTime() {
      const singleTimePattern = /^\d{2}-\d{2}到\d{2}-\d{2}$/;
      const timeValue = this.editTime.trim();
      
      if (!timeValue) {
        this.$message.error("请输入时间");
        return;
      }
      
      // 验证时间格式
      if (!singleTimePattern.test(timeValue)) {
        this.$message.error("时间格式错误，请输入如：06-13到06-15");
        return;
      }
      
      // 获取期望的次数，确保是数字
      let expectedCount = 0;
      if (this.editForm.count && /^\d+$/.test(this.editForm.count.toString().trim())) {
        expectedCount = parseInt(this.editForm.count.toString().trim());
      } else {
        this.$message.error("请先输入有效的发生次数");
        return;
      }
      
      // 检查是否已达到最大次数
      if (this.editForm.timeList.length >= expectedCount) {
        this.$message.error(`最多只能输入 ${expectedCount} 组发生时间`);
        return;
      }
      
      // 添加时间到列表
      this.editForm.timeList.push(timeValue);
      this.editTime = ""; // 清空输入框
      
      // 显示添加成功消息
      this.$message.success(`成功添加时间: ${timeValue}，当前已添加 ${this.editForm.timeList.length}/${expectedCount} 组`);
    },
    removeEditTime(index) {
      this.editForm.timeList.splice(index, 1);
    },
    submitEditData() {
      // 校验各字段格式
      if (!/^\d{4}$/.test(String(this.editForm.year))) {
        this.$message.error("年份格式错误，请输入4位数字，如：1982");
        return;
      }
      if (!/^\d+x\d+$/.test(String(this.editForm.location))) {
        this.$message.error("像元位置格式错误，请输入如：4x186");
        return;
      }
      if (!/^\d+\.\d+,\d+\.\d+$/.test(String(this.editForm.coordinates))) {
        this.$message.error("经纬度格式错误，请输入如：52.625240725535,120.12554948578496");
        return;
      }
      
      // 确保 count 是字符串，修复 trim 方法错误
      const countValue = String(this.editForm.count);
      if (!/^\d+$/.test(countValue)) {
        this.$message.error("发生次数格式错误，请输入纯数字");
        return;
      }
      
      // 检查是否有足够的时间记录
      const expectedCount = parseInt(countValue);
      if (this.editForm.timeList.length < expectedCount) {
        this.$message.warning(`请添加 ${expectedCount} 组发生时间，当前只有 ${this.editForm.timeList.length} 组`);
        return;
      }
      
      // 构造 payload，将 timeList 数组转换为字符串
      const payload = {
        id: this.editForm.id,
        year: this.editForm.year,
        location: this.editForm.location,
        coordinates: this.editForm.coordinates,
        count: this.editForm.count,
        time: this.editForm.timeList.join(";")
      };
      
      console.log("提交更新的数据:", payload);
      
      this.submitLoading = true; // 添加loading状态
      
      axios
        .put(`${API_BASE_URL}/api/data/${payload.id}`, payload)
        .then(response => {
          console.log("更新成功响应:", response.data);
          
          // 确保更新本地数据
          const index = this.dataList.findIndex(item => item.id === payload.id);
          if (index !== -1) {
            this.$set(this.dataList, index, response.data);
          }
          
          this.filteredData = [...this.dataList]; // 重新过滤
          this.updatePagination();
          this.editDialogVisible = false;
          this.$message.success("数据更新成功");
        })
        .catch(error => {
          console.error("更新失败详情:", error);
          this.$message.error("数据更新失败：" + (error.response?.data?.message || error.message));
        })
        .finally(() => {
          this.submitLoading = false;
        });
    },
    // 切换新增表单显示/隐藏
    toggleAddForm() {
      this.showAddForm = !this.showAddForm;
    },
    
    // 处理每页显示数量变化
    handleSizeChange(val) {
      this.pageSize = val;
      this.currentPage = 1; // 重置到第一页
      this.updatePagination();
    },
    
    // 调整表格高度
    adjustTableHeight() {
      // 动态计算表格高度，留出页面其他元素的空间
      const windowHeight = window.innerHeight;
      // 假设其他元素总高度约350px，可根据实际情况调整
      this.tableHeight = Math.max(windowHeight - 350, 400);
    },
    
    // 导出命令处理器
    handleExportCommand(command) {
      switch(command) {
        case 'current':
          this.exportCurrentPage();
          break;
        case 'search':
          this.exportSearchResults();
          break;
        case 'byYear':
          this.showExportYearDialog();
          break;
        case 'all':
          this.exportAllData();
          break;
        default:
          this.$message.warning('未知的导出命令');
      }
    },
    
    // 显示年份选择对话框
    showExportYearDialog() {
      // 如果没有数据，提示用户
      if (this.availableYears.length === 0) {
        this.$message.warning('没有可用的年份数据');
        return;
      }
      
      this.selectedExportYear = this.availableYears[0]; // 默认选择第一个年份
      this.exportYearDialogVisible = true;
    },
    
    // 导出当前页数据
    exportCurrentPage() {
      // 使用当前显示的数据
      const dataToExport = [...this.paginatedData];
      
      if (dataToExport.length === 0) {
        this.$message.warning('当前页没有可导出的数据');
        return;
      }
      
      this.executeExport(dataToExport, `当前页数据_${this.currentPage}`);
    },
    
    // 修改 exportSearchResults 方法
    exportSearchResults() {
      // 检查是否进行过搜索
      const hasSearched = this.queryYear || this.queryCoordinates || this.queryCount;
      
      if (!hasSearched) {
        this.$confirm('您还未进行搜索，是否导出全部数据？', '提示', {
          confirmButtonText: '导出全部',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          // 用户确认导出全部数据
          this.exportAllData();
        }).catch(() => {
          // 用户取消操作
          this.$message({
            type: 'info',
            message: '已取消导出，请先进行搜索再导出搜索结果'
          });
        });
        return;
      }
      
      // 使用过滤后的数据
      const dataToExport = [...this.filteredData];
      
      if (dataToExport.length === 0) {
        this.$message.warning('没有搜索结果可导出');
        return;
      }
      
      // 构建文件名，包含搜索条件
      let searchConditions = [];
      if (this.queryYear) searchConditions.push(`年份${this.queryYear}`);
      if (this.queryCoordinates) searchConditions.push(`坐标${this.queryCoordinates}`);
      if (this.queryCount) searchConditions.push(`次数${this.queryCount}`);
      
      const filename = searchConditions.length > 0 ? 
        `搜索结果_${searchConditions.join('_')}_${new Date().toISOString().slice(0,10)}` : 
        `全部数据_${new Date().toISOString().slice(0,10)}`;
        
      this.executeExport(dataToExport, filename);
    },
    
    // 按年份导出
    exportDataByYear() {
      if (!this.selectedExportYear) {
        this.$message.warning('请选择要导出的年份');
        return;
      }
      
      // 过滤选定年份的数据
      const dataToExport = this.dataList.filter(
        item => String(item.year) === String(this.selectedExportYear)
      );
      
      if (dataToExport.length === 0) {
        this.$message.warning(`没有${this.selectedExportYear}年的数据可导出`);
        return;
      }
      
      this.executeExport(dataToExport, `${this.selectedExportYear}年数据`);
      this.exportYearDialogVisible = false;
    },
    
    // 导出全部数据
    exportAllData() {
      // 先确认数据量
      const totalCount = this.dataList.length;
      
      if (totalCount === 0) {
        this.$message.warning('没有数据可导出');
        return;
      }
      
      // 对于大数据量，先询问用户
      if (totalCount > 1000) {
        this.$confirm(`将要导出 ${totalCount} 条数据，这可能需要较长时间，是否继续？`, '提示', {
          confirmButtonText: '继续导出',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          this.executeExport(this.dataList, `全部数据_${new Date().toISOString().slice(0,10)}`);
        }).catch(() => {
          this.$message.info('已取消导出');
        });
      } else {
        this.executeExport(this.dataList, `全部数据_${new Date().toISOString().slice(0,10)}`);
      }
    },
    
    // 执行导出操作
    executeExport(data, fileNamePrefix) {
      this.exportLoading = true;
      
      try {
        // 准备数据数组
        const excelData = [
          ['年份', '像元位置', '经纬度', '发生次数', '发生时间'] // 表头行
        ];
        
        // 添加数据行
        data.forEach(item => {
          excelData.push([
            item.year,
            item.location,
            item.coordinates,
            item.count,
            item.time || ''
          ]);
        });
        
        // 创建工作簿
        const wb = XLSX.utils.book_new();
        const ws = XLSX.utils.aoa_to_sheet(excelData);
        
        // 设置列宽
        const colWidths = [
          { wch: 8 },  // 年份
          { wch: 12 }, // 像元位置
          { wch: 30 }, // 经纬度
          { wch: 10 }, // 发生次数
          { wch: 40 }  // 发生时间
        ];
        ws['!cols'] = colWidths;
        
        // 添加工作表到工作簿
        XLSX.utils.book_append_sheet(wb, ws, '灾害事件数据');
        
        // 生成二进制数据
        const wbout = XLSX.write(wb, { 
          bookType: 'xlsx', 
          bookSST: true,  // 生成共享字符串表，这对中文支持很重要
          type: 'array' 
        });
        
        // 保存文件
        saveAs(
          new Blob([wbout], { type: 'application/octet-stream' }), 
          `灾害事件数据_${fileNamePrefix}.xlsx`
        );
        
        this.$message({
          type: 'success',
          message: `成功导出 ${data.length} 条数据`,
          duration: 3000
        });
      } catch (error) {
        console.error('导出数据失败:', error);
        this.$message.error('导出数据失败: ' + error.message);
      } finally {
        this.exportLoading = false;
      }
    },
    decreaseCount() {
      if (this.newData.count > 1) {
        this.newData.count--;
      }
    },
    increaseCount() {
      if (this.newData.count < 10) {
        this.newData.count++;
      }
    },
    decreaseEditCount() {
      if (this.editForm.count > 1) {
        this.editForm.count--;
      }
    },
    increaseEditCount() {
      if (this.editForm.count < 10) {
        this.editForm.count++;
      }
    },
    async showEcdfAnalysis(basinName) {
      console.log(`Requesting ECDF for basin: ${basinName === null ? 'All Basins' : basinName}`);
      
      this.ecdfLoading = true;
      this.ecdfDialogVisible = true;
      this.ecdfData1 = [];
      this.ecdfData2 = [];
      
      if (this.ecdfChartInstance) {
        this.ecdfChartInstance.showLoading();
      }

      try {
        // 构建 API URL
        let apiUrl = `${API_BASE_URL}/api/ecdf_analysis`;
        if (basinName !== null) { // 只有当 basinName 不是 null 时才添加参数
          apiUrl += `?basin=${encodeURIComponent(basinName)}`;
        }
        
        console.log(`Fetching ECDF data from: ${apiUrl}`);
        const response = await axios.get(apiUrl);

        if (response.data && response.data.period1_ecdf !== undefined && response.data.period2_ecdf !== undefined) {
          console.log("ECDF data received:", response.data);
          this.ecdfData1 = response.data.period1_ecdf;
          this.ecdfData2 = response.data.period2_ecdf;
          
          if (this.ecdfChartInstance) {
            this.ecdfChartInstance.hideLoading();
            
            // 完整的图表配置
            const option = {
              tooltip: {
                trigger: 'axis',
                backgroundColor: 'rgba(50, 50, 50, 0.9)',
                borderColor: '#aaa',
                borderWidth: 1,
                textStyle: {
                  color: '#fff'
                },
                axisPointer: {
                  type: 'cross',
                  label: {
                    backgroundColor: '#6a7985'
                  }
                },
                formatter: function(params) {
                  if (!params || params.length === 0) return '';
                  let result = `发生次数: ${params[0].data[0]}<br/>`;
                  params.forEach(param => {
                    if (param.data && Array.isArray(param.data) && param.data.length > 1) {
                      const probability = (param.data[1] * 100).toFixed(1);
                      result += `${param.marker}${param.seriesName}: ${probability}%<br/>`;
                    }
                  });
                  return result;
                }
              },
              grid: {
                left: '5%',
                right: '5%',
                bottom: '12%',
                containLabel: true
              },
              axisPointer: {
                link: {xAxisIndex: 'all'},
                label: {
                  backgroundColor: '#777'
                }
              },
              xAxis: {
                type: 'value',
                name: '发生次数',
                nameLocation: 'middle',
                nameGap: 30,
                min: 0,
                axisLine: { show: true, lineStyle: { color: '#666' } },
                axisTick: { show: true, lineStyle: { color: '#666' } },
                splitLine: {
                  show: true,
                  lineStyle: {
                    color: '#E0E6F1',
                    type: 'dashed'
                  }
                },
                axisLabel: { color: '#333' }
              },
              yAxis: {
                type: 'value',
                name: 'ECDF (累积概率)',
                nameLocation: 'end',
                min: 0,
                max: 1,
                axisLine: { show: true, lineStyle: { color: '#666' } },
                axisTick: { show: true, lineStyle: { color: '#666' } },
                splitLine: {
                  show: true,
                  lineStyle: {
                    color: '#E0E6F1',
                    type: 'dashed'
                  }
                },
                axisLabel: {
                  color: '#333',
                  formatter: '{value}'
                }
              },
              series: [
                {
                  name: '1982-2002年',
                  type: 'line',
                  smooth: false,
                  step: 'end',
                  data: this.ecdfData1,
                  symbol: 'none',
                  lineStyle: { width: 2, color: '#5470C6' },
                  emphasis: { focus: 'series', lineStyle: { width: 3.5 } }
                },
                {
                  name: '2003-2022年',
                  type: 'line',
                  smooth: false,
                  step: 'end',
                  data: this.ecdfData2,
                  symbol: 'none',
                  lineStyle: { width: 2, color: '#91CC75' },
                  emphasis: { focus: 'series', lineStyle: { width: 3.5 } }
                }
              ],
              legend: {
                data: [
                  {
                    name: '1982-2002年',
                    icon: 'rect',
                    itemWidth: 14,
                    itemHeight: 14
                  },
                  {
                    name: '2003-2022年',
                    icon: 'rect',
                    itemWidth: 14,
                    itemHeight: 14
                  }
                ],
                top: 'bottom',
                selected: this.seriesVisibility
              }
            };

            // 一次性设置完整配置
            this.ecdfChartInstance.setOption(option, true);
          }
          
          if (this.ecdfData1.length <= 1 && this.ecdfData2.length <= 1) { // <=1 因为可能有 [0,0] 点
            this.$nextTick(() => {
              if(this.ecdfDialogVisible){ // 确保弹窗还开着
                this.$message.warning(`在 ${this.selectedBasinForTitle} 未找到足够的数据进行分析`);
              }
            });
          }
        } else {
          console.error("后端返回的 ECDF 数据格式不正确:", response.data);
          this.$message.error("获取 ECDF 数据失败：响应格式错误");
          if (this.ecdfChartInstance) this.ecdfChartInstance.hideLoading();
        }
      } catch (error) {
        console.error("获取 ECDF 数据失败:", error);
        let errorMsg = "获取 ECDF 分析数据失败";
        if (error.response && error.response.data && error.response.data.error) {
          errorMsg += `: ${error.response.data.error}`;
        } else if (error.message) {
          errorMsg += `: ${error.message}`;
        }
        this.$message.error(errorMsg);
        if (this.ecdfChartInstance) this.ecdfChartInstance.hideLoading();
      } finally {
        this.ecdfLoading = false; 
        if (this.ecdfChartInstance && this.ecdfDialogVisible) { // 仅当弹窗还可见时
          this.ecdfChartInstance.hideLoading();
        }
      }
    },

    initEcdfChart() {
       // 销毁可能存在的旧实例
       if (this.ecdfChartInstance) {
           this.ecdfChartInstance.dispose();
       }
      const chartDom = this.$refs.ecdfChart;
      if (!chartDom) return;
      
      this.ecdfChartInstance = echarts.init(chartDom);
      
      if (this.ecdfLoading) {
           this.ecdfChartInstance.showLoading({ // 自定义加载样式
               text: '正在加载数据...',
               color: '#409EFF',
               textColor: '#333',
               maskColor: 'rgba(255, 255, 255, 0.8)',
               zlevel: 0
           });
           return; 
      }

      // 配置 ECharts 选项
      const option = {
        // color: ['#5470C6', '#91CC75'], // 可以自定义颜色系列
        tooltip: { 
          trigger: 'axis',
          backgroundColor: 'rgba(50, 50, 50, 0.9)',
          borderColor: '#aaa',
          borderWidth: 1,
          textStyle: {
              color: '#fff'
          },
          axisPointer: {
            type: 'cross',
            label: {
              backgroundColor: '#6a7985'
            }
          },
          formatter: function(params) {
            if (!params || params.length === 0) return '';
            let result = `发生次数: ${params[0].data[0]}<br/>`;
            params.forEach(param => {
              if (param.data && Array.isArray(param.data) && param.data.length > 1) {
                const probability = (param.data[1] * 100).toFixed(1);
                result += `${param.marker}${param.seriesName}: ${probability}%<br/>`;
              }
            });
            return result;
          }
        },
        legend: {
          data: [
            {
              name: '1982-2002年',
              icon: 'rect',
              itemWidth: 14,
              itemHeight: 14
            },
            {
              name: '2003-2022年',
              icon: 'rect',
              itemWidth: 14,
              itemHeight: 14
            }
          ],
          top: 'bottom',
          selected: this.seriesVisibility
        },
        grid: { 
          left: '5%', // 稍微增加左边距给 Y 轴标签
          right: '5%', 
          bottom: '12%', // 为图例留出更多空间
          containLabel: true
        },
        xAxis: { 
          type: 'value', 
          name: '发生次数', 
          nameLocation: 'middle', 
          nameGap: 30, // 增加与轴的距离
          nameTextStyle: {
              fontSize: 14,
              fontWeight: 'bold'
          },
          min: 0,
          axisLine: { show: true, lineStyle: { color: '#666' } }, // 显示轴线
          axisTick: { show: true, lineStyle: { color: '#666' } }, // 显示刻度
          splitLine: { // 网格线样式
              show: true,
              lineStyle: {
                  color: '#E0E6F1', // 更浅的网格线
                  type: 'dashed' // 虚线
              }
          },
           axisLabel: { color: '#333' } // 轴标签颜色
        },
        yAxis: { 
          type: 'value', 
          name: 'ECDF (累积概率)', // 更清晰的 Y 轴名称
           nameLocation: 'end', // 名称放在末尾
           nameTextStyle: {
              fontSize: 14,
              fontWeight: 'bold',
              align: 'left' // 左对齐
          },
          min: 0, 
          max: 1, 
          axisLine: { show: true, lineStyle: { color: '#666' } }, 
          axisTick: { show: true, lineStyle: { color: '#666' } },
          splitLine: { 
              show: true,
              lineStyle: {
                  color: '#E0E6F1',
                  type: 'dashed'
              }
           },
           axisLabel: { 
               color: '#333',
               formatter: '{value}' // 可以改为百分比: v => (v*100)+'%' 
            }
        },
        series: [
          {
            name: '1982-2002年',
            type: 'line',
            smooth: false, 
            step: 'end', 
            data: this.ecdfData1, 
             symbol: 'none', 
             lineStyle: { width: 2, color: '#5470C6' }, // 指定颜色
             emphasis: { focus: 'series', lineStyle: { width: 3.5 } } // 加粗更明显
          },
          {
            name: '2003-2022年',
            type: 'line',
            smooth: false,
            step: 'end',
            data: this.ecdfData2, 
             symbol: 'none',
             lineStyle: { width: 2, color: '#91CC75' }, // 指定颜色
             emphasis: { focus: 'series', lineStyle: { width: 3.5 } }
          }
        ],
        axisPointer: {
          link: {xAxisIndex: 'all'},
          label: {
            backgroundColor: '#777'
          }
        },
      };
      
      this.ecdfChartInstance.setOption(option);
      
      // 监听图例选择事件
      this.ecdfChartInstance.on('legendselectchanged', this.handleLegendSelectChanged);

      window.addEventListener('resize', this.resizeEcdfChart);
    },
    
    resizeEcdfChart() { /* ... (保持不变) ... */ },
    disposeEcdfChart() { /* ... (保持不变) ... */ },
    handleEcdfCommand(command) {
        console.log('Dropdown command received:', command); 
        
        if (command === 'all_basins') {
            this.selectedBasin = '所有流域汇总'; 
            this.showEcdfAnalysis(null);      
        } 
        else if (typeof command === 'string' && this.basinOptions.includes(command)) {
            this.selectedBasin = command;      
            this.showEcdfAnalysis(command);    
        } 
        else {
            console.error('Invalid ECDF command:', command);
            this.$message.error('无效的选择。');
        }
    },
    // 打开 ECDF 对话框
    openEcdfDialog() {
      this.selectedBasin = 'all_basins';
      this.ecdfDialogVisible = true;
      this.showEcdfAnalysis(null);
    },

    // 处理流域选择变化
    handleBasinChange(basinName) {
      if (basinName === 'all_basins') {
        this.showEcdfAnalysis(null);
      } else {
        this.showEcdfAnalysis(basinName);
      }
    },

    // 添加一个方法来处理图例选择事件
    handleLegendSelectChanged(params) {
      const { name, selected } = params;
      this.seriesVisibility = { ...this.seriesVisibility, [name]: selected };
      
      // 在选择发生变化时重新设置选项
      this.ecdfChartInstance.setOption({
        legend: {
          selected: this.seriesVisibility
        }
      });
    },
  },
  mounted() {
    this.fetchData();
  },
  beforeDestroy() {
    // 清理工作...
  }
};
</script>
