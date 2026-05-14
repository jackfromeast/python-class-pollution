from django_unicorn.components import UnicornView


PRODUCTS = [
    {
        "id": 1,
        "name": "Wireless Noise-Cancelling Headphones",
        "price": 299.99,
        "category": "electronics",
        "rating": 4.8,
        "reviews": 2341,
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop",
        "description": "Premium over-ear headphones with active noise cancellation and 30-hour battery life.",
    },
    {
        "id": 2,
        "name": "Minimalist Leather Watch",
        "price": 189.00,
        "category": "accessories",
        "rating": 4.6,
        "reviews": 876,
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop",
        "description": "Elegant timepiece with genuine Italian leather strap and sapphire crystal face.",
    },
    {
        "id": 3,
        "name": "Organic Cotton T-Shirt",
        "price": 45.00,
        "category": "clothing",
        "rating": 4.4,
        "reviews": 1203,
        "image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop",
        "description": "Sustainably sourced 100% organic cotton. Available in 12 colors.",
    },
    {
        "id": 4,
        "name": "Smart Home Speaker",
        "price": 129.99,
        "category": "electronics",
        "rating": 4.5,
        "reviews": 3102,
        "image": "https://images.unsplash.com/photo-1543512214-318c7553f230?w=400&h=400&fit=crop",
        "description": "Voice-controlled speaker with premium sound and smart home integration.",
    },
    {
        "id": 5,
        "name": "Running Shoes Pro",
        "price": 159.99,
        "category": "clothing",
        "rating": 4.7,
        "reviews": 1890,
        "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop",
        "description": "Lightweight performance running shoes with responsive cushioning technology.",
    },
    {
        "id": 6,
        "name": "Ceramic Pour-Over Set",
        "price": 68.00,
        "category": "home",
        "rating": 4.9,
        "reviews": 456,
        "image": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400&h=400&fit=crop",
        "description": "Handcrafted ceramic dripper with thermal carafe. Makes the perfect cup every time.",
    },
    {
        "id": 7,
        "name": "Portable Bluetooth Speaker",
        "price": 79.99,
        "category": "electronics",
        "rating": 4.3,
        "reviews": 2105,
        "image": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400&h=400&fit=crop",
        "description": "Waterproof, dustproof portable speaker with 20-hour playtime.",
    },
    {
        "id": 8,
        "name": "Scented Soy Candle Set",
        "price": 42.00,
        "category": "home",
        "rating": 4.6,
        "reviews": 934,
        "image": "https://images.unsplash.com/photo-1602028915047-37269d1a73f7?w=400&h=400&fit=crop",
        "description": "Set of 3 hand-poured soy candles in lavender, vanilla, and sandalwood.",
    },
]


class ProductSearchView(UnicornView):
    search_query = ""
    selected_category = "all"
    sort_by = "featured"
    min_price = 0
    max_price = 500
    products = []
    result_count = 0
    cart_items = []
    cart_notification = ""
    show_cart = False
    total_items = 0
    subtotal = 0.0

    def mount(self):
        self._refresh_products()

    def updated(self, name, value):
        if name in ("search_query", "selected_category", "sort_by", "min_price", "max_price"):
            self._refresh_products()

    def _refresh_products(self):
        results = PRODUCTS

        if self.search_query:
            q = self.search_query.lower()
            results = [p for p in results if q in p["name"].lower() or q in p["description"].lower()]

        if self.selected_category != "all":
            results = [p for p in results if p["category"] == self.selected_category]

        results = [p for p in results if self.min_price <= p["price"] <= self.max_price]

        if self.sort_by == "price_low":
            results.sort(key=lambda p: p["price"])
        elif self.sort_by == "price_high":
            results.sort(key=lambda p: p["price"], reverse=True)
        elif self.sort_by == "rating":
            results.sort(key=lambda p: p["rating"], reverse=True)

        self.products = results
        self.result_count = len(results)

    def _refresh_cart_totals(self):
        self.total_items = sum(item["quantity"] for item in self.cart_items)
        self.subtotal = sum(item["price"] * item["quantity"] for item in self.cart_items)

    def add_to_cart(self, product_id):
        product = next((p for p in PRODUCTS if p["id"] == product_id), None)
        if not product:
            return
        for item in self.cart_items:
            if item["product_id"] == product_id:
                item["quantity"] += 1
                self.cart_notification = f"Updated: {product['name']}"
                self._refresh_cart_totals()
                return
        self.cart_items.append({
            "product_id": product_id,
            "name": product["name"],
            "price": product["price"],
            "image": product["image"],
            "quantity": 1,
        })
        self.cart_notification = f"Added: {product['name']}"
        self._refresh_cart_totals()

    def remove_from_cart(self, product_id):
        self.cart_items = [item for item in self.cart_items if item["product_id"] != product_id]
        self._refresh_cart_totals()

    def update_quantity(self, product_id, quantity):
        if quantity <= 0:
            self.remove_from_cart(product_id)
            return
        for item in self.cart_items:
            if item["product_id"] == product_id:
                item["quantity"] = quantity
                break
        self._refresh_cart_totals()

    def toggle_cart(self):
        self.show_cart = not self.show_cart
        self.cart_notification = ""
