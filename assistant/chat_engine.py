import re
import unicodedata
from django.db.models import Q
from store.models import Product
from payment.models import Order, OrderItem
import os, pickle

try:
    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer
except Exception:
    faiss = None
    SentenceTransformer = None


# ===================== TEXT UTILS =====================

def _norm(s: str) -> str:
    s = (s or "").lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return s


def _custom_reply(msg_norm: str):
    # Funny reply
    if "dep trai" in msg_norm and ("nhat the gioi" in msg_norm or "nhat tg" in msg_norm):
        return "Nguyễn An 😎"

    if re.search(r"dep\s*trai.*nhat.*(the\s*gioi|tg)", msg_norm):
        return "Nguyễn An 😎"

    if re.search(r"who.*(most|the)\s*handsome.*world", msg_norm):
        return "Nguyễn An 😎"

    # Contact info
    if re.search(r"thong tin.*lien he", msg_norm):
        return """📞 Hotline: 18001234
📧 Email: support@example.com"""

    # About / introduction
    if re.search(r"gioi thieu", msg_norm):
        return """Từ 2022, SamCenter là đại lý uỷ quyền Samsung tại Việt Nam."""

    return None


# ===================== PERMISSION HELPERS =====================

def _is_logged_in(user) -> bool:
    return user and getattr(user, "is_authenticated", False)


def _is_admin(user) -> bool:
    return _is_logged_in(user) and (user.is_staff or user.is_superuser)


# ===================== ORDER HELPERS =====================

def _orders_by_user_or_email(user, email=None):
    if _is_logged_in(user):
        return Order.objects.filter(Q(user_id=user.id) | Q(email=user.email)).order_by("-id")

    if email:
        return Order.objects.filter(email=email).order_by("-id")

    return Order.objects.none()


def _extract_order_id(text: str):
    m = re.search(r"\b(\d{1,10})\b", text)
    return int(m.group(1)) if m else None


# ===================== ORDER ANSWER =====================

def _answer_order(message, user=None):
    msg = message.lower()

    # ===================== 1️⃣ TRA ĐƠN HÀNG CỦA TÔI =====================
    if "đơn hàng của tôi" in msg or "don hang cua toi" in msg:
        if not _is_logged_in(user):
            return "🔐 Bạn cần đăng nhập để xem đơn hàng của mình."

        orders = _orders_by_user_or_email(user)
        if not orders:
            return "✨ Bạn chưa có đơn hàng nào."

        text = "📦 Đơn hàng của bạn:\n"
        for o in orders:
            total = getattr(o, "amount_paid", getattr(o, "total", 0))
            text += f"- #{o.id} | {o.shipping_status} | ₫{total}\n"
        return text

    # ===================== 2️⃣ TRA THEO EMAIL =====================
    email_match = re.search(r"[\w\.-]+@[\w\.-]+", msg)
    if email_match:
        email = email_match.group(0).strip()
        orders = Order.objects.filter(email=email).order_by("-id")

        if not orders:
            return f" Không tìm thấy đơn hàng nào cho email **{email}**."

        text = f"📧 Đơn hàng của email **{email}**:\n"
        for o in orders:
            total = getattr(o, "amount_paid", getattr(o, "total", 0))
            text += f"- #{o.id} | {o.shipping_status} | ₫{total}\n"
        return text

    # ===================== 3️⃣ TRA THEO MÃ ĐƠN (fallback) =====================
    order_id = _extract_order_id(msg)
    if not order_id:
        return "🔎 Vui lòng nhập email hoặc gõ **Tra đơn hàng của tôi** để xem đơn hàng."

    if not _is_logged_in(user):
        return "🔐 Bạn cần đăng nhập để xem chi tiết đơn hàng."

    try:
        o = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return f"❌ Không tìm thấy đơn hàng **#{order_id}**."

    if not (_is_admin(user) or (o.user_id == user.id) or (o.email == user.email)):
        return " Vui lòng nhập đúng mã vận đơn hoặc soạn theo cú pháp *tra đơn hàng của tôi*."

    items = OrderItem.objects.filter(order=o)
    s = ", ".join([f"{it.product.title} x{it.quantity}" for it in items]) or "(trống)"
    total = getattr(o, "amount_paid", getattr(o, "total", 0))
    date = o.date_ordered.strftime('%d/%m/%Y %H:%M') if o.date_ordered else "(N/A)"

    return (
        f"📦 Đơn hàng **#{o.id}**\n"
        f"👤 Khách: **{o.full_name}**\n"
        f"📧 Email: **{o.email}**\n"
        f"🔎 Trạng thái: **{o.shipping_status}**\n"
        f"💰 Tổng: **₫{total}**\n"
        f"🛒 Sản phẩm: {s}\n"
        f"📅 Ngày đặt: {date}"
    )


# ===================== PRODUCT SEARCH =====================

INDEX_DIR = "var/assistant_index"

def _load_index():
    idx_path = os.path.join(INDEX_DIR, "products.faiss")
    meta_path = os.path.join(INDEX_DIR, "meta.pkl")
    if not (os.path.exists(idx_path) and os.path.exists(meta_path)):
        return None, None, None
    index = faiss.read_index(idx_path) if faiss else None
    meta = pickle.load(open(meta_path, "rb"))
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2") if SentenceTransformer else None
    return index, meta, model


def _answer_product(message, k=5):
    index, meta, model = _load_index()
    if not index or not model:
        qs = Product.objects.filter(Q(title__icontains=message) | Q(description__icontains=message))[:k]
        if not qs:
            return "Không tìm thấy sản phẩm phù hợp."
        return "Gợi ý:\n" + "\n".join([f"- {p.title} (₫{p.price})" for p in qs])

    qv = model.encode([message], convert_to_numpy=True)[0]
    qv = (qv / (np.linalg.norm(qv) + 1e-10)).astype("float32")[None, :]
    D, I = index.search(qv, k)
    ids = [meta[i]["id"] for i in I[0] if i >= 0]
    products = list(Product.objects.filter(id__in=ids))

    if not products:
        return "Không tìm thấy sản phẩm phù hợp."

    return "Gợi ý theo mô tả:\n" + "\n".join([f"- {p.title} (₫{p.price}) — /product/{p.slug}" for p in products])


# ===================== MAIN ROUTER =====================

def process_message(msg: str, user=None):
    m_norm = _norm(msg)

    fixed = _custom_reply(m_norm)
    if fixed:
        return fixed

    # Order-related intent
    if re.search(r"(tra|check|kiem|kiểm|đơn|don|order|mã|ma)\s*(đơn|don)?", msg.lower()):
        return _answer_order(msg, user)

    return _answer_product(msg)
