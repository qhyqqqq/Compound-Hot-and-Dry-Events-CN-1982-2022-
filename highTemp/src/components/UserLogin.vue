<template>
  <div class="login-container">
    <div class="login-background"></div>
    
    <div class="login-card">
      <div class="login-logo">
        <i class="el-icon-cloudy-and-sunny"></i>
      </div>
      
      <h1 class="login-title">复合高温干旱灾害监测系统</h1>
      <h3 class="login-subtitle">ERA5-Land数据驱动的长时间序列复合高温干旱事件监测平台</h3>
      
      <div class="login-form">
        <el-form ref="loginForm" :model="loginForm" :rules="loginRules">
          <el-form-item prop="username">
            <el-input 
              v-model="loginForm.username" 
              prefix-icon="el-icon-user" 
              placeholder="请输入用户名"
              clearable>
            </el-input>
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input 
              v-model="loginForm.password" 
              prefix-icon="el-icon-lock" 
              placeholder="请输入密码" 
              show-password
              @keyup.enter.native="login">
            </el-input>
          </el-form-item>
          
          <el-form-item class="remember-me">
            <el-checkbox v-model="rememberMe">记住我</el-checkbox>
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              class="login-button" 
              :loading="loading" 
              @click="login">
              登录
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <div class="login-footer">
        <p>© {{ new Date().getFullYear() }} 滁州学院空间信息与数字技术专业21级毕业设计</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      loginForm: {
        username: '',
        password: ''
      },
      loginRules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' }
        ]
      },
      rememberMe: false,
      loading: false
    };
  },
  methods: {
    login() {
      this.$refs.loginForm.validate(valid => {
        if (valid) {
          this.loading = true;
          
          // 模拟登录过程
          setTimeout(() => {
            localStorage.setItem('isLoggedIn', 'true');
            this.$router.push('/spi');
            this.loading = false;
            
            this.$notify({
              title: '登录成功',
              message: '欢迎使用灾害监测系统',
              type: 'success',
              position: 'bottom-right',
              duration: 3000
            });
          }, 1500);
        } else {
          return false;
        }
      });
    }
  },
  mounted() {
    // 检查是否有保存的登录状态
    if (localStorage.getItem('isLoggedIn') === 'true') {
      this.$router.push('/spi');
    }
    
    // 添加动画效果
    document.querySelector('.login-card').classList.add('show');
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  overflow: hidden;
  background-color: #f5f7fa;
  position: relative;
}

.login-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: linear-gradient(135deg, rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.3)), url('~@/assets/logo.jpg');
  background-size: cover;
  background-position: center;
  z-index: 0;
}

.login-card {
  width: 400px;
  padding: 40px;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  position: relative;
  z-index: 1;
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.8s ease;
}

.login-card.show {
  opacity: 1;
  transform: translateY(0);
}

.login-logo {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.login-logo i {
  font-size: 64px;
  color: #f39c12;
  animation: pulse 2s infinite;
}

.login-title {
  font-size: 24px;
  font-weight: 600;
  text-align: center;
  color: #303133;
  margin-bottom: 8px;
}

.login-subtitle {
  font-size: 14px;
  font-weight: 400;
  text-align: center;
  color: #606266;
  margin-bottom: 30px;
}

.login-form {
  margin-bottom: 20px;
}

.el-input {
  margin-bottom: 10px;
}

.login-button {
  width: 100%;
  height: 44px;
  border-radius: 22px;
  font-size: 16px;
  background: linear-gradient(45deg, #f39c12, #e67e22);
  border: none;
  transition: all 0.3s;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(230, 126, 34, 0.4);
}

.login-button:active {
  transform: translateY(0);
}

.remember-me {
  margin-bottom: 20px;
  color: #606266;
}

.login-footer {
  text-align: center;
  font-size: 12px;
  color: #909399;
  margin-top: 30px;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

/* 响应式设计 */
@media screen and (max-width: 480px) {
  .login-card {
    width: 90%;
    padding: 30px;
  }
  
  .login-title {
    font-size: 20px;
  }
  
  .login-subtitle {
    font-size: 12px;
  }
}
</style>
