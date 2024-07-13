import aws_cdk
from constructs import Construct

from aws_cdk import (
    Stack,
    aws_kms as kms,
    aws_s3 as s3,
    RemovalPolicy,
    aws_lambda as lambda_,
)


class GoalieDataEngineering(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        encryption_key = kms.Key(self, "Gl-Eng-Key", enable_key_rotation=True)

        bucket = s3.Bucket(
            self,
            'jk-app-cloud-stats2-bucket-us-east-1',
            encryption_key=encryption_key,
            removal_policy=RemovalPolicy.DESTROY,
            bucket_name='hockey-goalie-engineering-bucket-323-2'
        )

        lambda_.DockerImageFunction(
            self,
            'mp-data-scraper-lambda',
            code=lambda_.DockerImageCode.from_image_asset('./lambda/mp-scraper/'),
            function_name='mp-data-scraper-lambda',
            environment={"bucket": bucket.bucket_name},
            timeout=aws_cdk.Duration.seconds(300),
            memory_size=5000,
            ephemeral_storage_size=aws_cdk.Size.mebibytes(512)
        )
