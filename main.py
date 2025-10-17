import os
import mysql.connector
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_ollama import OllamaLLM as Ollama
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document

DATA_PATH = "data.txt"
DB_DIR = "db"
SIMILARITY_THRESHOLD = 0.8

# Load components at startup
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
llm = Ollama(model="llama3.2")
# llm = Ollama(model="llama3.2:1b", max_tokens=200, temperature=0.0)

if os.path.exists(DB_DIR):
    db = Chroma(persist_directory=DB_DIR, embedding_function=embedding_model)
else:
    loader = TextLoader(DATA_PATH, encoding='utf-8')
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50) # 500 50
    docs = text_splitter.split_documents(documents)
    db = Chroma.from_documents(docs, embedding_model, persist_directory=DB_DIR)

retriever = db.as_retriever(search_kwargs={"k": 2})

prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
        {context}

        Câu hỏi: {question}
        """
)
def fetch_new_tours_from_mysql():
    conn = mysql.connector.connect(
        host="localhost", user="root", password="", database="travela"
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT tourId, title, time, quantity, priceAdult, priceChild, duration, 
               destination, availability, description, reviews, domain, startDate, endDate
        FROM tbl_tours 
        WHERE startDate >= NOW() - INTERVAL 5 MINUTE
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_vector_db_from_mysql():
    new_tours = fetch_new_tours_from_mysql()
    if not new_tours:
        return
    docs = []
    for tour in new_tours:
        content = (
            f"Tiêu đề: {tour['title']}\n"
            f"Thời gian: {tour['time']}\n"
            f"Số lượng: {tour['quantity']}\n"
            f"Giá người lớn: {tour['priceAdult']} VND\n"
            f"Giá trẻ em: {tour['priceChild']} VND\n"
            f"Thời lượng: {tour['duration']}\n"
            f"Điểm đến: {tour['destination']}\n"
            f"Trạng thái: {'Còn chỗ' if tour['availability'] else 'Hết chỗ'}\n"
            f"Mô tả: {tour['description']}\n"
            f"Đánh giá: {tour['reviews']}\n"
            f"Miền: {'Miền Bắc' if tour['domain']=='b' else 'Miền Trung' if tour['domain']=='t' else 'Miền Nam'}\n"
            f"Khởi hành: {tour['startDate']}\n"
            f"Kết thúc: {tour['endDate']}"
        )
        docs.append(Document(page_content=content, metadata={"tourId": tour["tourId"]}))
    db.add_documents(docs)
    print(f"✅ Đã cập nhật {len(docs)} tour mới vào VectorDB.")


# while True:
#     query = input("Bạn: ")
#     if query.lower() == "exit":
#         break

#     relevant_docs = db.similarity_search_with_score(query, k=3)

#     print("📊 Mức độ tương đồng:")
#     for doc, score in relevant_docs:
#         print(f"Score: {score:.4f} → {'Dùng' if score <= SIMILARITY_THRESHOLD else 'Bỏ'}")

#     filtered_docs = [doc for doc, score in relevant_docs if score <= SIMILARITY_THRESHOLD]

#     if filtered_docs:
#         context = "\n".join([doc.page_content for doc in filtered_docs])
#         formatted_prompt = prompt_template.format(context=context, question=query)
#         response = llm.invoke(formatted_prompt)
#         print(f"\nBot (từ dữ liệu): {response}")
#     else:
#         pretrain_response = llm.invoke(query)
#         print(f"Bot (pretrain): {pretrain_response}")

#     print("\n")
