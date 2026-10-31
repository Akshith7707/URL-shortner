import { randomBytes } from 'node:crypto';
import {
  PutItemCommand,
  ConditionalCheckFailedException,
} from '@aws-sdk/client-dynamodb';
import type {
  APIGatewayProxyEventV2,
  APIGatewayProxyResultV2,
  Context,
} from 'aws-lambda';
import { createDynamoClient, requireTableName } from '../shared/dynamo';

const ddb = createDynamoClient();
const SHORT_CODE_LENGTH = 7;
const MAX_COLLISION_RETRIES = 5;
const BASE62 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';

interface ShortenRequestBody {
  url?: unknown;
}

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

function generateShortCode(length = SHORT_CODE_LENGTH): string {
  const bytes = randomBytes(length);
  let code = '';
  for (let i = 0; i < length; i += 1) {
    code += BASE62[bytes[i]! % BASE62.length];
  }
  return code;
}

function isValidHttpsUrl(value: string): boolean {
  try {
    const parsed = new URL(value);
    if (parsed.protocol !== 'https:' && parsed.protocol !== 'http:') {
      return false;
    }
    if (!parsed.hostname || parsed.hostname.includes(' ')) {
      return false;
    }
    const host = parsed.hostname.toLowerCase();
    if (
      host === 'localhost' ||
      host === '127.0.0.1' ||
      host === '::1' ||
      host === '169.254.169.254' ||
      host.endsWith('.local')
    ) {
      return false;
    }
    return true;
  } catch {
    return false;
  }
}

function resolveBaseUrl(event: APIGatewayProxyEventV2): string {
  const domain = event.requestContext.domainName;
  const stage = event.requestContext.stage;
  if (!domain) {
    return '';
  }
  const forwarded = event.headers?.['x-forwarded-proto']
    || event.headers?.['X-Forwarded-Proto'];
  const isLocal = domain.startsWith('127.0.0.1') || domain.startsWith('localhost');
  const scheme = forwarded || (isLocal ? 'http' : 'https');
  if (!stage || stage === '$default') {
    return `${scheme}://${domain}`;
  }
  return `${scheme}://${domain}/${stage}`;
}

export async function handler(
  event: APIGatewayProxyEventV2,
  _context: Context,
): Promise<APIGatewayProxyResultV2> {
  const tableName = requireTableName();
  const method = event.requestContext.http.method;
  const path = event.rawPath;

  console.log(
    JSON.stringify({
      level: 'info',
      message: 'request_received',
      method,
      path,
      requestId: event.requestContext.requestId,
    }),
  );

  if (method === 'GET' && path === '/health') {
    return jsonResponse(200, { status: 'ok' });
  }

  if (method !== 'POST' || path !== '/shorten') {
    return jsonResponse(404, { error: 'Not found' });
  }

  let payload: ShortenRequestBody;
  try {
    payload = event.body
      ? (JSON.parse(event.isBase64Encoded
          ? Buffer.from(event.body, 'base64').toString('utf8')
          : event.body) as ShortenRequestBody)
      : {};
  } catch {
    return jsonResponse(400, { error: 'Invalid JSON body' });
  }

  if (typeof payload.url !== 'string' || payload.url.trim().length === 0) {
    return jsonResponse(400, {
      error: 'Missing required string field: url',
    });
  }

  const longUrl = payload.url.trim();
  if (!isValidHttpsUrl(longUrl)) {
    return jsonResponse(400, {
      error: 'url must be a valid http or https URL (localhost and link-local hosts are not allowed)',
    });
  }

  if (longUrl.length > 2048) {
    return jsonResponse(400, { error: 'url exceeds maximum length of 2048 characters' });
  }

  const createdAt = new Date().toISOString();
  let shortCode = '';
  let stored = false;

  for (let attempt = 0; attempt < MAX_COLLISION_RETRIES; attempt += 1) {
    shortCode = generateShortCode();
    try {
      await ddb.send(
        new PutItemCommand({
          TableName: tableName,
          Item: {
            shortCode: { S: shortCode },
            longUrl: { S: longUrl },
            createdAt: { S: createdAt },
            hitCount: { N: '0' },
          },
          ConditionExpression: 'attribute_not_exists(shortCode)',
        }),
      );
      stored = true;
      break;
    } catch (err) {
      if (err instanceof ConditionalCheckFailedException) {
        console.warn(
          JSON.stringify({
            level: 'warn',
            message: 'short_code_collision',
            shortCode,
            attempt: attempt + 1,
          }),
        );
        continue;
      }
      console.error(
        JSON.stringify({
          level: 'error',
          message: 'dynamodb_put_failed',
          error: err instanceof Error ? err.message : String(err),
        }),
      );
      return jsonResponse(500, { error: 'Failed to create short URL' });
    }
  }

  if (!stored) {
    return jsonResponse(500, {
      error: 'Unable to allocate a unique short code; please retry',
    });
  }

  const baseUrl = resolveBaseUrl(event);
  const shortUrl = `${baseUrl}/${shortCode}`;

  console.log(
    JSON.stringify({
      level: 'info',
      message: 'short_url_created',
      shortCode,
      requestId: event.requestContext.requestId,
    }),
  );

  return jsonResponse(201, {
    shortCode,
    shortUrl,
    longUrl,
    createdAt,
  });
}
