// Add your custom scripts here

document.addEventListener('DOMContentLoaded', () => {
    const readClientLogBtn = document.getElementById('readClientLog');
    const readServerLogBtn = document.getElementById('readServerLog');
    const getScreenshotBtn = document.getElementById('getScreenshot');
    // Removed downloadBtn

    if(readClientLogBtn) {
        readClientLogBtn.addEventListener('click', () => {
            console.log('读取客户端日志 button clicked');
            // Add functionality for reading client log
        });
    }

    if(readServerLogBtn) {
        readServerLogBtn.addEventListener('click', () => {
            console.log('读取服务器日志 button clicked');
            // Add functionality for reading server log
        });
    }

    if(getScreenshotBtn) {
        getScreenshotBtn.addEventListener('click', () => {
            console.log('获取截图 button clicked');
            // Add functionality for getting screenshot
        });
    }

    // Removed downloadBtn related code
});
