import sys
from src.shell import run_shell
from src.data_setup import setup_data_folder

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_data_folder()
        return
    run_shell()
    
    
if __name__ == "__main__":
    main()
