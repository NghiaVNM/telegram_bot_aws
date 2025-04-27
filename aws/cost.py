import boto3
from config.setting import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
from datetime import datetime

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

ce_client = session.client('ce')

def get_monthly_cost():
    today =datetime.utcnow().date()
    start_of_month = today.replace(day=1)

    response = ce_client.get_cost_and_usage(
        TimePeriod={
            'Start': start_of_month.strftime('%Y-%m-%d'),
            'End': today.strftime('%Y-%m-%d')
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost']
    )

    amount = response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']
    currency = response['ResultsByTime'][0]['Total']['UnblendedCost']['Unit']
    return f'{amount} {currency}'