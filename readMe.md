# 🤖 Chatbot

An intelligent RAG (Retrieval-Augmented Generation) chatbot that provides instant answers from Omnivoltaic's Notion documentation. Built with Flask, Groq AI, and a modern React-inspired UI.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

- 🔍 **Semantic Search** - Intelligently finds relevant documentation across all topics
- 🎯 **Topic Filtering** - Quick access to specific documentation sections
- 🖼️ **Image Support** - Displays images from Notion documentation with captions
- 📊 **Confidence Scores** - Shows how confident the AI is in its answers
- 💬 **Natural Conversations** - Context-aware responses powered by Groq AI
- 🎨 **Modern UI** - Beautiful, responsive interface with smooth animations
- ⚡ **Real-time Responses** - Fast answer generation with typing indicators

## 📸 Screenshots

```
image.png
```

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Frontend  │ ──HTTP──▶│   Flask API  │ ──────▶│   Notion    │
│   (HTML/JS) │         │   (Python)   │         │     API     │
└─────────────┘         └──────────────┘         └─────────────┘
                               │
                               │
                               ▼
                        ┌──────────────┐
                        │   Groq AI    │
                        │   (LLaMA)    │
                        └──────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Notion API Token
- Groq API Key
- Modern web browser

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/chatbot.git
   cd chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   NOTION_TOKEN=your_notion_integration_token
   GROQ_API_KEY=your_groq_api_key
   ```

4. **Configure Notion sources**
   
   Create `notion_sources.json` with your documentation URLs:
   ```json
   {
     "IOT": "https://www.notion.so/your-page-id",
     "BLE Protocols": "https://www.notion.so/another-page-id",
     "API Documentation": "https://www.notion.so/api-docs-page-id"
   }
   ```

5. **Run the backend**
   ```bash
   python app.py
   ```
   The server will start at `http://localhost:5000`

6. **Open the frontend**
   
   Open `index.html` in your browser or serve it with:
   ```bash
   python -m http.server 8000
   ```
   Then navigate to `http://localhost:5500`

## 📁 Project Structure

```
omnivoltaic-chatbot/
│
├── app.py                      # Flask backend application
├── notion_sources.json         # Notion page URLs configuration
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── .env.example               # Example environment file
├── .gitignore                 # Git ignore rules
│
├── public/
│   └── index.html             # Frontend chat interface
│
├── README.md                  # This file
└── LICENSE                    # License file
```

## 🔧 Configuration

### Backend Configuration

Edit `app.py` to customize:

- **Model**: Change the Groq model in `ask_groq()` function
  ```python
  model="llama-3.1-8b-instant"  # or "llama-3.1-70b-versatile"
  ```

- **Confidence Threshold**: Adjust relevance thresholds
  ```python
  if relevance["confidence"] > 60:  # Default is 60
  ```

- **Content Preview Length**: Change text preview size
  ```python
  text_preview = text_content[:1500]  # Default is 1500 chars
  ```

### Frontend Configuration

Edit `index.html` to customize:

- **API URL**: Update the backend URL
  ```javascript
  const API_BASE_URL = 'http://localhost:5000';
  ```

- **Theme Colors**: Modify CSS gradient colors
  ```css
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  ```

## 🌐 Deployment

### Deploy Backend (Render)

1. Create a `Procfile`:
   ```
   web: gunicorn app:app
   ```

2. Create `runtime.txt`:
   ```
   python-3.11.0
   ```

3. Push to GitHub and connect to Render

4. Add environment variables in Render dashboard

### Deploy Frontend (Netlify/Vercel)

1. Update `API_BASE_URL` in `index.html` with your backend URL

2. Deploy using Netlify CLI:
   ```bash
   netlify deploy --dir=public
   ```

Or push to GitHub and connect to Vercel/Netlify

## 📚 API Documentation

### Endpoints

#### `GET /`
Health check endpoint
```json
{
  "message": "🚀 Notion RAG Chatbot is running!",
  "available_topics": ["IOT", "BLE Protocols", ...]
}
```

#### `GET /api/topics`
Get all available documentation topics
```json
{
  "topics": ["IOT", "BLE Protocols", "API Documentation"],
  "count": 3
}
```

#### `POST /api/chat`
Send a query and get an answer

**Request:**
```json
{
  "query": "How do I configure MQTT?",
  "topic": "IOT"  // Optional
}
```

**Response:**
```json
{
  "topic": "IOT",
  "response": "To configure MQTT...",
  "confidence": 85,
  "source": "keyword_match",
  "images": [
    {
      "url": "https://...",
      "caption": "MQTT Configuration Diagram"
    }
  ]
}
```

## 🔑 Getting API Keys

### Notion API Token

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Give it a name and select your workspace
4. Copy the "Internal Integration Token"
5. Share your Notion pages with the integration

### Groq API Key

1. Sign up at [Groq Console](https://console.groq.com)
2. Go to API Keys section
3. Create a new API key
4. Copy and save it securely

## 🛠️ Development

### Running in Development Mode

```bash
# Backend with auto-reload
FLASK_ENV=development python app.py

# Frontend with live server
python -m http.server 8000
```

### Testing

Test the API endpoints:

```bash
# Test topics endpoint
curl http://localhost:5000/api/topics

# Test chat endpoint
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is IOT?"}'
```

### Adding New Documentation

1. Add new Notion pages to your integration
2. Update `notion_sources.json`:
   ```json
   {
     "New Topic": "https://www.notion.so/new-page-id"
   }
   ```
3. Restart the backend
4. New topics will appear automatically in the UI

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Troubleshooting

### Common Issues

**"Failed to load topics" error:**
- Ensure Flask backend is running
- Check CORS is enabled
- Verify API URL in frontend matches backend

**"KeyError" on content:**
- Check `notion_sources.json` format
- Verify Notion integration has access to pages
- Ensure pages contain text content

**Slow responses:**
- Consider using a faster Groq model
- Reduce content preview length
- Optimize Notion page content

**Images not loading:**
- Verify Notion image permissions
- Check if images are external or uploaded
- Ensure image URLs are accessible

## 📧 Support

For questions or issues:
- Open an [issue](https://github.com/yourusername/omnivoltaic-chatbot/issues)
- Email: support@omnivoltaic.com
- Documentation: [Wiki](https://github.com/yourusername/omnivoltaic-chatbot/wiki)

## 🙏 Acknowledgments

- [Notion API](https://developers.notion.com/) - For documentation storage
- [Groq](https://groq.com/) - For fast AI inference
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Tailwind CSS](https://tailwindcss.com/) - UI styling inspiration

## 🔮 Roadmap

- [ ] Multi-language support
- [ ] Voice input/output
- [ ] Export conversation history
- [ ] Admin dashboard
- [ ] Analytics and usage tracking
- [ ] Integration with Slack/Teams
- [ ] Mobile app (React Native)
- [ ] Advanced search filters

---


**Star ⭐ this repo if you find it helpful!**