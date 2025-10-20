// --- JS nút search (chỉ gắn khi có đủ phần tử) ---==============================================
const searchBtn = document.getElementById("search-btn");
const searchBox = document.getElementById("search-box");
const overlay = document.getElementById("overlay");

if (searchBtn && searchBox && overlay) {
  searchBtn.addEventListener("click", (e) => {
    // e.preventDefault();
    const open = searchBox.style.display === "block";
    searchBox.style.display = open ? "none" : "block";
    overlay.style.display = open ? "none" : "block";
  });

  overlay.addEventListener("click", () => {
    searchBox.style.display = "none";
    overlay.style.display = "none";
  });
}

// --- Carousel (chỉ chạy khi có đủ phần tử & slide) ---
const slides = document.querySelectorAll(".carousel img");
const prevBtn = document.querySelector(".prev");
const nextBtn = document.querySelector(".next");
let slideIndex = 0;

function showSlide(i) {
  // Bảo vệ nếu không có slide
  if (!slides || slides.length === 0) return;
  slides.forEach(slide => slide.classList.remove("active"));
  const safeIndex = ((i % slides.length) + slides.length) % slides.length; // luôn 0..length-1
  slides[safeIndex].classList.add("active");
  slideIndex = safeIndex;
}

if (slides.length > 0) {
  // Gắn nút nếu có
  if (prevBtn) {
    prevBtn.addEventListener("click", () => {
      showSlide(slideIndex - 1);
    });
  }
  if (nextBtn) {
    nextBtn.addEventListener("click", () => {
      showSlide(slideIndex + 1);
    });
  }

  // Tự động chạy nếu có ít nhất 2 ảnh
  if (slides.length > 1) {
    setInterval(() => {
      showSlide(slideIndex + 1);
    }, 5000);
  }

  // Hiển thị frame đầu tiên
  showSlide(0);
}

// ---------------- Trang đăng ký (giữ nguyên phần đã có) ----------------========================
document.addEventListener('DOMContentLoaded', () => {
  // Toggle mắt
  function togglePwd(id, el) {
    const inp = document.getElementById(id);
    if (!inp) return;
    const hide = inp.type === 'password';
    inp.type = hide ? 'text' : 'password';
    el.innerHTML = hide ? '<i class="fa-regular fa-eye-slash"></i>' : '<i class="fa-regular fa-eye"></i>';
  }
  window.togglePwd = togglePwd;

  const form = document.getElementById('signupForm');
  const pwd1 = document.getElementById('pwd1');
  const pwd2 = document.getElementById('pwd2');
  const msg = document.getElementById('pwdMsg');
  // Kiểm tra email đúng định dạng
  // --- Kiểm tra email hợp lệ ---
  const emailInput = document.querySelector('input[type="email"]');
  const emailMsg = document.getElementById('emailMsg');

  if (emailInput) {
    emailInput.addEventListener('input', () => {
      const emailVal = emailInput.value.trim();
      const emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailVal);

      if (emailVal === '') {
        emailInput.setCustomValidity('');
        if (emailMsg) emailMsg.textContent = '';
      } else if (!emailOk) {
        emailInput.setCustomValidity('Email không hợp lệ');
        if (emailMsg) emailMsg.textContent = 'Email không hợp lệ';
      } else {
        emailInput.setCustomValidity('');
        if (emailMsg) emailMsg.textContent = '';
      }
    });
  }



  if (!form || !pwd1 || !pwd2) return;

  function setPwValidity() {
    const v1 = pwd1.value.trim();
    const v2 = pwd2.value.trim();
    const mismatch = v1 !== '' && v2 !== '' && v1 !== v2;

    pwd2.setCustomValidity(mismatch ? 'Mật khẩu xác nhận không khớp' : '');
    if (msg) msg.textContent = mismatch ? 'Mật khẩu xác nhận không khớp' : '';
  }

  pwd1.addEventListener('input', setPwValidity);
  pwd2.addEventListener('input', setPwValidity);

  form.addEventListener('submit', (e) => {
    // e.preventDefault();
    setPwValidity();

    if (form.checkValidity()) {
      form.submit();     // chỉ submit khi KHỚP & các required khác hợp lệ
    } else {
      form.reportValidity();
    }
  });
});
