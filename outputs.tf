output "lambda_function_name" {
  description = "The name of the deployed Lambda function"
  value       = aws_lambda_function.chatbot_lambda.function_name
}

output "lambda_function_arn" {
  description = "The ARN of the Lambda function"
  value       = aws_lambda_function.chatbot_lambda.arn
}

output "api_gateway_invoke_url" {
  description = "The invoke URL for the API Gateway"
  value       = aws_api_gateway_stage.chatbot_stage.invoke_url
}

output "api_gateway_execution_arn" {
  description = "The execution ARN for API Gateway"
  value       = aws_api_gateway_rest_api.chatbot_api.execution_arn
}

output "api_gateway_stage_name" {
  description = "The deployed API Gateway stage name"
  value       = aws_api_gateway_stage.chatbot_stage.stage_name
}