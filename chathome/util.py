import json

# 保存cookie到文件
def save_cookies_to_file(cookies, filename):
    with open(filename, 'w') as f:
        json.dump(cookies, f)

# 从文件中加载cookie
def load_cookies_from_file(filename):
    with open(filename, 'r') as f:
        cookies = json.load(f)
    return cookies