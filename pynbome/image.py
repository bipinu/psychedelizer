#!/usr/bin/env python

import os
import random
import pkgutil
import importlib

from wand.image import Image as Wand

DATA_DIR = 'data'

class NoImage(Exception):
    def __str__(self):
        return 'No suitiable image or filename were specified'
      
class NoFilter(Exception):
    def __str__(self):
        return 'No filter for image processing'


class Image(object):
    
    STATE_PATTERNS = 'patterns'
    STATE_FILTERS = 'filters'
    
    def __init__(self, img=None, filename=None):
        self.img = img if img is not None else Wand(filename=filename)
        
        if not self.img:
            raise NoImage
          
        self.state = {
            self.STATE_PATTERNS: [],
            self.STATE_FILTERS: []
        }
        
    @property
    def image(self):
        return self.img

    def get_state(self):
        return self.state
      
    def save_state(self, state_type, state_value):
        assert state_type in self.state, 'No such state type'
        
        self.state[state_type].append(state_value)
      
    def size(self):
        return self.img.size
        
    def resize(self, width=None, height=None):
        self.img.resize(width, height)

    def combine(self, pattern_name=None):
        if pattern_name is None:
            pattern_name = random.choice(self.list_patterns())
        
        pattern_filename = os.path.join(DATA_DIR, pattern_name)
            
        with Wand(filename=pattern_filename) as fg_img:
            width, height = fg_img.size
            self.img.crop(width=width, height=height)
    
            self.img.composite(fg_img, 0, 0)
            
            self.save_state(self.STATE_PATTERNS, pattern_name)
        
    def psychedelic(self, filter_name=None, filter_module=None):
        if filter_module is not None:
            image_filter = filter_module
        elif filter_name is not None:
            image_filter = self.get_filter(filter_name)
        else:
            image_filter = self.get_filter(random.choice(self.list_filters()))
        
        self.img = image_filter.apply_filter(self.img)
        
        self.save_state(self.STATE_FILTERS, image_filter)
          
    def save(self, filename):
        self.img.save(filename=filename)
          
    def get_filter(self, filter_name):
        return importlib.import_module('filters.%s'%filter_name)
          
    def list_filters(self):
        return [name for _, name, _ in pkgutil.iter_modules(['filters'])]
      
    def list_patterns(self):
        return os.listdir(DATA_DIR)
      
