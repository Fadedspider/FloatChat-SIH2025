from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os
from pydantic import BaseModel

app = FastAPI(title="FloatChat AI Chatbot Server")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model and tokenizer
model = None
tokenizer = None

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    question: str
    answer: str
    model_type: str
    confidence: str

@app.on_event("startup")
async def load_model():
    global model, tokenizer
    
    print("🔄 Loading your fine-tuned ocean chatbot...")
    
    # Optimize for CPU
    torch.set_num_threads(min(8, os.cpu_count()))
    
    try:
        model = AutoModelForCausalLM.from_pretrained(
            "./ocean_chatbot_final",
            dtype=torch.float32,
            device_map="cpu",
            low_cpu_mem_usage=True
        )
        
        tokenizer = AutoTokenizer.from_pretrained("./ocean_chatbot_final")
        
        if tokenizer.pad_token is None or tokenizer.pad_token == tokenizer.eos_token:
            tokenizer.add_special_tokens({"pad_token": "[PAD]"})
            model.resize_token_embeddings(len(tokenizer))
            
        print("✅ Ocean chatbot loaded successfully!")
        
    except Exception as e:
        print(f"❌ Error loading model: {str(e)}")
        raise

def ask_ocean_question(question: str) -> str:
    global model, tokenizer
    
    if model is None or tokenizer is None:
        return "AI model is not loaded yet. Please try again in a moment."
    
    prompt = f"System: You are an oceanographic data expert that provides accurate information about ocean measurements.\nUser: {question}\nBot:"

    try:
        encoded = tokenizer(
            prompt,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=256
        )

        with torch.no_grad():
            outputs = model.generate(
                encoded["input_ids"],
                attention_mask=encoded["attention_mask"],
                max_new_tokens=60,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )

        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        if "Bot:" in decoded:
            return decoded.split("Bot:")[-1].strip()
        else:
            return "I need more specific ocean data to answer that question."
            
    except Exception as e:
        return f"Sorry, I encountered an error processing your question: {str(e)}"

@app.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """Chat with the fine-tuned ocean AI chatbot"""
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        answer = ask_ocean_question(request.question.strip())
        
        # Determine confidence based on answer quality
        confidence = "high" if len(answer) > 10 and "error" not in answer.lower() else "medium"
        
        return ChatResponse(
            question=request.question,
            answer=answer,
            model_type="Fine-tuned Transformers",
            confidence=confidence
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check for AI chatbot"""
    global model, tokenizer
    
    return {
        "status": "healthy" if model is not None and tokenizer is not None else "loading",
        "model_loaded": model is not None,
        "tokenizer_loaded": tokenizer is not None,
        "model_type": "Fine-tuned Ocean Chatbot"
    }

@app.get("/test")
async def test_ai():
    """Test the AI with sample questions"""
    test_questions = [
        "What is the ocean temperature?",
        "What is the salinity?",
        "What data did ARGO floats collect?"
    ]
    
    results = []
    for question in test_questions:
        answer = ask_ocean_question(question)
        results.append({"question": question, "answer": answer})
    
    return {"test_results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Different port from main API
