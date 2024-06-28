from frontend import parse
from backend import encode_constraint

example = '''
con main { all:
  size == 1024 * 5;
  
  2 SOCKET { all:
    5 CORE;
  };
} 
'''

if __name__ == '__main__':
    file = parse(example)
    main = encode_constraint(file.main_constraint())

    print(main)
