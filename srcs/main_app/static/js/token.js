let pid = setInterval(() => {
  console.log('SOMETHING');
  fetch("/renew_token")
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
    })
    .catch(() => {
      console.log('FAIL TOKEN');
      engine('/login');
    });
}, 60 * 1000 * 60);
