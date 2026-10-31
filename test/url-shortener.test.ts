import * as cdk from 'aws-cdk-lib/core';
import { Template, Match } from 'aws-cdk-lib/assertions';
import { UrlShortenerStack } from '../lib/url-shortener-stack';

describe('UrlShortenerStack', () => {
  const app = new cdk.App();
  const stack = new UrlShortenerStack(app, 'TestStack', {
    env: { account: '111122223333', region: 'ap-south-1' },
  });
  const template = Template.fromStack(stack);

  test('creates a DynamoDB table with shortCode partition key', () => {
    template.hasResourceProperties('AWS::DynamoDB::Table', {
      TableName: 'url-shortener-urls',
      BillingMode: 'PAY_PER_REQUEST',
      KeySchema: [
        {
          AttributeName: 'shortCode',
          KeyType: 'HASH',
        },
      ],
    });
  });

  test('creates application Lambda functions', () => {
    // Application functions plus optional CDK log-retention custom resource functions
    const functions = template.findResources('AWS::Lambda::Function');
    const names = Object.values(functions).map(
      (fn) => (fn as { Properties?: { FunctionName?: string } }).Properties?.FunctionName,
    );
    expect(names).toEqual(expect.arrayContaining([
      'url-shortener-create',
      'url-shortener-redirect',
    ]));
  });

  test('creates an HTTP API', () => {
    template.hasResourceProperties('AWS::ApiGatewayV2::Api', {
      Name: 'url-shortener-api',
      ProtocolType: 'HTTP',
    });
  });

  test('create function IAM allows PutItem only on the table', () => {
    template.hasResourceProperties('AWS::IAM::Policy', {
      PolicyDocument: {
        Statement: Match.arrayWith([
          Match.objectLike({
            Action: 'dynamodb:PutItem',
            Effect: 'Allow',
          }),
        ]),
      },
    });
  });

  test('exports ApiUrl output', () => {
    template.hasOutput('ApiUrl', {});
  });
});
