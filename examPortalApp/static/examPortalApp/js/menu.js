// Collapsable sidepan
function openNav() {
    document.getElementById("menu").classList.add("opened");
    document.getElementById("menu").classList.remove("closed");
}

function closeNav() {
    document.getElementById("menu").classList.add("closed");
    document.getElementById("menu").classList.remove("opened");
}