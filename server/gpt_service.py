from flask import Blueprint, request, jsonify
import os
import openai
import base64
import requests
from io import BytesIO
from PIL import Image

gpt_bp = Blueprint('gpt', __name__)

# 配置OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')

@gpt_bp.route('/process-image', methods=['POST'])
def process_image():
    try:
        data = request.get_json()
        image_data = data.get('image')
        style = data.get('style')
        
        # 解码Base64图片
        image_bytes = base64.b64decode(image_data.split(',')[1])
        image = Image.open(BytesIO(image_bytes))
        
        # 调整图片大小以符合API要求
        max_size = (1024, 1024)
        image.thumbnail(max_size, Image.LANCZOS)
        
        # 将图片转换回Base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        processed_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # 准备提示词
        prompts = {
            'anime': 'Transform this image into anime style art',
            'oil': 'Transform this image into an oil painting style',
            'sketch': 'Transform this image into a detailed pencil sketch',
            'watercolor': 'Transform this image into watercolor painting style',
            'pixel': 'Transform this image into pixel art style'
        }
        
        prompt = prompts.get(style, 'Transform this image into a artistic style')
        
        # 调用DALL-E API
        response = openai.Image.create_variation(
            image=processed_image,
            n=1,
            size="1024x1024"
        )
        
        # 获取生成的图片URL
        result_url = response['data'][0]['url']
        
        # 下载生成的图片并转换为Base64
        result_response = requests.get(result_url)
        result_image = base64.b64encode(result_response.content).decode('utf-8')
        
        return jsonify({
            'status': 'success',
            'image': f'data:image/png;base64,{result_image}'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@gpt_bp.route('/styles', methods=['GET'])
def get_styles():
    """获取可用的图片风格列表"""
    styles = [
        {
            'id': 'anime',
            'name': '动漫风格',
            'description': '将图片转换为动漫艺术风格'
        },
        {
            'id': 'oil',
            'name': '油画风格',
            'description': '将图片转换为油画艺术风格'
        },
        {
            'id': 'sketch',
            'name': '素描风格',
            'description': '将图片转换为铅笔素描风格'
        },
        {
            'id': 'watercolor',
            'name': '水彩风格',
            'description': '将图片转换为水彩画风格'
        },
        {
            'id': 'pixel',
            'name': '像素风格',
            'description': '将图片转换为像素艺术风格'
        }
    ]
    
    return jsonify(styles)