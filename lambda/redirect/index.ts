import {
  GetItemCommand,
  UpdateItemCommand,
} from '@aws-sdk/client-dynamodb';
import type {
  APIGatewayProxyEventV2,
  APIGatewayProxyResultV2,
  Context,
} from 'aws-lambda';
import { createDynamoClient, requireTableName } from '../shared/dynamo';

const ddb = createDynamoClient();
const SHORT_CODE_PATTERN = /^[0-9A-Za-z]{4,16}$/;

function jsonResponse(
  statusCode: number,
  body: Record<string, unknown>,
): APIGatewayProxyResultV2 {
  return {
    statusCode,
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'no-store',
    },
    body: JSON.stringify(body),
  };
}

export async function handler(
  event: APIGatewayProxyEventV2,
  _context: Context,
): Promise<APIGatewayProxyResultV2> {
  const tableName = requireTableName();
  const shortCode = event.pathParameters?.code;

  console.log(
    JSON.stringify({
      level: 'info',
      message: 'redirect_request',
      shortCode,
      requestId: event.requestContext.requestId,
    }),
  );

  if (!shortCode || !SHORT_CODE_PATTERN.test(shortCode)) {
    return jsonResponse(400, { error: 'Invalid short code' });
  }

  try {
    const result = await ddb.send(
      new GetItemCommand({
        TableName: tableName,
        Key: {
          shortCode: { S: shortCode },
        },
        ProjectionExpression: 'longUrl',
      }),
    );

    const longUrl = result.Item?.longUrl?.S;
    if (!longUrl) {
      return jsonResponse(404, { error: 'Short URL not found' });
    }

    try {
      await ddb.send(
        new UpdateItemCommand({
          TableName: tableName,
          Key: {
            shortCode: { S: shortCode },
          },
          UpdateExpression: 'ADD hitCount :one SET lastAccessedAt = :now',
          ExpressionAttributeValues: {
            ':one': { N: '1' },
            ':now': { S: new Date().toISOString() },
          },
        }),
      );
    } catch (updateErr) {
      console.warn(
        JSON.stringify({
          level: 'warn',
          message: 'hit_count_update_failed',
          shortCode,
          error: updateErr instanceof Error ? updateErr.message : String(updateErr),
        }),
      );
    }

    console.log(
      JSON.stringify({
        level: 'info',
        message: 'redirect_success',
        shortCode,
        requestId: event.requestContext.requestId,
      }),
    );

    return {
      statusCode: 301,
      headers: {
        Location: longUrl,
        'Cache-Control': 'no-cache',
      },
      body: '',
    };
  } catch (err) {
    console.error(
      JSON.stringify({
        level: 'error',
        message: 'redirect_failed',
        shortCode,
        error: err instanceof Error ? err.message : String(err),
      }),
    );
    return jsonResponse(500, { error: 'Failed to resolve short URL' });
  }
}
