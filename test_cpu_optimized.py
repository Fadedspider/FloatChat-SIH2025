from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os

torch.set_num_threads(min(8, os.cpu_count()))

print("🔄 Loading your fine-tuned ocean chatbot...")
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

def ask_ocean_question(question):
    prompt = f"System: You are an oceanographic data expert that provides accurate information about ocean measurements.\nUser: {question}\nBot:"

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

def test_various_questions():
    test_questions = [
        "What is the ocean temperature at 13.33°N, 85.23°E?",
        "What is the salinity at 0.3 dbar pressure?",
        "What data did float 4903775 collect?",
        "What are the ocean conditions at 13.33, 85.23?",
        "What is the temperature and salinity in the Bay of Bengal?"
    ]
    
    print("\n🧪 Running automated tests...")
    for i, question in enumerate(test_questions, 1):
        print(f"\n--- Test {i} ---")
        print(f"Q: {question}")
        answer = ask_ocean_question(question)
        print(f"A: {answer}")

def main():
    print("🌊 Ocean Data Chatbot Ready! (Intel CPU Optimized)")
    print("💡 Type 'test' to run automated tests")
    print("💡 Type 'quit' to exit")
    
    while True:
        question = input("\nAsk about ocean data: ").strip()
        
        if question.lower() == "quit":
            print("👋 Goodbye!")
            break
        elif question.lower() == "test":
            test_various_questions()
        elif question:
            try:
                answer = ask_ocean_question(question)
                print(f"🤖 Bot: {answer}")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        else:
            print("💡 Please ask a question about ocean data")

if __name__ == "__main__":
    main()
