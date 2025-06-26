// 全局JavaScript功能

// 檢查用戶是否已登入
function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        return false;
    }
    return true;
}

// 登出功能
function logout() {
    localStorage.removeItem('token');
    window.location.href = '/';
}

// 頁面加載時檢查認證狀態
document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;
    const protectedPaths = ['/dashboard', '/trip'];
    
    // 檢查是否是受保護的頁面
    const isProtectedPage = protectedPaths.some(path => currentPath.startsWith(path));
    
    if (isProtectedPage && !checkAuth()) {
        window.location.href = '/login';
    }
});

// API請求助手函數
async function apiRequest(url, options = {}) {
    const token = localStorage.getItem('token');
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        }
    };
    
    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(url, mergedOptions);
        
        if (response.status === 401) {
            // Token過期或無效
            localStorage.removeItem('token');
            window.location.href = '/login';
            return;
        }
        
        return response;
    } catch (error) {
        console.error('API請求錯誤:', error);
        throw error;
    }
}

// 格式化日期
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-TW');
}

// 格式化金額
function formatCurrency(amount, currency = 'TWD') {
    return new Intl.NumberFormat('zh-TW', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    }).format(amount);
}

// 顯示成功訊息
function showSuccessMessage(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // 5秒後自動消失
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// 顯示錯誤訊息
function showErrorMessage(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // 5秒後自動消失
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// 確認對話框
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// 載入指示器
function showLoading(element) {
    const originalText = element.textContent;
    element.textContent = '載入中...';
    element.disabled = true;
    
    return function hideLoading() {
        element.textContent = originalText;
        element.disabled = false;
    };
}

// 表單驗證助手
function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Email驗證
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}