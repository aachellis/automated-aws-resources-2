#!/usr/bin/env python3
import os
import logging
import json

import aws_cdk as cdk

from stack import AutomatedPipelineStack

logging.basicConfig(
    level = logging.INFO,
    format= '%(levelname)s %(asctime)s \t %(name)s - > %(message)s'
)

with open("configuarions.json") as f:
    conf = json.load(f)

pipeline_name = os.environ.get("PIPELINE_NAME", "AutomatedResoursesPipeline")
pipeline_name_conf = conf["name"].replace(' ', '-')
default_description = f"""'{pipeline_name}/{pipeline_name_conf}' pipeline resources"""

app = cdk.App()
AutomatedPipelineStack(app, "TempInitDictStack",
                       conf,
                       pipeline_name_conf,
                       env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
                       description = conf.get("description", default_description)
    )

app.synth()
