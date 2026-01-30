/**
 * 初始化所有弹窗动画效果
 */
export function initializeDialogAnimations() {
  // 监听DOM变化，检测新弹窗
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.addedNodes.length > 0) {
        mutation.addedNodes.forEach(node => {
          // 确保是元素节点
          if (node.nodeType !== 1) return;
          
          // 处理对话框
          if (node.classList && node.classList.contains('el-dialog__wrapper')) {
            const dialog = node.querySelector('.el-dialog');
            if (dialog) {
              // 添加入场动画
              dialog.style.transform = 'scale(0.9) translateY(-20px)';
              dialog.style.opacity = '0';
              
              // 强制重绘
              dialog.offsetHeight;
              
              // 应用动画
              dialog.style.transform = 'scale(1) translateY(0)';
              dialog.style.opacity = '1';
            }
          }
          
          // 处理消息框
          if (node.classList && node.classList.contains('el-message-box__wrapper')) {
            const msgbox = node.querySelector('.el-message-box');
            if (msgbox) {
              msgbox.style.transform = 'translateY(-30px)';
              msgbox.style.opacity = '0';
              
              msgbox.offsetHeight;
              
              msgbox.style.transform = 'translateY(0)';
              msgbox.style.opacity = '1';
            }
          }
          
          // 处理抽屉
          if (node.classList && node.classList.contains('el-drawer__container')) {
            const drawer = node.querySelector('.el-drawer');
            if (drawer) {
              // 抽屉已有内置动画，这里不需要额外处理
            }
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
  
  // 添加弹窗关闭动画
  document.addEventListener('click', (e) => {
    // 检查是否点击了关闭按钮
    if (e.target.classList.contains('el-dialog__headerbtn') || 
        e.target.closest('.el-dialog__headerbtn')) {
      const wrapper = e.target.closest('.el-dialog__wrapper');
      if (wrapper) {
        const dialog = wrapper.querySelector('.el-dialog');
        if (dialog) {
          dialog.style.transition = 'transform 0.3s, opacity 0.3s';
          dialog.style.transform = 'scale(0.9) translateY(20px)';
          dialog.style.opacity = '0';
          
          // 延迟关闭，等待动画完成
          // 注意：这可能不会生效，因为Element UI有自己的关闭逻辑
          // 正式实现可能需要修改Element UI的源代码
        }
      }
    }
  });
  
  // 修复全局输入框样式
  const style = document.createElement('style');
  style.textContent = `
    .el-input-number input.el-input__inner,
    .el-input input.el-input__inner {
      transition: border-color 0.2s cubic-bezier(0.645, 0.045, 0.355, 1);
      transform: none !important;
    }
  `;
  document.head.appendChild(style);
} 