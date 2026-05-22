import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

class RAGManager:
    def __init__(self, data_path=None):
        # Resolve data path relative to the backend directory
        if data_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.data_path = os.path.join(base_dir, "data", "kb.txt")
        else:
            self.data_path = data_path

        # Initialize embeddings lazily; may fail if API key missing or network unavailable
        try:
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=os.getenv("GEMINI_API_KEY")
            )
        except Exception as e:
            print(f"Warning: Could not initialize GoogleGenerativeAIEmbeddings: {e}")
            self.embeddings = None
        self.db = None
        self._initialize_db()


    def _initialize_db(self):
        if not os.path.exists(self.data_path):
            print(f"Warning: Data path {self.data_path} not found.")
            return

        if self.embeddings is None:
            print("Skipping vector store initialization due to missing embeddings.")
            self.db = None
            return
        loader = TextLoader(self.data_path)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = text_splitter.split_documents(documents)
        try:
            self.db = FAISS.from_documents(docs, self.embeddings)
        except Exception as e:
            print(f"Warning: Could not create FAISS vector store: {e}")
            self.db = None


    def search(self, query, k=3):
        if not self.db:
            return ""
        results = self.db.similarity_search(query, k=k)
        return "\n".join([r.page_content for r in results])
