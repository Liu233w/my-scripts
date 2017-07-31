import hashlib, os

data = input(">>> ")
out = hashlib.new('md5', data.encode('utf-8'))

print(out.hexdigest())

os.system('pause')
