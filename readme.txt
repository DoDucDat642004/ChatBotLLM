Dowload Ollama (https://ollama.com/)
Sau khi get model chú ý là phiên bản nào thì sửa đổi load đúng phiên bản đó trong app.py --> Sửa llm = Ollama(model="llama3.2")

pip install -U langchain langchain-community langchain-ollama
pip install -U langchain-huggingface
pip install -U langchain-ollama

pip install mysql-connector-python

pip install diskcache

brew install ngrok     # Mac
choco install ngrok    # Windows

pip install fastapi uvicorn

### Run
Run in terminal (VSCode) : uvicorn app:app --host 0.0.0.0 --port 8000
Run in terminal (Windows/Mac) : ngrok http 8000

Thay đổi đường dẫn trong chatbot.js, index.html
<script src="https://71ac-171-235-249-77.ngrok-free.app/chatbot.js"></script>