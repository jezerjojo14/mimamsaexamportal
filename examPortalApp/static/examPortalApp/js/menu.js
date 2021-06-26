// Collapsable sidepan
function openNav() {
    document.getElementById('chat-logo').style.fill="#59d56a"
    document.getElementById("menu").classList.add("opened");
    document.getElementById("menu").classList.remove("closed");
}

function closeNav() {
    document.getElementById('chat-logo').style.fill="#59d56a";
    document.getElementById("menu").classList.add("closed");
    document.getElementById("menu").classList.remove("opened");
}
