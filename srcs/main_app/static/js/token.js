let pid = setInterval(() => {
    console.log('inside');
    console.log('inside');
    fetch("/renew_token")
        .then(response => {
            if (!response.ok) {
                return response.json().then(body => {
                    throw new Error(body.error || 'Network response was not ok');
                });
            }
        })
        .catch((error) => {
            clearInterval(pid);
            console.log(error.message);
            showError(`Failed to renew access_token, please logout. [${error.message}]`, 'logout', () => {
                engine('/logout')
            });
        });
}, 5000);
