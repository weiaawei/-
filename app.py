import os
from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv
from services.deepseek_service import DeepseekService
from services.question_generator import QuestionGenerator
from services.export_service import ExportService
import logging
from werkzeug.utils import secure_filename

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 增加到32MB
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key')

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 初始化服务
deepseek_service = DeepseekService()
question_generator = QuestionGenerator(deepseek_service)
export_service = ExportService()

ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'xlsx', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-single', methods=['POST'])
def generate_single():
    try:
        data = request.form
        subject = data.get('subject', '')
        topic = data.get('topic', '')
        question_type = data.get('questionType', '')
        difficulty = data.get('difficulty', '')
        context = data.get('context', '')
        
        # 处理上传的文件（如果有）
        file_content = ""
        if 'referenceFile' in request.files:
            file = request.files['referenceFile']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # 提取文件内容
                file_content = export_service.extract_text_from_file(file_path)
        
        # 生成试题
        question = question_generator.generate_single_question(
            subject=subject,
            topic=topic,
            question_type=question_type,
            difficulty=difficulty,
            context=context,
            reference_text=file_content
        )
        
        return jsonify(question)
    except Exception as e:
        logger.error(f"生成试题失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate-batch', methods=['POST'])
def generate_batch():
    try:
        data = request.form
        subject = data.get('subject', '')
        topic = data.get('topic', '')
        num_questions = int(data.get('numQuestions', 5))
        question_types = request.form.getlist('questionTypes')
        difficulty = data.get('difficulty', '')
        context = data.get('context', '')
        
        # 处理上传的文件
        file_content = ""
        if 'referenceFile' in request.files:
            file = request.files['referenceFile']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # 提取文件内容
                file_content = export_service.extract_text_from_file(file_path)
        
        # 生成批量试题
        questions = question_generator.generate_batch_questions(
            subject=subject,
            topic=topic,
            num_questions=num_questions,
            question_types=question_types,
            difficulty=difficulty,
            context=context,
            reference_text=file_content
        )
        
        return jsonify(questions)
    except Exception as e:
        logger.error(f"批量生成试题失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/export', methods=['POST'])
def export():
    try:
        data = request.json
        questions = data.get('questions', [])
        export_format = data.get('format', 'xlsx')
        
        if not questions:
            return jsonify({"error": "没有要导出的试题"}), 400
        
        # 导出文件
        export_path = export_service.export_questions(questions, export_format)
        
        return send_file(export_path, as_attachment=True)
    except Exception as e:
        logger.error(f"导出试题失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 