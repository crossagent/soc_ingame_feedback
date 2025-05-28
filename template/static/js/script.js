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

    const getBugInfoButton = document.getElementById('get-bug-info-button');
    if (getBugInfoButton) {
        getBugInfoButton.addEventListener('click', async function() {
            console.log('获取 Bug 信息 button clicked');
            try {
                const response = await fetch(`/sessions/${currentSessionName}/bug_info`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const bugInfo = await response.json();
                console.log('Fetched Bug Info:', bugInfo);

                // Populate the form fields
                if (bugInfo.bug_title) {
                    document.getElementById('bug-title').value = bugInfo.bug_title;
                }
                if (bugInfo.bug_description) {
                    document.getElementById('bug-description').value = bugInfo.bug_description;
                }
                if (bugInfo.steps_to_reproduce) {
                    document.getElementById('steps-to-reproduce').value = bugInfo.steps_to_reproduce;
                }

            } catch (error) {
                console.error('Error fetching bug info:', error);
                // Optionally display an error message to the user
            }
        });
    }
});
