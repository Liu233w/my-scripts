import os

can_extensions = ['.java', '.tag', '.jsp']

base_path = r'c:\temp'
dir_ = 'java-codes'

filea = open('out.md', 'w', encoding='utf-8')

the_path = os.path.join(base_path, dir_)
print(the_path)

for fpath, dirs, fs in os.walk(the_path):
    for f in fs:
        _, ext = os.path.splitext(f)
        if ext in can_extensions:
            print('### ' + f, file=filea)
            print('``` ' + ext[1:], file=filea)
            with open(os.path.join(fpath, f), encoding='utf-8') as fr:
                for line in fr:
                    print(line, file=filea, end='')
            print('\n```', file=filea)
            print('', file=filea)

filea.close()
