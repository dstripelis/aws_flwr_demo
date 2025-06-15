# aws-flwr-demo: A Flower / NumPy app using data from S3

The current repo is used just to showcase how to interact with S3 and download a file from an S3 bucket and load it into the Flower app to run the application. 

# S3 Configuration

## Create a new Bucket & File
1. Create a bucket in S3 and assign a name, e.g., `aws-flwr-demo`. Please check all default security settings when creating the bucket.
2. Upload the file, e.g., the [IRIS dataset](https://huggingface.co/datasets/scikit-learn/iris)
3. Once the file is uploaded, to enable access to the file it is preferable to create an access policy for the specific file. The policy below grants public get object access (principal is *) to the iris dataset only, not to the entire S3 bucket:
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Statement-Get-Object",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::aws-flwr-demo/iris.csv"
        }
    ]
}
```

## Create a New Account
3. Next to be able to interact with S3 you need to create a new account. To do so, go to the `IAM` settings and create the new user account.
4. Get the AWS Access Key and Secret Access Key
5. Finally, update the `pyproject.toml` file using the credentials and all other fields referring to an exiting or the newly create S3 bucket.      


## Install dependencies and project

```bash
pip install -e .
```

## Run with the Simulation Engine

In the `aws-flwr-demo` directory, use `flwr run` to run a local simulation:

```bash
flwr run .
```
