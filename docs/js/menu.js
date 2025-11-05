document.addEventListener('DOMContentLoaded', () => {
    const menuToggle = document.getElementById('menu');
    const menuList = menuToggle.querySelector('ul');
    menuToggle.addEventListener('click', () => {
        menuToggle.classList.toggle('open');
        if(menuToggle.classList.contains('open')){
            menuList.classList.add('show');
        }
    });
});