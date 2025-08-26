// Admin panel JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    setupEventListeners();
});

function loadStats() {
    // Load conversation and order counts (would be implemented with API calls)
    // For now, setting placeholder values
    document.getElementById('conversations-count').textContent = '-';
    document.getElementById('orders-count').textContent = '-';
}

function setupEventListeners() {
    // Add Product Form
    document.getElementById('addProductForm').addEventListener('submit', function(e) {
        e.preventDefault();
        addProduct();
    });

    // Send Message Form
    document.getElementById('sendMessageForm').addEventListener('submit', function(e) {
        e.preventDefault();
        sendMessage();
    });
}

function addProduct() {
    const form = document.getElementById('addProductForm');
    const formData = new FormData(form);
    
    const productData = {
        name: document.getElementById('productName').value,
        price: parseFloat(document.getElementById('productPrice').value),
        category_id: parseInt(document.getElementById('productCategory').value),
        description: document.getElementById('productDescription').value
    };

    // Show loading state
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Adicionando...';
    submitBtn.disabled = true;

    fetch('/api/products', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(productData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Produto adicionado com sucesso!', 'success');
            form.reset();
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('addProductModal'));
            modal.hide();
            // Reload page to show new product
            setTimeout(() => location.reload(), 1000);
        } else {
            showAlert('Erro ao adicionar produto: ' + (data.error || 'Erro desconhecido'), 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Erro ao adicionar produto. Tente novamente.', 'danger');
    })
    .finally(() => {
        // Restore button state
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    });
}

function sendMessage() {
    const phoneNumber = document.getElementById('phoneNumber').value;
    const messageText = document.getElementById('messageText').value;

    if (!phoneNumber || !messageText) {
        showAlert('Por favor, preencha todos os campos.', 'warning');
        return;
    }

    // Validate phone number format
    const phoneRegex = /^\+\d{10,15}$/;
    if (!phoneRegex.test(phoneNumber)) {
        showAlert('Formato de número inválido. Use o formato +5511999999999', 'warning');
        return;
    }

    const submitBtn = document.querySelector('#sendMessageForm button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Enviando...';
    submitBtn.disabled = true;

    fetch('/send-message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            phone_number: phoneNumber,
            message: messageText
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Mensagem enviada com sucesso!', 'success');
            document.getElementById('sendMessageForm').reset();
        } else {
            showAlert('Erro ao enviar mensagem: ' + (data.error || 'Erro desconhecido'), 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Erro ao enviar mensagem. Verifique as configurações do Twilio.', 'danger');
    })
    .finally(() => {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    });
}

function editProduct(productId) {
    showAlert('Funcionalidade de edição será implementada em breve.', 'info');
}

function deleteProduct(productId) {
    if (confirm('Tem certeza que deseja excluir este produto?')) {
        showAlert('Funcionalidade de exclusão será implementada em breve.', 'info');
    }
}

function showAlert(message, type) {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Insert at top of container
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);

    // Auto dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv && alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

function formatPhoneNumber(phone) {
    // Remove all non-digit characters
    const cleaned = phone.replace(/\D/g, '');
    
    // Format as Brazilian phone number
    if (cleaned.length === 11) {
        return `+55${cleaned}`;
    } else if (cleaned.length === 13 && cleaned.startsWith('55')) {
        return `+${cleaned}`;
    }
    
    return phone;
}

// Real-time phone number formatting
document.getElementById('phoneNumber')?.addEventListener('input', function(e) {
    let value = e.target.value.replace(/\D/g, '');
    
    if (value.length > 0 && !value.startsWith('55')) {
        value = '55' + value;
    }
    
    if (value.length > 2) {
        e.target.value = '+' + value;
    }
});

// Price formatting for product form
document.getElementById('productPrice')?.addEventListener('input', function(e) {
    const value = parseFloat(e.target.value);
    if (!isNaN(value)) {
        // Update a preview element if needed
        const preview = document.getElementById('pricePreview');
        if (preview) {
            preview.textContent = formatCurrency(value);
        }
    }
});
