<template>
  <div class="home">
    <!-- 头部导航栏 -->
    <div class="header">
      <!-- 左侧：系统标题 -->
      <div class="header-left">
        <div class="logo-container">
          <div class="icon-placeholder">
            <i class="el-icon-monitor"></i>
          </div>
          <div class="title-container" @click="showSystemInfo">
            <h1 class="main-title">ERA5-Land数据驱动</h1>
            <p class="sub-title">长时间序列复合高温干旱灾害监测</p>
          </div>
        </div>
      </div>
      
      <!-- 中间：菜单导航 -->
      <div class="header-center">
        <el-menu
          :default-active="currentRoute"
          mode="horizontal"
          class="el-menu-horizontal-demo"
          text-color="#333"
          active-text-color="#D46F03"
          background-color="transparent"
          router
        >
          <el-menu-item index="/spi">
            <i class="el-icon-data-analysis"></i>
            <span slot="title">SPI指数</span>
          </el-menu-item>
          <el-menu-item index="/spei">
            <i class="el-icon-data-line"></i>
            <span slot="title">SPEI指数</span>
          </el-menu-item>
          <el-menu-item index="/Hwmid">
            <i class="el-icon-hot-water"></i>
            <span slot="title">HWMId指数</span>
          </el-menu-item>
          <el-menu-item index="/high">
            <i class="el-icon-warning"></i>
            <span slot="title">复合灾害识别</span>
          </el-menu-item>
          <el-menu-item index="/data">
            <i class="el-icon-folder-opened"></i>
            <span slot="title">灾害事件管理</span>
          </el-menu-item>
        </el-menu>
      </div>
      
      <!-- 右侧：天气信息和用户信息 -->
      <div class="header-right">
        <div class="weather-card" @click="fetchWeather">
          <div class="weather-icon">
            <i :class="getWeatherIcon()"></i>
          </div>
          <div class="weather-details">
            <div class="weather-location">{{ weather.location }}</div>
            <div class="weather-data">
              <span class="weather-temp">{{ weather.temperature }}°C</span>
              <span class="weather-desc">{{ weather.description }}</span>
            </div>
            <div class="weather-update-time" v-if="weather.lastUpdate">
              {{ formatLastUpdate() }}
            </div>
          </div>
        </div>
        
        <!-- 全屏按钮 -->
        <div class="fullscreen-btn" @click="toggleFullScreen">
          <i :class="isFullScreen ? 'el-icon-close' : 'el-icon-full-screen'"></i>
        </div>
        
        <el-dropdown class="user-dropdown" @command="handleCommand">
          <span class="user-dropdown-link">
            <i class="el-icon-user"></i>
            <i class="el-icon-arrow-down el-icon--right"></i>
          </span>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item command="profile">个人资料</el-dropdown-item>
            <el-dropdown-item command="settings">系统设置</el-dropdown-item>
            <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
      </div>
    </div>
    
    <!-- 主体内容（地图区域） -->
    <div class="main-content">
      <transition name="router-view" mode="out-in">
        <router-view />
      </transition>
    </div>
    
    <!-- 页脚信息 -->
    <div class="footer">
      <p>© {{ currentYear }} ERA5-Land数据监测系统 | 版本 v1.0.0</p>
      <div class="footer-links">
        <a href="#" @click.prevent="showSystemInfo">关于系统</a>
      </div>
    </div>
    
    <!-- 个人资料弹窗 -->
    <el-dialog
      title="个人资料"
      :visible.sync="profileDialogVisible"
      width="500px"
      center
    >
      <el-form ref="profileForm" :model="userProfile" label-width="80px">
        <el-form-item label="姓名">
          <el-input v-model="userProfile.name" :disabled="!isEditing"></el-input>
        </el-form-item>
        <el-form-item label="学校">
          <el-input v-model="userProfile.school" :disabled="!isEditing"></el-input>
        </el-form-item>
        <el-form-item label="学号">
          <el-input v-model="userProfile.studentId" :disabled="!isEditing"></el-input>
        </el-form-item>
        <el-form-item label="生日">
          <el-date-picker
            v-model="userProfile.birthday"
            type="date"
            placeholder="选择日期"
            format="yyyy-MM-dd"
            :disabled="!isEditing"
            style="width: 100%"
          ></el-date-picker>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="toggleEdit" v-if="!isEditing">编辑</el-button>
        <el-button @click="cancelEdit" v-if="isEditing">取消</el-button>
        <el-button type="primary" @click="saveProfile" v-if="isEditing">保存</el-button>
        <el-button @click="profileDialogVisible = false" v-if="!isEditing">关闭</el-button>
      </div>
    </el-dialog>
    
    <!-- 系统设置弹窗 -->
    <el-dialog
      title="系统设置"
      :visible.sync="settingsDialogVisible"
      width="500px"
      center
    >
      <el-form ref="settingsForm" :model="systemSettings" label-width="120px">
        <el-form-item label="主题设置">
          <el-radio-group v-model="systemSettings.theme">
            <el-radio label="light">明亮模式</el-radio>
            <el-radio label="dark">暗黑模式</el-radio>
            <el-radio label="auto">跟随系统</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="数据刷新频率">
          <el-select v-model="systemSettings.refreshRate" placeholder="选择刷新频率" style="width: 100%">
            <el-option label="实时（每分钟）" value="1"></el-option>
            <el-option label="每5分钟" value="5"></el-option>
            <el-option label="每15分钟" value="15"></el-option>
            <el-option label="每30分钟" value="30"></el-option>
            <el-option label="每小时" value="60"></el-option>
            <el-option label="手动刷新" value="0"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="地图显示设置">
          <el-checkbox-group v-model="systemSettings.mapOptions">
            <el-checkbox label="showBorders">显示行政边界</el-checkbox>
            <el-checkbox label="showLegend">显示图例</el-checkbox>
            <el-checkbox label="show3D">启用3D视图</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="默认查询时长">
          <el-select v-model="systemSettings.defaultTimeRange" placeholder="选择默认时长" style="width: 100%">
            <el-option label="最近一周" value="7days"></el-option>
            <el-option label="最近一个月" value="1month"></el-option>
            <el-option label="最近三个月" value="3months"></el-option>
            <el-option label="最近一年" value="1year"></el-option>
            <el-option label="全部数据" value="all"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="界面缩放">
          <el-slider v-model="systemSettings.uiScale" :min="80" :max="120" :step="10" show-stops :format-tooltip="formatUIScale"></el-slider>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="resetSettings">恢复默认设置</el-button>
        <el-button type="primary" @click="saveSettings">保存设置</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  data() {
    return {
      weather: {
        location: "滁州市",
        temperature: "--",
        description: "加载中...",
        lastUpdate: null,
      },
      currentRoute: '/spi',
      currentYear: new Date().getFullYear(),
      theme: "light",
      profileDialogVisible: false,
      settingsDialogVisible: false,
      userProfile: {
        name: "齐宏宇",
        school: "滁州学院",
        studentId: "2021212022",
        birthday: "2003-08-20"
      },
      userProfileBackup: null,
      systemSettings: {
        theme: "light",
        refreshRate: "15",
        mapOptions: ["showBorders", "showLegend"],
        defaultTimeRange: "1month",
        uiScale: 100
      },
      showCoordinates: true,
      coordinates: "纬度: 60.4309, 经度: 62.3497",
      isFullScreen: false,
      isEditing: false,
    };
  },
  watch: {
    '$route'(to) {
      this.currentRoute = to.path;
    }
  },
  methods: {
    showUserInfoPopup() {
      this.$alert("用户信息详情", "用户信息", {
        confirmButtonText: "确定",
      });
    },
    logout() {
      localStorage.setItem("isLoggedIn", "false");
      this.$router.push("/login");
      this.$message({
        type: "success",
        message: "用户已退出",
      });
    },
    async fetchWeather() {
      // 添加加载状态
      this.weather.description = "更新中...";
      
      // 添加旋转动画
      const weatherCard = document.querySelector('.weather-card');
      weatherCard.classList.add('refreshing');
      
      const apiKey = "02826a7e6dd187767204762ffa0f08ba";
      const url = `https://api.openweathermap.org/data/2.5/weather?q=Chuzhou,cn&appid=${apiKey}&units=metric&lang=zh_cn`;

      try {
        const response = await fetch(url);
        const data = await response.json();
        this.weather.temperature = Math.round(data.main.temp);
        this.weather.description = data.weather[0].description;
        this.weather.lastUpdate = new Date();
        
        // 显示更新成功提示
        this.$message({
          message: '天气数据已更新',
          type: 'success',
          duration: 2000
        });
      } catch (err) {
        console.error("获取天气数据失败", err);
        this.weather.description = "更新失败";
        
        // 显示错误提示
        this.$message.error('天气数据更新失败');
      } finally {
        // 移除旋转动画
        setTimeout(() => {
          weatherCard.classList.remove('refreshing');
        }, 1000);
      }
    },
    showSystemInfo() {
      this.$alert(
        "ERA5-Land是气候预测系统的再分析数据集，提供高分辨率的土地参数信息。本系统基于该数据集，实现了对复合高温干旱灾害的长时间序列监测与分析。",
        "系统信息",
        { confirmButtonText: "确定" }
      );
    },
    showUserProfile() {
      this.profileDialogVisible = true;
      this.isEditing = false;
    },
    toggleEdit() {
      this.isEditing = true;
      // 备份当前数据，用于取消编辑
      this.userProfileBackup = JSON.parse(JSON.stringify(this.userProfile));
    },
    cancelEdit() {
      this.isEditing = false;
      // 恢复备份的数据
      if (this.userProfileBackup) {
        this.userProfile = JSON.parse(JSON.stringify(this.userProfileBackup));
      }
    },
    saveProfile() {
      this.$message.success('个人资料已保存');
      this.isEditing = false;
      // 保存个人资料到本地存储
      localStorage.setItem('userProfile', JSON.stringify(this.userProfile));
    },
    showSettings() {
      this.settingsDialogVisible = true;
    },
    resetSettings() {
      this.systemSettings = {
        theme: "light",
        refreshRate: "15",
        mapOptions: ["showBorders", "showLegend"],
        defaultTimeRange: "1month",
        uiScale: 100
      };
      this.$message.info('已重置为默认设置');
    },
    saveSettings() {
      this.$message.success('设置已保存');
      this.settingsDialogVisible = false;
      
      // 应用主题设置
      document.body.className = this.systemSettings.theme;
      
      // 应用UI缩放
      document.documentElement.style.fontSize = `${this.systemSettings.uiScale}%`;
      
      // 保存设置到本地存储
      localStorage.setItem('systemSettings', JSON.stringify(this.systemSettings));
    },
    formatUIScale(value) {
      return value + '%';
    },
    getWeatherIcon() {
      // 根据天气描述返回适当的图标
      const desc = this.weather.description.toLowerCase();
      if (desc.includes("晴")) return "el-icon-sunny";
      if (desc.includes("云")) return "el-icon-partly-cloudy";
      if (desc.includes("雨")) return "el-icon-umbrella";
      if (desc.includes("雪")) return "el-icon-heavy-rain";
      return "el-icon-cloudy"; // 默认图标
    },
    getCurrentPageName() {
      const nameMap = {
        '/spi': 'SPI指数分析',
        '/spei': 'SPEI指数分析',
        '/Hwmid': 'HWMId热浪指数分析',
        '/high': '复合高温干旱灾害事件识别',
        '/data': '灾害事件管理与查询'
      };
      return nameMap[this.currentRoute] || '系统首页';
    },
    toggleTheme() {
      this.theme = this.theme === 'light' ? 'dark' : 'light';
      document.body.className = this.theme;
      localStorage.setItem('theme', this.theme);
    },
    handleCommand(command) {
      switch(command) {
        case 'profile':
          this.showUserProfile();
          break;
        case 'settings':
          this.showSettings();
          break;
        case 'logout':
          this.logout();
          break;
      }
    },
    toggleFullScreen() {
      if (!document.fullscreenElement) {
        // 进入全屏模式
        document.documentElement.requestFullscreen().then(() => {
          this.isFullScreen = true;
        }).catch(err => {
          this.$message.error(`全屏模式出错: ${err.message}`);
        });
      } else {
        // 退出全屏模式
        document.exitFullscreen().then(() => {
          this.isFullScreen = false;
        }).catch(err => {
          this.$message.error(`退出全屏出错: ${err.message}`);
        });
      }
    },
    formatLastUpdate() {
      if (!this.weather.lastUpdate) return '';
      const now = new Date();
      const diff = Math.floor((now - this.weather.lastUpdate) / 1000 / 60); // 转换为分钟
      
      if (diff < 1) return '刚刚更新';
      if (diff < 60) return `${diff}分钟前更新`;
      return `${Math.floor(diff / 60)}小时前更新`;
    }
  },
  mounted() {
    // 初始加载天气数据
    this.fetchWeather();
    
    // 设置30分钟自动刷新
    this.weatherInterval = setInterval(this.fetchWeather, 30 * 60 * 1000);
    
    // 加载保存的个人资料
    const savedProfile = localStorage.getItem('userProfile');
    if (savedProfile) {
      this.userProfile = JSON.parse(savedProfile);
    }
    
    // 加载保存的系统设置
    const savedSettings = localStorage.getItem('systemSettings');
    if (savedSettings) {
      this.systemSettings = JSON.parse(savedSettings);
      
      // 应用主题设置
      document.body.className = this.systemSettings.theme;
      
      // 应用UI缩放
      document.documentElement.style.fontSize = `${this.systemSettings.uiScale}%`;
    }
    
    // 初始化当前模块名称
    this.currentRoute = this.$route.path;
    
    // 恢复保存的主题设置
    const savedTheme = localStorage.getItem('theme') || 'light';
    this.theme = savedTheme;
    document.body.className = savedTheme;
    
    // 监听全屏状态变化
    document.addEventListener('fullscreenchange', () => {
      this.isFullScreen = !!document.fullscreenElement;
    });
    
    // 添加按钮波纹效果
    this.$nextTick(() => {
      const buttons = document.querySelectorAll('.func-button, .el-button');
      buttons.forEach(button => {
        button.addEventListener('click', function(e) {
          const x = e.clientX - this.getBoundingClientRect().left;
          const y = e.clientY - this.getBoundingClientRect().top;
          
          const ripple = document.createElement('span');
          ripple.classList.add('ripple');
          ripple.style.left = `${x}px`;
          ripple.style.top = `${y}px`;
          
          this.appendChild(ripple);
          
          setTimeout(() => {
            ripple.remove();
          }, 600);
        });
        
        // 添加鼠标跟随效果
        button.addEventListener('mousemove', function(e) {
          const x = e.clientX - this.getBoundingClientRect().left;
          const y = e.clientY - this.getBoundingClientRect().top;
          const percentX = Math.round((x / this.offsetWidth) * 100);
          const percentY = Math.round((y / this.offsetHeight) * 100);
          
          this.style.setProperty('--x', percentX + '%');
          this.style.setProperty('--y', percentY + '%');
        });
      });
      
      // 弹窗鼠标跟随效果
      const addDialogEffect = () => {
        const dialogs = document.querySelectorAll('.el-dialog');
        dialogs.forEach(dialog => {
          const dialogBody = dialog.querySelector('.el-dialog__body');
          if (!dialogBody) return;
          
          dialog.addEventListener('mousemove', function(e) {
            const dialogRect = this.getBoundingClientRect();
            const centerX = dialogRect.width / 2;
            const centerY = dialogRect.height / 2;
            
            const mouseX = e.clientX - dialogRect.left;
            const mouseY = e.clientY - dialogRect.top;
            
            const moveX = (mouseX - centerX) / 25;
            const moveY = (mouseY - centerY) / 25;
            
            if (dialogBody) {
              dialogBody.style.transform = `translate3d(${moveX}px, ${moveY}px, 0)`;
            }
          });
          
          dialog.addEventListener('mouseleave', function() {
            if (dialogBody) {
              dialogBody.style.transform = 'translate3d(0, 0, 0)';
            }
          });
        });
        
        // 给弹窗内容添加依次淡入效果
        const dialogBodies = document.querySelectorAll('.el-dialog__body');
        dialogBodies.forEach(body => {
          const children = Array.from(body.children);
          children.forEach((child, index) => {
            child.style.setProperty('--index', index);
          });
        });
      };
      
      // 监听弹窗打开事件
      const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          if (mutation.addedNodes.length > 0) {
            // 检查是否添加了弹窗
            const addedDialogs = Array.from(mutation.addedNodes).filter(
              node => node.nodeType === 1 && node.classList && node.classList.contains('el-dialog__wrapper')
            );
            
            if (addedDialogs.length > 0) {
              setTimeout(addDialogEffect, 100);
            }
          }
        });
      });
      
      observer.observe(document.body, { childList: true, subtree: false });
      
      // 给上传项添加渐入效果
      const uploadItems = document.querySelectorAll('.upload-item');
      uploadItems.forEach((item, index) => {
        item.style.setProperty('--index', index);
      });
    });
  },
  beforeDestroy() {
    // 组件销毁前清除定时器
    if (this.weatherInterval) {
      clearInterval(this.weatherInterval);
    }
  }
};
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f6f8fa;
  overflow-x: hidden;
}

/* 头部区域 */
.header {
  position: fixed;
  width: 100%;
  top: 0;
  z-index: 1000;
  height: 70px;
  display: flex;
  align-items: center;
  padding: 0;
  background: linear-gradient(to right, #ffd37b, #ffedb2); /* 渐变背景 */
  color: #444;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

/* 左侧标题区域优化 */
.header-left {
  width: 22%;
  padding: 0 20px;
  height: 100%;
  display: flex;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.2);
  border-right: 1px solid rgba(0, 0, 0, 0.05);
}

.logo-container {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 10px 0;
}

.icon-placeholder {
  width: 45px;
  height: 45px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
}

.icon-placeholder:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.12);
  background: rgba(255, 255, 255, 0.8);
}

.icon-placeholder i {
  font-size: 24px;
  color: #D46F03;
}

.main-title {
  font-size: 22px;
  font-weight: 700;
  margin: 0;
  color: #333;
  white-space: nowrap;
  letter-spacing: 1px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
}

.sub-title {
  font-size: 14px;
  margin: 4px 0 0;
  color: #D46F03;
  letter-spacing: 0.5px;
  font-weight: 600;
  background: linear-gradient(45deg, #D46F03, #FF9F45);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.title-container {
  padding: 2px 0;
  transition: transform 0.3s ease;
}

.title-container:hover {
  transform: translateY(-2px);
}

/* 中间导航菜单优化 */
.header-center {
  width: 55%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0 10px;
}

.el-menu-horizontal-demo {
  display: flex;
  justify-content: space-around;
  width: 100%;
  height: 100%;
  border: none !important;
  background-color: transparent !important;
}

.el-menu-item {
  height: 70px;
  line-height: 70px;
  padding: 0 22px;
  margin: 0 5px;
  border-radius: 0;
  transition: all 0.3s;
  position: relative;
  border-bottom: 3px solid transparent;
}

.el-menu-item::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 3px;
  background-color: #D46F03;
  transform: translateX(-50%);
  transition: width 0.3s ease;
}

.el-menu-item:hover::after,
.el-menu-item.is-active::after {
  width: 70%;
}

.el-menu-item:hover {
  background-color: rgba(255, 255, 255, 0.2) !important;
  color: #D46F03;
}

.el-menu-item.is-active {
  background-color: rgba(255, 255, 255, 0.3) !important;
  font-weight: bold;
  color: #D46F03 !important;
}

.el-menu-item i {
  margin-right: 6px;
  font-size: 18px;
}

/* 右侧功能区域优化 */
.header-right {
  width: 23%;
  height: 100%;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 15px;
  padding-right: 25px;
  background-color: rgba(255, 255, 255, 0.2);
  border-left: 1px solid rgba(0, 0, 0, 0.05);
}

.weather-card {
  cursor: pointer;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.7);
  padding: 8px 12px;
  border-radius: 50px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
  max-width: 160px;
  margin-right: 10px;
}

.weather-card:active {
  transform: scale(0.95);
}

.weather-update-time {
  font-size: 9px;
  color: #999;
  margin-top: 1px;
}

.weather-icon {
  font-size: 20px;
  color: #D46F03;
  margin-right: 8px;
  flex-shrink: 0;
}

.weather-details {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.weather-location {
  font-size: 12px;
  font-weight: 600;
  color: #555;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.weather-data {
  display: flex;
  align-items: center;
  gap: 4px;
}

.weather-temp {
  font-size: 16px;
  font-weight: bold;
  color: #D46F03;
}

.weather-desc {
  font-size: 11px;
  color: #666;
}

.fullscreen-btn {
  cursor: pointer;
  background: rgba(255, 255, 255, 0.7);
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.fullscreen-btn:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.fullscreen-btn i {
  font-size: 22px;
  color: #D46F03;
}

.user-dropdown-link {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.7);
  padding: 10px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.user-dropdown-link:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.user-dropdown-link i {
  font-size: 20px;
  color: #D46F03;
}

/* 添加额外的视觉细节 */
@media (min-width: 1200px) {
  .el-menu-item::before {
    content: '';
    position: absolute;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    height: 20px;
    width: 1px;
    background-color: rgba(0, 0, 0, 0.05);
  }
  
  .el-menu-item:last-child::before {
    display: none;
  }
}

/* 主体内容 */
.main-content {
  flex-grow: 1;
  padding: 20px;
  margin-top: 70px;
  background-color: #ffffff;
  min-height: calc(100vh - 70px);
  animation: fadeIn 0.6s ease-in;
}

/* 页脚样式 */
.footer {
  background-color: #f0f0f0;
  color: #666;
  text-align: center;
  padding: 15px;
  font-size: 13px;
  border-top: 1px solid #eaeaea;
}

.footer-links {
  margin-top: 5px;
}

.footer-links a {
  color: #D46F03;
  text-decoration: none;
  transition: color 0.3s;
}

.footer-links a:hover {
  color: #b25a00;
  text-decoration: underline;
}

/* 过渡动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
}

/* 响应式调整 */
@media screen and (max-width: 1400px) {
  .header-right {
    width: 30%;
    gap: 15px;
  }
  
  .weather-card {
    margin-right: 10px;
  }
  
  .fullscreen-btn {
    margin-right: 10px;
  }
}

@media screen and (max-width: 1200px) {
  .sub-title {
    display: none;
  }
  
  .el-menu-item {
    padding: 0 10px;
  }
  
  .header-left {
    min-width: 180px;
  }
}

@media screen and (max-width: 992px) {
  .header {
    flex-wrap: wrap;
    height: auto;
    padding: 10px 20px;
  }
  
  .header-left, .header-center, .header-right {
    width: 100%;
    justify-content: center;
    padding: 5px 0;
  }
  
  .main-content {
    margin-top: 150px;
  }
}

/* 当前页面名称 */
.page-indicator {
  height: 40px;
  padding: 0 30px;
  margin-top: 60px;
  background-color: #f9f2e0;
  font-size: 16px;
  color: #333;
  display: flex;
  align-items: center;
}

.location-info {
  display: flex;
  align-items: center;
}

.location-info i {
  margin-right: 8px;
  color: #D46F03;
}

.coordinate-info {
  font-family: monospace;
  color: #888;
}

/* 系统状态指示栏 */
.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background-color: #fff;
  border-bottom: 1px solid #eaeaea;
}

.status-item {
  display: flex;
  align-items: center;
}

.status-item i {
  font-size: 20px;
  margin-right: 5px;
}

.status-item span {
  font-size: 14px;
  font-weight: bold;
}

.breadcrumb {
  display: flex;
  align-items: center;
}

.breadcrumb .el-breadcrumb {
  margin-left: 10px;
}

/* 页面淡入动画 */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 全局动画和过渡效果 */

/* 1. 页面切换动画 */
.router-view-transition {
  transition: all 0.5s cubic-bezier(0.55, 0, 0.1, 1);
}

.router-view-enter-active,
.router-view-leave-active {
  transition: opacity 0.3s, transform 0.4s;
}

.router-view-enter-from,
.router-view-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* 2. 弹窗动画 */
.el-dialog__wrapper {
  perspective: 1200px;
}

.el-dialog {
  transform-origin: center center;
  backface-visibility: hidden;
  transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), 
              opacity 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

/* 弹窗内容跟随鼠标微动效果 */
.el-dialog__body {
  transition: transform 0.2s ease-out;
  transform-style: preserve-3d;
}

/* 上传弹窗增强动画 */
.upload-container {
  transition: all 0.3s ease;
}

.upload-item {
  transform: translateY(10px);
  opacity: 0;
  animation: fadeInUp 0.4s forwards;
  animation-delay: calc(var(--index) * 0.1s);
}

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 按钮鼠标跟随光晕效果 */
.func-button::before,
.el-button::before {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at var(--x) var(--y), 
              rgba(255, 255, 255, 0.8) 0%, 
              rgba(255, 255, 255, 0) 50%);
  opacity: 0;
  top: 0;
  left: 0;
  transition: opacity 0.3s;
  z-index: 0;
  pointer-events: none;
}

.func-button:hover::before,
.el-button:hover::before {
  opacity: 0.5;
}

/* 图片展示弹窗动画 */
.zoomed-image-container {
  transition: all 0.4s ease;
}

.zoomed-image {
  transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

/* 图片鼠标悬停放大效果 */
.analysis-image {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.analysis-image:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

/* 图片弹窗图片缩放动画 */
.image-container {
  overflow: hidden;
  transition: transform 0.3s ease;
}

/* 控制弹窗元素依次淡入 */
.el-dialog__body > * {
  opacity: 0;
  transform: translateY(10px);
  animation: dialogContentFadeIn 0.5s forwards;
  animation-delay: calc(var(--index, 0) * 0.08s + 0.2s);
}

@keyframes dialogContentFadeIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 按钮悬停和点击动画增强 */
.func-button,
.el-button {
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  transform-style: preserve-3d;
  perspective: 800px;
}

/* 按钮悬停时3D倾斜效果 */
.func-button:hover,
.el-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

/* 按钮点击动画 */
.func-button:active,
.el-button:active {
  transform: translateY(0) scale(0.98);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 按钮波纹点击效果 */
.ripple {
  position: absolute;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.7);
  pointer-events: none;
  transform: scale(0);
  animation: rippleEffect 0.6s linear;
}

@keyframes rippleEffect {
  to {
    transform: scale(20);
    opacity: 0;
  }
}

/* 弹窗展示和关闭动画 */
.el-dialog__wrapper {
  perspective: 1200px;
}

.el-dialog {
  transform-origin: center center;
  backface-visibility: hidden;
  transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), 
              opacity 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

/* 弹窗内容跟随鼠标微动效果 */
.el-dialog__body {
  transition: transform 0.2s ease-out;
  transform-style: preserve-3d;
}

/* 上传弹窗增强动画 */
.upload-container {
  transition: all 0.3s ease;
}

.upload-item {
  transform: translateY(10px);
  opacity: 0;
  animation: fadeInUp 0.4s forwards;
  animation-delay: calc(var(--index) * 0.1s);
}

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 按钮鼠标跟随光晕效果 */
.func-button::before,
.el-button::before {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at var(--x) var(--y), 
              rgba(255, 255, 255, 0.8) 0%, 
              rgba(255, 255, 255, 0) 50%);
  opacity: 0;
  top: 0;
  left: 0;
  transition: opacity 0.3s;
  z-index: 0;
  pointer-events: none;
}

.func-button:hover::before,
.el-button:hover::before {
  opacity: 0.5;
}

/* 图片展示弹窗动画 */
.zoomed-image-container {
  transition: all 0.4s ease;
}

.zoomed-image {
  transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

/* 图片鼠标悬停放大效果 */
.analysis-image {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.analysis-image:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

/* 图片弹窗图片缩放动画 */
.image-container {
  overflow: hidden;
  transition: transform 0.3s ease;
}

/* 控制弹窗元素依次淡入 */
.el-dialog__body > * {
  opacity: 0;
  transform: translateY(10px);
  animation: dialogContentFadeIn 0.5s forwards;
  animation-delay: calc(var(--index, 0) * 0.08s + 0.2s);
}

@keyframes dialogContentFadeIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 保持旋转动画不变 */
.weather-card.refreshing {
  animation: refreshRotate 1s linear;
}

@keyframes refreshRotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>


