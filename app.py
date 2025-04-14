import os
import logging
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from cloudformation_generator import generate_lambda_cloudformation

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key_change_in_production")

@app.route('/')
def index():
    """Render the main page with the form to create CloudFormation template"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Generate the CloudFormation template based on form inputs"""
    try:
        # Get form data
        lambda_name = request.form.get('lambda_name', 'MyLambdaFunction')
        lambda_description = request.form.get('lambda_description', 'Lambda function created by CloudFormation')
        lambda_runtime = request.form.get('lambda_runtime', 'python3.9')
        lambda_handler = request.form.get('lambda_handler', 'index.handler')
        lambda_timeout = int(request.form.get('lambda_timeout', 60))
        lambda_memory = int(request.form.get('lambda_memory', 128))
        schedule_hour = int(request.form.get('schedule_hour', 8))
        schedule_minute = int(request.form.get('schedule_minute', 0))
        
        # Get custom code, IAM policy, and role name
        custom_code = request.form.get('custom_code', '')
        custom_iam_policy = request.form.get('custom_iam_policy', '')
        custom_role_name = request.form.get('custom_role_name', '')
        
        # Validate inputs
        if not 0 <= schedule_hour <= 23:
            flash('Schedule hour must be between 0 and 23', 'danger')
            return redirect(url_for('index'))
        
        if not 0 <= schedule_minute <= 59:
            flash('Schedule minute must be between 0 and 59', 'danger')
            return redirect(url_for('index'))
        
        if not 1 <= lambda_timeout <= 900:
            flash('Lambda timeout must be between 1 and 900 seconds', 'danger')
            return redirect(url_for('index'))
        
        if not 128 <= lambda_memory <= 10240:
            flash('Lambda memory must be between 128 and 10240 MB', 'danger')
            return redirect(url_for('index'))
        
        # Generate CloudFormation template
        template = generate_lambda_cloudformation(
            lambda_name=lambda_name,
            lambda_description=lambda_description,
            lambda_runtime=lambda_runtime,
            lambda_handler=lambda_handler,
            lambda_timeout=lambda_timeout,
            lambda_memory=lambda_memory,
            schedule_hour=schedule_hour,
            schedule_minute=schedule_minute,
            custom_code=custom_code,
            custom_iam_policy=custom_iam_policy,
            custom_role_name=custom_role_name
        )
        
        # Render the result page with the template
        return render_template('result.html', template=template, lambda_name=lambda_name)
    
    except Exception as e:
        logging.error(f"Error generating CloudFormation template: {e}", exc_info=True)
        flash(f'Error generating CloudFormation template: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/api/generate', methods=['POST'])
def api_generate():
    """API endpoint to generate the CloudFormation template"""
    try:
        # Get JSON data
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Get parameters with defaults
        lambda_name = data.get('lambda_name', 'MyLambdaFunction')
        lambda_description = data.get('lambda_description', 'Lambda function created by CloudFormation')
        lambda_runtime = data.get('lambda_runtime', 'python3.9')
        lambda_handler = data.get('lambda_handler', 'index.handler')
        lambda_timeout = int(data.get('lambda_timeout', 60))
        lambda_memory = int(data.get('lambda_memory', 128))
        schedule_hour = int(data.get('schedule_hour', 8))
        schedule_minute = int(data.get('schedule_minute', 0))
        
        # Get custom code, IAM policy, and role name
        custom_code = data.get('custom_code', '')
        custom_iam_policy = data.get('custom_iam_policy', '')
        custom_role_name = data.get('custom_role_name', '')
        
        # Generate CloudFormation template
        template = generate_lambda_cloudformation(
            lambda_name=lambda_name,
            lambda_description=lambda_description,
            lambda_runtime=lambda_runtime,
            lambda_handler=lambda_handler,
            lambda_timeout=lambda_timeout,
            lambda_memory=lambda_memory,
            schedule_hour=schedule_hour,
            schedule_minute=schedule_minute,
            custom_code=custom_code,
            custom_iam_policy=custom_iam_policy,
            custom_role_name=custom_role_name
        )
        
        return jsonify({'template': template})
    
    except Exception as e:
        logging.error(f"API error generating CloudFormation template: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
