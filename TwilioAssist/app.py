import os
import logging
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///chatbot.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models to ensure tables are created
    import models
    from chatbot import chatbot_bp
    
    # Register blueprints
    app.register_blueprint(chatbot_bp)
    
    # Create all tables
    db.create_all()
    
    # Initialize default products if none exist
    from models import Product, Category
    if not Category.query.first():
        categories = [
            Category(name="Ebooks de Investimentos", description="Guias completos sobre investimentos"),
            Category(name="Ebooks de Emagrecimento", description="Dicas e estratégias para emagrecimento"),
            Category(name="Cursos de Investimentos", description="Cursos completos sobre investimentos"),
            Category(name="Apps Free Fire", description="Aplicativos e ferramentas para Free Fire"),
            Category(name="Outros", description="Outros produtos digitais")
        ]
        
        for category in categories:
            db.session.add(category)
        db.session.commit()
        
        # Add sample products
        products = [
            Product(name="Ebook: Primeiros Passos nos Investimentos", price=16.99, category_id=1, description="Guia completo para iniciantes em investimentos"),
            Product(name="Ebook: Investindo em Ações", price=24.99, category_id=1, description="Estratégias avançadas para investir em ações"),
            Product(name="Ebook: Dieta Cetogênica", price=19.99, category_id=2, description="Guia completo da dieta cetogênica"),
            Product(name="Ebook: Exercícios em Casa", price=14.99, category_id=2, description="Rotina de exercícios para fazer em casa"),
            Product(name="Curso: Trading Avançado", price=199.99, category_id=3, description="Curso completo de trading profissional"),
            Product(name="App: FF Helper Pro", price=9.99, category_id=4, description="Ferramenta avançada para Free Fire"),
        ]
        
        for product in products:
            db.session.add(product)
        db.session.commit()

@app.route('/')
def index():
    """Main page showing chatbot information"""
    return render_template('index.html')

@app.route('/admin')
def admin():
    """Admin panel for managing products and categories"""
    from models import Product, Category
    products = Product.query.all()
    categories = Category.query.all()
    return render_template('admin.html', products=products, categories=categories)

@app.route('/api/products', methods=['GET', 'POST'])
def api_products():
    """API endpoint for managing products"""
    from models import Product
    
    if request.method == 'GET':
        products = Product.query.all()
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'price': p.price,
            'description': p.description,
            'category_id': p.category_id,
            'category_name': p.category.name if p.category else None
        } for p in products])
    
    elif request.method == 'POST':
        data = request.get_json()
        product = Product(
            name=data['name'],
            price=data['price'],
            description=data['description'],
            category_id=data['category_id']
        )
        db.session.add(product)
        db.session.commit()
        return jsonify({'success': True, 'id': product.id})

@app.route('/api/categories', methods=['GET'])
def api_categories():
    """API endpoint for getting categories"""
    from models import Category
    categories = Category.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'description': c.description
    } for c in categories])
