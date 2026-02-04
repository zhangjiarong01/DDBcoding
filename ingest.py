import os
# --- 新增这一行 ---
# 强制使用国内镜像站下载模型，速度快且能连通
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
import torch  # 引入 torch 用来检查 GPU
from llama_index.core import (
    SimpleDirectoryReader, 
    StorageContext, 
    VectorStoreIndex, 
    Settings
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.ingestion import IngestionPipeline, IngestionCache
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.vector_stores.lancedb import LanceDBVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# --- 核心修改部分开始 ---

# 1. 检查 GPU 是否可用
device_type = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🚀 正在使用的计算设备: {device_type.upper()}")
if device_type == "cuda":
    print(f"   显卡型号: {torch.cuda.get_device_name(0)}")

# 2. 设置 Embedding 模型
# 既然有 A30，直接用 BAAI/bge-m3，效果比 small 好很多，支持多语言和长文本
# device参数强制让它跑在 GPU 上
Settings.embedding_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-m3", 
    device=device_type 
)
Settings.chunk_size = 512

# --- 核心修改部分结束 ---

# 准备存储路径
PERSIST_DIR = os.getenv("PERSIST_DIR", "./storage_data")  # 存放 docstore.json 等
DB_URI = os.getenv("DB_URI", "./lancedb_data")       # 存放向量数据
DOCS_DIR = os.getenv("DOCS_DIR", "/hdd/hdd9/jrzhang/projects/rag/DocForRag/docforrag/funcs/")
MODEL_NAME = "BAAI/bge-m3"

def ingest_documents():
    print(f"开始扫描目录: {DOCS_DIR}")
    
    vector_store = LanceDBVectorStore(uri=DB_URI, table_name="my_vectors")
    
    try:
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        docstore = storage_context.docstore
        print("✅ 加载了已有的 Docstore 状态。")
    except:
        docstore = SimpleDocumentStore()
        storage_context = StorageContext.from_defaults(docstore=docstore)
        print("🆕 创建了新的 Docstore。")

    try:
        # 读取文件
        documents = SimpleDirectoryReader(DOCS_DIR, recursive=True, required_exts=[".md"]).load_data()
        if not documents:
            print("⚠️ 目录中没有找到 .md 文件。")
            return
    except Exception as e:
        print(f"❌ 读取文件出错: {e}")
        return

    pipeline = IngestionPipeline(
        transformations=[
            SentenceSplitter(chunk_size=512, chunk_overlap=50),
            Settings.embedding_model, # 这里会调用 GPU
        ],
        vector_store=vector_store,
        docstore=docstore,
        cache=IngestionCache(), 
    )

    print("🔥 开始运行管道 (GPU 加速中)...")
    nodes = pipeline.run(documents=documents, show_progress=True)
    
    storage_context.persist(persist_dir=PERSIST_DIR)
    
    print(f"🎉 处理完成！本次处理了 {len(nodes)} 个分块。")

if __name__ == "__main__":
    ingest_documents()
