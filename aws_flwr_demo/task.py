"""aws-flwr-demo: A Flower / NumPy app using data from S3."""

import boto3

import numpy as np
import pandas as pd

from io import StringIO
from datasets import Dataset
from flwr_datasets.partitioner import IidPartitioner

# We cache partitioner, because we are not using a Federated Dataset in this example
# and we assign the loaded dataset from S3 to the `partitioner.dataset` property
partitioner = None

# This information is needed to create a correct scikit-learn model for the iria dataset
FEATURES = ["SepalLengthCm", "SepalWidthCm", "PetalLengthCm", "PetalWidthCm"]
LABEL = "Species"

def get_dummy_model():
    return np.ones((1, 1))

def load_file_from_s3(
        aws_access_key_id: str,
        aws_secret_access_key: str,
        aws_region: str,
        aws_s3_bucket: str,
        aws_s3_file: str
    ) -> pd.DataFrame:

    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region
    )

    # To download the file and save it the local file system, simply run
    # s3_client.download_file(bucket, key, local_filename)

    # Get the object from S3
    response = s3_client.get_object(
        Bucket=aws_s3_bucket,
        Key=aws_s3_file)

    # Read the object's body (a bytes stream) as text
    csv_content = response['Body'].read().decode('utf-8')

    # Use StringIO to load it into pandas
    df = pd.read_csv(StringIO(csv_content), header=0)

    return df


def load_data(
        partition_id: int,
        num_partitions: int,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        aws_region: str,
        aws_s3_bucket: str,
        aws_s3_file: str
    ):
    """Load data from S3 and use Random partitioner."""
    # Only initialize `FederatedDataset` once
    global partitioner
    if partitioner is None:
        partitioner = IidPartitioner(
            num_partitions=num_partitions)
        s3_data_df = load_file_from_s3(
            aws_access_key_id,
            aws_secret_access_key,
            aws_region,
            aws_s3_bucket,
            aws_s3_file)

        # This will perform Label Encoding using pandas
        # Iris-setosa → 0
        # Iris-versicolor → 1
        # Iris-virginica → 2
        s3_data_df[f"{LABEL}_encoded"], labels = pd.factorize(s3_data_df['Species'])
        s3_data_df[LABEL] = s3_data_df[f"{LABEL}_encoded"].astype(float)
        s3_data_df.drop([f"{LABEL}_encoded"], axis=1, inplace=True)

        dataset = Dataset.from_pandas(s3_data_df)
        partitioner.dataset = dataset

    partition = partitioner.load_partition(partition_id)

    # this was failing ... w/ `{ValueError}ValueError("invalid literal for int() with base 10: 'SepalWidthCm'")` Error
    # X = partition[FEATURES]
    X = []
    for row in partition:
        X.append([row[col] for col in FEATURES])

    y = partition[LABEL]
    # Split the data: 80% train, 20% test
    X_train, X_test = X[: int(0.8 * len(X))], X[int(0.8 * len(X)) :]
    y_train, y_test = y[: int(0.8 * len(y))], y[int(0.8 * len(y)) :]
    return X_train, y_train, X_test, y_test
