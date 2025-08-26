import os
import logging
from datetime import datetime
from flask import Blueprint, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from app import db
from models import Category, Product, Conversation, Message, Order

# Twilio configuration
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")

# Business configuration
BUSINESS_NAME = "Ediinho Boor"
ATTENDANT_NAME = "Edii"

# Create blueprint
chatbot_bp = Blueprint('chatbot', __name__)

def get_twilio_client():
    """Get Twilio client instance"""
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
        return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    return None

def save_message(phone_number, message_body, is_incoming=True):
    """Save message to database"""
    message = Message(
        phone_number=phone_number,
        message_body=message_body,
        is_incoming=is_incoming
    )
    db.session.add(message)
    db.session.commit()

def get_or_create_conversation(phone_number):
    """Get existing conversation or create new one"""
    conversation = Conversation.query.filter_by(phone_number=phone_number).first()
    if not conversation:
        conversation = Conversation(phone_number=phone_number)
        db.session.add(conversation)
        db.session.commit()
    return conversation

def get_main_menu():
    """Generate main menu message"""
    return f"""✨ Oi! Eu sou {ATTENDANT_NAME}, atendente virtual de {BUSINESS_NAME}!  
Aqui você encontra produtos incríveis 🚀  
Responda com o número da opção que deseja:

1️⃣ Ebooks de Investimentos
2️⃣ Ebooks de Emagrecimento
3️⃣ Cursos de Investimentos
4️⃣ Apps Free Fire
5️⃣ Outros

Digite *menu* a qualquer momento para voltar ao início.
Digite *ajuda* para falar com atendimento humano."""

def get_category_products(category_id):
    """Get products for a specific category"""
    # Special handling for "Outros" category (category 5) - show donation option
    if category_id == 5:
        return get_donation_options()
    
    category = Category.query.get(category_id)
    if not category:
        return "❌ Categoria não encontrada."
    
    products = Product.query.filter_by(category_id=category_id, is_active=True).all()
    if not products:
        return f"😔 Não temos produtos disponíveis em {category.name} no momento.\n\nDigite *menu* para voltar ao início."
    
    message = f"📋 *{category.name}*\n\n"
    for i, product in enumerate(products, 1):
        message += f"{i}️⃣ *{product.name}*\n"
        message += f"💰 {product.formatted_price()}\n"
        if product.description:
            message += f"📝 {product.description}\n"
        message += "\n"
    
    message += "Responda com o número do produto que deseja comprar.\n"
    message += "Digite *voltar* para retornar ao menu principal."
    
    return message

def get_donation_options():
    """Show donation options for category Outros"""
    message = "💝 *Apoie nosso trabalho!*\n\n"
    message += "Se você gostou do nosso conteúdo e quer nos apoiar, pode fazer uma doação via PIX:\n\n"
    
    message += "💳 *Opções de Doação:*\n"
    message += "1️⃣ R$ 5,00 - Cafezinho ☕\n"
    message += "2️⃣ R$ 10,00 - Lanche 🍕\n"
    message += "3️⃣ R$ 20,00 - Almoço 🍽️\n"
    message += "4️⃣ R$ 50,00 - Apoio Premium 🌟\n"
    message += "5️⃣ Outro valor (você escolhe) 💰\n\n"
    
    message += "🔑 **Chave PIX:** ediinhoboor@gmail.com\n\n"
    message += "Responda com o número da opção desejada.\n"
    message += "Digite *voltar* para retornar ao menu principal.\n\n"
    message += "Muito obrigado pelo seu apoio! 🙏"
    
    return message

def process_donation_selection(option):
    """Process donation option selection"""
    donation_amounts = {
        '1': ('5.00', 'Cafezinho ☕'),
        '2': ('10.00', 'Lanche 🍕'),
        '3': ('20.00', 'Almoço 🍽️'),
        '4': ('50.00', 'Apoio Premium 🌟'),
        '5': ('0.00', 'Outro valor 💰')
    }
    
    if option == '5':
        message = "💰 *Outro valor*\n\n"
        message += "Por favor, me informe o valor que deseja doar (apenas números):\n"
        message += "Exemplo: 25.50 ou 15\n\n"
        message += "Qual valor gostaria de contribuir?"
        return message
    else:
        amount, description = donation_amounts[option]
        message = f"💝 *Doação Selecionada*\n\n"
        message += f"📦 {description}\n"
        message += f"💰 Valor: R$ {amount}\n\n"
        message += "Para finalizar a doação, me informe seu nome:"
        return message

def process_donation_payment(name, amount, description="Doação"):
    """Process donation payment"""
    message = f"🙏 *Obrigado, {name}!*\n\n"
    message += f"💝 Doação: {description}\n"
    message += f"💰 Valor: R$ {amount}\n\n"
    
    message += "💳 *Dados para PIX:*\n"
    message += "🔑 **Chave PIX:** ediinhoboor@gmail.com\n"
    message += "🏷️ **Nome:** Ediinho Boor\n\n"
    
    message += "📱 Após fazer o PIX, pode enviar o comprovante aqui mesmo!\n\n"
    message += "✨ Sua contribuição nos ajuda muito a continuar criando conteúdo de qualidade!\n\n"
    message += "Digite *menu* para voltar ao início."
    
    return message

def get_product_details(product_id):
    """Get detailed information about a product"""
    product = Product.query.get(product_id)
    if not product:
        return "❌ Produto não encontrado."
    
    message = f"🛍️ *{product.name}*\n\n"
    message += f"💰 Preço: {product.formatted_price()}\n"
    if product.description:
        message += f"📝 Descrição: {product.description}\n"
    message += f"📂 Categoria: {product.category.name}\n\n"
    
    message += "Para comprar este produto, responda:\n"
    message += "*1* - Confirmar compra\n"
    message += "*2* - Ver outros produtos desta categoria\n"
    message += "*3* - Voltar ao menu principal\n"
    
    return message

def process_payment(phone_number, product_id, customer_name=None):
    """Process payment for a product"""
    product = Product.query.get(product_id)
    if not product:
        return "❌ Produto não encontrado."
    
    # Create order
    order = Order(
        phone_number=phone_number,
        customer_name=customer_name,
        product_id=product_id,
        status='pending'
    )
    db.session.add(order)
    db.session.commit()
    
    message = f"🛒 *Pedido Confirmado!*\n\n"
    message += f"📦 Produto: {product.name}\n"
    message += f"💰 Valor: {product.formatted_price()}\n"
    message += f"🔢 Pedido #: {order.id}\n\n"
    
    message += "💳 *Instruções de Pagamento:*\n"
    message += f"• PIX: Envie {product.formatted_price()} para a chave PIX\n"
    message += "• Cartão: Acesse o link de pagamento\n\n"
    
    message += "📱 Após o pagamento, envie o comprovante para receber o produto!\n\n"
    message += "⏰ Você receberá o produto em até 2 horas úteis após a confirmação do pagamento."
    
    return message

def handle_help_request():
    """Handle help request"""
    return f"""🆘 *Atendimento Humano*

Em breve um de nossos atendentes entrará em contato com você!

⏰ Horário de atendimento:
Segunda a Sexta: 8h às 18h
Sábado: 8h às 12h

📞 Ou ligue para: (11) 99999-9999
📧 Email: contato@{BUSINESS_NAME.lower().replace(' ', '')}.com

Digite *menu* para voltar ao menu principal."""

@chatbot_bp.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming WhatsApp messages from Twilio"""
    try:
        # Get message details
        phone_number = request.form.get('From', '').replace('whatsapp:', '')
        message_body = request.form.get('Body', '').strip()
        
        logging.info(f"Received message from {phone_number}: {message_body}")
        
        # Save incoming message
        save_message(phone_number, message_body, is_incoming=True)
        
        # Get or create conversation
        conversation = get_or_create_conversation(phone_number)
        
        # Normalize message
        message_lower = message_body.lower()
        
        # Create response
        response = MessagingResponse()
        reply_message = ""
        
        # Handle special commands
        if message_lower in ['menu', 'início', 'inicio', 'oi', 'olá', 'ola', 'começar', 'comecar']:
            conversation.current_state = 'main_menu'
            conversation.selected_category = None
            conversation.selected_product = None
            reply_message = get_main_menu()
            
        elif message_lower in ['ajuda', 'help', 'atendimento', 'humano']:
            reply_message = handle_help_request()
            
        elif message_lower == 'voltar':
            if conversation.current_state == 'viewing_products':
                conversation.current_state = 'main_menu'
                conversation.selected_category = None
                reply_message = get_main_menu()
            elif conversation.current_state == 'product_details':
                conversation.current_state = 'viewing_products'
                reply_message = get_category_products(conversation.selected_category)
            else:
                reply_message = get_main_menu()
                
        # Handle main menu selection
        elif conversation.current_state == 'main_menu':
            if message_body in ['1', '2', '3', '4', '5']:
                category_id = int(message_body)
                conversation.current_state = 'viewing_products'
                conversation.selected_category = category_id
                reply_message = get_category_products(category_id)
            else:
                reply_message = "❌ Opção inválida. " + get_main_menu()
                
        # Handle product selection
        elif conversation.current_state == 'viewing_products':
            # Special handling for donations (category 5 - Outros)
            if conversation.selected_category == 5:
                if message_body in ['1', '2', '3', '4', '5']:
                    # Store donation option in selected_product temporarily 
                    conversation.selected_product = int(message_body)
                    conversation.current_state = 'requesting_donation_name'
                    reply_message = process_donation_selection(message_body)
                else:
                    reply_message = "❌ Opção inválida. Escolha uma opção de 1 a 5."
            else:
                # Regular product selection
                try:
                    product_index = int(message_body) - 1
                    products = Product.query.filter_by(
                        category_id=conversation.selected_category, 
                        is_active=True
                    ).all()
                    
                    if 0 <= product_index < len(products):
                        selected_product = products[product_index]
                        conversation.current_state = 'product_details'
                        conversation.selected_product = selected_product.id
                        reply_message = get_product_details(selected_product.id)
                    else:
                        reply_message = "❌ Número de produto inválido. Tente novamente."
                except ValueError:
                    reply_message = "❌ Por favor, digite apenas o número do produto."
                
        # Handle product details actions
        elif conversation.current_state == 'product_details':
            if message_body == '1':  # Confirm purchase
                conversation.current_state = 'requesting_name'
                reply_message = "😊 Ótima escolha! Para finalizar o pedido, me informe seu nome completo:"
                
            elif message_body == '2':  # See other products
                conversation.current_state = 'viewing_products'
                reply_message = get_category_products(conversation.selected_category)
                
            elif message_body == '3':  # Back to main menu
                conversation.current_state = 'main_menu'
                conversation.selected_category = None
                conversation.selected_product = None
                reply_message = get_main_menu()
            else:
                reply_message = "❌ Opção inválida. Escolha 1, 2 ou 3."
                
        # Handle name input for regular products
        elif conversation.current_state == 'requesting_name':
            conversation.customer_name = message_body
            conversation.current_state = 'main_menu'
            reply_message = process_payment(phone_number, conversation.selected_product, message_body)
            
            # Reset conversation state
            conversation.selected_category = None
            conversation.selected_product = None
            
        # Handle name input for donations
        elif conversation.current_state == 'requesting_donation_name':
            conversation.customer_name = message_body
            conversation.current_state = 'main_menu'
            
            # Process donation based on previously selected option (stored in selected_product)
            if conversation.selected_product:
                option = str(conversation.selected_product)
                if option == '5':
                    # For custom amount, ask for the value
                    conversation.current_state = 'requesting_donation_amount'
                    reply_message = "💰 Perfeito! Agora me informe o valor que deseja doar:\n\nExemplo: 25.50 ou 30"
                else:
                    # Process fixed amount donation
                    amounts = {'1': '5.00', '2': '10.00', '3': '20.00', '4': '50.00'}
                    descriptions = {'1': 'Cafezinho ☕', '2': 'Lanche 🍕', '3': 'Almoço 🍽️', '4': 'Apoio Premium 🌟'}
                    amount = amounts.get(option, '5.00')
                    description = descriptions.get(option, 'Doação')
                    reply_message = process_donation_payment(message_body, amount, description)
            else:
                reply_message = "❌ Houve um erro. " + get_main_menu()
            
            # Reset conversation state
            conversation.selected_category = None
            conversation.selected_product = None
            
        # Handle custom donation amount
        elif conversation.current_state == 'requesting_donation_amount':
            try:
                amount = float(message_body.replace(',', '.'))
                if amount > 0:
                    conversation.current_state = 'main_menu'
                    reply_message = process_donation_payment(conversation.customer_name, f"{amount:.2f}", "Contribuição Personalizada 💰")
                else:
                    reply_message = "❌ Por favor, informe um valor válido maior que zero."
            except ValueError:
                reply_message = "❌ Por favor, informe apenas números. Exemplo: 25.50 ou 30"
            
        else:
            # Default response
            reply_message = "❓ Não entendi sua mensagem. " + get_main_menu()
            conversation.current_state = 'main_menu'
        
        # Update conversation
        conversation.last_message_at = datetime.utcnow()
        db.session.commit()
        
        # Save outgoing message
        save_message(phone_number, reply_message, is_incoming=False)
        
        # Send response
        response.message(reply_message)
        
        logging.info(f"Sent response to {phone_number}: {reply_message[:100]}...")
        
        return str(response)
        
    except Exception as e:
        logging.error(f"Error processing webhook: {str(e)}")
        response = MessagingResponse()
        response.message("❌ Desculpe, ocorreu um erro. Tente novamente em alguns instantes.")
        return str(response)

@chatbot_bp.route('/send-message', methods=['POST'])
def send_message():
    """Send message via Twilio (for testing or admin use)"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        message = data.get('message')
        
        client = get_twilio_client()
        if not client:
            return {'error': 'Twilio not configured'}, 400
        
        # Send message
        twilio_message = client.messages.create(
            body=message,
            from_=f'whatsapp:{TWILIO_PHONE_NUMBER}',
            to=f'whatsapp:{phone_number}'
        )
        
        # Save outgoing message
        save_message(phone_number, message, is_incoming=False)
        
        return {'success': True, 'message_sid': twilio_message.sid}
        
    except Exception as e:
        logging.error(f"Error sending message: {str(e)}")
        return {'error': str(e)}, 500
