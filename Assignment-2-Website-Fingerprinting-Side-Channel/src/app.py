# from flask import Flask, send_from_directory, request, jsonify
# import matplotlib
# matplotlib.use('Agg')  # Use non-interactive backend
# import matplotlib.pyplot as plt
# import numpy as np  
# import io
# import base64
# import os
# from datetime import datetime

# app = Flask(__name__)

# stored_traces = []
# stored_heatmaps = []

# @app.route('/')
# def index():
#     return send_from_directory('static', 'index.html')

# @app.route('/<path:path>')
# def static_files(path):
#     return send_from_directory('static', path)

# @app.route('/collect_trace', methods=['POST'])
# def collect_trace():
#     """ 
#     Implement the collect_trace endpoint to receive trace data from the frontend and generate a heatmap.
#     1. Receive trace data from the frontend as JSON
#     2. Generate a heatmap using matplotlib
#     3. Store the heatmap and trace data in the backend temporarily
#     4. Return the heatmap image and optionally other statistics to the frontend
#     """
#     try:
#         # Receive trace data from the frontend as JSON
#         data = request.get_json()
#         if not data or 'trace_data' not in data:
#             return jsonify({'error': 'No trace data provided'}), 400
            
#         trace_data = data['trace_data']
#         timestamp = data.get('timestamp', datetime.now().timestamp() * 1000)
        
#         # Convert trace data to numpy array for processing
#         trace_array = np.array(trace_data, dtype=float)
        
#         # Generate a heatmap using matplotlib
#         plt.figure(figsize=(10, 6))
        
#         # Create heatmap - reshape data into 2D for visualization
#         # We'll create a time-series heatmap
#         rows = int(np.sqrt(len(trace_array)))
#         cols = len(trace_array) // rows
#         if rows * cols < len(trace_array):
#             cols += 1
            
#         # Pad array if necessary
#         padded_length = rows * cols
#         if len(trace_array) < padded_length:
#             trace_array = np.pad(trace_array, (0, padded_length - len(trace_array)), 'constant')
        
#         heatmap_data = trace_array[:rows*cols].reshape(rows, cols)
        
#         # Create the heatmap
#         plt.imshow(heatmap_data, cmap='hot', interpolation='nearest', aspect='auto')
#         plt.colorbar(label='Cache Access Count')
#         plt.title(f'Cache Trace Heatmap - {datetime.fromtimestamp(timestamp/1000).strftime("%H:%M:%S")}')
#         plt.xlabel('Time Period')
#         plt.ylabel('Cache Line Group')
        
#         # Save heatmap to base64 string
#         img_buffer = io.BytesIO()
#         plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
#         img_buffer.seek(0)
#         img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
#         plt.close()
        
#         # Generate heatmap URL
#         heatmap_url = f"data:image/png;base64,{img_base64}"
        
#         # Calculate statistics
#         stats = {
#             'min': float(np.min(trace_data)),
#             'max': float(np.max(trace_data)),
#             'mean': float(np.mean(trace_data)),
#             'std': float(np.std(trace_data))
#         }
        
#         # Store the heatmap and trace data in the backend temporarily
#         stored_traces.append({
#             'trace_data': trace_data,
#             'timestamp': timestamp,
#             'stats': stats
#         })
        
#         stored_heatmaps.append({
#             'url': heatmap_url,
#             'timestamp': timestamp,
#             'stats': stats
#         })
        
#         # Return the heatmap image and statistics to the frontend
#         return jsonify({
#             'success': True,
#             'heatmap_url': heatmap_url,
#             'timestamp': timestamp,
#             'stats': stats,
#             'trace_count': len(stored_traces)
#         })
        
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/clear_results', methods=['POST'])
# def clear_results():
#     """ 
#     Implment a clear results endpoint to reset stored data.
#     1. Clear stored traces and heatmaps
#     2. Return success/error message
#     """
#     try:
#         global stored_traces, stored_heatmaps
        
#         # Clear stored traces and heatmaps
#         stored_traces.clear()
#         stored_heatmaps.clear()
        
#         return jsonify({
#             'success': True,
#             'message': 'Cleared all results successfully!'
#         })
        
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# @app.route('/api/get_results', methods=['GET'])
# def get_results():
#     """
#     Get all stored results including traces and heatmaps
#     """
#     try:
#         return jsonify({
#             'success': True,
#             'traces': stored_traces,
#             'heatmaps': stored_heatmaps,
#             'count': len(stored_traces)
#         })
        
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500


# # Additional endpoints can be implemented here as needed.

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)


from flask import Flask, send_from_directory, request, jsonify
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np  
import io
import base64
import os
from datetime import datetime

app = Flask(__name__)

stored_traces = []
stored_heatmaps = []

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

@app.route('/collect_trace', methods=['POST'])
def collect_trace():
    """ 
    Implement the collect_trace endpoint to receive trace data from the frontend and generate a heatmap.
    1. Receive trace data from the frontend as JSON
    2. Generate a heatmap using matplotlib
    3. Store the heatmap and trace data in the backend temporarily
    4. Return the heatmap image and optionally other statistics to the frontend
    """
    try:
        # Receive trace data from the frontend as JSON
        data = request.get_json()
        if not data or 'trace_data' not in data:
            return jsonify({'error': 'No trace data provided'}), 400
            
        trace_data = data['trace_data']
        timestamp = data.get('timestamp', datetime.now().timestamp() * 1000)
        
        # Convert trace data to numpy array for processing
        trace_array = np.array(trace_data, dtype=float)
        
        # Generate a timeline-style heatmap using matplotlib
        plt.figure(figsize=(12, 2))
        
        # Create a horizontal timeline heatmap - reshape data into a single row
        heatmap_data = trace_array.reshape(1, -1)
        
        # Create the heatmap with a colormap similar to the screenshot
        plt.imshow(heatmap_data, cmap='plasma', interpolation='nearest', aspect='auto')
        
        # Remove ticks and labels for cleaner look
        plt.xticks([])
        plt.yticks([])
        
        # Remove axes for cleaner appearance
        plt.axis('off')
        
        # Set tight layout
        plt.tight_layout(pad=0)
        
        # Save heatmap to base64 string
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        img_buffer.close()
        
        # Generate heatmap URL
        heatmap_url = f"data:image/png;base64,{img_base64}"
        
        # Calculate statistics
        stats = {
            'min': float(np.min(trace_data)),
            'max': float(np.max(trace_data)),
            'mean': float(np.mean(trace_data)),
            'std': float(np.std(trace_data)),
            'range': float(np.max(trace_data) - np.min(trace_data)),
            'samples': len(trace_data)
        }
        
        # Store the heatmap and trace data in the backend temporarily
        stored_traces.append({
            'trace_data': trace_data,
            'timestamp': timestamp,
            'stats': stats
        })
        
        stored_heatmaps.append({
            'url': heatmap_url,
            'timestamp': timestamp,
            'stats': stats
        })
        
        # Return the heatmap image and statistics to the frontend
        return jsonify({
            'success': True,
            'heatmap_url': heatmap_url,
            'timestamp': timestamp,
            'stats': stats,
            'trace_count': len(stored_traces)
        })
        
    except Exception as e:
        print(f"Error in collect_trace: {str(e)}")  # Add logging
        import traceback
        traceback.print_exc()  # Print full traceback for debugging
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear_results', methods=['POST'])
def clear_results():
    """ 
    Implment a clear results endpoint to reset stored data.
    1. Clear stored traces and heatmaps
    2. Return success/error message
    """
    try:
        global stored_traces, stored_heatmaps
        
        # Clear stored traces and heatmaps
        stored_traces.clear()
        stored_heatmaps.clear()
        
        return jsonify({
            'success': True,
            'message': 'Cleared all results successfully!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get_results', methods=['GET'])
def get_results():
    """
    Get all stored results including traces and heatmaps
    """
    try:
        return jsonify({
            'success': True,
            'traces': stored_traces,
            'heatmaps': stored_heatmaps,
            'count': len(stored_traces)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Additional endpoints can be implemented here as needed.

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)