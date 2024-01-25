"""

Remove those pesky AWS default VPCs.

Python Version: 3.7.0
Boto3 Version: 1.7.50

"""

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os

def delete_igw(ec2, vpc_id):
  """
  Detach and delete the internet gateway
  """

  args = {
    'Filters' : [
      {
        'Name' : 'attachment.vpc-id',
        'Values' : [ vpc_id ]
      }
    ]
  }

  try:
    igw = ec2.describe_internet_gateways(**args)['InternetGateways']
  except ClientError as e:
    print(e.response['Error']['Message'])

  if igw:
    igw_id = igw[0]['InternetGatewayId']

    try:
      ec2.detach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
    except ClientError as e:
      print(e.response['Error']['Message'])

    try:
      ec2.delete_internet_gateway(InternetGatewayId=igw_id)
    except ClientError as e:
      print(e.response['Error']['Message'])

  return


def delete_subs(ec2, args):
  """
  Delete the subnets
  """

  try:
    subs = ec2.describe_subnets(**args)['Subnets']
  except ClientError as e:
    print(e.response['Error']['Message'])

  if subs:
    for sub in subs:
      sub_id = sub['SubnetId']

      try:
        ec2.delete_subnet(SubnetId=sub_id)
      except ClientError as e:
        print(e.response['Error']['Message'])

  return


def delete_rtbs(ec2, args):
  """
  Delete the route tables
  """

  try:
    rtbs = ec2.describe_route_tables(**args)['RouteTables']
  except ClientError as e:
    print(e.response['Error']['Message'])

  if rtbs:
    for rtb in rtbs:
      main = 'false'
      for assoc in rtb['Associations']:
        main = assoc['Main']
      if main == True:
        continue
      rtb_id = rtb['RouteTableId']
        
      try:
        ec2.delete_route_table(RouteTableId=rtb_id)
      except ClientError as e:
        print(e.response['Error']['Message'])

  return


def delete_acls(ec2, args):
  """
  Delete the network access lists (NACLs)
  """

  try:
    acls = ec2.describe_network_acls(**args)['NetworkAcls']
  except ClientError as e:
    print(e.response['Error']['Message'])

  if acls:
    for acl in acls:
      default = acl['IsDefault']
      if default == True:
        continue
      acl_id = acl['NetworkAclId']

      try:
        ec2.delete_network_acl(NetworkAclId=acl_id)
      except ClientError as e:
        print(e.response['Error']['Message'])

  return


def delete_sgps(ec2, args):
  """
  Delete any security groups
  """

  try:
    sgps = ec2.describe_security_groups(**args)['SecurityGroups']
  except ClientError as e:
    print(e.response['Error']['Message'])

  if sgps:
    for sgp in sgps:
      default = sgp['GroupName']
      if default == 'default':
        continue
      sg_id = sgp['GroupId']

      try:
        ec2.delete_security_group(GroupId=sg_id)
      except ClientError as e:
        print(e.response['Error']['Message'])

  return


def delete_vpc(ec2, vpc_id, region, count):
  """
  Delete the VPC
  """

  try:
    ec2.delete_vpc(VpcId=vpc_id)
  except ClientError as e:
    print(e.response['Error']['Message'])
    return False
  else:
    print('#{} - {} has been deleted from the {} region.'.format(count, vpc_id, region))
    return True


def get_regions(ec2):
  """
  Return all AWS regions
  """

  regions = []

  try:
    aws_regions = ec2.describe_regions()['Regions']
  except ClientError as e:
    print(e.response['Error']['Message'])

  else:
    for region in aws_regions:
      regions.append(region['RegionName'])

  return regions

# Function definitions remain the same...

def assume_role(role_arn, session_name):
  """
  Assumes the specified role and returns the temporary credentials.
  """
  sts_client = boto3.client('sts',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.getenv('AWS_SESSION_TOKEN'),  # This may be None if not using session tokens
    region_name=os.getenv('AWS_REGION')
  )
  try:
    assumed_role_object = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName=session_name
    )
    return assumed_role_object['Credentials']
  except ClientError as e:
    print(f"Failed to assume role: {e}")
    exit(1)

def main():
  """
  Do the work..

  Order of operation:

  1.) Delete the internet gateway
  2.) Delete subnets
  3.) Delete route tables
  4.) Delete network access lists
  5.) Delete security groups
  6.) Delete the VPC 
  """

  # AWS Credentials
  # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html

  # Load environment variables from .env.auth file
  dotenv_path = os.path.join(os.path.dirname(__file__), '.env.auth')
  load_dotenv(dotenv_path=dotenv_path)
  
  role_arn = os.getenv('ROLE_ARN')
  session_name = "AssumedRoleSession"

  credentials = assume_role(role_arn, session_name)

  session = boto3.Session(
      aws_access_key_id=credentials['AccessKeyId'],
      aws_secret_access_key=credentials['SecretAccessKey'],
      aws_session_token=credentials['SessionToken'],
      region_name=os.getenv('AWS_REGION')
  )

  ec2 = session.client('ec2', region_name='us-east-1')

  regions = get_regions(ec2)
  deleted_vpcs_count = 1

  for region in regions:

    ec2 = session.client('ec2', region_name=region)

    try:
      attribs = ec2.describe_account_attributes(AttributeNames=[ 'default-vpc' ])['AccountAttributes']
    except ClientError as e:
      print(e.response['Error']['Message'])
      return

    else:
      vpc_id = attribs[0]['AttributeValues'][0]['AttributeValue']

    if vpc_id == 'none':
      print('VPC (default) was not found in the {} region.'.format(region))
      continue

    # Are there any existing resources?  Since most resources attach an ENI, let's check..

    args = {
      'Filters' : [
        {
          'Name' : 'vpc-id',
          'Values' : [ vpc_id ]
        }
      ]
    }

    try:
      eni = ec2.describe_network_interfaces(**args)['NetworkInterfaces']
    except ClientError as e:
      print(e.response['Error']['Message'])
      return

    if eni:
      print('VPC {} has existing resources in the {} region.'.format(vpc_id, region))
      continue

    delete_igw(ec2, vpc_id)
    delete_subs(ec2, args)
    delete_rtbs(ec2, args)
    delete_acls(ec2, args)
    delete_sgps(ec2, args)
    
    if delete_vpc(ec2, vpc_id, region, deleted_vpcs_count):
      deleted_vpcs_count += 1

  return


if __name__ == "__main__":
  main()

