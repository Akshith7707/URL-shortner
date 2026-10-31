/** Side-effect module: configure local DynamoDB env before handlers load. */
process.env.TABLE_NAME ||= 'url-shortener-urls';
process.env.DYNAMODB_ENDPOINT ||= 'http://127.0.0.1:8000';
process.env.AWS_REGION ||= 'ap-south-1';
process.env.AWS_ACCESS_KEY_ID ||= 'local';
process.env.AWS_SECRET_ACCESS_KEY ||= 'local';
