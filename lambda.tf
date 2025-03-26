resource "aws_lambda_function" "chatbot_lambda" {
  filename         = "lambda.zip"  # Path to your zipped Python code
  function_name    = "chatbotLambda"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "index.lambda_handler"  # The handler function name
  runtime          = "python3.12"  # Use Python 3.12 runtime

  source_code_hash = filebase64sha256("lambda.zip")
}

resource "aws_iam_role" "lambda_exec" {
  name               = "lambda_exec_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}