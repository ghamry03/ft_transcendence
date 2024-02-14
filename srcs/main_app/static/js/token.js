// setInterval(() => {
//   fetch("/renew_token")
//     .catch(() => {
//       engine('login/', 'false', 0);
//     });
//   console.log('ttttttttt');
// }, 10000);
let pid = setInterval(() => {
  console.log("renewing thingy");
  // fetch("/token")
  //   .then(response => {
  //     if (!response.ok) {
  //       throw new Error('Network response was not ok');
  //     }
  //   })
  //   .catch(error => {
  //     console.error('There was a problem with the fetch operation:', error);
  //     fetchPage("/login", "#mainContentArea");
  //   });
}, 1000);
