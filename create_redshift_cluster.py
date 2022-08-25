import configparser
import boto3
import json
import time
import argparse

# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# CONFIG VARIABLES
KEY                     = config.get('AWS', 'KEY')
SECRET                  = config.get('AWS', "SECRET")

DWH_CLUSTER_IDENTIFIER  = config.get('DWH', 'DWH_CLUSTER_IDENTIFIER')
DWH_CLUSTER_TYPE        = config.get('DWH', 'DWH_CLUSTER_TYPE')
DWH_NODE_TYPE           = config.get('DWH', 'DWH_NODE_TYPE')
DWH_NUM_NODES           = config.get('DWH', 'DWH_NUM_NODES')
DWH_REGION              = config.get('DWH', 'DWH_REGION')
DWH_IAM_ROLE_NAME       = config.get('DWH', 'DWH_IAM_ROLE_NAME')

IAM_POLICY_ARN          = config.get("IAM_ROLE", 'POLICY_ARN')

DB_NAME                 = config.get('CLUSTER', 'DB_NAME')
DB_USER                 = config.get('CLUSTER', 'DB_USER')
DB_PASSWORD             = config.get('CLUSTER', 'DB_PASSWORD')
DB_PORT                 = config.get('CLUSTER', 'DB_PORT')


def create_dwh_resources():
    """
    Creates EC2, IAM and Redshift resources for the specified AWS region.
    Resources are created by using AWS user's access & secret key (chcek config variables).

    Returns
    -------
    ec2, iam and redshift resource objects.
    """
    
    print('Creating data warehouse resources...')
    
    params = {
        'aws_access_key_id': KEY,
        'aws_secret_access_key' : SECRET,
        'region_name': DWH_REGION
    }
    
    ec2 = boto3.resource('ec2', **params)
#     s3 = boto3.resource('s3', **params)
    iam = boto3.client('iam', **params)
    redshift = boto3.client('redshift', **params)
    
    return ec2, iam, redshift


def create_iam_role(iam):
    """
    Creates iam role and apply specific policy.
    By using iam role name and polucy arn (check config variables).

    Parameters
    ----------
    iam resource object.

    Returns
    -------
    role_arn string value.
    """
    
    try:
        print('Creating new IAM role: {}...'.format(DWH_IAM_ROLE_NAME))
        
        dwh_role = iam.create_role(
            Path = '/',
            RoleName = DWH_IAM_ROLE_NAME,
            Description = 'Allows Redshift clusters to call AWS services on your behalf.',
            AssumeRolePolicyDocument = json.dumps({
                'Statement': [{
                    'Action': 'sts:AssumeRole',
                    'Effect': 'Allow',
                    'Principal': {'Service': 'redshift.amazonaws.com'}}],
                'Version': '2012-10-17'
            })
        )
    except Exception as e:
        print(e)

    print('Attaching policy to IAM role...')
    iam.attach_role_policy(RoleName = DWH_IAM_ROLE_NAME, PolicyArn = IAM_POLICY_ARN)
    
    role_arn = iam.get_role(RoleName = DWH_IAM_ROLE_NAME)['Role']['Arn']
    print('==================================================')
    print('Role ARN: ', role_arn)
    print('==================================================')
    
    return role_arn


def create_redshift_cluster(redshift, role_arn):
    """
    Creates redshift cluster with specified configuration (check config variables).

    Parameters
    ----------
    redshift resource object.
    role_arn string value.
    """
    
    print('Creating cluster {}...'.format(DWH_CLUSTER_IDENTIFIER))
    
    try:
        response = redshift.create_cluster(        
            #HW
            ClusterType = DWH_CLUSTER_TYPE,
            NodeType = DWH_NODE_TYPE,
            NumberOfNodes = int(DWH_NUM_NODES),

            #Identifiers & Credentials
            DBName = DB_NAME,
            ClusterIdentifier = DWH_CLUSTER_IDENTIFIER,
            MasterUsername = DB_USER,
            MasterUserPassword = DB_PASSWORD,

            #Roles (for s3 access)
            IamRoles = [role_arn]  
        )
    except Exception as e:
        print(e)


def open_tcp_port(ec2, vpc_id):
    """
    Opens TCP port to access the cluster with specified port (check config variables).

    Parameters
    ----------
    ec2 resource object.
    vpc_id string value.
    """
    
    print('Open an incoming TCP port to access the cluster ednpoint')
    
    try:
        vpc = ec2.Vpc(id = vpc_id)
        defaultSg = list(vpc.security_groups.all())[0]
        print(defaultSg)
        defaultSg.authorize_ingress(
            GroupName=defaultSg.group_name,
            CidrIp='0.0.0.0/0',
            IpProtocol='TCP',
            FromPort=int(DB_PORT),
            ToPort=int(DB_PORT)
        )
    except Exception as e:
        print(e)


def delete_redshift_cluster(redshift):
    """
    Remove redshift cluster by using the redshift resource object.

    Parameters
    ----------
    redshift resource object.
    """
    
    try:
        redshift.delete_cluster(ClusterIdentifier = DWH_CLUSTER_IDENTIFIER, SkipFinalClusterSnapshot = True,)
        print('Removing Cluster {}...'.format(DWH_CLUSTER_IDENTIFIER))
    except Exception as e:
        print(e)


def delete_iam_role(iam):
    """
    Remove iam role policy and delete iam role by using iam resource object.

    Parameters
    ----------
    iam resource object.
    """
    
    iam.detach_role_policy(RoleName = DWH_IAM_ROLE_NAME, PolicyArn = IAM_POLICY_ARN)
    iam.delete_role(RoleName = DWH_IAM_ROLE_NAME)
    
    print('Removed role {}'.format(DWH_IAM_ROLE_NAME))


def main(args):
    """
    Orchestrate the process of creating and removing the AWS resources.

    Parameters
    ----------
    args object.
    """
        
    ec2, iam, redshift = create_dwh_resources()
        
    if args.delete:
        delete_redshift_cluster(redshift)
        delete_iam_role(iam)
        
        print('AWS resources removed.')
    else:
        role_arn = create_iam_role(iam)
        create_redshift_cluster(redshift, role_arn)

        sleeptime = 10
        for _ in range(int(600 / sleeptime)):
            cluster = redshift.describe_clusters(ClusterIdentifier = DWH_CLUSTER_IDENTIFIER)['Clusters'][0]

            if cluster['ClusterStatus'] == 'available':
                break

            print('Cluster status: "{}". Please wait. checking again in {} seconds.'.format(cluster['ClusterStatus'], sleeptime))
            time.sleep(sleeptime)

        if cluster:
            print('==================================================')
            print('Cluster created at {}'.format(cluster['Endpoint']))
            print('==================================================')
            open_tcp_port(ec2, cluster['VpcId'])
        else:
            print("Could not connect to cluster.")


if __name__ == '__main__':
    """
    Entry point of the current script.
    initiate the process.
    """
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-d', '--delete', action='store_true', help="Clean up resources")
    args = parser.parse_args()
    
    main(args)