# 文件名: server.py
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import dolphindb as ddb
import sys
import os
import torch
import json

# --- LlamaIndex 引用 ---
from llama_index.core import VectorStoreIndex, Settings, StorageContext
from llama_index.vector_stores.lancedb import LanceDBVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.retrievers import QueryFusionRetriever

# ==========================================
# 1. 全局配置 (DolphinDB & LlamaIndex)
# ==========================================
load_dotenv() 

# --- DolphinDB 配置 ---
DDB_HOST = os.getenv("DDB_HOST", "127.0.0.1")
DDB_PORT = int(os.getenv("DDB_PORT", 8848))
DDB_USER = os.getenv("DDB_USER", "admin")
DDB_PASS = os.getenv("DDB_PASS", "123456")

# --- MCP Server 配置 ---
MCP_SERVER_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_SERVER_PORT = int(os.getenv("MCP_PORT", 8000))
MCP_NAME = "DDB_AI_Agent"

# --- 知识库配置 ---
PERSIST_DIR = os.getenv("PERSIST_DIR", "./storage_data")  # 存放 docstore.json 等
DB_URI = os.getenv("DB_URI", "./lancedb_data")       # 存放向量数据
MODEL_NAME = "BAAI/bge-m3"

# ==========================================
# 2. 初始化资源 (启动时加载一次，避免每次搜索都卡顿)
# ==========================================
print("🚀 正在启动 MCP Server...")

# --- A. 初始化 DolphinDB 连接 ---
ddb_session = ddb.session()
try:
    ddb_session.connect(DDB_HOST, DDB_PORT, DDB_USER, DDB_PASS)
    print(f"✅ DolphinDB connected: {DDB_HOST}:{DDB_PORT}")
except Exception as e:
    print(f"❌ DolphinDB connection failed: {e}")

# --- B. 初始化 AI 检索系统 (完全遵循你的逻辑) ---
global_retriever = None 
try:
    print("📥 [1/4] 正在加载 Embedding 模型到 GPU...")
    Settings.llm = None
    device_type = "cuda" if torch.cuda.is_available() else "cpu"
    Settings.embedding_model = HuggingFaceEmbedding(
        model_name=MODEL_NAME, 
        device=device_type
    )
    print(f"   模型加载完成 (Device: {device_type.upper()})")
    if not os.path.exists(PERSIST_DIR) or not os.path.exists(DB_URI):
        print(f"⚠️ 警告：找不到数据目录 ({PERSIST_DIR} 或 {DB_URI})，搜索功能将不可用。")
    else:
        print("📚 [2/4] 正在加载 LanceDB 和 StorageContext...")
        vector_store = LanceDBVectorStore(uri=DB_URI, table_name="my_vectors")
        
        # 【关键】从持久化目录加载 docstore，确保 BM25 数据源准确
        storage_context = StorageContext.from_defaults(
            persist_dir=PERSIST_DIR, 
            vector_store=vector_store
        )
        
        # 加载索引
        index = VectorStoreIndex.from_vector_store(
            vector_store, 
            storage_context=storage_context,
            embed_model=Settings.embedding_model
        )
        
        # 准备向量检索器
        vector_retriever = index.as_retriever(similarity_top_k=5)
        print("🧮 [3/4] 正在构建 BM25 索引 (从 docstore)...")
        # 直接从加载好的 docstore 获取所有节点
        all_nodes = list(storage_context.docstore.docs.values())
        
        if all_nodes:
            bm25_retriever = BM25Retriever.from_defaults(
                nodes=all_nodes, 
                similarity_top_k=5,
                verbose=False
            )
            print("🔗 [4/4] 组装混合检索器 (QueryFusion)...")
            # 【关键】完全遵循你的要求：去掉了 mode="reciprocal_rank"
            global_retriever = QueryFusionRetriever(
                [vector_retriever, bm25_retriever],
                similarity_top_k=5,
                num_queries=1, 
                # mode="reciprocal_rank",  <-- 已删除，使用默认值
                use_async=False,
            )
            print("✅ 混合检索系统准备就绪！")
        else:
            print("⚠️ Docstore 为空，跳过 BM25 构建。")
except Exception as e:
    print(f"❌ AI 模块初始化失败: {e}")
    import traceback
    traceback.print_exc()
# ==========================================
# 3. 定义 MCP Server 与 工具
# ==========================================
mcp = FastMCP(
    name=MCP_NAME, 
    host=MCP_SERVER_HOST, 
    port=MCP_SERVER_PORT
)

@mcp.tool()
def execute_ddb_code(code: str) -> str:
    """
    执行一段 DolphinDB 脚本代码，并返回结果。
    用于查询数据库状态、验证DolphinDB语法或获取数据样本。
    """
    print(f"📝 [DDB] Executing: {code[:50]}...")
    try:
        # 1. 尝试直接运行 (DolphinDB SDK 会自动处理部分连接状态，或者抛出异常)
        result = ddb_session.run(code)
        return str(result)
    except Exception as e:
        # 2. 如果失败（可能是连接断开），尝试重连一次
        print(f"⚠️ 执行失败: {e}。正在尝试重连 DolphinDB...")
        try:
            ddb_session.connect(DDB_HOST, DDB_PORT, DDB_USER, DDB_PASS)
            print("✅ 重连成功，重试执行代码...")
            result = ddb_session.run(code)
            return str(result)
        except Exception as e2:
            # 3. 如果还失败，那就是真的失败了（语法错误或数据库挂了）
            return f"DolphinDB Error: {str(e2)}"
        
@mcp.tool()
def search_knowledge_base(query: str) -> str:
    """
    搜索本地知识库文档。
    当你需要查找 DolphinDB 的用法、项目文档或教程时使用此工具。
    返回最相关的文档片段。
    """
    print(f"🔍 [Search] Query: {query}")
    
    if global_retriever is None:
        return "Error: 检索系统未初始化 (请检查服务器启动日志)。"
    try:
        # 执行检索
        results = global_retriever.retrieve(query)
        
        # 格式化结果
        output = []
        for node in results:
            output.append({
                "score": round(node.score, 4),
                "file": node.metadata.get("file_name"),
                "content": node.text
            })
        
        return json.dumps(output, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Search Error: {str(e)}"
# ==========================================
# 4. 启动入口
# ==========================================
if __name__ == "__main__":
    transport_mode = "streamable-http"
    if len(sys.argv) > 1:
        transport_mode = sys.argv[1]
    print(f"📡 MCP Server Listening on {MCP_SERVER_HOST}:{MCP_SERVER_PORT}")
    mcp.run(transport_mode)