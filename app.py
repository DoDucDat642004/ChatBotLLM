from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from main import *
from diskcache import Cache
from time import perf_counter

# Khởi tạo cache LLM
cache = Cache(".llm_cache")

# FastAPI app
app = FastAPI()

# Enable CORS for frontend (localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return FileResponse("index.html")

@app.get("/style.css")
async def get_css():
    return FileResponse("style.css")

@app.get("/chatbot.html")
async def get_html():
    return FileResponse("chatbot.html")

@app.get("/chatbot.js")
async def get_js():
    return FileResponse("chatbot.js")

class ChatQuery(BaseModel):
    query: str

@app.post("/chat")
async def chat(query: ChatQuery):
    t0 = perf_counter()
    q = query.query.strip()

    # Check cache
    if q in cache:
        print("Trả lời từ cache")
        return {"response": cache[q]}

    # Vector search
    t1 = perf_counter()
    relevant_docs = db.similarity_search_with_score(q, k=3)
    filtered_docs = [doc for doc, score in relevant_docs if score <= SIMILARITY_THRESHOLD]
    t2 = perf_counter()

    # Format prompt
    if filtered_docs:
        context = "\n\n".join([doc.page_content.strip() for doc in filtered_docs])
        prompt = prompt_template.format(context=context, question=q)
        print(f"Bot (từ dữ liệu)\n")
    else:
        prompt = q
        print(f"Bot (pretrain)\n")
    t3 = perf_counter()

    # LLM response
    result = llm.invoke(prompt)
    t4 = perf_counter()

    # Store to cache
    cache[q] = result

    print(f"""
        - Tổng thời gian: {(t4 - t0):.2f}s
        - Vector search: {(t2 - t1):.2f}s
        - Tạo prompt:    {(t3 - t2):.2f}s
        - Ollama LLM:    {(t4 - t3):.2f}s
    """)
    return {"response": result}
