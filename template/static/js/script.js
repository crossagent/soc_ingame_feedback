document.addEventListener('DOMContentLoaded', function() {
    const bugReportForm = document.getElementById('bug-report-form');
    const logButton = document.getElementById('log-button');
    const videoButton = document.getElementById('video-button');
    const screenshotButton = document.getElementById('screenshot-button');

    if (bugReportForm) {
        bugReportForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent default form submission

            const formData = new FormData(bugReportForm);
            const bugData = {};
            formData.forEach((value, key) => {
                bugData[key] = value;
            });

            console.log('Bug Report Submitted:', bugData);
            // Here you would typically send the data to your backend
        });
    }

    if (logButton) {
        logButton.addEventListener('click', function() {
            console.log('Extract Logs button clicked');
            // Add functionality to extract logs
        });
    }

    if (videoButton) {
        videoButton.addEventListener('click', function() {
            console.log('Record Video button clicked');
            // Add functionality to record video
        });
    }

    if (screenshotButton) {
        screenshotButton.addEventListener('click', function() {
            console.log('Take Screenshot button clicked');
            // Add functionality to take screenshot
        });
    }
});
