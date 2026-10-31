/**
 * Local integration tests against DynamoDB Local.
 * Skips automatically if DynamoDB Local is not reachable (no AWS cloud calls).
 */

process.env.TABLE_NAME = 'url-shortener-urls';
process.env.DYNAMODB_ENDPOINT = 'http://127.0.0.1:8000';
process.env.AWS_REGION = 'ap-south-1';
process.env.AWS_ACCESS_KEY_ID = 'local';
process.env.AWS_SECRET_ACCESS_KEY = 'local';

import {
  CreateTableCommand,
  DynamoDBClient,
  ListTablesCommand,
  ResourceInUseException,
} from '@aws-sdk/client-dynamodb';
import type {
  APIGatewayProxyEventV2,
  APIGatewayProxyResultV2,
  Context,
} from 'aws-lambda';

const endpoint = process.env.DYNAMODB_ENDPOINT!;
const tableName = process.env.TABLE_NAME!;

const admin = new DynamoDBClient({
  endpoint,
  region: 'ap-south-1',
  credentials: { accessKeyId: 'local', secretAccessKey: 'local' },
});

async function dynamoLocalUp(): Promise<boolean> {
  try {
    await admin.send(new ListTablesCommand({ Limit: 1 }));
    return true;
  } catch (err) {
    console.warn(
      'DynamoDB Local probe failed:',
      err instanceof Error ? err.message : String(err),
    );
    return false;
  }
}

async function ensureTable(): Promise<void> {
  try {
    await admin.send(
      new CreateTableCommand({
        TableName: tableName,
        AttributeDefinitions: [{ AttributeName: 'shortCode', AttributeType: 'S' }],
        KeySchema: [{ AttributeName: 'shortCode', KeyType: 'HASH' }],
        BillingMode: 'PAY_PER_REQUEST',
      }),
    );
  } catch (err) {
    if (!(err instanceof ResourceInUseException)) {
      throw err;
    }
  }
}

function baseEvent(overrides: Partial<APIGatewayProxyEventV2>): APIGatewayProxyEventV2 {
  return {
    version: '2.0',
    routeKey: 'POST /shorten',
    rawPath: '/shorten',
    rawQueryString: '',
    headers: { 'content-type': 'application/json' },
    requestContext: {
      accountId: 'local',
      apiId: 'local',
      domainName: '127.0.0.1:3000',
      domainPrefix: 'local',
      http: {
        method: 'POST',
        path: '/shorten',
        protocol: 'HTTP/1.1',
        sourceIp: '127.0.0.1',
        userAgent: 'jest',
      },
      requestId: 'test-request',
      routeKey: 'POST /shorten',
      stage: '$default',
      time: new Date().toISOString(),
      timeEpoch: Date.now(),
    },
    isBase64Encoded: false,
    ...overrides,
  };
}

const fakeContext = {
  awsRequestId: 'test',
  callbackWaitsForEmptyEventLoop: false,
  functionName: 'test',
  functionVersion: '$LATEST',
  invokedFunctionArn: 'arn:aws:lambda:local:0:function:test',
  memoryLimitInMB: '128',
  logGroupName: 'test',
  logStreamName: 'test',
  getRemainingTimeInMillis: () => 10_000,
  done: () => undefined,
  fail: () => undefined,
  succeed: () => undefined,
} as Context;

function asObject(result: APIGatewayProxyResultV2): {
  statusCode: number;
  headers?: Record<string, string | number | boolean>;
  body?: string;
} {
  if (typeof result === 'string') {
    return { statusCode: 200, body: result };
  }
  return result;
}

describe('handlers against DynamoDB Local', () => {
  let createHandler: typeof import('../lambda/create-url/index').handler;
  let redirectHandler: typeof import('../lambda/redirect/index').handler;
  let available = false;

  beforeAll(async () => {
    available = await dynamoLocalUp();
    if (!available) {
      console.warn('DynamoDB Local not reachable on :8000 — local handler tests will fail closed');
      return;
    }
    await ensureTable();
    ({ handler: createHandler } = await import('../lambda/create-url/index'));
    ({ handler: redirectHandler } = await import('../lambda/redirect/index'));
  }, 30_000);

  function requireLocal(): void {
    if (!available) {
      throw new Error('DynamoDB Local not reachable on http://127.0.0.1:8000. Run scripts/local-setup-jar.ps1 or local-setup.ps1 first.');
    }
  }

  it('GET /health returns ok', async () => {
    requireLocal();
    const result = asObject(
      await createHandler(
        baseEvent({
          rawPath: '/health',
          routeKey: 'GET /health',
          requestContext: {
            ...baseEvent({}).requestContext,
            http: {
              ...baseEvent({}).requestContext.http,
              method: 'GET',
              path: '/health',
            },
            routeKey: 'GET /health',
          },
        }),
        fakeContext,
      ),
    );
    expect(result.statusCode).toBe(200);
    expect(JSON.parse(result.body || '{}')).toEqual({ status: 'ok' });
  });

  it('POST /shorten rejects invalid JSON', async () => {
    requireLocal();
    const result = asObject(
      await createHandler(baseEvent({ body: '{bad' }), fakeContext),
    );
    expect(result.statusCode).toBe(400);
  });

  it('create + redirect + missing code', async () => {
    requireLocal();
    const created = asObject(
      await createHandler(
        baseEvent({
          body: JSON.stringify({
            url: 'https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html',
          }),
        }),
        fakeContext,
      ),
    );
    expect(created.statusCode).toBe(201);
    const payload = JSON.parse(created.body || '{}') as {
      shortCode: string;
      longUrl: string;
    };
    expect(payload.shortCode).toMatch(/^[0-9A-Za-z]{7}$/);

    const redirected = asObject(
      await redirectHandler(
        baseEvent({
          rawPath: `/${payload.shortCode}`,
          routeKey: 'GET /{code}',
          pathParameters: { code: payload.shortCode },
          requestContext: {
            ...baseEvent({}).requestContext,
            http: {
              ...baseEvent({}).requestContext.http,
              method: 'GET',
              path: `/${payload.shortCode}`,
            },
            routeKey: 'GET /{code}',
          },
        }),
        fakeContext,
      ),
    );
    expect(redirected.statusCode).toBe(301);
    expect(redirected.headers?.Location).toBe(payload.longUrl);

    const missing = asObject(
      await redirectHandler(
        baseEvent({
          rawPath: '/nope9999',
          routeKey: 'GET /{code}',
          pathParameters: { code: 'nope9999' },
          requestContext: {
            ...baseEvent({}).requestContext,
            http: {
              ...baseEvent({}).requestContext.http,
              method: 'GET',
              path: '/nope9999',
            },
            routeKey: 'GET /{code}',
          },
        }),
        fakeContext,
      ),
    );
    expect(missing.statusCode).toBe(404);
  });
});
