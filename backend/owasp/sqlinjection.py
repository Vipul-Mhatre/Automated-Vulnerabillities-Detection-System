import requests
from bs4 import BeautifulSoup
import sys
from urllib.parse import urljoin

s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"

def get_forms(url):
    soup = BeautifulSoup(s.get(url).content, "html.parser")
    return soup.find_all("form")

def form_details(form):
    detailsOfForm = {}
    action = form.attrs.get("action", "").lower()  
    method = form.attrs.get("method", "get").lower()  
    inputs = []
    
    for input_tag in form.find_all("input"):
        input_type = input_tag.attrs.get("type", "text") 
        input_name = input_tag.attrs.get("name")
        input_value = input_tag.attrs.get("value", "")  
        inputs.append({"type": input_type, "name": input_name, "value": input_value})
    
    detailsOfForm["action"] = action
    detailsOfForm["method"] = method
    detailsOfForm["inputs"] = inputs
    
    return detailsOfForm

def vulnerable(response):
    errors = {"quoted string not properly terminated",
              "unclosed quotation mark after the character string",
              "you have an error in your sql syntax;"}

    for error in errors:
        if error in response.content.decode().lower():
            return True
    return False

def sql_injection_scan(url):
    forms = get_forms(url)
    print(f"[+] Detected {len(forms)} forms on {url}.")
    for form in forms:
        details = form_details(form)

        for c in "\"'":
            data = {}
            
            for input_tag in details["inputs"]:
                if input_tag["type"] == "hidden" or input_tag["value"]: 
                    data[input_tag["name"]] = input_tag["value"] + c
                elif input_tag["type"] != "submit": 
                    data[input_tag["name"]] = f"test{c}"
            
            url = urljoin(url, details["action"])
            
            if details["method"] == "post":
                res = s.post(url, data=data)
            elif details["method"] == "get":
                res = s.get(url, params=data)
        
            if vulnerable(res):
                print(f"SQL Injection attack vulnerability detected in form at {url}")
            else:
                print("No SQL Injection vulnerability detected")

if __name__ == "__main__":
    url_arg = "https://www.geeksforgeeks.org/python-programming-language/"
    sql_injection_scan(url_arg)