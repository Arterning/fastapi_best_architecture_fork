import requests

from pathlib import Path

## 1 PDF 请求
def post_pdf_recog(input_path,
                   output_folder,
                   
                   language):
    url = "http://172.17.0.1:8101/process_imgpdf_files/"
    data = {
        "input_path": input_path,   # 替换为实际的输入文件路径
        "output_folder": output_folder,  # 替换为实际的输出文件路径
        "language" : language
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed:", response.status_code, response.text)

## 2  text 请求
def post_text_recog(input_path,
                   output_folder,
                   language):
    url = "http://172.17.0.1:8101/process_text_files/"
    data = {
        "input_path": input_path,   # 替换为实际的输入文件路径
        "output_folder": output_folder,  # 替换为实际的输出文件路径
        "language" : language
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed:", response.status_code, response.text)


## 3 image 请求
def post_imagesocr_recog(input_path,
                   output_folder,
                   language):
    url = "http://172.17.0.1:8101/process_imgocr_files/"
    data = {
        "input_path": input_path,   # 替换为实际的输入文件路径
        "output_folder": output_folder,  # 替换为实际的输出文件路径
        "language" : language
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed:", response.status_code, response.text)



## 4 audios 请求
def post_audios_recog(input_path,
                   output_folder,
                   language):
    url = "http://172.17.0.1:8101/process_audio_files/"
    data = {
        "input_path": input_path,   # 替换为实际的输入文件路径
        "output_folder": output_folder,  # 替换为实际的输出文件路径
        "language" : language
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed:", response.status_code, response.text)




## 5 emails 处理 
def post_emails_recog(input_path, # 输入含有邮件的目录
                   output_folder, # 附录下载目录
                   output_folder2, # 附录二次识别输出目录
                   language,
                   language2):
    url = "http://172.17.0.1:8101/process_email_files/"
    data = {
        "input_path": input_path,  
        "output_folder": output_folder, 
        "output_folder2": output_folder2,
        "language" : language,
        "language2" : language2
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed:", response.status_code, response.text)

