# AI Finance SaaS

A comprehensive AI-powered finance workspace platform for intelligent financial decision-making. Combines machine learning-driven fraud detection, revenue forecasting, intelligent document analysis, and AI-assisted finance team workflows.

## Overview

AI Finance SaaS is a full-stack application designed to help finance teams leverage artificial intelligence for:

- **Fraud Detection**: Real-time fraud detection for credit card and payment transactions using trained ML models
- **Revenue Forecasting**: AI-powered revenue predictions based on historical financial data
- **Intelligent Document Analysis**: Q&A interface for financial documents powered by Gemini AI
- **Finance Team Collaboration**: Centralized workspace for finance professionals with AI assistance
- **Payment Integration**: Stripe integration for subscription and billing management

## Key Features

### Backend (FastAPI)
- RESTful API with JWT authentication
- MongoDB integration for persistent data storage
- ML model inference pipeline for fraud detection
- Celery task queue for background processing
- PDF and document processing capabilities
- Stripe payment webhook handling
- CORS-enabled for frontend integration

### Frontend (Next.js + TypeScript)
- Modern, responsive dashboard UI with Tailwind CSS
- Real-time data visualization and charts
- Authentication and user profile management
- Document upload and Q&A interface
- Fraud detection interface with prediction results
- Revenue forecasting visualization
- Subscription management

### Machine Learning
- Credit card fraud detection model (trained on credit card dataset)
- PaySim fraud detection model (trained on synthetic payment data)
- Revenue forecasting model for financial predictions
- Model serialization with scikit-learn pipelines
- Metrics tracking and performance monitoring

## Tech Stack

### Frontend
- **Framework**: Next.js 14.2
- **Language**: TypeScript 5.6
- **Styling**: Tailwind CSS 3.4
- **Runtime**: React 18.3

### Backend
- **Framework**: FastAPI 0.115
- **Server**: Uvicorn with standard extras
- **Database**: MongoDB with Motor async driver
- **Authentication**: Python-Jose with cryptography
- **ML/Data**: scikit-learn, pandas, joblib
- **Task Queue**: Celery 5.4
- **Payments**: Stripe SDK
- **Document Processing**: python-docx, pypdf
- **AI**: Google Gemini API
- **Testing**: pytest

### DevOps
- Docker and Docker Compose
- Multi-container orchestration (frontend, backend, MongoDB)
