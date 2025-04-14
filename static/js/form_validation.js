// Form validation and dynamic UI updates

document.addEventListener('DOMContentLoaded', function() {
    // Form validation
    const form = document.getElementById('cfnForm');
    
    if (form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
        
        // Update displayed schedule time when inputs change
        const hourInput = document.getElementById('schedule_hour');
        const minuteInput = document.getElementById('schedule_minute');
        const scheduleDisplay = document.getElementById('scheduleTime');
        
        if (hourInput && minuteInput && scheduleDisplay) {
            const updateScheduleDisplay = function() {
                let hour = parseInt(hourInput.value, 10);
                const minute = parseInt(minuteInput.value, 10).toString().padStart(2, '0');
                
                // Format hour for display
                let displayHour;
                let amPm;
                
                if (hour === 0) {
                    displayHour = '12';
                    amPm = 'AM';
                } else if (hour < 12) {
                    displayHour = hour.toString();
                    amPm = 'AM';
                } else if (hour === 12) {
                    displayHour = '12';
                    amPm = 'PM';
                } else {
                    displayHour = (hour - 12).toString();
                    amPm = 'PM';
                }
                
                scheduleDisplay.textContent = `${displayHour}:${minute}`;
                scheduleDisplay.nextSibling.textContent = ` ${amPm}`;
            };
            
            // Set initial display
            updateScheduleDisplay();
            
            // Update on input change
            hourInput.addEventListener('input', updateScheduleDisplay);
            minuteInput.addEventListener('input', updateScheduleDisplay);
            
            // Validate hour input
            hourInput.addEventListener('change', function() {
                const value = parseInt(this.value, 10);
                if (isNaN(value) || value < 0) {
                    this.value = 0;
                } else if (value > 23) {
                    this.value = 23;
                }
                updateScheduleDisplay();
            });
            
            // Validate minute input
            minuteInput.addEventListener('change', function() {
                const value = parseInt(this.value, 10);
                if (isNaN(value) || value < 0) {
                    this.value = 0;
                } else if (value > 59) {
                    this.value = 59;
                }
                updateScheduleDisplay();
            });
        }
        
        // Lambda name validation
        const lambdaNameInput = document.getElementById('lambda_name');
        if (lambdaNameInput) {
            lambdaNameInput.addEventListener('input', function() {
                // Replace invalid characters
                this.value = this.value.replace(/[^a-zA-Z0-9_-]/g, '');
            });
        }
        
        // Lambda handler validation
        const lambdaHandlerInput = document.getElementById('lambda_handler');
        if (lambdaHandlerInput) {
            lambdaHandlerInput.addEventListener('input', function() {
                // Ensure there's at least one dot
                if (!this.value.includes('.') && this.value.length > 0) {
                    this.setCustomValidity('Handler must be in format: file.function_name');
                } else {
                    this.setCustomValidity('');
                }
            });
        }
        
        // Runtime change handler for code template
        const runtimeSelect = document.getElementById('lambda_runtime');
        const customCodeTextarea = document.getElementById('custom_code');
        
        if (runtimeSelect && customCodeTextarea) {
            // Function to show code template based on runtime
            const showCodeTemplate = function() {
                const runtime = runtimeSelect.value;
                let templateCode = '';
                
                if (runtime.includes('python')) {
                    templateCode = `import json
import boto3
import os
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info('Lambda function invoked!')
    logger.info(f'Event: {json.dumps(event)}')
    
    # Get environment variables
    table_name = os.environ.get('TABLE_NAME')
    
    # Your business logic here
    result = {'status': 'success', 'message': 'Task completed successfully'}
    
    return {
        'statusCode': 200,
        'body': json.dumps(result),
        'headers': {'Content-Type': 'application/json'}
    }`;
                } else if (runtime.includes('nodejs')) {
                    templateCode = `const AWS = require('aws-sdk');

exports.handler = async (event, context) => {
    console.log('Lambda function invoked!');
    console.log('Event:', JSON.stringify(event, null, 2));
    
    // Get environment variables
    const tableName = process.env.TABLE_NAME;
    
    try {
        // Your business logic here
        const result = { status: 'success', message: 'Task completed successfully' };
        
        return {
            statusCode: 200,
            body: JSON.stringify(result),
            headers: { 'Content-Type': 'application/json' }
        };
    } catch (error) {
        console.error('Error:', error);
        
        return {
            statusCode: 500,
            body: JSON.stringify({ status: 'error', message: error.message }),
            headers: { 'Content-Type': 'application/json' }
        };
    }
};`;
                }
                
                // Only replace if the textarea is empty
                if (!customCodeTextarea.value.trim()) {
                    customCodeTextarea.value = templateCode;
                }
            };
            
            // Add template code button next to the textarea
            const codeLabel = document.querySelector('label[for="custom_code"]');
            if (codeLabel) {
                const templateButton = document.createElement('button');
                templateButton.type = 'button';
                templateButton.className = 'btn btn-sm btn-outline-secondary ms-2';
                templateButton.innerHTML = 'Show Template';
                templateButton.addEventListener('click', function(e) {
                    e.preventDefault();
                    showCodeTemplate();
                });
                codeLabel.appendChild(templateButton);
            }
            
            // Update template on runtime change
            runtimeSelect.addEventListener('change', function() {
                // Only show template if textarea is empty
                if (!customCodeTextarea.value.trim()) {
                    showCodeTemplate();
                }
            });
        }
        
        // IAM Policy template button
        const policyTextarea = document.getElementById('custom_iam_policy');
        if (policyTextarea) {
            const policyLabel = document.querySelector('label[for="custom_iam_policy"]');
            if (policyLabel) {
                const policyTemplateButton = document.createElement('button');
                policyTemplateButton.type = 'button';
                policyTemplateButton.className = 'btn btn-sm btn-outline-secondary ms-2';
                policyTemplateButton.innerHTML = 'Show Template';
                policyTemplateButton.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    const policyTemplate = {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Action": [
                                    "logs:CreateLogGroup",
                                    "logs:CreateLogStream",
                                    "logs:PutLogEvents",
                                    "logs:DescribeLogStreams"
                                ],
                                "Resource": "arn:aws:logs:*:*:log-group:/aws/lambda/*"
                            },
                            {
                                "Effect": "Allow",
                                "Action": [
                                    "xray:PutTraceSegments",
                                    "xray:PutTelemetryRecords"
                                ],
                                "Resource": "*"
                            }
                        ]
                    };
                    
                    policyTextarea.value = JSON.stringify(policyTemplate, null, 4);
                });
                policyLabel.appendChild(policyTemplateButton);
            }
        }
    }
});
