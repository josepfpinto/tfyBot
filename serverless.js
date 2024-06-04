// serverless.js
require('dotenv').config();

const stage = 'dev';
const region = 'eu-west-1';
const sessionsTableName = `sessions-table-${stage}`;
const usersTableName = `users-table-${stage}`;

const serverlessConfiguration = {
  service: 'serverless-flask',
  plugins: [],
  custom: {
    wsgi: {
      app: 'app.app',
      packRequirements: false
    },
    pythonRequirements: {
      dockerizePip: false,
      usePipenv: true
    },
    serverlessOffline: {
      noPrependStageInUrl: true,
      httpPort: 8080
    },
    dynamodb: {
      // stages: [stage],
      start: {
        // port: 8000,
        // inMemory: true,
        migrate: true,
      },
    },
  },
  provider: {
    name: 'aws',
    runtime: 'python3.11',
    stage: stage,
    region: region,
    environment: {
      OPENAI_API_KEY: process.env.OPENAI_API_KEY || '',
      SERVERLESS_ACCESS_KEY: process.env.SERVERLESS_ACCESS_KEY || '',
      PERPLEXITY_API_KEY: process.env.PERPLEXITY_API_KEY || '',
      TAVILY_API_KEY: process.env.TAVILY_API_KEY || '',
      SERPER_API_KEY: process.env.SERPER_API_KEY || '',
      BRAVE_API_KEY: process.env.BRAVE_API_KEY || '',
      TOKEN: process.env.TOKEN || '',
      WHATSAPP_APP_ID: process.env.WHATSAPP_APP_ID || '',
      WHATSAPP_APP_SECRET: process.env.WHATSAPP_APP_SECRET || '',
      WHATSAPP_TOKEN: process.env.WHATSAPP_TOKEN || '',
      WHATSAPP_RECIPIENT_WAID: process.env.WHATSAPP_RECIPIENT_WAID || '',
      WHATSAPP_PHONE_NUMBER_ID: process.env.WHATSAPP_PHONE_NUMBER_ID || '',
      WHATSAPP_VERSION: process.env.WHATSAPP_VERSION || '',
      WHATSAPP_VERIFY_TOKEN: process.env.WHATSAPP_VERIFY_TOKEN || '',
      IS_DEBUG: process.env.IS_DEBUG || '',
      IS_OFFLINE: process.env.IS_OFFLINE || '',
      LANGCHAIN_TRACING_V2: process.env.LANGCHAIN_TRACING_V2 || '',
      LANGCHAIN_API_KEY: process.env.LANGCHAIN_API_KEY || '',
      LANGCHAIN_PROJECT: process.env.LANGCHAIN_PROJECT || '',
      LANGCHAIN_ENDPOINT: process.env.LANGCHAIN_ENDPOINT || '',
      REGION: process.env.REGION || '',
      USERS_TABLE: usersTableName,
      SESSIONS_TABLE: sessionsTableName,
    },
    iamRoleStatements: [
      {
        Effect: 'Allow',
        Action: [
          'dynamodb:Query',
          'dynamodb:Scan',
          'dynamodb:GetItem',
          'dynamodb:PutItem',
          'dynamodb:UpdateItem',
          'dynamodb:DeleteItem',
        ],
        Resource: [
          { 'Fn::GetAtt': ['UsersDynamoDBTable', 'Arn'] },
          { 'Fn::GetAtt': ['SessionsDynamoDBTable', 'Arn'] },
        ],
      },
      {
        Effect: 'Allow',
        Action: [
          'dynamodb:Query',
        ],
        Resource: `arn:aws:dynamodb:${region}:*:table/${sessionsTableName}/index/SessionIdTimestampIndex`,
      },
    ],
    ecr: {
      images: {
        appimage: {
          path: './',
        },
      },
    },
  },
  functions: {},
  resources: {
    Resources: {
      UsersDynamoDBTable: {
        Type: "AWS::DynamoDB::Table",
        Properties: {
          AttributeDefinitions: [
            {
              AttributeName: "phone_number",
              AttributeType: "S",
            },
          ],
          KeySchema: [
            {
              AttributeName: "phone_number",
              KeyType: "HASH",
            },
          ],
          ProvisionedThroughput: {
            ReadCapacityUnits: 4,
            WriteCapacityUnits: 2,
          },
          TableName: usersTableName,
        },
      },
      SessionsDynamoDBTable: {
        Type: "AWS::DynamoDB::Table",
        Properties: {
          AttributeDefinitions: [
            {
              AttributeName: "message_id",
              AttributeType: "S",
            },
            {
              AttributeName: "session_id",
              AttributeType: "S",
            },
            {
              AttributeName: "timestamp",
              AttributeType: "N",
            },
          ],
          KeySchema: [
            {
              AttributeName: "message_id",
              KeyType: "HASH",
            },
          ],
          ProvisionedThroughput: {
            ReadCapacityUnits: 2,
            WriteCapacityUnits: 2,
          },
          TableName: sessionsTableName,
          GlobalSecondaryIndexes: [
            {
              IndexName: "SessionIdTimestampIndex",
              KeySchema: [
                {
                  AttributeName: "session_id",
                  KeyType: "HASH",
                },
                {
                  AttributeName: "timestamp",
                  KeyType: "RANGE",
                },
              ],
              Projection: {
                ProjectionType: "ALL",
              },
              ProvisionedThroughput: {
                ReadCapacityUnits: 2,
                WriteCapacityUnits: 2,
              },
            },
          ],
        },
      },
    },
  },
  package: {
    individually: true,
    exclude: [
      '.serverless/**',
      'src/python/**',
    ],
    include: [
      '.venv/lib/python3.8/site-packages/pydantic/**',
      '.venv/lib/python3.8/site-packages/pydantic_core/**',
    ],
  },
};

if (process.env.IS_OFFLINE && process.env.IS_OFFLINE !== 'false') {
  console.log("I'm OFFLINE")
  serverlessConfiguration.plugins = [
    'serverless-python-requirements',
    'serverless-wsgi',
    'serverless-offline',
    'serverless-dynamodb-local',
    // 'serverless-dotenv-plugin'
  ]
  serverlessConfiguration.functions.app = {
    handler: 'wsgi_handler.handler',
    timeout: 300,
    events: [
      { http: 'ANY /' },
      { http: 'ANY {proxy+}' },
    ],
  };
} else {
  console.log("I'm ONLINE")
  serverlessConfiguration.plugins = [
    'serverless-python-requirements'
  ]
  serverlessConfiguration.functions.appTFY = {
    image: {
      name: 'appimage',
    },
    timeout: 300,
    events: [
      { http: 'ANY /' },
      { http: 'ANY {proxy+}' },
    ],
  };
}

module.exports = serverlessConfiguration;