import subprocess
import os

def export_logs_to_txt(folder_path="src\python\data_files", file_name="logs.txt"):
    # Ensure the folder exists
    os.makedirs(folder_path, exist_ok=True)

    # Full path for output file
    output_file = os.path.join(folder_path, file_name)

    cmd = [
        r"C:\Program Files\MongoDB\Tools\100\bin\mongoexport.exe",
        "--uri=mongodb://localhost:27017/User_logs",
        "--collection=logs",
        "--out", output_file,
        "--jsonArray"   # export as JSON array
    ]
    
    subprocess.run(cmd, check=True)
    print(f"Logs exported to {output_file}")
    
if __name__ == "__main__":
    export_logs_to_txt()