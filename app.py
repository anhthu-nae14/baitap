from flask import Flask, render_template, request
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import io

app = Flask(__name__)

# Hàm để chạy notebook và lấy kết quả
def run_notebook(filepath):
    try:
        # Mở notebook
        with open(filepath, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)

        # Tạo một preprocessor để thực thi notebook
        ep = ExecutePreprocessor(timeout=600, kernel_name='python3')

        # Tạo một biến lưu kết quả
        buffer = io.StringIO()

        # Thực thi notebook
        ep.preprocess(nb, {'metadata': {'path': './'}})

        # Trả lại nội dung các ô output từ notebook (nếu cần)
        for cell in nb.cells:
            if 'outputs' in cell:
                for output in cell['outputs']:
                    if output.output_type == 'stream':
                        buffer.write(output.text)
                    elif output.output_type == 'execute_result':
                        buffer.write(str(output['data']))

        # Trả về kết quả đầu ra
        return buffer.getvalue()
    except Exception as e:
        return f"Lỗi khi chạy notebook: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

# Route xử lý khi người dùng tải file Excel lên và chọn notebook
@app.route('/submit', methods=['POST'])
def submit():
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files['file']
    
    if file.filename == '':
        return "No selected file"
    
    if file:
        # Lưu file Excel tải lên
        file.save('./input_data.xlsx')  # Lưu file vào thư mục hiện tại

        # Lấy notebook mà người dùng chọn
        notebook = request.form['notebook']
        
        # Xử lý theo notebook được chọn
        if notebook == 'knn1':
            result = run_notebook('KNN_BT1-practice.ipynb')
        elif notebook == 'knn2':
            result = run_notebook('KNN_BT2-practice.ipynb')
        elif notebook == 'centroid':
            result = run_notebook('Centroid_practice.ipynb')
        else:
            return "Invalid notebook selected"

        # Trả kết quả về template results.html
        return render_template('results.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
