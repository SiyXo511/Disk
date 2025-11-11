function getToken(){
    return sessionStorage.getItem('accessToken');
}

function logout(){
    sessionStorage.removeItem("accessToken");
    window.location.href = "/static/login.html";
}

document.addEventListener("DOMContentLoaded", () => {
    if(document.getElementById("loginForm")){
        handleLoginPage();
    }
    if (document.getElementById('uploadForm')) {
        handleUploadPage();
    }
});

function handleLoginPage() {
    const loginForm = document.getElementById('loginForm');
    const loginMessage = document.getElementById('loginMessage');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const button = loginForm.querySelector('button[type="submit"]');
        button.ariaBusy = "true"; // (Pico.css) 显示加载中
        loginMessage.textContent = '登录中...';

        const username = loginForm.username.value;
        const password = loginForm.password.value;
        
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        try {
            const response = await fetch('/users/token', {
                method: 'POST',
                body: formData,
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || '登录失败');

            sessionStorage.setItem('accessToken', data.access_token);
            
            // 登录成功，跳转到 index.html
            // (注意: 我们在 main.py 中把 /static 挂载到了 'frontend' 目录)
            window.location.href = '/static/index.html'; 

        } catch (error) {
            loginMessage.textContent = `错误: ${error.message}`;
            button.ariaBusy = "false";
        }
    });
}

function handleUploadPage(){
    const token = getToken();
    if(!token){
        alert("请先登录!");
        logout();
        return;
    };
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');
    const uploadButton = document.getElementById('uploadButton');
    const uploadResult = document.getElementById('uploadResult');
    const fileListContainer = document.getElementById('fileListContainer');
    const logoutButton = document.getElementById('logoutButton');
    const refreshButton = document.getElementById('refreshButton');
   
    uploadForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        uploadButton.ariaBusy = "true";
        uploadResult.textContent = '上传中...';
        const file = fileInput.files[0];
        if(!file){
            uploadResult.textContent = '请选择一个文件！';
            uploadButton.ariaBusy = "false";
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        try{
            const response = await fetch("/files/upload", {
                method: "POST",
                body: formData,
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            const data = await response.json();
            if(!response.ok){
                throw new Error(data.detail || '上传失败');
            }
            uploadResult.innerHTML = `
                <p><strong>上传成功!</strong></p>
                <p>文件名: ${data.original_filename}</p>
                <p>Unique ID: ${data.unique_id}</p>
                <p><strong>公开访问 URL:</strong></p>
                <a href="/files/download/${data.unique_id}" target="_blank">
                    /files/download/${data.unique_id}
                </a>
            `;

            fileInput.value = "";
            await fetchUserFiles();
        } catch(error){
            uploadResult.textContent = `错误: ${error.message}`;
            if(error.message.includes('401')){
                sessionStorage.removeItem("accessToken");
                alert("登录已过期，请重新登录!");
                window.location.href = "/static/login.html";
            }
        } finally {
            uploadButton.ariaBusy = "false";
        }
    });

    logoutButton.addEventListener('click', (e) => {
        e.preventDefault();
        if (confirm("你确定要退出登录吗？")) {
            logout();
        }
    });

    refreshButton.addEventListener('click', async () => {
        refreshButton.ariaBusy = "true";
        await fetchUserFiles();
        refreshButton.ariaBusy = "false";
    });

    async function fetchUserFiles() {
        fileListContainer.innerHTML = `<p aria-busy="true">正在加载文件...</p>`; // (Pico.css) 加载中
        
        try {
            const response = await fetch('/files/', { // <-- 调用我们新的 GET /files/ API
                method: 'GET',
                headers: { 'Authorization': `Bearer ${token}` }
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || '获取文件列表失败');

            // 渲染文件列表
            renderFileList(data);

        } catch (error) {
            fileListContainer.innerHTML = `<p>错误: ${error.message}</p>`;
            checkAuthError(error);
        }
    }

    // --- (新!) 核心函数：渲染列表 HTML ---
    function renderFileList(files) {
        if (files.length === 0) {
            fileListContainer.innerHTML = `<p>你还没有上传任何文件。</p>`;
            return;
        }

        fileListContainer.innerHTML = ''; // 清空
        files.forEach(file => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            
            // (新!) 格式化文件大小
            const sizeInKB = (file.file_size / 1024).toFixed(1);
            
            // 文件信息 (左侧)
            const fileInfo = document.createElement('div');
            fileInfo.className = 'file-info';
            fileInfo.innerHTML = `
                <strong>${file.original_filename}</strong>
                <br>
                <small>${new Date(file.created_at).toLocaleString()} | ${sizeInKB} KB</small>
            `;
            
            // 操作按钮 (右侧)
            const fileActions = document.createElement('div');
            fileActions.className = 'file-actions';

            const viewButton = document.createElement('button');
            viewButton.textContent = '查看';
            viewButton.className = 'outline';
            viewButton.onclick = () => {
                window.open(`/files/download/${file.unique_id}`, '_blank');
            };

            const deleteButton = document.createElement('button');
            deleteButton.textContent = '删除';
            deleteButton.className = 'secondary'; // (Pico.css) 红色按钮
            deleteButton.onclick = () => {
                // (新!) 绑定删除事件
                handleDeleteClick(file.unique_id, file.original_filename);
            };

            fileActions.appendChild(viewButton);
            fileActions.appendChild(deleteButton);
            
            fileItem.appendChild(fileInfo);
            fileItem.appendChild(fileActions);
            
            fileListContainer.appendChild(fileItem);
        });
    }

    // --- (新!) 核心函数：处理删除点击 ---
    async function handleDeleteClick(uniqueId, filename) {
        if (!confirm(`你确定要删除 "${filename}" 吗？\n这个操作无法撤销！`)) {
            return;
        }

        uploadResult.textContent = `正在删除 ${filename}...`;

        try {
            const response = await fetch(`/files/${uniqueId}`, { // <-- 调用我们新的 DELETE API
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || '删除失败');
            
            uploadResult.textContent = `文件 "${filename}" 已删除。`;
            
            // (新!) 删除成功后，刷新文件列表
            await fetchUserFiles();

        } catch (error) {
            uploadResult.textContent = `错误: ${error.message}`;
            checkAuthError(error);
        }
    }

    // --- (新!) 辅助函数：检查401错误
    function checkAuthError(error) {
        if (error.message.includes('401') || error.message.includes('credentials')) {
            alert('登录已过期，请重新登录。');
            logout();
        }
    }

    // --- 页面加载时，立即获取文件列表 ---
    fetchUserFiles();
}