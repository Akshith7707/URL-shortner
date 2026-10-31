import { DynamoDBClient } from '@aws-sdk/client-dynamodb';

/**
 * Build a DynamoDB client.
 * - Cloud/default: uses the Lambda execution role / ambient AWS credentials.
 * - Local: set DYNAMODB_ENDPOINT (e.g. http://127.0.0.1:8000) for DynamoDB Local.
 */
export function createDynamoClient(): DynamoDBClient {
  const endpoint = process.env.DYNAMODB_ENDPOINT;

  if (endpoint) {
    return new DynamoDBClient({
      endpoint,
      region: process.env.AWS_REGION || process.env.AWS_DEFAULT_REGION || 'ap-south-1',
      credentials: {
        accessKeyId: process.env.AWS_ACCESS_KEY_ID || 'local',
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY || 'local',
      },
    });
  }

  return new DynamoDBClient({});
}

export function requireTableName(): string {
  const tableName = process.env.TABLE_NAME;
  if (!tableName) {
    throw new Error('TABLE_NAME environment variable is required');
  }
  return tableName;
}
