const API_BASE = "http://localhost:8000";
async function loadProducts() {
  const res = await fetch(`${API_BASE}/api/products`);
  const data = await res.json();
  const wrap = document.getElementById("products");
  wrap.innerHTML = data.map(p => `
    <div class="card">
      <img src="${p.image_url}" alt="${p.name}">
      <h3>${p.name}</h3>
      <p>${(p.price).toLocaleString()} đ</p>
      <button class="btn" onclick="alert('Thêm vào giỏ: ${p.name}')">Thêm vào giỏ</button>
    </div>
  `).join("");
}
document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("products")) loadProducts();
});
