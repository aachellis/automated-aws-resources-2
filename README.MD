# Automated AWS Resources
It's an experimentation to create aws resource stacks with the reference of a given text file in json format.

## Components of the json file
It will have the following components
    - __Name:__ It signifies the name of the stack that will comprise the aws resources.
    - __Description:__ _(Optional)_ Gives a short description for the step function.
    - __Region:__ The region os aws account to use.
    - __Resources:__ The aws resources we need to create.
    - __States:__ The orchestration of resources to be included in the step function.

