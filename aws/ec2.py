import boto3
from config.setting import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed
from botocore.exceptions import ClientError


session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

ec2_client = session.client('ec2')

def find_instance_region(instance_id):
    ec2_client_global = session.client('ec2', region_name='us-east-1')
    regions_response = ec2_client_global.describe_regions(AllRegions=True)

    regions = [region['RegionName'] for region in regions_response['Regions']]

    def check_region(region):
        try:
            ec2_client = session.client('ec2', region_name=region)
            response = ec2_client.describe_instances(InstanceIds=[instance_id])
            reservations = response.get('Reservations', [])
            if reservations:
                return region
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['InvalidInstanceID.NotFound', 'AuthFailure']:
                return None
            else:
                print(f"Unexpected error checking instance in {region}: {str(e)}")
                return None
        except Exception as e:
            print(f"General error checking {region}: {str(e)}")
            return None


    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(check_region, region): region for region in regions}
        for future in as_completed(futures):
            region_found = future.result()
            if region_found:
                return region_found
    return None

def start_instance(instance_id):
    region = find_instance_region(instance_id)
    if not region:
        return f"❌ Instance ID {instance_id} not found in any region."

    ec2_client = session.client('ec2', region_name=region)
    ec2_client.start_instances(InstanceIds=[instance_id])
    return f"▶️ Started instance {instance_id} in region {region}"

def stop_instance(instance_id):
    region = find_instance_region(instance_id)
    if not region:
        return f"❌ Instance ID {instance_id} not found in any region."
    ec2_client = session.client('ec2', region_name=region)
    ec2_client.stop_instances(InstanceIds=[instance_id])
    return f"⏹️ Stopped instance {instance_id} in region {region}"

def fetch_running_instances(region_name):
    try:
        ec2_client = session.client('ec2', region_name=region_name)
        reservations = ec2_client.describe_instances(
            Filters=[
                {'Name': 'instance-state-name', 'Values': ['running']}
            ]
        ).get('Reservations', [])

        instances = []
        for reservation in reservations:
            for instance in reservation.get('Instances', []):
                instance_id = instance['InstanceId']
                public_ip = instance.get('PublicIpAddress', 'N/A')
                name_tag = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'Unnamed')
                instances.append(f"{region_name} - {instance_id} ({name_tag}) - {public_ip}")
        return instances
    except Exception as e:
        print(f"Could not fetch running instances in {region_name}: {e}")
        return []

def list_running_instances():
    ec2_global_client = session.client('ec2', region_name="us-east-1")
    regions = [region['RegionName'] for region in ec2_global_client.describe_regions(AllRegions=True)['Regions']]
    
    instances_list = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(fetch_running_instances, regions)

    for region_instances in results:
        instances_list.extend(region_instances)

    return instances_list

def fetch_instances(region_name):
    ec2_client = session.client('ec2', region_name=region_name)
    instances = []

    try:
        response = ec2_client.describe_instances()
        reservations = response.get('Reservations', [])

        for reservation in reservations:
            for instance in reservation.get('Instances', []):
                instance_id = instance.get('InstanceId')
                state = instance.get('State', {}).get('Name')
                tags = instance.get('Tags', [])
                name = next((tag['Value'] for tag in tags if tag['Key'] == 'Name'), None)
                name_text = f"[Name: {name}]" if name else "[No Name]"
                instances.append(f"{instance_id} ({state}) {name_text}")
    except Exception as e:
        print(f"Error fetching instances from {region_name}: {str(e)}")

    return region_name, instances


def list_all_instances_across_regions():
    ec2_client_global = session.client('ec2', region_name='us-east-1')
    regions_response = ec2_client_global.describe_regions(AllRegions=True)

    regions = [region['RegionName'] for region in regions_response['Regions']]

    region_instance_map = {}

    def fetch_instances(region_name):
        ec2_client = session.client('ec2', region_name=region_name)
        instances = []
        try:
            response = ec2_client.describe_instances()
            reservations = response.get('Reservations', [])
            for reservation in reservations:
                for instance in reservation.get('Instances', []):
                    instance_id = instance.get('InstanceId')
                    state = instance.get('State', {}).get('Name')

                    tags = instance.get('Tags', [])
                    name = next((tag['Value'] for tag in tags if tag['Key'] == 'Name'), None)
                    name_text = f"[Name: {name}]" if name else "[No Name]"

                    public_ip = instance.get('PublicIpAddress', None)
                    ip_text = f"[IP: {public_ip}]" if public_ip else ""

                    instances.append(f"{instance_id} ({state}) {name_text} {ip_text}".strip())

        except Exception:
            pass

        return region_name, instances

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_instances, region): region for region in regions}
        for future in as_completed(futures):
            region_name, instances = future.result()
            if instances:
                region_instance_map[region_name] = instances

    if not region_instance_map:
        return ["No instances found."]

    # Format kết quả
    formatted_list = []
    for region, instances in region_instance_map.items():
        formatted_list.append(f"🌍 Region: {region}")
        for instance in instances:
            formatted_list.append(f" - {instance}")
        formatted_list.append("") 

    return formatted_list