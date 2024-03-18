navBar = document.getElementsByClassName('navigationBar')[0]

friends = document.getElementsByClassName('friendName')

navBar.addEventListener("mouseover", (event) => {
  for (let i = 0; i < friends.length; i++) {
    friends[i].style.width = '75%!important';
    friends[i].style.display = 'flex';
  }

});
navBar.addEventListener("mouseout", (event) => {
  for (let i = 0; i < friends.length; i++) {
    friends[i].style.width = '0px!impotant';
    friends[i].style.display = 'none';
  }

});
