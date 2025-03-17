import PyPDF2

# 输入和输出文件路径
input_pdf_path = "book/模拟电子技术基础（第五版）高清版- 清华大学电子学教研组编、童诗白、华成英.pdf"  # 原始 PDF 文件路径
output_pdf_path = "book/test.pdf"  # 输出文件路径

# 读取原始 PDF
with open(input_pdf_path, "rb") as file:
    pdf_reader = PyPDF2.PdfReader(file)

    # 创建一个写入器
    pdf_writer = PyPDF2.PdfWriter()

    # 截取前 100 页（如果总页数不足 100 页则取所有页）
    total_pages = len(pdf_reader.pages)
    num_pages_to_extract = min(total_pages, 60)

    print(f"Original PDF has {total_pages} pages. Extracting first {num_pages_to_extract} pages.")

    for page_num in range(num_pages_to_extract):
        pdf_writer.add_page(pdf_reader.pages[page_num])

    # 保存新 PDF
    with open(output_pdf_path, "wb") as output_file:
        pdf_writer.write(output_file)

print(f"Output saved to {output_pdf_path}")