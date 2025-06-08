from dotenv import load_dotenv
import os

load_dotenv()

def main():
    example = os.getenv('EXAMPLE_VAR')
    print(f'EXAMPLE_VAR={example}')

if __name__ == '__main__':
    main()
    