function getToken(){
    return sessionStorage.getItem('accessToken');
}

document.addEventListener("DOMContentLoaded", () => {
    if(document.getElementById("loginForm")){
        handleLoginPage();
    }
    if (document.getElementById('uploadForm')) {
        handleUploadPage();
    }
});

function handleLoginPage(){
    const loginForm = document.getElementById("loginForm");
    const loginMessage = document.getElementById("loginMessage");
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        loginMessage.textContent = "正在登录...";
        const username = loginForm.username.value;
        const password = loginForm.password.value;

        const formData = new URLSearchParams();
        formData.append("username", username);
        formData.append("password", password);
        try{
            const response = await fetch("/users/token", {
                method: "POST",
                body: formData,
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            });

            const data = await response.json();
            if(!response.ok){
                throw new Error(data.detail || "登录失败");
            }

            loginMessage.textContent = "登录成功！正在跳转...";
            sessionStorage.setItem("accessToken", data.access_token);

            setTimeout(() => {
                window.location.href = "/static/index.html";
            }, 500);
        } catch (error) {
            loginMessage.textContent = `错误: ${error.message}`;
        }
    });
}

function handleUploadPage(){
    const token = getToken();
    if(!token){
        alert("请先登录!");
        window.location.href = "/static/login.html";
        return;
    };
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');
    const uploadResult = document.getElementById('uploadResult');
    uploadForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        uploadResult.textContent = '上传中...';
        const file = fileInput.files[0];
        if(!file){
            uploadResult.textContent = '请选择一个文件！';
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
        } catch(error){
            uploadResult.textContent = `错误: ${error.message}`;
            if(error.message.includes('401')){
                sessionStorage.removeItem("accessToken");
                alert("登录已过期，请重新登录!");
                window.location.href = "/static/login.html";
            }
        }
    });
}