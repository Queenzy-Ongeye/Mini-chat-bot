import os, json
from flask import Flask, request, jsonify
from flask_cors import CORS
from notion_client import Client
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Debug: Check if keys are loaded
print(f"GROQ_API_KEY loaded: {GROQ_API_KEY is not None}")
print(f"NOTION_TOKEN loaded: {NOTION_TOKEN is not None}")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables")
if not NOTION_TOKEN:
    raise ValueError("NOTION_TOKEN not found in environment variables")

# Initialize clients
notion = Client(auth=NOTION_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY)

# Load Notion page URLs
with open("notion_sources.json") as f:
    NOTION_PAGES = json.load(f)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

def extract_page_id(url: str) -> str:
    """Extract Notion page ID from the URL"""
    return url.split("-")[-1]

def fetch_page_content(page_id: str) -> dict:
    """Fetch readable text and images from a Notion page"""
    blocks = notion.blocks.children.list(block_id=page_id)
    texts = []
    images = []
    
    for block in blocks["results"]:
        block_type = block.get("type")
        
        # Extract text content
        if block_type and block[block_type].get("rich_text"):
            texts.append(block[block_type]["rich_text"][0]["plain_text"])
        
        # Extract images
        if block_type == "image":
            image_data = block["image"]
            image_url = None
            caption = ""
            
            # Get image URL (can be external or uploaded)
            if image_data.get("type") == "external":
                image_url = image_data["external"]["url"]
            elif image_data.get("type") == "file":
                image_url = image_data["file"]["url"]
            
            # Get caption if available
            if image_data.get("caption"):
                caption = " ".join([text["plain_text"] for text in image_data["caption"]])
            
            if image_url:
                images.append({
                    "url": image_url,
                    "caption": caption
                })
    
    return {
        "text": " ".join(texts),
        "images": images
    }

def find_relevant_topics(query: str) -> list:
    """Find all potentially relevant topics based on query keywords"""
    query_lower = query.lower()
    relevant_topics = []
    
    # Check each topic for keyword matches
    for topic in NOTION_PAGES.keys():
        if topic.lower() in query_lower:
            relevant_topics.append(topic)
    
    return relevant_topics

def check_content_relevance(query: str, content: dict) -> dict:
    """Use LLM to check if the content is relevant to the query"""
    # Extract text from content dict
    text_content = content.get("text", "")
    text_preview = text_content[:1500] if text_content else ""
    
    relevance_prompt = f"""
    Analyze if the following documentation content can answer the user's question.
    
    User Question: {query}
    
    Documentation Content Preview: {text_preview}
    
    Respond with ONLY a JSON object in this exact format:
    {{"relevant": true/false, "confidence": 0-100, "reason": "brief explanation"}}
    """
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": relevance_prompt}],
            temperature=0.1
        )
        result = json.loads(response.choices[0].message.content)
        return result
    except:
        return {"relevant": False, "confidence": 0, "reason": "Failed to parse relevance"}

def search_all_topics(query: str) -> tuple:
    """Search through all topics to find the most relevant content"""
    best_match = None
    best_confidence = 0
    all_contents = {}
    
    for topic, url in NOTION_PAGES.items():
        page_id = extract_page_id(url)
        content = fetch_page_content(page_id)
        
        # Check if content has text
        if content and content.get("text"):
            all_contents[topic] = content
            relevance = check_content_relevance(query, content)
            
            if relevance["relevant"] and relevance["confidence"] > best_confidence:
                best_confidence = relevance["confidence"]
                best_match = {"topic": topic, "content": content, "confidence": relevance["confidence"]}
    
    return best_match, all_contents

def ask_groq(prompt: str) -> str:
    """Query Groq LLM for an answer"""
    chat_completion = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return chat_completion.choices[0].message.content

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    query = data.get("query")
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    # First, try to find relevant topics by keyword
    relevant_topics = find_relevant_topics(query)
    
    # If specific topics found, search those first
    if relevant_topics:
        for topic in relevant_topics:
            page_id = extract_page_id(NOTION_PAGES[topic])
            content_data = fetch_page_content(page_id)
            
            # Check if content has text
            if content_data and content_data.get("text"):
                relevance = check_content_relevance(query, content_data)
                
                if relevance["relevant"] and relevance["confidence"] > 60:
                    prompt = f"""
You are a helpful assistant for Omnivoltaic's internal documentation.

Context from '{topic}' documentation:
{content_data["text"][:7000]}

User Question: {query}

Instructions:
- Answer ONLY if the documentation contains relevant information
- If the question cannot be answered from this documentation, clearly state: "I don't have information about that in the documentation."
- Be specific and cite relevant details from the documentation
- Keep responses clear and concise
- If procedures or steps are involved, present them clearly
- If there are images in the documentation that would help answer the question, mention that visual references are available
"""
                    answer = ask_groq(prompt)
                    return jsonify({
                        "topic": topic,
                        "response": answer,
                        "confidence": relevance["confidence"],
                        "source": "keyword_match",
                        "images": content_data["images"]
                    })
    
    # If no keyword matches or low relevance, search all topics
    print("No strong keyword match, searching all topics...")
    best_match, all_contents = search_all_topics(query)
    
    if best_match and best_match["confidence"] > 50:
        prompt = f"""
You are a helpful assistant for Omnivoltaic's internal documentation.

Context from '{best_match['topic']}' documentation:
{best_match['content']["text"][:7000]}

User Question: {query}

Instructions:
- Answer based on the documentation provided
- Be specific and cite relevant details
- Keep responses clear and concise
- If there are images in the documentation that would help answer the question, mention that visual references are available
"""
        answer = ask_groq(prompt)
        return jsonify({
            "topic": best_match["topic"],
            "response": answer,
            "confidence": best_match["confidence"],
            "source": "semantic_search",
            "images": best_match["content"]["images"]
        })
    
    # No relevant content found - provide helpful fallback
    available_topics = list(NOTION_PAGES.keys())
    fallback_prompt = f"""
The user asked: "{query}"

Unfortunately, this question cannot be answered from the available documentation topics: {', '.join(available_topics)}.

Provide a helpful response that:
1. Acknowledges you don't have documentation about this specific topic
2. Lists what documentation IS available
3. Suggests they contact support or rephrase their question
4. Be friendly and professional

Do NOT make up information or pretend to know the answer.
"""
    
    answer = ask_groq(fallback_prompt)
    return jsonify({
        "topic": None,
        "response": answer,
        "confidence": 0,
        "source": "no_match",
        "available_topics": available_topics,
        "images": []
    })

@app.route("/")
def home():
    return jsonify({
        "message": "🚀 Omnivoltaic Notion RAG Chatbot is running!",
        "available_topics": list(NOTION_PAGES.keys()),
        "endpoints": {
            "/api/chat": "POST - Send queries to the chatbot"
        }
    })

@app.route("/api/topics", methods=["GET"])
def get_topics():
    """Endpoint to list all available topics"""
    return jsonify({
        "topics": list(NOTION_PAGES.keys()),
        "count": len(NOTION_PAGES)
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)