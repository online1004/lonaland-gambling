import requests 

def request(token, toss_id, amount):
    try:
        header = {"token" : token}
        json = {"id": toss_id, "amount": str(amount)}
        res = requests.post('http://##DOMAIN/api/toss/request', headers=header, json=json)
        post_json = res.json()
        if post_json['result'] == 'FAIL':
            print(post_json['message'])
            return 'FAIL'
        name = post_json['code']
        acc = post_json['accNumber']
        return name, acc
    except Exception as e:
        print(e)
        return 'FAIL'
    
def confirm(token, code):
    header = {"token" : token}
    json = {"code": code}
    res = requests.post('http://##DOMAIN/api/toss/confirm', json=json, headers=header)
    post_json = res.json()
    return post_json