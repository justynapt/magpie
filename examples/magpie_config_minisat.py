import argparse
import configparser
import pathlib

import magpie


# ================================================================================
# Experimental protocol
# ================================================================================

from bin.magpie_runtime import ExpProtocol


# ================================================================================
# Target software specifics
# ================================================================================

class MyEngine(magpie.params.ConfigFileParamsEngine):
    CLI_PREFIX = '-'
    CLI_GLUE = '='
    CLI_BOOLEAN = 'prefix'
    CLI_BOOLEAN_PREFIX_TRUE = ''
    CLI_BOOLEAN_PREFIX_FALSE = 'no-'

    @classmethod
    def resolve_cli_param(cls, all_params, param, value):
        # special parameters
        if param == 'sub-lim-unbounded':
            return ''
        if param == 'sub-lim':
            if all_params['sub-lim-unbounded'] == 'True':
                return '-sub-lim=-1'
        if param == 'cl-lim-unbounded':
            return ''
        if param == 'cl-lim':
            if all_params['cl-lim-unbounded'] == 'True':
                return '-cl-lim=-1'

        # all other parameters
        return super().resolve_cli_param(all_params, param, value)


class MyProgram(magpie.base.Program):
    def __init__(self, config):
        self.base_init(config['program']['path'])
        self.possible_edits = [
            magpie.params.ParamSetting,
        ]
        self.target_files = config['program']['target_files'].split()
        self.compile_cmd = config['exec']['compile']
        self.test_cmd = config['exec']['test']
        self.run_cmd = config['exec']['run']
        self.reset_timestamp()
        self.reset_logger()
        self.reset_contents()

    def get_engine(self, target_file):
        return MyEngine

    def process_run_exec(self, run_result, exec_result):
        run_result.fitness = round(exec_result.runtime, 4)


# ================================================================================

from bin.magpie_runtime import apply_global_config


# ================================================================================
# Main function
# ================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MAGPIE Runtime Example')
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
