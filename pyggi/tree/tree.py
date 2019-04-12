import os
import ast
import astor
import random
from abc import abstractmethod
from .engine import AstorEngine#, SrcMLEngine
from ..base import AbstractProgram, AbstractEdit
from ..utils import get_file_extension

class TreeProgram(AbstractProgram):
    @classmethod
    def get_engine(cls, file_name):
        extension = get_file_extension(file_name)
        if extension in ['.py']:
            return AstorEngine
        # elif extension in ['.java', '.cpp']:
        #     return SrcMLEngine
        else:
            raise Exception('{} file is not supported'.format(extension))

"""
Possible Edit Operators
"""

class TreeEdit(AbstractEdit):
    @property
    def domain(self):
        return TreeProgram

class StmtReplacement(TreeEdit):
    def __init__(self, target, ingredient):
        self.target = target
        self.ingredient = ingredient

    def apply(self, program, new_contents, modification_points):
        engine = program.engines[self.target[0]]
        assert engine == program.engines[self.ingredient[0]]
        return engine.do_replace(program, self, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, method='random'):
        return cls(program.random_target(target_file, method),
                   program.random_target(ingr_file, 'random'))

class StmtInsertion(TreeEdit):
    def __init__(self, target, ingredient, direction='before'):
        assert direction in ['before', 'after']
        self.target = target
        self.ingredient = ingredient
        self.direction = direction

    def apply(self, program, new_contents, modification_points):
        engine = program.engines[self.target[0]]
        assert engine == program.engines[self.ingredient[0]]
        return engine.do_insert(program, self, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, direction='before', method='random'):
        return cls(program.random_target(target_file, method),
                   program.random_target(ingr_file, 'random'),
                   direction)

class StmtDeletion(TreeEdit):
    def __init__(self, target):
        self.target = target

    def apply(self, program, new_contents, modification_points):
        engine = program.engines[self.target[0]]
        return engine.do_delete(program, self, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, method='random'):
        return cls(program.random_target(target_file, method))

class StmtMoving(TreeEdit):
    def __init__(self, target, ingredient, direction='before'):
        assert direction in ['before', 'after']
        self.target = target
        self.ingredient = ingredient
        self.direction = direction

    def apply(self, program, new_contents, modification_points):
        engine = program.engines[self.target[0]]
        assert engine == program.engines[self.ingredient[0]]
        engine.do_insert(program, self, new_contents, modification_points)
        return engine.do_delete(program, self, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, direction='before', method='random'):
        return cls(program.random_target(target_file, method),
                   program.random_target(ingr_file, 'random'),
                   direction)