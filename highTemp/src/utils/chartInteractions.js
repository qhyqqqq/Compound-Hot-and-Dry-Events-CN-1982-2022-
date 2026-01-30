/**
 * 为统计分析图表添加高级鼠标互动效果
 */
export function initializeChartInteractions() {
  // 监听DOM变化，检测新添加的弹窗
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.addedNodes.length > 0) {
        mutation.addedNodes.forEach(node => {
          // 确保是元素节点
          if (node.nodeType !== 1) return;
          
          // 检查是否是统计分析弹窗
          if (node.classList && node.classList.contains('el-dialog__wrapper')) {
            // 延迟处理，确保内容已完全加载
            setTimeout(() => {
              const dialogBody = node.querySelector('.el-dialog__body');
              if (!dialogBody) return;
              
              // 为图片添加3D倾斜效果
              const images = dialogBody.querySelectorAll('img');
              images.forEach(img => {
                img.addEventListener('mousemove', function(e) {
                  const { left, top, width, height } = this.getBoundingClientRect();
                  const x = e.clientX - left;
                  const y = e.clientY - top;
                  
                  // 计算旋转角度，最大±5度
                  const rotateX = ((y / height) * 10 - 5).toFixed(2);
                  const rotateY = (((x / width) * 10 - 5) * -1).toFixed(2);
                  
                  // 应用3D变换
                  this.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
                });
                
                img.addEventListener('mouseleave', function() {
                  this.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
                });
              });
              
              // 为图表添加鼠标追随光晕效果
              const chartContainers = dialogBody.querySelectorAll('.chart-container, [class*="chart"], [class*="graph"], .echarts');
              chartContainers.forEach(chart => {
                chart.style.position = 'relative';
                chart.style.overflow = 'hidden';
                
                const glow = document.createElement('div');
                glow.classList.add('chart-glow-effect');
                glow.style.cssText = `
                  position: absolute;
                  width: 150px;
                  height: 150px;
                  background: radial-gradient(circle, rgba(255,211,123,0.3) 0%, rgba(255,211,123,0) 70%);
                  border-radius: 50%;
                  pointer-events: none;
                  transform: translate(-50%, -50%);
                  opacity: 0;
                  transition: opacity 0.3s ease;
                  z-index: 1;
                `;
                
                chart.appendChild(glow);
                
                chart.addEventListener('mousemove', function(e) {
                  const rect = this.getBoundingClientRect();
                  const x = e.clientX - rect.left;
                  const y = e.clientY - rect.top;
                  
                  glow.style.left = `${x}px`;
                  glow.style.top = `${y}px`;
                  glow.style.opacity = '1';
                });
                
                chart.addEventListener('mouseleave', function() {
                  glow.style.opacity = '0';
                });
              });
              
              // 为统计数据项添加鼠标悬停高亮
              const dataItems = dialogBody.querySelectorAll('.data-item, .stat-item, [class*="data-"], [class*="stat-"], .el-table__row');
              dataItems.forEach(item => {
                item.addEventListener('mouseenter', function() {
                  // 保存原始样式
                  this.dataset.originalBackground = this.style.background;
                  this.dataset.originalZIndex = this.style.zIndex;
                  
                  // 添加临时样式
                  this.style.background = 'rgba(255, 211, 123, 0.1)';
                  this.style.zIndex = '10';
                });
                
                item.addEventListener('mouseleave', function() {
                  // 恢复原始样式
                  this.style.background = this.dataset.originalBackground || '';
                  this.style.zIndex = this.dataset.originalZIndex || '';
                });
              });
            }, 300);
          }
        });
      }
    });
  });
  
  // 开始观察文档
  observer.observe(document.body, { 
    childList: true,
    subtree: false
  });
} 