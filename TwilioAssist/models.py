from app import db
from datetime import datetime

class Category(db.Model):
    """Product categories"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    products = db.relationship('Product', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Product(db.Model):
    """Digital products for sale"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def formatted_price(self):
        """Return price formatted in Brazilian Real"""
        return f"R$ {self.price:.2f}".replace('.', ',')

class Conversation(db.Model):
    """Store conversation states and history"""
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)
    current_state = db.Column(db.String(50), default='main_menu')
    selected_category = db.Column(db.Integer, db.ForeignKey('category.id'))
    selected_product = db.Column(db.Integer, db.ForeignKey('product.id'))
    customer_name = db.Column(db.String(100))
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Conversation {self.phone_number}>'

class Message(db.Model):
    """Store message history"""
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)
    message_body = db.Column(db.Text, nullable=False)
    is_incoming = db.Column(db.Boolean, default=True)  # True for customer, False for bot
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Message {self.phone_number}>'

class Order(db.Model):
    """Store order information"""
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)
    customer_name = db.Column(db.String(100))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, paid, delivered, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    product = db.relationship('Product', backref='orders')
    
    def __repr__(self):
        return f'<Order {self.id} - {self.phone_number}>'
