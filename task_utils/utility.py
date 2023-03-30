import aws_cdk.aws_stepfunctions as sfn
import aws_cdk.aws_stepfunctions_tasks as tasks

def create_glue_job_task(stack, name, glue_job):
    return tasks.GlueStartJobRun(
        stack, name + "-" + glue_job.name + "-task",
        glue_job_name = glue_job.name
    ) 

def create_invoke_lambda(stack, name, function):
    return tasks.LambdaInvoke(
        stack, name + "-" + function.function_name + "-task",
        lambda_function=function
    )
