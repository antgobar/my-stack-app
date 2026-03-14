import * as cdk from 'aws-cdk-lib/core';
import { Template } from 'aws-cdk-lib/assertions';
import { InfrastructureStack } from '../lib/infrastructure-stack';

describe('InfrastructureStack', () => {
  let template: Template;

  beforeAll(() => {
    const app = new cdk.App();
    const stack = new InfrastructureStack(app, 'TestStack', {
      env: { account: '123456789012', region: 'eu-west-1' },
    });
    template = Template.fromStack(stack);
  });

  test('matches snapshot', () => {
    const json = template.toJSON();

    for (const [, resource] of Object.entries(json.Resources ?? {})) {
      stripAssetHashes(resource);
    }

    expect(json).toMatchSnapshot();
  });

  test('creates a VPC with no NAT gateways', () => {
    template.resourceCountIs('AWS::EC2::VPC', 1);
    template.resourceCountIs('AWS::EC2::NatGateway', 0);
  });

  test('creates public subnets in 2 AZs', () => {
    template.resourceCountIs('AWS::EC2::Subnet', 2);
  });

  test('creates an ECS cluster', () => {
    template.resourceCountIs('AWS::ECS::Cluster', 1);
  });

  test('creates a Fargate service with expected configuration', () => {
    template.hasResourceProperties('AWS::ECS::Service', {
      LaunchType: 'FARGATE',
      DesiredCount: 1,
      DeploymentConfiguration: {
        MinimumHealthyPercent: 100,
      },
    });
  });

  test('task definition has correct CPU and memory', () => {
    template.hasResourceProperties('AWS::ECS::TaskDefinition', {
      Cpu: '256',
      Memory: '512',
    });
  });

  test('container listens on port 8000 with production env vars', () => {
    template.hasResourceProperties('AWS::ECS::TaskDefinition', {
      ContainerDefinitions: [
        {
          PortMappings: [{ ContainerPort: 8000 }],
          Environment: [
            { Name: 'ENVIRONMENT', Value: 'production' },
            { Name: 'DEBUG', Value: 'false' },
          ],
        },
      ],
    });
  });

  test('ALB health check targets /health', () => {
    template.hasResourceProperties('AWS::ElasticLoadBalancingV2::TargetGroup', {
      HealthCheckPath: '/health',
      Matcher: { HttpCode: '200' },
    });
  });

  test('creates a public-facing ALB', () => {
    template.hasResourceProperties('AWS::ElasticLoadBalancingV2::LoadBalancer', {
      Scheme: 'internet-facing',
    });
  });

  test('outputs the load balancer DNS name', () => {
    const outputs = template.toJSON().Outputs ?? {};
    const dnsOutput = Object.values(outputs).find(
      (o: any) => o.Description?.includes('ALB DNS name'),
    );
    expect(dnsOutput).toBeDefined();
  });
});

function stripAssetHashes(obj: any): void {
  if (obj == null || typeof obj !== 'object') return;
  for (const [key, value] of Object.entries(obj)) {
    if (typeof value === 'string' && /^[a-f0-9]{64}\./.test(value)) {
      (obj as any)[key] = value.replace(/^[a-f0-9]{64}/, '<ASSET_HASH>');
    } else {
      stripAssetHashes(value);
    }
  }
}
