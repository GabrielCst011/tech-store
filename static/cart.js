if (!localStorage.getItem("cart")) {
    localStorage.setItem("cart", JSON.stringify([]));
}

function getCart() {
    return JSON.parse(localStorage.getItem("cart"));
}

function saveCart(cart) {
    localStorage.setItem("cart", JSON.stringify(cart));
    updateCartCount();
}

function addToCart(id, name, price) {
    let cart = getCart();
    cart.push({id, name, price});
    saveCart(cart);
}

function updateCartCount() {
    document.getElementById("cart-count").innerText = getCart().length;
}

updateCartCount();

document.getElementById("cart-btn").onclick = () => {
    const modal = document.getElementById("cart-modal");
    modal.style.display = "flex";

    const itemsDiv = document.getElementById("cart-items");
    const totalSpan = document.getElementById("cart-total");

    let cart = getCart();
    itemsDiv.innerHTML = "";
    let total = 0;

    cart.forEach(item => {
        itemsDiv.innerHTML += `
            <p>${item.name} — R$ ${item.price.toFixed(2)}</p>
        `;
        total += item.price;
    });

    totalSpan.innerText = total.toFixed(2);
};

function closeCart() {
    document.getElementById("cart-modal").style.display = "none";
}
