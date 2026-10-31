/**
 * Local HTTP stand-in for API Gateway HTTP API.
 * Invokes the same Lambda handlers against DynamoDB Local.
 * Zero AWS cloud cost.
 */
import './set-local-env';
import http from 'node:http';
import { randomUUID } from 'node:crypto';
import type {
  APIGatewayProxyEventV2,
  APIGatewayProxyHandlerV2,
  APIGatewayProxyResultV2,
  Context,
} from 'aws-lambda';

const PORT = Number(process.env.LOCAL_API_PORT || 3000);

function buildEvent(
  req: http.IncomingMessage,
  body: string,
  pathParameters?: Record<string, string>,
): APIGatewayProxyEventV2 {
  const host = req.headers.host || `127.0.0.1:${PORT}`;
  const url = new URL(req.url || '/', `http://${host}`);
  return {
    version: '2.0',
    routeKey: `${req.method} ${url.pathname}`,
    rawPath: url.pathname,
    rawQueryString: url.search.replace(/^\?/, ''),
    headers: Object.fromEntries(
      Object.entries(req.headers)
        .filter(([, v]) => typeof v === 'string')
        .map(([k, v]) => [k, v as string]),
    ),
    requestContext: {
      accountId: 'local',
      apiId: 'local',
      domainName: host,
      domainPrefix: 'local',
      http: {
        method: req.method || 'GET',
        path: url.pathname,
        protocol: 'HTTP/1.1',
        sourceIp: req.socket.remoteAddress || '127.0.0.1',
        userAgent: req.headers['user-agent'] || 'local-api',
      },
      requestId: randomUUID(),
      routeKey: `${req.method} ${url.pathname}`,
      stage: '$default',
      time: new Date().toISOString(),
      timeEpoch: Date.now(),
    },
    body: body || undefined,
    isBase64Encoded: false,
    pathParameters,
  };
}

const fakeContext = {
  awsRequestId: 'local',
  callbackWaitsForEmptyEventLoop: false,
  functionName: 'local',
  functionVersion: '$LATEST',
  invokedFunctionArn: 'arn:aws:lambda:local:0:function:local',
  memoryLimitInMB: '128',
  logGroupName: 'local',
  logStreamName: 'local',
  getRemainingTimeInMillis: () => 10_000,
  done: () => undefined,
  fail: () => undefined,
  succeed: () => undefined,
} as Context;

function sendResult(res: http.ServerResponse, result: APIGatewayProxyResultV2): void {
  if (typeof result === 'string') {
    res.statusCode = 200;
    res.setHeader('Content-Type', 'application/json');
    res.end(result);
    return;
  }

  res.statusCode = result.statusCode ?? 200;
  const headers = result.headers ?? {};
  for (const [key, value] of Object.entries(headers)) {
    if (value !== undefined) {
      res.setHeader(key, String(value));
    }
  }
  res.end(result.body ?? '');
}

async function main(): Promise<void> {
  const { handler: createHandler } = await import('../lambda/create-url/index') as {
    handler: APIGatewayProxyHandlerV2;
  };
  const { handler: redirectHandler } = await import('../lambda/redirect/index') as {
    handler: APIGatewayProxyHandlerV2;
  };

  const server = http.createServer(async (req, res) => {
    try {
      const chunks: Buffer[] = [];
      for await (const chunk of req) {
        chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
      }
      const body = Buffer.concat(chunks).toString('utf8');
      const host = req.headers.host || `127.0.0.1:${PORT}`;
      const url = new URL(req.url || '/', `http://${host}`);
      const method = req.method || 'GET';
      const path = url.pathname;

      let result: APIGatewayProxyResultV2;

      if ((method === 'GET' && path === '/health') || (method === 'POST' && path === '/shorten')) {
        result = await createHandler(buildEvent(req, body), fakeContext);
      } else if (method === 'GET' && path !== '/') {
        const code = path.replace(/^\//, '');
        result = await redirectHandler(
          buildEvent(req, body, { code }),
          fakeContext,
        );
      } else {
        result = {
          statusCode: 404,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ error: 'Not found' }),
        };
      }

      sendResult(res, result);
    } catch (err) {
      console.error(err);
      res.statusCode = 500;
      res.setHeader('Content-Type', 'application/json');
      res.end(JSON.stringify({
        error: 'Local API failure',
        detail: err instanceof Error ? err.message : String(err),
      }));
    }
  });

  server.listen(PORT, () => {
    console.log(`Local URL shortener listening on http://127.0.0.1:${PORT}`);
    console.log(`DynamoDB endpoint: ${process.env.DYNAMODB_ENDPOINT}`);
    console.log(`Table: ${process.env.TABLE_NAME}`);
    console.log('Routes: GET /health | POST /shorten | GET /{code}');
  });
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
