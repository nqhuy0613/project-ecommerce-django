// ================== GIỎ HÀNG ===================================================
const CART_KEY = 'cartItems';

// ---- Lưu & đọc localStorage ----
function getCart() {
  try { return JSON.parse(localStorage.getItem(CART_KEY)) || []; }
  catch { return []; }
}
function saveCart(items) {
  localStorage.setItem(CART_KEY, JSON.stringify(items));
}
function clearCart() {
  localStorage.removeItem(CART_KEY);
}
function cartTotalQty(items = getCart()) {
  return items.length; // mỗi sản phẩm chỉ 1 lần
}
function renderCartCount() {
  const el = document.getElementById('cart-count');
  if (el) el.textContent = cartTotalQty();
}

// ---- Hiện popup thông báo ----
// giữ được
function showAddToast(text) {
  const popup = document.getElementById('cart-popup');
  const textEl = document.getElementById('cart-popup-text');
  if (!popup) return;
  if (textEl) textEl.textContent = text;
  else popup.textContent = text;

  popup.classList.remove('hidden');
  popup.classList.add('show');
  setTimeout(() => {
    popup.classList.remove('show');
    popup.classList.add('hidden');
  }, 2000);
}

// ---- Thêm sản phẩm vào giỏ ----
function addToCartFromCard(cardEl) {
  const id = cardEl.getAttribute('data-product-id');
  const name = cardEl.getAttribute('data-name') || 'Sản phẩm';
  const price = Number(cardEl.getAttribute('data-price') || 0);

  const cart = getCart();
  const found = cart.find(item => item.id === id);

  if (found) {
    showAddToast(`${name} đã có trong giỏ hàng!`);
    return;
  }

  cart.push({ id, name, price });
  saveCart(cart);
  renderCartCount();
  showAddToast(`${name} đã được thêm vào giỏ hàng!`);
}

// ---- Khi nhấn icon giỏ hàng: xóa giỏ & chuyển trang ----
function setupCartIcon() {
  const cartIcon = document.querySelector('a[href="cart.html"], [aria-label="Giỏ hàng"]');
  if (!cartIcon) return;

  cartIcon.addEventListener('click', (e) => {
    // Reset giỏ hàng rồi đi tới cart.html
    clearCart();
    renderCartCount();
    // Không ngăn chuyển trang — để link hoạt động bình thường
  });
}

// ---- Gắn sự kiện ----
document.addEventListener('DOMContentLoaded', () => {
  renderCartCount();

  // Nút "Thêm vào giỏ"
  document.querySelectorAll('[data-action="add-to-cart"]').forEach(btn => {
    btn.addEventListener('click', () => {
      const card = btn.closest('.product-card');
      if (card) addToCartFromCard(card);
    });
  });

  setupCartIcon();
});


// trang giỏ hàng cart.html-------------------------------================================================
// ======= DỮ LIỆU MẪU (thay bằng API nếu có) =======
const products = [
  {
    id: 'fold7',
    name: 'Samsung Galaxy Z Fold7',
    price: 42990000,
    image: 'https://samcenter.vn/images/thumbs/0014792_xanh-navy_550.jpeg',
    colors: [
      { key: 'navy', name: 'Xanh Navy', hex: '#22344a' },
      { key: 'silver', name: 'Bạc', hex: '#d4d4d8' },
      { key: 'black', name: 'Đen', hex: '#111827' }
    ],
    color: 'navy',
    qty: 1
  },

];
//
const nf = new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' });
const cartListEl = document.getElementById('cartList');
const cartTotalsEl = document.getElementById('cartTotals');

const colorName = p => (p.colors.find(c => c.key === p.color) || {}).name || '';

function renderCart() {
  cartListEl.innerHTML = '';
  products.forEach(p => {
    const el = document.createElement('div');
    el.className = 'cart-item';
    el.dataset.id = p.id;
    el.innerHTML = `
        <div class="cart-thumb"><img src="${p.image}" alt="${p.name}"></div>
        <div class="cart-meta">
          <h3>${p.name}</h3>
          <div class="cart-muted">Màu sắc: <span class="cart-color-name">${colorName(p)}</span></div>
          <div class="cart-colors">
            ${p.colors.map(c => `<button class="cart-color-dot ${p.color === c.key ? 'active' : ''}" title="${c.name}" style="background:${c.hex}" data-color="${c.key}"></button>`).join('')}
          </div>
        </div>
        <div class="cart-right">
          <div class="cart-qty">
            <button class="qminus" aria-label="Giảm">−</button>
            <input class="qinput" type="number" min="1" value="${p.qty}">
            <button class="qplus" aria-label="Tăng">＋</button>
          </div>
          <div class="cart-price">${nf.format(p.price)}</div>
          <button class="cart-remove" title="Xoá"><i class="fa-regular fa-trash-can"></i></button>
        </div>`;
    cartListEl.appendChild(el);
  });
  bindCartLineEvents();
  renderTotals();
  updateCartBadge();
}

function bindCartLineEvents() {
  document.querySelectorAll('.cart-item').forEach(line => {
    const id = line.dataset.id;
    const prod = products.find(p => p.id === id);
    const minus = line.querySelector('.qminus');
    const plus = line.querySelector('.qplus');
    const input = line.querySelector('.qinput');
    const remove = line.querySelector('.cart-remove');
    const colorBtns = line.querySelectorAll('.cart-color-dot');

    minus.onclick = () => { prod.qty = Math.max(1, prod.qty - 1); input.value = prod.qty; renderTotals(); updateCartBadge(); };
    plus.onclick = () => { prod.qty += 1; input.value = prod.qty; renderTotals(); updateCartBadge(); };
    input.oninput = () => { const v = parseInt(input.value || '1', 10); prod.qty = Math.max(1, v); input.value = prod.qty; renderTotals(); updateCartBadge(); };

    remove.onclick = () => { const i = products.findIndex(p => p.id === id); if (i > -1) { products.splice(i, 1); renderCart(); } };

    colorBtns.forEach(btn => {
      btn.onclick = () => {
        prod.color = btn.dataset.color;
        colorBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        line.querySelector('.cart-color-name').textContent = colorName(prod);
      };
    });
  });
}

function calcTotals() {
  const sub = products.reduce((s, p) => s + p.price * p.qty, 0);
  const discount = 0; // demo
  const ship = 0;     // demo
  const grand = Math.max(0, sub - discount + ship);
  return { sub, discount, ship, grand };
}

function renderTotals() {
  const { sub, discount, ship, grand } = calcTotals();
  document.getElementById('sum-sub').textContent = nf.format(sub);
  document.getElementById('sum-discount').textContent = nf.format(discount);
  document.getElementById('sum-ship').textContent = nf.format(ship);
  document.getElementById('sum-grand').textContent = nf.format(grand);
  cartTotalsEl.innerHTML = `<div class="cart-total-row"><span>Tạm tính (${products.length} sản phẩm)</span><strong>${nf.format(sub)}</strong></div>`;
}

function updateCartBadge() {
  const totalQty = products.reduce((s, p) => s + p.qty, 0);
  const badge = document.getElementById('cart-count'); // nếu navbar có badge
  if (badge) badge.textContent = totalQty;
}

// ========== SHIPPING TOGGLE ==========
// giữ được
(function bindShippingToggle() {
  const radios = document.querySelectorAll('input[name="ship"]');
  const storeBox = document.getElementById('cart-store');
  const panel = document.getElementById('cart-delivery');
  const province = document.getElementById('province');
  const district = document.getElementById('district');
  const address = document.getElementById('address');

  if (!radios.length || !panel || !storeBox) return;

  const map = {
    ND: ['Huyện Hải Hậu', 'Huyện Giao Thủy', 'Huyện Xuân Trường', 'Huyện Trực Ninh'],
    HCM: ['Quận 1', 'Quận 3', 'Quận 7', 'Thủ Đức'],
    HN: ['Ba Đình', 'Cầu Giấy', 'Hoàn Kiếm', 'Long Biên'],
  };

  function setRequired(on) {
    if (province) province.required = on;
    if (district) { district.required = on; district.disabled = !on || !province.value; }
    if (address) address.required = on;
  }

  function renderDistricts() {
    const list = map[province?.value] || [];
    district.innerHTML =
      '<option value="">Mời bạn chọn quận/huyện</option>' +
      list.map(d => `<option value="${d}">${d}</option>`).join('');
    district.disabled = list.length === 0;
  }

  function applyMode() {
    const isHome = document.querySelector('input[name="ship"]:checked')?.value === 'home';
    panel.classList.toggle('hide', !isHome);   // giao tận nơi
    storeBox.classList.toggle('hide', isHome); // cửa hàng
    setRequired(isHome);
    if (isHome && province.value) renderDistricts();
  }

  radios.forEach(r => r.addEventListener('change', applyMode));
  province?.addEventListener('change', () => {
    renderDistricts();
    if (document.querySelector('input[name="ship"]:checked')?.value === 'home') {
      district.required = true;
    }
  });

  applyMode(); // init
})();

// Init cart
renderCart();

