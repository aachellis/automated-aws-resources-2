from aws_cdk import Stack
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_iam as iam
import uuid
from utils.utility import create_aws_resources, create_step_function

class AutomatedPipelineStack(Stack):

    def __init__(self, scope, id, conf, conf_name, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.resources = {}

        self.role = iam.Role(
            self, "my-role",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("glue.amazonaws.com"), 
                iam.ServicePrincipal("lambda.amazonaws.com"), 
                iam.ServicePrincipal("states.amazonaws.com")
            ),
        )
        self.role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess"))

        self.create_aws_resources(conf, conf_name) 
        self.create_step_function(conf, conf_name)

    def add_resource(self, name, resource, type):
        self.resources[name] = (resource, type)

    def get_resource(self, name):
        return self.resources[name]
        
    def create_aws_resources(self, conf, conf_name):
        create_aws_resources(self, conf, conf_name) 

    def create_step_function(self, conf, conf_name):
        create_step_function(self, conf, conf_name)