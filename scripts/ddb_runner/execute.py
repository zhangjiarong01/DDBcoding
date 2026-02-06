# execute.py
import dolphindb as ddb
import os
import argparse
import sys
from dotenv import load_dotenv

def load_config():
    # 优先加载当前目录 .env
    current_dir = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(current_dir, ".env"))
    
    # 尝试加载上级目录 .env 作为 fallback
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir))) # DDBcoding root
    load_dotenv(os.path.join(parent_dir, ".env"))

    host = os.getenv("DDB_HOST")
    port = os.getenv("DDB_PORT")
    user = os.getenv("DDB_USER", "admin")
    password = os.getenv("DDB_PASS", "123456")
    
    if not host or not port:
        print("❌ Error: DDB_HOST and DDB_PORT must be set in .env file or environment variables.")
        sys.exit(1)
        
    return host, int(port), user, password

def run_script(session, script_content):
    try:
        print("Executing script...")
        result = session.run(script_content)
        print("✅ Execution Successful")
        print("--- Result ---")
        print(result)
        print("--------------")
        return result
    except Exception as e:
        print(f"❌ Execution Failed: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="DolphinDB Script Executor")
    parser.add_argument("file", nargs="?", help="Path to .dos or .txt script file")
    parser.add_argument("-c", "--code", help="Direct code string to execute")
    
    args = parser.parse_args()
    
    if not args.file and not args.code:
        print("Please provide a file path or use -c to specify code.")
        parser.print_help()
        sys.exit(1)

    host, port, user, password = load_config()
    
    s = ddb.session()
    print(f"🔌 Connecting to {host}:{port}...")
    try:
        s.connect(host, port, user, password)
        print("✅ Connected")
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        sys.exit(1)

    script = args.code
    if args.file:
        if os.path.exists(args.file):
            with open(args.file, "r", encoding="utf-8") as f:
                script = f.read()
        else:
            print(f"❌ File not found: {args.file}")
            sys.exit(1)

    if script:
        run_script(s, script)

if __name__ == "__main__":
    main()
