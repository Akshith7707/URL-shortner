import * as cdk from 'aws-cdk-lib/core';
import { Construct } from 'constructs';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { NodejsFunction } from 'aws-cdk-lib/aws-lambda-nodejs';
import * as apigwv2 from 'aws-cdk-lib/aws-apigatewayv2';
import { HttpLambdaIntegration } from 'aws-cdk-lib/aws-apigatewayv2-integrations';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as path from 'node:path';

export class UrlShortenerStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const urlsTable = new dynamodb.Table(this, 'UrlsTable', {
      tableName: 'url-shortener-urls',
      partitionKey: {
        name: 'shortCode',
        type: dynamodb.AttributeType.STRING,
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY, // demo-friendly; use RETAIN in production
      pointInTimeRecoverySpecification: {
        pointInTimeRecoveryEnabled: false,
      },
    });

    const createLogGroup = new logs.LogGroup(this, 'CreateUrlLogGroup', {
      logGroupName: '/aws/lambda/url-shortener-create',
      retention: logs.RetentionDays.ONE_WEEK,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    const redirectLogGroup = new logs.LogGroup(this, 'RedirectLogGroup', {
      logGroupName: '/aws/lambda/url-shortener-redirect',
      retention: logs.RetentionDays.ONE_WEEK,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    const commonLambdaProps = {
      runtime: lambda.Runtime.NODEJS_24_X,
      timeout: cdk.Duration.seconds(10),
      memorySize: 128,
      tracing: lambda.Tracing.ACTIVE,
      environment: {
        TABLE_NAME: urlsTable.tableName,
        NODE_OPTIONS: '--enable-source-maps',
      },
      bundling: {
        minify: true,
        sourceMap: true,
        target: 'node24',
        externalModules: ['@aws-sdk/*'],
      },
    };

    const createUrlFn = new NodejsFunction(this, 'CreateUrlFunction', {
      ...commonLambdaProps,
      functionName: 'url-shortener-create',
      entry: path.join(__dirname, '..', 'lambda', 'create-url', 'index.ts'),
      handler: 'handler',
      description: 'Creates a short URL mapping in DynamoDB',
      logGroup: createLogGroup,
    });

    const redirectFn = new NodejsFunction(this, 'RedirectFunction', {
      ...commonLambdaProps,
      functionName: 'url-shortener-redirect',
      entry: path.join(__dirname, '..', 'lambda', 'redirect', 'index.ts'),
      handler: 'handler',
      description: 'Looks up short codes and redirects to the long URL',
      logGroup: redirectLogGroup,
    });

    // Least privilege: create = PutItem only; redirect = GetItem + UpdateItem
    urlsTable.grant(createUrlFn, 'dynamodb:PutItem');
    urlsTable.grant(redirectFn, 'dynamodb:GetItem', 'dynamodb:UpdateItem');

    const httpApi = new apigwv2.HttpApi(this, 'UrlShortenerApi', {
      apiName: 'url-shortener-api',
      description: 'HTTP API for the URL shortener',
      corsPreflight: {
        allowHeaders: ['Content-Type'],
        allowMethods: [
          apigwv2.CorsHttpMethod.GET,
          apigwv2.CorsHttpMethod.POST,
          apigwv2.CorsHttpMethod.OPTIONS,
        ],
        allowOrigins: ['*'],
        maxAge: cdk.Duration.days(1),
      },
      createDefaultStage: true,
    });

    const accessLogGroup = new logs.LogGroup(this, 'ApiAccessLogs', {
      logGroupName: '/aws/apigateway/url-shortener',
      retention: logs.RetentionDays.ONE_WEEK,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    accessLogGroup.addToResourcePolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        principals: [new iam.ServicePrincipal('apigateway.amazonaws.com')],
        actions: ['logs:CreateLogStream', 'logs:PutLogEvents'],
        resources: [accessLogGroup.logGroupArn, `${accessLogGroup.logGroupArn}:*`],
      }),
    );

    const defaultStage = httpApi.defaultStage?.node.defaultChild as apigwv2.CfnStage | undefined;
    if (defaultStage) {
      defaultStage.accessLogSettings = {
        destinationArn: accessLogGroup.logGroupArn,
        format: JSON.stringify({
          requestId: '$context.requestId',
          ip: '$context.identity.sourceIp',
          requestTime: '$context.requestTime',
          httpMethod: '$context.httpMethod',
          routeKey: '$context.routeKey',
          status: '$context.status',
          protocol: '$context.protocol',
          responseLength: '$context.responseLength',
          integrationError: '$context.integrationErrorMessage',
        }),
      };
    }

    const createIntegration = new HttpLambdaIntegration('CreateIntegration', createUrlFn);
    const redirectIntegration = new HttpLambdaIntegration('RedirectIntegration', redirectFn);

    httpApi.addRoutes({
      path: '/shorten',
      methods: [apigwv2.HttpMethod.POST],
      integration: createIntegration,
    });

    httpApi.addRoutes({
      path: '/health',
      methods: [apigwv2.HttpMethod.GET],
      integration: createIntegration,
    });

    httpApi.addRoutes({
      path: '/{code}',
      methods: [apigwv2.HttpMethod.GET],
      integration: redirectIntegration,
    });

    new cloudwatch.Alarm(this, 'CreateUrlErrorAlarm', {
      alarmName: 'url-shortener-create-errors',
      metric: createUrlFn.metricErrors({
        period: cdk.Duration.minutes(1),
        statistic: 'Sum',
      }),
      threshold: 1,
      evaluationPeriods: 1,
      datapointsToAlarm: 1,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
      treatMissingData: cloudwatch.TreatMissingData.NOT_BREACHING,
      alarmDescription: 'CreateUrl Lambda reported errors',
    });

    new cloudwatch.Alarm(this, 'RedirectErrorAlarm', {
      alarmName: 'url-shortener-redirect-errors',
      metric: redirectFn.metricErrors({
        period: cdk.Duration.minutes(1),
        statistic: 'Sum',
      }),
      threshold: 1,
      evaluationPeriods: 1,
      datapointsToAlarm: 1,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
      treatMissingData: cloudwatch.TreatMissingData.NOT_BREACHING,
      alarmDescription: 'Redirect Lambda reported errors',
    });

    new cdk.CfnOutput(this, 'ApiUrl', {
      value: httpApi.apiEndpoint,
      description: 'Base URL of the URL shortener HTTP API',
      exportName: 'UrlShortenerApiUrl',
    });

    new cdk.CfnOutput(this, 'TableName', {
      value: urlsTable.tableName,
      description: 'DynamoDB table storing short URL mappings',
      exportName: 'UrlShortenerTableName',
    });

    new cdk.CfnOutput(this, 'CreateFunctionName', {
      value: createUrlFn.functionName,
      description: 'Create URL Lambda function name',
    });

    new cdk.CfnOutput(this, 'RedirectFunctionName', {
      value: redirectFn.functionName,
      description: 'Redirect Lambda function name',
    });
  }
}
