# WhatsApp Business Chatbot

## Overview

This is a WhatsApp Business chatbot application built with Flask that automates sales of digital products. The system provides an intelligent conversational interface for customers to browse categories, view products, and make purchases through WhatsApp messaging. It includes an admin panel for managing products, categories, and monitoring conversations.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask web application with SQLAlchemy ORM for database operations
- **Database**: SQLite for development with configurable DATABASE_URL for production databases
- **Blueprint Structure**: Modular design using Flask blueprints to separate chatbot functionality from main application
- **Session Management**: Flask sessions with configurable secret key for security

### Database Schema
- **Product Management**: Categories and Products with one-to-many relationship
- **Conversation Tracking**: Conversation states and message history for maintaining chat context
- **Order Management**: Order tracking system for purchase workflows
- **Message Logging**: Complete message history storage for analytics and debugging

### WhatsApp Integration
- **Twilio API**: Integration with Twilio's WhatsApp Business API for message handling
- **Webhook Architecture**: Receives incoming messages via webhooks and responds with TwiML
- **State Management**: Conversation state tracking to maintain context across message exchanges
- **Message Routing**: Intelligent message parsing and response generation based on user input

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap for responsive admin interface
- **Admin Panel**: Web-based interface for product management and conversation monitoring
- **Dark Theme**: Bootstrap dark theme implementation for modern UI/UX
- **Static Assets**: CSS and JavaScript files for custom styling and functionality

### Security & Configuration
- **Environment Variables**: Secure configuration management for API keys and database URLs
- **Proxy Support**: ProxyFix middleware for deployment behind reverse proxies
- **Logging**: Comprehensive logging system for debugging and monitoring
- **Session Security**: Configurable session secret for production security

## External Dependencies

### Third-Party Services
- **Twilio**: WhatsApp Business API integration for message sending and receiving
  - Account SID and Auth Token required
  - Phone number configuration for business messaging
- **Database**: Configurable database backend (SQLite default, PostgreSQL production-ready)

### Python Packages
- **Flask**: Web framework and core application structure
- **SQLAlchemy**: Database ORM and migration management
- **Twilio**: WhatsApp messaging SDK and TwiML response generation
- **Werkzeug**: WSGI utilities and middleware support

### Frontend Dependencies
- **Bootstrap**: CSS framework for responsive design
- **Font Awesome**: Icon library for UI elements
- **jQuery**: JavaScript functionality for admin panel interactions

### Development Tools
- **Flask Debug Mode**: Development server with auto-reload
- **SQLAlchemy Pool Management**: Connection pooling and health checks for database reliability