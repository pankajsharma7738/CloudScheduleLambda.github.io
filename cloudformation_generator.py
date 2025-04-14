import yaml
import logging
import json

def generate_lambda_cloudformation(
    lambda_name="MyLambdaFunction",
    lambda_description="Lambda function created by CloudFormation",
    lambda_runtime="python3.9",
    lambda_handler="index.handler",
    lambda_timeout=60,
    lambda_memory=128,
    schedule_hour=8,
    schedule_minute=0,
    custom_code="",
    custom_iam_policy="",
    custom_role_name=""
):
    """
    Generate AWS CloudFormation template for Lambda function with daily schedule
    
    Parameters:
    ----------
    lambda_name : str
        Name of the Lambda function
    lambda_description : str
        Description of the Lambda function
    lambda_runtime : str
        Runtime for the Lambda function (e.g., python3.9)
    lambda_handler : str
        Handler function in format file.function_name
    lambda_timeout : int
        Timeout in seconds (1-900)
    lambda_memory : int
        Memory allocation in MB (128-10240)
    schedule_hour : int
        Hour of day to run (0-23)
    schedule_minute : int
        Minute of hour to run (0-59)
    
    Returns:
    -------
    str
        YAML CloudFormation template
    """
    
    try:
        # Create cron expression for the schedule (8 AM daily by default)
        cron_expression = f"cron({schedule_minute} {schedule_hour} * * ? *)"
        
        # If custom code is provided, use it instead of the default template
        if custom_code.strip():
            # Split the custom code into lines
            lambda_code = custom_code.strip().split('\n')
        else:
            # Default code templates based on runtime
            if "python" in lambda_runtime:
                lambda_code = [
                    "import json",
                    "import boto3",
                    "import os",
                    "import logging",
                    "",
                    "# Configure logging",
                    "logger = logging.getLogger()",
                    "logger.setLevel(logging.INFO)",
                    "",
                    "# Initialize AWS clients",
                    "s3_client = boto3.client('s3')",
                    "dynamodb = boto3.resource('dynamodb')",
                    "",
                    "def handler(event, context):",
                    "    logger.info('Lambda function invoked!')",
                    "    logger.info(f'Event: {json.dumps(event)}')",
                    "    ",
                    "    # Example: Get environment variables",
                    "    table_name = os.environ.get('TABLE_NAME')",
                    "    bucket_name = os.environ.get('BUCKET_NAME')",
                    "    ",
                    "    logger.info(f'Using DynamoDB table: {table_name}')",
                    "    logger.info(f'Using S3 bucket: {bucket_name}')",
                    "    ",
                    "    # Example: Process data from S3 and store in DynamoDB",
                    "    try:",
                    "        # Your business logic here",
                    "        result = {'status': 'success', 'message': 'Task completed successfully'}",
                    "        logger.info('Process completed successfully')",
                    "        ",
                    "        # Example: Write to DynamoDB if table exists",
                    "        if table_name:",
                    "            table = dynamodb.Table(table_name)",
                    "            table.put_item(Item={",
                    "                'id': context.aws_request_id,",
                    "                'timestamp': int(context.get_remaining_time_in_millis()),",
                    "                'status': 'COMPLETED'",
                    "            })",
                    "    except Exception as e:",
                    "        logger.error(f'Error processing data: {str(e)}')",
                    "        result = {'status': 'error', 'message': str(e)}",
                    "    ",
                    "    return {",
                    "        'statusCode': 200,",
                    "        'body': json.dumps(result),",
                    "        'headers': {'Content-Type': 'application/json'}",
                    "    }"
                ]
            elif "nodejs" in lambda_runtime:
                lambda_code = [
                    "const AWS = require('aws-sdk');",
                    "const s3 = new AWS.S3();",
                    "const dynamoDB = new AWS.DynamoDB.DocumentClient();",
                    "",
                    "exports.handler = async (event, context) => {",
                    "    console.log('Lambda function invoked!');",
                    "    console.log('Event:', JSON.stringify(event, null, 2));",
                    "    ",
                    "    // Example: Get environment variables",
                    "    const tableName = process.env.TABLE_NAME;",
                    "    const bucketName = process.env.BUCKET_NAME;",
                    "    ",
                    "    console.log(`Using DynamoDB table: ${tableName}`);", 
                    "    console.log(`Using S3 bucket: ${bucketName}`);",
                    "    ",
                    "    // Example: Process data from S3 and store in DynamoDB",
                    "    try {",
                    "        // Your business logic here",
                    "        const result = { status: 'success', message: 'Task completed successfully' };",
                    "        console.log('Process completed successfully');",
                    "        ",
                    "        // Example: Write to DynamoDB if table exists",
                    "        if (tableName) {",
                    "            await dynamoDB.put({",
                    "                TableName: tableName,",
                    "                Item: {",
                    "                    id: context.awsRequestId,",
                    "                    timestamp: Date.now(),",
                    "                    status: 'COMPLETED'",
                    "                }",
                    "            }).promise();",
                    "        }",
                    "        ",
                    "        return {",
                    "            statusCode: 200,",
                    "            body: JSON.stringify(result),",
                    "            headers: { 'Content-Type': 'application/json' }",
                    "        };",
                    "    } catch (error) {",
                    "        console.error('Error processing data:', error);",
                    "        ",
                    "        return {",
                    "            statusCode: 500,",
                    "            body: JSON.stringify({ status: 'error', message: error.message }),",
                    "            headers: { 'Content-Type': 'application/json' }",
                    "        };",
                    "    }",
                    "};"
                ]
            else:
                # Default code for other runtimes
                lambda_code = [
                    "def handler(event, context):",
                    "    print('Lambda function invoked!')",
                    "    print(f'Event: {event}')",
                    "    # Add your custom code here",
                    "    return {",
                    "        'statusCode': 200,",
                    "        'body': 'Success!'",
                    "    }"
                ]
        
        # Define the CloudFormation template
        cf_template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "CloudFormation template to create a Lambda function with EventBridge schedule rule",
            
            "Parameters": {
                "LambdaName": {
                    "Type": "String",
                    "Default": lambda_name,
                    "Description": "Name of the Lambda function"
                },
                "LambdaDescription": {
                    "Type": "String",
                    "Default": lambda_description,
                    "Description": "Description of the Lambda function"
                },
                "LambdaRuntime": {
                    "Type": "String",
                    "Default": lambda_runtime,
                    "Description": "Runtime for the Lambda function",
                    "AllowedValues": [
                        "nodejs14.x", "nodejs16.x", "nodejs18.x",
                        "python3.8", "python3.9", "python3.10", "python3.11",
                        "java11", "java17", "java21",
                        "dotnet6", "dotnet8",
                        "go1.x"
                    ]
                },
                "LambdaHandler": {
                    "Type": "String",
                    "Default": lambda_handler,
                    "Description": "Handler function in format file.function_name"
                },
                "LambdaTimeout": {
                    "Type": "Number",
                    "Default": lambda_timeout,
                    "Description": "Timeout in seconds (1-900)",
                    "MinValue": 1,
                    "MaxValue": 900
                },
                "LambdaMemory": {
                    "Type": "Number",
                    "Default": lambda_memory,
                    "Description": "Memory allocation in MB (128-10240)",
                    "MinValue": 128,
                    "MaxValue": 10240
                },
                "ScheduleExpression": {
                    "Type": "String",
                    "Default": cron_expression,
                    "Description": "Schedule expression when to trigger the Lambda function"
                }
            },
            
            "Resources": {
                # IAM Role for the Lambda function with extended permissions
                "LambdaExecutionRole": {
                    "Type": "AWS::IAM::Role",
                    "Properties": {
                        "AssumeRolePolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [{
                                "Effect": "Allow",
                                "Principal": {"Service": ["lambda.amazonaws.com"]},
                                "Action": ["sts:AssumeRole"]
                            }]
                        },
                        "ManagedPolicyArns": [
                            "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
                        ],
                        "Path": "/",
                        "RoleName": custom_role_name if custom_role_name.strip() else {"Fn::Sub": "${LambdaName}-ExecutionRole"}
                    }
                },
                
                # Custom IAM Policy for additional permissions
                "LambdaCustomPolicy": {
                    "Type": "AWS::IAM::Policy",
                    "Properties": {
                        "PolicyName": {"Fn::Sub": "${LambdaName}-CustomPolicy"},
                        "PolicyDocument": custom_iam_policy.strip() if custom_iam_policy.strip() else {
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
                                    "Resource": {"Fn::Sub": "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:/aws/lambda/${LambdaName}*"}
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
                        },
                        "Roles": [{"Ref": "LambdaExecutionRole"}]
                    }
                },
                

                
                # Lambda function
                "LambdaFunction": {
                    "Type": "AWS::Lambda::Function",
                    "Properties": {
                        "FunctionName": {"Ref": "LambdaName"},
                        "Description": {"Ref": "LambdaDescription"},
                        "Runtime": {"Ref": "LambdaRuntime"},
                        "Handler": {"Ref": "LambdaHandler"},
                        "Role": {"Fn::GetAtt": ["LambdaExecutionRole", "Arn"]},
                        "Timeout": {"Ref": "LambdaTimeout"},
                        "MemorySize": {"Ref": "LambdaMemory"},
                        "Code": {
                            "ZipFile": {
                                "Fn::Join": ["\n", lambda_code]
                            }
                        },
                        "Environment": {
                            "Variables": {
                                "SCHEDULED_TIME": {"Fn::Sub": "${schedule_hour}:${schedule_minute}"}
                            }
                        },
                        "TracingConfig": {
                            "Mode": "Active"
                        },
                        "Tags": [
                            {
                                "Key": "CreatedBy",
                                "Value": "CloudFormation"
                            }
                        ]
                    }
                },
                
                # CloudWatch Log Group with retention
                "LambdaLogGroup": {
                    "Type": "AWS::Logs::LogGroup",
                    "Properties": {
                        "LogGroupName": {"Fn::Sub": "/aws/lambda/${LambdaName}"},
                        "RetentionInDays": 30
                    }
                },
                
                # EventBridge Rule for scheduled execution
                "ScheduledRule": {
                    "Type": "AWS::Events::Rule",
                    "Properties": {
                        "Name": {"Fn::Sub": "${LambdaName}-DailySchedule"},
                        "Description": {"Fn::Sub": "Triggers ${LambdaName} Lambda function on schedule"},
                        "ScheduleExpression": {"Ref": "ScheduleExpression"},
                        "State": "ENABLED",
                        "Targets": [{
                            "Id": {"Ref": "LambdaName"},
                            "Arn": {"Fn::GetAtt": ["LambdaFunction", "Arn"]}
                        }]
                    }
                },
                
                # Permission to allow EventBridge to invoke Lambda
                "PermissionForEventsToInvokeLambda": {
                    "Type": "AWS::Lambda::Permission",
                    "Properties": {
                        "FunctionName": {"Ref": "LambdaFunction"},
                        "Action": "lambda:InvokeFunction",
                        "Principal": "events.amazonaws.com",
                        "SourceArn": {"Fn::GetAtt": ["ScheduledRule", "Arn"]}
                    }
                }
            },
            
            "Outputs": {
                "LambdaFunctionArn": {
                    "Description": "ARN of the Lambda function",
                    "Value": {"Fn::GetAtt": ["LambdaFunction", "Arn"]}
                },
                "LambdaRoleArn": {
                    "Description": "ARN of the IAM Role for Lambda",
                    "Value": {"Fn::GetAtt": ["LambdaExecutionRole", "Arn"]}
                },
                "ScheduleRuleArn": {
                    "Description": "ARN of the EventBridge schedule rule",
                    "Value": {"Fn::GetAtt": ["ScheduledRule", "Arn"]}
                }
            }
        }
        
        # Convert to YAML
        yaml_template = yaml.dump(cf_template, default_flow_style=False, sort_keys=False)
        
        return yaml_template
    
    except Exception as e:
        logging.error(f"Error generating CloudFormation template: {e}", exc_info=True)
        raise ValueError(f"Failed to generate CloudFormation template: {str(e)}")
