import aws_cdk
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_glue as glue 
import aws_cdk.aws_iam as iam
import aws_cdk.aws_stepfunctions as sfn
import os
import boto3
import shutil
from staging import bucket_name

from task_utils.utility import create_glue_job_task, create_invoke_lambda

s3 = boto3.client("s3", region_name=os.getenv('CDK_DEFAULT_REGION'))

def create_aws_resources(stack, conf, conf_name):
    for resource in conf["resources"]:
        if resource["type"] == "glue_job":
            configuration = resource["configuration"]

            shutil.make_archive("glue_helper", "zip", os.path.join("glue_jobs", configuration["working_directory"]))
            s3.upload_file("glue_helper.zip", bucket_name, "glue_jobs/" + configuration["working_directory"] + "/glue_helper.zip")
            s3.upload_file(os.path.join("glue_jobs", configuration["working_directory"], "glue_main.py"), bucket_name, "glue_jobs/" + configuration["working_directory"] + "/glue_main.py")

            glue_job = glue.CfnJob(
                stack,
                f'{conf_name}-{resource.get("name")}',
                name=resource.get("name"),
                command=glue.CfnJob.JobCommandProperty(
                    name="glueetl",
                    python_version=configuration.get("python_version", "3"),
                    script_location=f"s3://{bucket_name}/glue_jobs/{configuration.get('working_directory')}/glue_main.py",
                ),
                default_arguments={
                    "--extra-py-files": f"s3://{bucket_name}/glue_jobs/{configuration.get('working_directory')}/glue_helper.zip",
                    "--enable-glue-datacatalog": "",
                    "--enable-metrics": "",
                    "--enable-continuous-cloudwatch-log": "true",
                    "--BUCKET_NAME": f"{bucket_name}",
                    "--ISGLUERUNTIME": "True"
                },
                timeout=int(configuration.get("timeout", 20)),
                glue_version=configuration.get("glue_version", "2.0"),
                number_of_workers=int(configuration.get("num_workers", 10)),
                execution_property=glue.CfnJob.ExecutionPropertyProperty(max_concurrent_runs=int(configuration.get("max_concurrent_runs", 1))),
                worker_type=configuration.get("properties", {}).get("worker_type", "G.1X"),
                role=stack.role.role_arn,
            )
            stack.add_resource(resource["name"], glue_job, "glue_job")

        if resource["type"] == "lambda_function":
            configuration = resource["configuration"]

            shutil.make_archive("lambda_zip", "zip", os.path.join("glue_jobs", configuration["working_directory"]))
            s3.upload_file("lambda_zip.zip", bucket_name, "lambda_functions/" + configuration["working_directory"] + "/lambda_zip.zip")

            lambda_function = lambda_.Function(
                stack,
                f'{conf_name}-{resource.get("name")}',
                code = lambda_.Code.from_asset(path = os.path.join("lambda_functions", configuration["working_directory"])),
                handler = configuration.get("file_name", "lambda_module") + "." + configuration.get("handler", "handler"),
                runtime = lambda_.Runtime(configuration.get("runtime", "python3.7")),
                timeout = aws_cdk.Duration.seconds(configuration.get("timeout", "timeout")),
                function_name = f'{conf_name}-{resource.get("name")}'
            )

            principal = iam.ArnPrincipal(stack.role.role_arn)

            lambda_function.add_permission(f'{conf_name}-{resource.get("name")}-role', principal=principal, action="lambda:*")
            stack.add_resource(resource["name"], lambda_function, "lambda_function")

def create_step_function(stack, conf, conf_name):
    parallels = []
    for state in conf["states"]:
        if len(state["jobs"]) == 1:
            job = state["jobs"][0]
            job_conf = stack.get_resource(job["name"])
            if job_conf[1] == "glue_job":
                task = create_glue_job_task(stack, conf_name, job_conf[0])
            elif job_conf[1] == "lambda_function":
                task = create_invoke_lambda(stack, conf_name, job_conf[0])
            parallels.append(task)
        else:
            parallel = sfn.Parallel(stack, state["name"], result_path=sfn.JsonPath.DISCARD, comment=state.get("comment", "job Stage"))
            for job in state["jobs"]:
                job_conf = stack.get_resource(job["name"])
                if job_conf[1] == "glue_job":
                    task = create_glue_job_task(stack, conf_name, job_conf[0])
                elif job_conf[1] == "lambda_function":
                    task = create_invoke_lambda(stack, conf_name, job_conf[0])
                parallel.branch(task)
                
            parallels.append(parallel)

    definition = parallels[0]
    if len(parallels) > 1:
        for item in reversed(parallels[1:]):
            definition = definition.next(item)

    machine = sfn.StateMachine(
        stack, 
        conf_name,
        definition=definition,
        role=stack.role
    )

    stack.resources["state_machine"] = machine

