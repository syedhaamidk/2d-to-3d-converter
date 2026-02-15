#!/usr/bin/env python3
"""
Flask API Backend for Advanced 3D Converter
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import tempfile
import sys
from pathlib import Path

# Import the converter
sys.path.insert(0, os.path.dirname(__file__))
from advanced_converter import (
    HeightmapConverter,
    TopoMapConverter,
    BrailleConverter,
    QRCodeConverter,
    AIDepthConverter,
    MultiMaterialConverter
)

app = Flask(__name__, static_folder='.')
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

@app.route('/')
def index():
    """Serve the web interface"""
    return send_from_directory('.', 'web_interface.html')

@app.route('/api/convert/heightmap', methods=['POST'])
def convert_heightmap():
    """Convert image to heightmap 3D model"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        max_height = float(request.form.get('max_height', 10.0))
        base_thickness = float(request.form.get('base_thickness', 2.0))
        
        input_path = os.path.join(UPLOAD_FOLDER, 'input.jpg')
        file.save(input_path)
        
        output_path = os.path.join(UPLOAD_FOLDER, 'output.stl')
        result = HeightmapConverter.convert(
            input_path, output_path, 
            max_height=max_height, 
            base_thickness=base_thickness
        )
        
        return send_file(
            output_path,
            as_attachment=True,
            download_name='heightmap_model.stl',
            mimetype='model/stl'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/convert/braille', methods=['POST'])
def convert_braille():
    """Convert text to Braille 3D model"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        output_path = os.path.join(UPLOAD_FOLDER, 'braille.stl')
        result = BrailleConverter.convert(text, output_path)
        
        return send_file(
            output_path,
            as_attachment=True,
            download_name='braille_model.stl',
            mimetype='model/stl'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/convert/qr', methods=['POST'])
def convert_qr():
    """Convert data to QR code 3D model"""
    try:
        data = request.get_json()
        qr_data = data.get('data', '')
        stamp_mode = data.get('stamp', False)
        
        if not qr_data:
            return jsonify({'error': 'No data provided'}), 400
        
        output_path = os.path.join(UPLOAD_FOLDER, 'qr.stl')
        result = QRCodeConverter.convert(qr_data, output_path, invert=stamp_mode)
        
        return send_file(
            output_path,
            as_attachment=True,
            download_name='qr_model.stl',
            mimetype='model/stl'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/convert/topo', methods=['POST'])
def convert_topo():
    """Generate topographic map"""
    try:
        output_path = os.path.join(UPLOAD_FOLDER, 'terrain.stl')
        result = TopoMapConverter.from_fake_data(output_path)
        
        return send_file(
            output_path,
            as_attachment=True,
            download_name='terrain_model.stl',
            mimetype='model/stl'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/convert/depth', methods=['POST'])
def convert_depth():
    """Convert image using AI depth estimation"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        input_path = os.path.join(UPLOAD_FOLDER, 'input_depth.jpg')
        file.save(input_path)
        
        output_path = os.path.join(UPLOAD_FOLDER, 'depth.stl')
        result = AIDepthConverter.convert(input_path, output_path)
        
        return send_file(
            output_path,
            as_attachment=True,
            download_name='depth_model.stl',
            mimetype='model/stl'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/convert/multi', methods=['POST'])
def convert_multi():
    """Convert to multi-material model"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        input_path = os.path.join(UPLOAD_FOLDER, 'input_multi.jpg')
        file.save(input_path)
        
        output_prefix = os.path.join(UPLOAD_FOLDER, 'multi')
        files = MultiMaterialConverter.convert(input_path, output_prefix)
        
        first_file = list(files.values())[0]
        
        return send_file(
            first_file,
            as_attachment=True,
            download_name='multi_material_1.stl',
            mimetype='model/stl'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'features': ['heightmap', 'topo', 'braille', 'qr', 'depth', 'multi']
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)