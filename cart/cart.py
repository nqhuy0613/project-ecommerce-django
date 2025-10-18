

class Cart():
    def __init__(self,request):
        self.session = request.session

        # ng dùng cũ - lấy session    
        cart = self.session.get("session_key")

        # ng mới - tạo
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        self.cart = cart
