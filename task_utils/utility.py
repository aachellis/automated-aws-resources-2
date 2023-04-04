import aws_cdk.aws_stepfunctions as sfn
import aws_cdk.aws_stepfunctions_tasks as tasks

def create_glue_job_task(stack, name, glue_job, job_conf):
    return tasks.GlueStartJobRun(
        stack, name + "-" + glue_job.name + "-task",
        glue_job_name = glue_job.name,
        integration_pattern=sfn.IntegrationPattern.RUN_JOB
    ) 

def create_invoke_lambda(stack, name, function, job_conf):
    return tasks.LambdaInvoke(
        stack, name + "-" + function.function_name + "-task",
        lambda_function=function
    )

def create_step_function(stack, conf, conf_name):
    parallels = []
    for state in conf["states"]:
        if len(state["jobs"]) == 1:
            job = state["jobs"][0]
            job_conf = stack.get_resource(job["entity"])
            if job_conf[1] == "glue_job":
                task = create_glue_job_task(stack, conf_name, job_conf[0], job)
            elif job_conf[1] == "lambda_function":
                task = create_invoke_lambda(stack, conf_name, job_conf[0], job)
            parallels.append(task)
        else:
            parallel = sfn.Parallel(stack, state["name"], result_path=sfn.JsonPath.DISCARD, comment=state.get("comment", "job Stage"))
            for job in state["jobs"]:
                job_conf = stack.get_resource(job["entity"])
                if job_conf[1] == "glue_job":
                    task = create_glue_job_task(stack, conf_name, job_conf[0], job)
                elif job_conf[1] == "lambda_function":
                    task = create_invoke_lambda(stack, conf_name, job_conf[0], job)
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
