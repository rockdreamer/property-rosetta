# -*- coding: utf-8 -*-

import pytest
from pathlib import Path
from property_rosetta.validate import main

__author__ = "Claudio Bantaloukas"
__copyright__ = "Claudio Bantaloukas"
__license__ = "new-bsd"


def test_validation():
    with pytest.raises(SystemExit):
        main([])
        assert False
    with pytest.raises(AssertionError):
        main(['invalidpath'])
        assert False
    main([str(Path(__file__).parent / 'data' /
              'dictionary_loading' / 'dictionary_ok' / 'dictionary.yaml')])
