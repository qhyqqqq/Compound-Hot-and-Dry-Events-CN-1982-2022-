/**
 * 为所有按钮添加波纹和鼠标跟随效果
 */
export function initializeButtonEffects() {
  // 添加波纹效果
  document.addEventListener('click', function(e) {
    // 检查点击的是否是按钮元素
    const isButton = e.target.matches('.el-button, .func-button, button, [class*="button"], [role="button"]') ||
                     e.target.closest('.el-button, .func-button, button, [class*="button"], [role="button"]');
    
    if (isButton) {
      const button = e.target.matches('.el-button, .func-button, button, [class*="button"], [role="button"]') 
                   ? e.target 
                   : e.target.closest('.el-button, .func-button, button, [class*="button"], [role="button"]');
      
      // 创建波纹元素
      const ripple = document.createElement('span');
      ripple.classList.add('ripple');
      
      // 计算位置
      const rect = button.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      ripple.style.left = `${x}px`;
      ripple.style.top = `${y}px`;
      
      // 添加到按钮
      button.appendChild(ripple);
      
      // 动画结束后移除
      setTimeout(() => {
        ripple.remove();
      }, 600);
    }
  });
  
  // 添加鼠标跟随效果
  document.addEventListener('mousemove', function(e) {
    const button = e.target.matches('.el-button, .func-button, button, [class*="button"], [role="button"]') 
                 ? e.target 
                 : e.target.closest('.el-button, .func-button, button, [class*="button"], [role="button"]');
    
    if (button) {
      const rect = button.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      const percentX = Math.round((x / button.offsetWidth) * 100);
      const percentY = Math.round((y / button.offsetHeight) * 100);
      
      button.style.setProperty('--x', percentX + '%');
      button.style.setProperty('--y', percentY + '%');
    }
  });
} 