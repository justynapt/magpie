import argparse
import configparser
import pathlib

import magpie
import magpie.astor # not by default

from magpie.bin.shared import ExpProtocol
from magpie.bin.shared import apply_global_config


# ================================================================================
# Target software specifics
# ================================================================================

class MyProgram(magpie.base.Program):
    def __init__(self, config):
        self.base_init(config['program']['path'])
        self.possible_edits = [
            magpie.astor.StmtReplacement,
            magpie.astor.StmtInsertion,
            magpie.astor.StmtDeletion,
        ]
        self.target_files = config['program']['target_files'].split()
        self.compile_cmd = config['exec']['compile']
        self.test_cmd = config['exec']['test']
        self.run_cmd = config['exec']['run']
        self.reset_timestamp()
        self.reset_logger()
        self.reset_contents()

    def get_engine(self, target_file):
        return magpie.astor.AstorEngine

    def process_run_exec(self, run_result, exec_result):
        run_result.fitness = round(exec_result.runtime, 4)


# ================================================================================
# Main function
# ================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MAGPIE Astor Runtime Example')
    parser.add_argument('--config', type=pathlib.Path, required=True)
    args = parser.parse_args()

    # read config file
    config = configparser.ConfigParser()
    config.read(args.config)
    apply_global_config(config)

    # setup protocol
    protocol = ExpProtocol()
    protocol.search = magpie.algo.FirstImprovement()
    if 'max_iter' in config['search']:
        protocol.search.stop['steps'] = int(config['search']['max_iter'])
    if 'max_time' in config['search']:
        protocol.search.stop['wall'] = int(config['search']['max_time'])
    protocol.program = MyProgram(config)

    # run experiments
    protocol.run()
