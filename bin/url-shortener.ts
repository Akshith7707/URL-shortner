#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib/core';
import { UrlShortenerStack } from '../lib/url-shortener-stack';

const app = new cdk.App();

new UrlShortenerStack(app, 'UrlShortenerStack', {
  env: {
    // Account comes from the active AWS CLI/SSO identity at deploy time.
    // Region is fixed to Mumbai per project plan.
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: 'ap-south-1',
  },
  description: 'Serverless URL shortener (API Gateway HTTP API + Lambda + DynamoDB)',
  tags: {
    Project: 'url-shortener',
    ManagedBy: 'cdk',
  },
});
