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
        # 输入输出目录
        input_path = Path(input_path)
        output_folder = Path(output_folder)  
        output_folder.parent.mkdir(exist_ok=True,parents=True)

        output_folder2 = Path(output_folder2)  
        output_folder2.parent.mkdir(exist_ok=True,parents=True)

        ## ## 获取所有邮件和附件 ， file_path,content,belong 
        # 其中附件的content均不知道，因此调用上述算法再次识别一遍。
        all_eml_infos =  parse_emails_fromfolder(folder=input_path,
                          attachments_savefolder=output_folder)
        
        ## 依次调用各个请求。
        attachments_results = []
        output_folder = str(output_folder)
        output_folder2 = str(output_folder2)

        ## 01 测试 PDF 文件提取
        pdf_records = post_pdf_recog(input_path = output_folder,
                       output_folder = output_folder2 ,
                       language = language)
        if pdf_records != None:
            attachments_results += pdf_records

        ## 02 测试 text文件提取
        text_records = post_text_recog(input_path = output_folder,
                       output_folder = output_folder2 ,
                        language = language)
        if text_records != None:
            attachments_results += text_records


        ## 03 测试 img 文件提取
        images_records = post_imagesocr_recog(input_path = output_folder,
                       output_folder = output_folder2,
                       language = language)
        if images_records!= None:
            attachments_results += images_records
        
        ## 04 音频文件提取
        audios_records = post_audios_recog(input_path = output_folder ,
                       output_folder = output_folder2,
                       language = language2)
        if audios_records!= None:
            attachments_results += audios_records

        # print("attachments_results:")
        # print([ x["file_path"] for x in attachments_results])
        # print("-***************************--")
        # print("all_eml_infos:")
        # print([x["file_path"] for x in all_eml_infos])
        # exit()

        attachments_results_reshape = {} # 转换为字典，方便索引
        for it in attachments_results:
            attachments_results_reshape[it["file_path"]] = it["content"]

        for eml_info in all_eml_infos:
            filepath  = eml_info["file_path"]
            # 开始附件内容替换
            try:
                eml_info["content"] = attachments_results_reshape[filepath]
            except Exception as e :
                continue
                
        return all_eml_infos


def all_datas_recog(input_path,output_folder,output_folder_eml01,output_folder_eml02,language,language2
                    ):
    ## 01 测试 PDF 文件提取
    pdf_records = post_pdf_recog(input_path = input_path,
                   output_folder = output_folder ,
                   language = language)
    print("pdf 识别完毕")
    ## 02 测试 text文件提取
    text_records = post_text_recog(input_path = input_path,
                   output_folder = output_folder ,
                    language = language)

    print("text 识别完毕")
    ## 03 测试 img 文件提取
    images_records = post_imagesocr_recog(input_path,
                   output_folder,
                   language)

    print("images 识别完毕")
    ## 04 音频文件提取
    audios_records = post_audios_recog(input_path,
                   output_folder,
                   language2)
    print("audios 识别完毕")

    ### 05 邮件 提取
    all_eml_infos = post_emails_recog(input_path = input_path, # 输入含有邮件的目录
                   output_folder =output_folder_eml01,
                    output_folder2=output_folder_eml02, # 附录下载目录
                   language = language,
                   language2 = language2)
    print("emails 识别完毕")
    # print("emails:")
    # for it in all_eml_infos:
    #     print(it)
    #     print("---=====-----")
    return pdf_records,text_records,images_records,audios_records,all_eml_infos

if __name__ =="__main__":

    """
    1、 mineru  + paddle ocr 技术 识别pdf文件。它会为每个pdf文件产生一个文件夹。
    2、sherpaonnx库识别语音
    3、eml文件产生的附件，仍然采取1、2去识别。
    
    """

    input_path = "多类别测试文件"   ## 含有各种类型文件的目录
    output_folder  = "多类别测试文件_识别输出"  # 输出pdf文件的识别的结果 存储目录 （由于mineru如此）
    output_folder_eml01= "多类别测试文件/附件下载" # 附件下载目录
    output_folder_eml02= "多类别测试文件/附件二次识别" # 附近再次识别的输出目录
    language = "zhen_light" ## 控制paddle OCR 语言
    language2 = "zhen" # 控制 语音识别模型语言

    ## 1 PDF 请求
    input_path = "多类别测试文件/ocr_en_pdf_01/en论文01.pdf"
    output_folder = "V3测试输出"
    language = "zhen_light"
    output = post_pdf_recog(input_path,
                   output_folder,
                   language)
    print(output[0])

    ## 2 text 请求
    input_path = "client.py"
    output_folder = "V3测试输出"
    language = ""
    output =  post_text_recog(input_path,
                   output_folder,
                   language)
    print(output[0])

    # 3 图像请求
    input_path = "多类别测试文件/ocr_zhen_image/微信截图_20241018112008.jpg"
    output_folder = "V3测试输出"
    language = "zhen_light"
    output = post_imagesocr_recog(input_path,
                   output_folder,
                   language)
    print(output[0])


    ##  4 音频
    input_path = "多类别测试文件/test_wavs/瑞瑞录音01.wav"
    output_folder = ""
    language2 = "zhen"
    output  = post_audios_recog(input_path,
                   output_folder,
                   language2)
    print(output[0])

    # ## 5 eml
    # input_path = "多类别测试文件"   ## 含有各种类型文件的目录
    # output_folder  = "多类别测试文件_识别输出"  # 输出pdf文件的识别的结果 存储目录 （由于mineru如此）
    # output_folder_eml01= "多类别测试文件/附件下载" # 附件下载目录
    # output_folder_eml02= "多类别测试文件/附件二次识别" # 附近再次识别的输出目录
    # language = "zhen_light" ## 控制paddle OCR 语言
    # language2 = "zhen" # 控制 语音识别模型语言
    # all_eml_infos = post_emails_recog(input_path = input_path, # 输入含有邮件的目录
    #                output_folder =output_folder_eml01,
    #                 output_folder2=output_folder_eml02, # 附录下载目录
    #                language = language,
    #                language2 = language2)
    # print(all_eml_infos)



    pass

