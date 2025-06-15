"""aws-flwr-demo: A Flower / NumPy app using data from S3."""

from flwr.client import ClientApp, NumPyClient
from flwr.common import Context
from aws_flwr_demo.task import get_dummy_model, load_data


class FlowerClient(NumPyClient):

    def fit(self, parameters, config):
        model = get_dummy_model()
        return [model], 1, {}

    def evaluate(self, parameters, config):
        return float(0.0), 1, {"accuracy": float(1.0)}


def client_fn(context: Context):
    X_train, y_train, X_test, y_test = load_data(
        partition_id=context.node_config["partition-id"],
        num_partitions=context.node_config["num-partitions"],
        aws_access_key_id=context.run_config["aws-access-key-id"],
        aws_secret_access_key=context.run_config["aws-secret-access-key"],
        aws_region=context.run_config["aws-region"],
        aws_s3_bucket=context.run_config["aws-s3-bucket"],
        aws_s3_file=context.run_config["aws-s3-file"],
    )
    print(f"#Train Samples: {len(X_train)}, #Test Samples: {len(X_test)}")
    return FlowerClient().to_client()

# Flower ClientApp
app = ClientApp(client_fn=client_fn)
