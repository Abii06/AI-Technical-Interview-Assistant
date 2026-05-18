import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

class RAGManager:
    def __init__(self, data_path=None):
        # Resolve data path relative to the project root
        if data_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.data_path = os.path.join(base_dir, "data", "kb.txt")
        else:
            self.data_path = data_path
            
        self.embeddings = HuggingFaceEmbeddings()
        self.db = None
        self._initialize_db()

    def _initialize_db(self):
        if not os.path.exists(self.data_path):
            print(f"Warning: Data path {self.data_path} not found.")
            return

        loader = TextLoader(self.data_path)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = text_splitter.split_documents(documents)
        self.db = FAISS.from_documents(docs, self.embeddings)

    def search(self, query, k=3):
        if not self.db:
            return ""
        results = self.db.similarity_search(query, k=k)
        return "\n".join([r.page_content for r in results])
