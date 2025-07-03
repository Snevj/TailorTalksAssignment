# AI-Powered Calendar Booking Assistant

A conversational AI application that enables users to book appointments through natural language interactions. Built with FastAPI, Streamlit, and Google's Gemini AI, integrated with Google Calendar for seamless appointment management.

## 🚀 Features

- **Natural Language Processing**: Powered by Google's Gemini 1.5 Flash model for intelligent conversation
- **Calendar Integration**: Direct integration with Google Calendar API for real-time availability checking
- **Appointment Booking**: Book, check, and manage appointments through conversational interface
- **Real-time Availability**: Check available time slots for any given date
- **Conversational Memory**: Maintains context throughout the conversation
- **RESTful API**: FastAPI backend with automatic API documentation
- **Interactive UI**: Clean Streamlit frontend for easy user interaction

## 🏗️ Architecture

```
┌─────────────────┐    HTTP Requests    ┌─────────────────┐
│   Streamlit     │ ──────────────────► │   FastAPI       │
│   Frontend      │                     │   Backend       │
│   (Port 8501)   │ ◄────────────────── │   (Port 8000)   │
└─────────────────┘    JSON Responses   └─────────────────┘
                                                │
                                                │
                                                ▼
                                        ┌─────────────────┐
                                        │   LangChain     │
                                        │   Agent         │
                                        └─────────────────┘
                                                │
                                    ┌───────────┴───────────┐
                                    ▼                       ▼
                            ┌─────────────────┐    ┌─────────────────┐
                            │   Gemini API    │    │ Google Calendar │
                            │   (AI Model)    │    │      API        │
                            └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- Python 3.8+
- Google Cloud Project with billing enabled
- Google Calendar API credentials
- Gemini API key from Google AI Studio

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Snevj/AiPoweredCalender.git
cd TailorTalksAssignment
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Google Cloud Services

#### Enable Required APIs
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the following APIs:
   - Google Calendar API
   - Generative Language API

#### Create Service Account
1. Navigate to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Fill in service account details
4. Download the JSON key file
5. Place it in `backend/credentials/service-account-key.json`

#### Get Gemini API Key
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Click "Get API key"
3. Create API key in your project
4. Copy the generated key

### 5. Configure Environment Variables

Create a `.env` file in the project root:
```env
GOOGLE_API_KEY="your_gemini_api_key_here"
GEMINI_API_KEY="your_gemini_api_key_here"
GOOGLE_CREDENTIALS_PATH="credentials/service-account-key.json"
BACKEND_URL="http://localhost:8000"
PORT=8000
```

### 6. Share Calendar with Service Account
1. Open Google Calendar
2. Go to Calendar Settings → "Share with specific people"
3. Add your service account email (found in the JSON credentials file)
4. Grant "Make changes to events" permission

## 🚀 Running the Application

### Start the Backend (Terminal 1)
```bash
cd backend
export GOOGLE_API_KEY="your_gemini_api_key_here"
python -m uvicorn main:app --reload
```

### Start the Frontend (Terminal 2)
```bash
streamlit run streamlit_app.py
```

### Access the Application
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 💬 Usage Examples

### Check Availability
```
User: "What's my availability tomorrow?"
Assistant: "Let me check your calendar for tomorrow..."
```

### Book an Appointment
```
User: "Book a meeting with John at 2 PM today"
Assistant: "I'll schedule that appointment for you..."
```

### General Conversation
```
User: "Hello, how can you help me?"
Assistant: "I'm your calendar assistant! I can help you check availability, book appointments, and manage your schedule."
```

## 🔧 API Endpoints

### POST /chat
Process conversational messages and return AI responses.

**Request:**
```json
{
  "message": "What's my availability tomorrow?"
}
```

**Response:**
```json
{
  "response": "Let me check your calendar for tomorrow. I can see you have the following available slots..."
}
```

## 🏗️ Project Structure

```
TailorTalksAssignment/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── agent.py               # LangChain agent with tools
│   ├── calendar_service.py    # Google Calendar integration
│   └── credentials/           # Service account credentials
├── frontend/
│   └── streamlit_app.py       # Streamlit user interface
├── .env                       # Environment variables
├── .gitignore                # Git ignore rules
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

## 🛡️ Security Features

- **Environment Variables**: Sensitive data stored in environment variables
- **Service Account**: Secure Google API authentication
- **Input Validation**: Safe JSON parsing instead of `eval()`
- **CORS Protection**: Configured for secure cross-origin requests

## 🧪 Testing

### Test Backend API
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

### Test Gemini API Connection
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}' \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=YOUR_API_KEY"
```

## 🔍 Troubleshooting

### Common Issues

#### API Key Invalid
- Ensure Gemini API key is correctly set in environment variables
- Verify Generative Language API is enabled in Google Cloud Console

#### Calendar Access Denied
- Check if service account email is added to calendar sharing
- Verify service account has "Make changes to events" permission

#### Connection Refused
- Ensure both backend and frontend are running
- Check if ports 8000 and 8501 are available

#### Environment Variables Not Loading
- Restart terminal after setting environment variables
- Use `python -m uvicorn` instead of direct `uvicorn` command

## 📊 Dependencies

### Backend
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `langchain` - AI agent framework
- `langchain-google-genai` - Gemini integration
- `google-auth` - Google authentication
- `google-api-python-client` - Google Calendar API
- `python-dotenv` - Environment variable management

### Frontend
- `streamlit` - Web application framework
- `requests` - HTTP client

## 🔄 Future Enhancements

- [ ] Multi-user support with authentication
- [ ] Email notifications for appointments
- [ ] Recurring appointment scheduling
- [ ] Integration with other calendar providers
- [ ] Voice interface support
- [ ] Mobile app development
- [ ] Advanced scheduling algorithms

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Sneh Vijay Vergiya**
- GitHub: [@Snevj](https://github.com/Snevj)
- Project: [TailorTalksAssignment](https://github.com/Snevj/TailorTalksAssignment)

## 🙏 Acknowledgments

- Google AI for providing the Gemini API
- LangChain for the agent framework
- Streamlit for the user interface framework
- FastAPI for the backend framework

**Note**: This project was developed as part of an AI/ML assignment to demonstrate conversational AI capabilities with real-world API integrations.