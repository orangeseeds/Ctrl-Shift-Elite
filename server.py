from flwr import server, common
import sys
import numpy as np
from typing import List


class SaveModelStrategy(server.strategy.FedAvg):
    def aggregate_fit(
        self,
        rnd,
        results,
        failures
    ):
        aggregated_weights, _ = super().aggregate_fit(rnd, results, failures)
        if aggregated_weights is not None:

            weights: List[np.ndarray] = common.parameters_to_ndarrays(
                aggregated_weights)
            print(f"Saving round {rnd} aggregated_weights...")
            np.savez(f"./models/round-{rnd}-weights.npz", *weights)
        return aggregated_weights, _


strategy = SaveModelStrategy()
'''
server.start_server(
    server_address='localhost:8001',
    config=server.ServerConfig(num_rounds=2),
    grpc_max_message_length=1024*1024*1024,
    strategy=strategy
)

'''
