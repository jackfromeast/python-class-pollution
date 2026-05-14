from django_unicorn.components import UnicornView


class ReviewFormView(UnicornView):
    reviewer_name = ""
    rating = 5
    review_text = ""
    submitted = False
    reviews = []

    def mount(self):
        self.reviews = [
            {"name": "Sarah M.", "rating": 5, "text": "Absolutely love these! The noise cancellation is incredible and they're so comfortable for long listening sessions.", "date": "2 days ago"},
            {"name": "James K.", "rating": 4, "text": "Great sound quality and battery life. Only wish the carrying case was a bit more compact.", "date": "1 week ago"},
            {"name": "Alex R.", "rating": 5, "text": "Best headphones I've ever owned. Worth every penny.", "date": "2 weeks ago"},
        ]

    def submit_review(self):
        if not self.reviewer_name or not self.review_text:
            return
        self.reviews.insert(0, {
            "name": self.reviewer_name,
            "rating": self.rating,
            "text": self.review_text,
            "date": "Just now",
        })
        self.submitted = True
        self.reviewer_name = ""
        self.review_text = ""
        self.rating = 5

    def reset_form(self):
        self.submitted = False
