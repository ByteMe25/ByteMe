document.addEventListener('DOMContentLoaded', () => {
  const menuToggle = document.getElementById('menu');
  const menuList = menuToggle.querySelector('ul');

  menuToggle.addEventListener('click', () => {
    menuToggle.classList.toggle('open');
    if (menuToggle.classList.contains('open')) {
      menuList.classList.add('show');
    } else {
      menuList.classList.remove('show');
    }
  });

  window.addEventListener('resize', () => {
    if (window.innerWidth > 980) {
      menuToggle.classList.remove('open');
      menuList.classList.remove('show');
    }
  });
});
